import pytest

from wcbet.models.elo import EloModel


def test_probabilities_sum_to_one():
    model = EloModel()
    p_home, p_draw, p_away = model.match_probabilities(2000, 1900)
    assert p_home + p_draw + p_away == pytest.approx(1.0)


def test_equal_teams_neutral_site_favors_neither():
    model = EloModel()
    p_home, p_draw, p_away = model.match_probabilities(2000, 2000, neutral_site=True)
    assert p_home == pytest.approx(p_away, abs=1e-9)


def test_home_advantage_shifts_probability_toward_home():
    model = EloModel()
    p_home_neutral, _, p_away_neutral = model.match_probabilities(2000, 2000, neutral_site=True)
    p_home_venue, _, p_away_venue = model.match_probabilities(2000, 2000, neutral_site=False)
    assert p_home_venue > p_home_neutral
    assert p_away_venue < p_away_neutral


def test_draw_probability_shrinks_as_gap_widens():
    model = EloModel()
    _, draw_close, _ = model.match_probabilities(2000, 1990, neutral_site=True)
    _, draw_wide, _ = model.match_probabilities(2400, 1600, neutral_site=True)
    assert draw_close > draw_wide


def test_update_ratings_symmetric_zero_sum():
    model = EloModel()
    new_home, new_away = model.update_ratings(2000, 1900, home_goals=2, away_goals=0, neutral_site=True)
    assert (new_home - 2000) == pytest.approx(-(new_away - 1900))


def test_update_ratings_rewards_upset():
    model = EloModel()
    new_home, new_away = model.update_ratings(2000, 1600, home_goals=0, away_goals=1, neutral_site=True)
    assert new_home < 2000
    assert new_away > 1600
