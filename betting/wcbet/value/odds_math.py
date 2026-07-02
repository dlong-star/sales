"""Decimal-odds <-> probability conversions, including vig removal."""
from __future__ import annotations

from collections.abc import Sequence


def decimal_to_implied_prob(odds: float) -> float:
    if odds <= 1.0:
        raise ValueError(f"Decimal odds must be > 1.0, got {odds}")
    return 1.0 / odds


def remove_vig_multiplicative(implied_probs: Sequence[float]) -> list[float]:
    """Normalize a set of implied probabilities that sum to > 1 (the overround)
    back down to a coherent probability distribution, proportionally."""
    total = sum(implied_probs)
    if total <= 0:
        raise ValueError("Implied probabilities must sum to a positive number")
    return [p / total for p in implied_probs]


def devig_market(odds: Sequence[float]) -> list[float]:
    return remove_vig_multiplicative([decimal_to_implied_prob(o) for o in odds])


def overround(implied_probs: Sequence[float]) -> float:
    return sum(implied_probs) - 1.0


def fair_odds_from_prob(prob: float) -> float:
    if prob <= 0:
        return float("inf")
    return 1.0 / prob
