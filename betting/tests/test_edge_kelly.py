import inspect

import pytest

from wcbet.value.edge import (
    evaluate_market,
    expected_value,
    kelly_fraction,
    edge_pct,
)


def test_kelly_fraction_zero_when_no_edge():
    # implied prob for these odds is exactly model_prob -> no edge
    assert kelly_fraction(0.5, 2.0) == 0.0


def test_kelly_fraction_positive_with_real_edge():
    # true prob 0.55 vs fair-odds-implied 0.5 (odds 2.0) is a real edge
    stake = kelly_fraction(0.55, 2.0, fraction=1.0, cap=1.0)
    assert stake > 0
    # full Kelly formula: (p*b - q) / b, b=1
    expected = (0.55 * 1 - 0.45) / 1
    assert stake == pytest.approx(expected)


def test_kelly_fraction_respects_cap():
    stake = kelly_fraction(0.9, 5.0, fraction=1.0, cap=0.05)
    assert stake == pytest.approx(0.05)


def test_kelly_fraction_negative_edge_is_zero():
    assert kelly_fraction(0.3, 2.0) == 0.0


def test_expected_value_sign_matches_edge_direction():
    assert expected_value(0.6, 2.0) > 0  # model favors selection more than fair coin
    assert expected_value(0.4, 2.0) < 0


def test_edge_pct_basic():
    assert edge_pct(0.55, 0.50) == pytest.approx(0.05)


def test_evaluate_market_rejects_when_edge_too_small():
    rec = evaluate_market("1x2", "home", model_prob=0.52, decimal_odds=1.92, implied_prob=0.50,
                           disagreement=0.0, ci_width=0.0)
    assert not rec.recommended


def test_evaluate_market_recommends_when_all_thresholds_clear():
    # big edge, positive EV, models fully agree, tight CI
    rec = evaluate_market("1x2", "home", model_prob=0.65, decimal_odds=2.20, implied_prob=0.50,
                           disagreement=0.0, ci_width=0.0)
    assert rec.recommended
    assert rec.kelly_stake_pct > 0
    assert rec.expected_value > 0


def test_evaluate_market_blocks_on_disagreement_even_with_big_edge():
    rec = evaluate_market("1x2", "home", model_prob=0.65, decimal_odds=2.20, implied_prob=0.50,
                           disagreement=0.5, ci_width=0.0)
    assert not rec.recommended
    assert not rec.model_agreement


def test_recommendation_never_takes_favorite_or_line_movement_signals():
    """CRITICAL RULE: recommendations must never be a function of which side
    is favored or whether the line moved. Enforce this structurally: the
    function signature must not even accept such parameters."""
    params = set(inspect.signature(evaluate_market).parameters)
    banned = {"is_favorite", "favorite", "line_moved", "odds_movement", "line_movement"}
    assert params.isdisjoint(banned)
