"""Model 4: Bayesian probability model.

Treats each team's attack and defense goal rates as Gamma-distributed
random variables with a conjugate Gamma prior centered on the league
average, updated with the team's trailing-20-match sample (a separate,
larger window than the multi-window blend Model 2 uses, so the two models
bring genuinely different information into the ensemble).

For each fixture we draw posterior samples of the four relevant rates
(home attack, home defense, away attack, away defense), combine them into
matched (lambda_home, lambda_away) pairs, and compute the analytic Poisson
outcome probabilities for every pair. Averaging over samples gives the
posterior-predictive point estimate; the spread across samples gives a
genuine Bayesian credible interval on the probability itself (parameter
uncertainty), distinct from the simulation noise the Monte Carlo model
reports.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.stats import poisson

from wcbet.data.models import TeamStats

DEFAULT_LEAGUE_AVG_GOALS = 1.35
DEFAULT_PRIOR_MATCHES = 8.0  # prior strength, in "pseudo-matches"
DEFAULT_WINDOW_MATCHES = 20


@dataclass
class BayesianMatchEstimate:
    home_mean: float
    draw_mean: float
    away_mean: float
    home_ci: tuple[float, float]
    draw_ci: tuple[float, float]
    away_ci: tuple[float, float]
    lambda_home_mean: float
    lambda_away_mean: float


class BayesianGoalModel:
    def __init__(
        self,
        league_avg_goals: float = DEFAULT_LEAGUE_AVG_GOALS,
        prior_matches: float = DEFAULT_PRIOR_MATCHES,
        window_matches: int = DEFAULT_WINDOW_MATCHES,
        home_advantage_pct: float = 0.10,
    ) -> None:
        self.league_avg_goals = league_avg_goals
        self.alpha0 = prior_matches
        self.beta0 = prior_matches / league_avg_goals
        self.window_matches = window_matches
        self.home_advantage_pct = home_advantage_pct

    def _attack_posterior(self, team: TeamStats) -> tuple[float, float]:
        goals_observed = team.last20_xg_for * self.window_matches
        return self.alpha0 + goals_observed, self.beta0 + self.window_matches

    def _defense_posterior(self, team: TeamStats) -> tuple[float, float]:
        goals_observed = team.last20_xg_against * self.window_matches
        return self.alpha0 + goals_observed, self.beta0 + self.window_matches

    def sample_lambdas(
        self,
        home: TeamStats,
        away: TeamStats,
        n_samples: int = 3000,
        neutral: bool = False,
        rng: np.random.Generator | None = None,
    ) -> tuple[np.ndarray, np.ndarray]:
        rng = rng or np.random.default_rng()

        ha_a, ha_b = self._attack_posterior(home)
        hd_a, hd_b = self._defense_posterior(home)
        aa_a, aa_b = self._attack_posterior(away)
        ad_a, ad_b = self._defense_posterior(away)

        home_attack = rng.gamma(ha_a, 1.0 / ha_b, n_samples)
        home_defense = rng.gamma(hd_a, 1.0 / hd_b, n_samples)
        away_attack = rng.gamma(aa_a, 1.0 / aa_b, n_samples)
        away_defense = rng.gamma(ad_a, 1.0 / ad_b, n_samples)

        lam_h = self.league_avg_goals * (home_attack / self.league_avg_goals) * (away_defense / self.league_avg_goals)
        lam_a = self.league_avg_goals * (away_attack / self.league_avg_goals) * (home_defense / self.league_avg_goals)

        if not neutral:
            lam_h = lam_h * (1 + self.home_advantage_pct)
            lam_a = lam_a * (1 - self.home_advantage_pct * 0.5)

        return np.maximum(lam_h, 0.05), np.maximum(lam_a, 0.05)

    def match_probabilities(
        self,
        home: TeamStats,
        away: TeamStats,
        n_samples: int = 3000,
        neutral: bool = False,
        max_goals: int = 10,
        rng: np.random.Generator | None = None,
    ) -> BayesianMatchEstimate:
        rng = rng or np.random.default_rng()
        lam_h, lam_a = self.sample_lambdas(home, away, n_samples, neutral, rng)

        goals = np.arange(max_goals + 1)
        home_p = np.empty(n_samples)
        draw_p = np.empty(n_samples)
        away_p = np.empty(n_samples)
        i_idx, j_idx = np.indices((max_goals + 1, max_goals + 1))

        for k in range(n_samples):
            hp = poisson.pmf(goals, lam_h[k])
            ap = poisson.pmf(goals, lam_a[k])
            mat = np.outer(hp, ap)
            mat = mat / mat.sum()
            home_p[k] = mat[i_idx > j_idx].sum()
            draw_p[k] = mat[i_idx == j_idx].sum()
            away_p[k] = mat[i_idx < j_idx].sum()

        def ci(arr: np.ndarray) -> tuple[float, float]:
            return float(np.percentile(arr, 2.5)), float(np.percentile(arr, 97.5))

        return BayesianMatchEstimate(
            home_mean=float(home_p.mean()),
            draw_mean=float(draw_p.mean()),
            away_mean=float(away_p.mean()),
            home_ci=ci(home_p),
            draw_ci=ci(draw_p),
            away_ci=ci(away_p),
            lambda_home_mean=float(lam_h.mean()),
            lambda_away_mean=float(lam_a.mean()),
        )
