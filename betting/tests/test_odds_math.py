import pytest

from wcbet.value.odds_math import (
    decimal_to_implied_prob,
    devig_market,
    fair_odds_from_prob,
    overround,
    remove_vig_multiplicative,
)


def test_decimal_to_implied_prob():
    assert decimal_to_implied_prob(2.0) == pytest.approx(0.5)
    assert decimal_to_implied_prob(4.0) == pytest.approx(0.25)


def test_decimal_to_implied_prob_rejects_invalid_odds():
    with pytest.raises(ValueError):
        decimal_to_implied_prob(1.0)
    with pytest.raises(ValueError):
        decimal_to_implied_prob(0.5)


def test_overround_is_positive_for_real_book_odds():
    implied = [decimal_to_implied_prob(o) for o in (2.0, 3.5, 4.0)]
    assert overround(implied) > 0


def test_remove_vig_multiplicative_sums_to_one():
    implied = [decimal_to_implied_prob(o) for o in (2.0, 3.5, 4.0)]
    devigged = remove_vig_multiplicative(implied)
    assert sum(devigged) == pytest.approx(1.0)
    # relative ordering must be preserved
    assert devigged[0] > devigged[1] > devigged[2]


def test_devig_market_matches_manual_pipeline():
    odds = (2.5, 3.2, 3.0)
    assert devig_market(odds) == pytest.approx(
        remove_vig_multiplicative([decimal_to_implied_prob(o) for o in odds])
    )


def test_fair_odds_roundtrip():
    prob = 0.4
    fair = fair_odds_from_prob(prob)
    assert decimal_to_implied_prob(fair) == pytest.approx(prob)
