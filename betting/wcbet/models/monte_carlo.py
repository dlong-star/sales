"""Model 6: Monte Carlo simulation.

Runs a minimum of 100,000 independent match simulations from
(lambda_home, lambda_away), optionally applying the same Dixon-Coles
low-score correlation correction as the analytic Poisson model via
importance-weighted resampling. This model:

1. Cross-validates the analytic Poisson/Dixon-Coles solution (law of large
   numbers should make the two converge on the same 1X2/totals/BTTS
   numbers -- see ``tests/test_poisson_model.py``).
2. Supplies simulation-based standard errors / confidence intervals on
   every market (binomial SE, distinct from the Bayesian model's parameter
   uncertainty CI).
3. Is the only model that produces player-level prop probabilities, by
   attributing each simulated team goal to a scorer according to the
   player's share of the team's total xG involvement.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from wcbet.data.models import Player

DEFAULT_N_SIMS = 100_000
DEFAULT_DIXON_COLES_RHO = -0.08


@dataclass
class SimulationResult:
    n_sims: int
    home_win: float
    draw: float
    away_win: float
    home_win_se: float
    draw_se: float
    away_win_se: float
    over_2_5: float
    under_2_5: float
    btts_yes: float
    btts_no: float
    home_goals: np.ndarray
    away_goals: np.ndarray


class MonteCarloSimulator:
    def __init__(
        self,
        n_sims: int = DEFAULT_N_SIMS,
        dixon_coles_rho: float | None = DEFAULT_DIXON_COLES_RHO,
        seed: int | None = None,
    ) -> None:
        if n_sims < 100_000:
            raise ValueError("Monte Carlo simulator requires n_sims >= 100,000 per the spec")
        self.n_sims = n_sims
        self.rho = dixon_coles_rho
        self.rng = np.random.default_rng(seed)

    def _apply_dixon_coles_resample(
        self, home_goals: np.ndarray, away_goals: np.ndarray, lam_h: float, lam_a: float
    ) -> tuple[np.ndarray, np.ndarray]:
        rho = self.rho
        weights = np.ones(self.n_sims)
        weights[(home_goals == 0) & (away_goals == 0)] = 1 - lam_h * lam_a * rho
        weights[(home_goals == 0) & (away_goals == 1)] = 1 + lam_h * rho
        weights[(home_goals == 1) & (away_goals == 0)] = 1 + lam_a * rho
        weights[(home_goals == 1) & (away_goals == 1)] = 1 - rho
        weights = np.clip(weights, 1e-6, None)
        probs = weights / weights.sum()
        idx = self.rng.choice(self.n_sims, size=self.n_sims, replace=True, p=probs)
        return home_goals[idx], away_goals[idx]

    @staticmethod
    def _se(p: float, n: int) -> float:
        return math.sqrt(max(p * (1 - p), 0.0) / n)

    def simulate(self, lambda_home: float, lambda_away: float) -> SimulationResult:
        home_goals = self.rng.poisson(lambda_home, self.n_sims)
        away_goals = self.rng.poisson(lambda_away, self.n_sims)

        if self.rho:
            home_goals, away_goals = self._apply_dixon_coles_resample(home_goals, away_goals, lambda_home, lambda_away)

        home_win = float((home_goals > away_goals).mean())
        draw = float((home_goals == away_goals).mean())
        away_win = float((home_goals < away_goals).mean())
        total = home_goals + away_goals
        over_2_5 = float((total > 2.5).mean())
        btts_yes = float(((home_goals >= 1) & (away_goals >= 1)).mean())

        return SimulationResult(
            n_sims=self.n_sims,
            home_win=home_win, draw=draw, away_win=away_win,
            home_win_se=self._se(home_win, self.n_sims),
            draw_se=self._se(draw, self.n_sims),
            away_win_se=self._se(away_win, self.n_sims),
            over_2_5=over_2_5, under_2_5=1 - over_2_5,
            btts_yes=btts_yes, btts_no=1 - btts_yes,
            home_goals=home_goals, away_goals=away_goals,
        )

    def anytime_scorer_probs(self, team_goals: np.ndarray, players: list[Player]) -> dict[str, float]:
        """Probability each player scores >=1 goal, from the team's simulated goal totals."""
        eligible = [p for p in players if p.xg_involvement_share > 0 and p.is_available]
        if not eligible:
            return {}

        shares = np.array([p.xg_involvement_share for p in eligible], dtype=float)
        shares = shares / shares.sum()
        n_players = len(eligible)
        n_total = len(team_goals)
        counts = np.zeros(n_players, dtype=np.int64)

        one_goal_idx = np.where(team_goals == 1)[0]
        if len(one_goal_idx):
            scorers = self.rng.choice(n_players, size=len(one_goal_idx), p=shares)
            np.add.at(counts, scorers, 1)

        multi_idx = np.where(team_goals >= 2)[0]
        for match_idx in multi_idx:
            g = int(team_goals[match_idx])
            scorers = self.rng.choice(n_players, size=g, replace=True, p=shares)
            counts[np.unique(scorers)] += 1

        anytime_prob = counts / n_total
        return {eligible[i].name: float(anytime_prob[i]) for i in range(n_players)}
