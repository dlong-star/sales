"""Orchestrates the full pipeline for one fixture: run Models 1-6, combine
them into an ensemble, run value detection against the sportsbook line, and
assemble the 10-part output report.
"""
from __future__ import annotations

from dataclasses import replace

import numpy as np

from wcbet.data.models import Fixture, TeamStats
from wcbet.models.bayesian import BayesianGoalModel
from wcbet.models.elo import DEFAULT_HOME_ADVANTAGE, EloModel
from wcbet.models.ensemble import EnsembleModel, MLEnsemble, ModelEstimate
from wcbet.models.goal_expectancy import DEFAULT_HOME_ADVANTAGE_PCT, GoalExpectancyModel, blended_xg
from wcbet.models.monte_carlo import MonteCarloSimulator
from wcbet.models.poisson_model import PoissonModel
from wcbet.report import MatchReport
from wcbet.value.edge import DEFAULT_MAX_DISAGREEMENT, DEFAULT_MIN_EDGE, evaluate_market
from wcbet.value.odds_math import devig_market


def _sensitivity_analysis(
    home: TeamStats, away: TeamStats, neutral: bool,
    elo_model: EloModel, ge_model: GoalExpectancyModel, poisson_model: PoissonModel,
) -> dict[str, tuple[float, float, float]]:
    def run(h: TeamStats, a: TeamStats, neutral_flag: bool) -> tuple[float, float, float]:
        elo_probs = elo_model.match_probabilities(h.elo_rating, a.elo_rating, neutral_site=neutral_flag)
        lam_h, lam_a = ge_model.expected_goals(h, a, neutral=neutral_flag)
        poisson_probs = poisson_model.outcome_probs(poisson_model.score_matrix(lam_h, lam_a))
        return tuple((x + y) / 2 for x, y in zip(elo_probs, poisson_probs))  # type: ignore[return-value]

    scenarios: dict[str, tuple[float, float, float]] = {"baseline": run(home, away, neutral)}
    scenarios["elo_home_+50"] = run(replace(home, elo_rating=home.elo_rating + 50), away, neutral)
    scenarios["elo_home_-50"] = run(replace(home, elo_rating=home.elo_rating - 50), away, neutral)
    scenarios["elo_away_+50"] = run(home, replace(away, elo_rating=away.elo_rating + 50), neutral)
    scenarios["elo_away_-50"] = run(home, replace(away, elo_rating=away.elo_rating - 50), neutral)
    scenarios["home_xg_+10%"] = run(
        replace(home, xg_for_per90=home.xg_for_per90 * 1.1, last5_xg_for=home.last5_xg_for * 1.1,
                last10_xg_for=home.last10_xg_for * 1.1, last20_xg_for=home.last20_xg_for * 1.1),
        away, neutral,
    )
    scenarios["home_xg_-10%"] = run(
        replace(home, xg_for_per90=home.xg_for_per90 * 0.9, last5_xg_for=home.last5_xg_for * 0.9,
                last10_xg_for=home.last10_xg_for * 0.9, last20_xg_for=home.last20_xg_for * 0.9),
        away, neutral,
    )
    if not neutral:
        scenarios["neutral_site"] = run(home, away, True)
    return scenarios


def _key_supporting_factors(home: TeamStats, away: TeamStats, fixture: Fixture) -> list[str]:
    factors = []
    elo_diff = home.elo_rating - away.elo_rating
    factors.append(f"Elo differential: {home.name} {elo_diff:+.0f} vs {away.name}")

    home_atk, _ = blended_xg(home)
    away_atk, _ = blended_xg(away)
    factors.append(f"Recency-weighted attack xG: {home.name} {home_atk:.2f}/90 vs {away.name} {away_atk:.2f}/90")

    if not fixture.neutral_site:
        factors.append(f"{home.name} plays at home (+{DEFAULT_HOME_ADVANTAGE:.0f} Elo, "
                        f"+{DEFAULT_HOME_ADVANTAGE_PCT:.0%} expected-goals boost)")
    else:
        factors.append("Neutral-site fixture: no home-advantage adjustment applied")

    for team in (home, away):
        form_delta = team.last5_xg_for - team.last20_xg_for
        if abs(form_delta) > 0.15:
            direction = "trending up" if form_delta > 0 else "trending down"
            factors.append(f"{team.name} attacking form {direction}: last5 xGF {team.last5_xg_for:.2f} "
                            f"vs last20 {team.last20_xg_for:.2f}")

    rest_diff = fixture.conditions.home_rest_days - fixture.conditions.away_rest_days
    if rest_diff != 0:
        favored = home.name if rest_diff > 0 else away.name
        factors.append(f"{favored} has a rest-day advantage ({abs(rest_diff)} extra day(s))")

    return factors


def _key_risk_factors(
    home: TeamStats, away: TeamStats, fixture: Fixture, disagreement: float, ml_active: bool,
) -> list[str]:
    risks = []
    if disagreement > DEFAULT_MAX_DISAGREEMENT:
        risks.append(f"Model disagreement is elevated ({disagreement:.1%} spread across 1X2 estimates)")
    if not ml_active:
        risks.append(f"ML ensemble inactive (needs >= {MLEnsemble.MIN_TRAINING_MATCHES} labeled historical matches); "
                      f"using the weighted statistical ensemble only")

    unavailable = [p.name for p in (*fixture.home_players, *fixture.away_players) if not p.is_available]
    if unavailable:
        risks.append(f"Availability doubts: {', '.join(unavailable)}")

    if fixture.conditions.altitude_m > 1500:
        risks.append(f"High-altitude venue ({fixture.conditions.altitude_m:.0f}m) may affect fitness/finishing")
    if fixture.conditions.temperature_c > 32:
        risks.append(f"Extreme heat forecast ({fixture.conditions.temperature_c:.0f}C) may affect pace/subs")
    if abs(fixture.conditions.home_rest_days - fixture.conditions.away_rest_days) >= 3:
        risks.append("Large rest-day imbalance between sides")

    odds = fixture.odds
    if odds.public_bet_pct_home is not None and odds.public_money_pct_home is not None:
        if abs(odds.public_bet_pct_home - odds.public_money_pct_home) > 10:
            risks.append("Ticket% vs money% divergence suggests sharp money against the public side")

    return risks


def analyze_fixture(
    fixture: Fixture,
    home: TeamStats,
    away: TeamStats,
    n_sims: int = 100_000,
    seed: int | None = None,
    min_edge: float = DEFAULT_MIN_EDGE,
    ml_ensemble: MLEnsemble | None = None,
) -> MatchReport:
    elo_model = EloModel()
    ge_model = GoalExpectancyModel()
    poisson_model = PoissonModel()
    bayesian_model = BayesianGoalModel()
    rng = np.random.default_rng(seed)

    # Model 1: Elo
    elo_probs = elo_model.match_probabilities(home.elo_rating, away.elo_rating, neutral_site=fixture.neutral_site)

    # Model 2: xG engine
    lambda_home, lambda_away = ge_model.expected_goals(home, away, neutral=fixture.neutral_site)

    # Model 3: Poisson / Dixon-Coles
    score_matrix = poisson_model.score_matrix(lambda_home, lambda_away)
    poisson_probs = poisson_model.outcome_probs(score_matrix)
    over_under = poisson_model.over_under(score_matrix, 2.5)
    btts = poisson_model.btts(score_matrix)
    correct_scores = poisson_model.correct_scores(score_matrix)
    first_half = poisson_model.first_half_outcome_probs(lambda_home, lambda_away)

    # Model 4: Bayesian
    bayes = bayesian_model.match_probabilities(home, away, neutral=fixture.neutral_site, rng=rng)
    bayes_probs = (bayes.home_mean, bayes.draw_mean, bayes.away_mean)
    bayes_ci_width = max(
        bayes.home_ci[1] - bayes.home_ci[0], bayes.draw_ci[1] - bayes.draw_ci[0], bayes.away_ci[1] - bayes.away_ci[0]
    )

    # Model 6: Monte Carlo (>=100,000 sims)
    mc = MonteCarloSimulator(n_sims=n_sims, seed=seed)
    mc_result = mc.simulate(lambda_home, lambda_away)
    mc_probs = (mc_result.home_win, mc_result.draw, mc_result.away_win)

    # Model 5: ensemble (weighted average, plus ML meta-learner if trained/available)
    estimates = [
        ModelEstimate("elo", *elo_probs),
        ModelEstimate("poisson", *poisson_probs),
        ModelEstimate("bayesian", *bayes_probs),
        ModelEstimate("monte_carlo", *mc_probs),
    ]
    ensemble_result = EnsembleModel().combine(estimates)

    ml_active = ml_ensemble is not None and ml_ensemble.is_trained
    ensemble_probs = (ensemble_result.home, ensemble_result.draw, ensemble_result.away)
    if ml_active:
        feature_row = [e for est in estimates for e in (est.home, est.draw, est.away)]
        ml_probs = ml_ensemble.predict_proba(feature_row)
        if ml_probs is not None:
            ensemble_probs = ml_probs

    # Value detection: 1X2 market
    implied_1x2 = devig_market([fixture.odds.home, fixture.odds.draw, fixture.odds.away])
    market_1x2 = []
    for selection, model_p, decimal_odds, implied_p in zip(
        ("home", "draw", "away"), ensemble_probs, (fixture.odds.home, fixture.odds.draw, fixture.odds.away), implied_1x2
    ):
        market_1x2.append(evaluate_market(
            "1x2", selection, model_p, decimal_odds, implied_p,
            disagreement=ensemble_result.disagreement, ci_width=bayes_ci_width, min_edge=min_edge,
        ))

    # Value detection: totals (over/under 2.5)
    implied_totals = devig_market([fixture.odds.over_2_5, fixture.odds.under_2_5])
    market_totals = [
        evaluate_market("totals_2.5", "over", over_under[0], fixture.odds.over_2_5, implied_totals[0],
                         disagreement=ensemble_result.disagreement, ci_width=bayes_ci_width, min_edge=min_edge),
        evaluate_market("totals_2.5", "under", over_under[1], fixture.odds.under_2_5, implied_totals[1],
                         disagreement=ensemble_result.disagreement, ci_width=bayes_ci_width, min_edge=min_edge),
    ]

    # Value detection: BTTS
    implied_btts = devig_market([fixture.odds.btts_yes, fixture.odds.btts_no])
    market_btts = [
        evaluate_market("btts", "yes", btts[0], fixture.odds.btts_yes, implied_btts[0],
                         disagreement=ensemble_result.disagreement, ci_width=bayes_ci_width, min_edge=min_edge),
        evaluate_market("btts", "no", btts[1], fixture.odds.btts_no, implied_btts[1],
                         disagreement=ensemble_result.disagreement, ci_width=bayes_ci_width, min_edge=min_edge),
    ]

    # Player props: anytime goalscorer, from the Monte Carlo goal simulation
    player_props = {
        f"{fixture.home_team} anytime scorer": mc.anytime_scorer_probs(mc_result.home_goals, fixture.home_players),
        f"{fixture.away_team} anytime scorer": mc.anytime_scorer_probs(mc_result.away_goals, fixture.away_players),
    }

    sensitivity = _sensitivity_analysis(home, away, fixture.neutral_site, elo_model, ge_model, poisson_model)

    return MatchReport(
        fixture_id=fixture.fixture_id,
        home_team=fixture.home_team,
        away_team=fixture.away_team,
        neutral_site=fixture.neutral_site,
        model_probabilities={
            "elo": elo_probs, "poisson": poisson_probs, "bayesian": bayes_probs, "monte_carlo": mc_probs,
        },
        ensemble_probabilities=ensemble_probs,
        ensemble_disagreement=ensemble_result.disagreement,
        ml_ensemble_active=ml_active,
        lambda_home=lambda_home,
        lambda_away=lambda_away,
        markets={"1x2": market_1x2, "totals_2.5": market_totals, "btts": market_btts},
        player_props=player_props,
        key_supporting_factors=_key_supporting_factors(home, away, fixture),
        key_risk_factors=_key_risk_factors(home, away, fixture, ensemble_result.disagreement, ml_active),
        sensitivity=sensitivity,
        correct_score_top=correct_scores,
        first_half_probabilities=first_half,
    )
