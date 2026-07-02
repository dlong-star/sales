import numpy as np
import pytest

from wcbet.data.sample_teams import SAMPLE_TEAMS
from wcbet.models.bayesian import BayesianGoalModel


def test_match_probabilities_sum_to_one():
    model = BayesianGoalModel()
    rng = np.random.default_rng(1)
    result = model.match_probabilities(SAMPLE_TEAMS["Argentina"], SAMPLE_TEAMS["Croatia"], n_samples=500, rng=rng)
    assert result.home_mean + result.draw_mean + result.away_mean == pytest.approx(1.0, abs=1e-6)


def test_credible_intervals_are_ordered_and_bounded():
    model = BayesianGoalModel()
    rng = np.random.default_rng(2)
    result = model.match_probabilities(SAMPLE_TEAMS["Brazil"], SAMPLE_TEAMS["Morocco"], n_samples=500, rng=rng)
    for lo, hi in (result.home_ci, result.draw_ci, result.away_ci):
        assert 0.0 <= lo <= hi <= 1.0


def test_stronger_attack_team_has_higher_home_win_mean():
    model = BayesianGoalModel()
    rng = np.random.default_rng(3)
    strong_vs_weak = model.match_probabilities(SAMPLE_TEAMS["Argentina"], SAMPLE_TEAMS["Morocco"], n_samples=1000, rng=rng)
    assert strong_vs_weak.home_mean > strong_vs_weak.away_mean


def test_more_prior_matches_narrows_credible_interval():
    """More pseudo-observations in the prior => less posterior variance =>
    narrower credible interval on the outcome probability."""
    home, away = SAMPLE_TEAMS["France"], SAMPLE_TEAMS["Germany"]
    loose = BayesianGoalModel(prior_matches=2.0)
    tight = BayesianGoalModel(prior_matches=200.0)
    rng1, rng2 = np.random.default_rng(4), np.random.default_rng(4)
    loose_result = loose.match_probabilities(home, away, n_samples=1500, rng=rng1)
    tight_result = tight.match_probabilities(home, away, n_samples=1500, rng=rng2)
    loose_width = loose_result.home_ci[1] - loose_result.home_ci[0]
    tight_width = tight_result.home_ci[1] - tight_result.home_ci[0]
    assert tight_width < loose_width
