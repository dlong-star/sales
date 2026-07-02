import numpy as np
import pytest

from wcbet.data.models import Player
from wcbet.models.monte_carlo import MonteCarloSimulator
from wcbet.models.poisson_model import PoissonModel


def _player(name, share, available=True):
    return Player(
        name=name, team="X", position="FW", is_projected_starter=True,
        goals_season=0, assists_season=0, xg_season=0.0, xa_season=0.0,
        shots_per90=0.0, shots_on_target_per90=0.0, key_passes_per90=0.0,
        progressive_carries_per90=0.0, defensive_actions_per90=0.0,
        minutes_played_season=0, minutes_last_5_matches=0, fatigue_index=0.0,
        injury_status="healthy" if available else "out", suspension_status="available",
        club_form_rating=0, international_form_rating=0, market_value_eur_m=0,
        xg_involvement_share=share,
    )


def test_requires_at_least_100000_sims():
    with pytest.raises(ValueError):
        MonteCarloSimulator(n_sims=99_999)


def test_outcome_probs_sum_to_one():
    sim = MonteCarloSimulator(n_sims=100_000, seed=1)
    result = sim.simulate(1.4, 1.1)
    assert result.home_win + result.draw + result.away_win == pytest.approx(1.0)


def test_converges_to_analytic_poisson_without_dixon_coles():
    lam_h, lam_a = 1.5, 1.0
    sim = MonteCarloSimulator(n_sims=300_000, dixon_coles_rho=None, seed=42)
    mc_result = sim.simulate(lam_h, lam_a)

    poisson_model = PoissonModel(dixon_coles_rho=None)
    analytic_home, analytic_draw, analytic_away = poisson_model.outcome_probs(
        poisson_model.score_matrix(lam_h, lam_a)
    )

    # 300k sims => binomial SE on the order of ~0.001; allow generous tolerance
    assert mc_result.home_win == pytest.approx(analytic_home, abs=0.01)
    assert mc_result.draw == pytest.approx(analytic_draw, abs=0.01)
    assert mc_result.away_win == pytest.approx(analytic_away, abs=0.01)


def test_anytime_scorer_probs_respect_xg_share_ordering():
    sim = MonteCarloSimulator(n_sims=100_000, seed=7)
    result = sim.simulate(1.8, 1.0)
    players = [_player("Star", 0.5), _player("Role player", 0.1)]
    probs = sim.anytime_scorer_probs(result.home_goals, players)
    assert probs["Star"] > probs["Role player"]


def test_anytime_scorer_probs_exclude_unavailable_players():
    sim = MonteCarloSimulator(n_sims=100_000, seed=8)
    result = sim.simulate(1.5, 1.0)
    players = [_player("Available", 0.6), _player("Injured", 0.4, available=False)]
    probs = sim.anytime_scorer_probs(result.home_goals, players)
    assert "Injured" not in probs
    assert "Available" in probs


def test_standard_errors_shrink_with_more_sims():
    small = MonteCarloSimulator(n_sims=100_000, seed=1).simulate(1.3, 1.2)
    large = MonteCarloSimulator(n_sims=400_000, seed=1).simulate(1.3, 1.2)
    assert large.home_win_se < small.home_win_se
