"""Illustrative historical dataset for exercising the backtest engine.

IMPORTANT CAVEATS:

* Match scores below reflect the author's best recollection of 2022 FIFA
  World Cup group-stage (matchday 1) results. They have not been
  re-verified against an authoritative results feed in this environment and
  should be treated as illustrative sample data for exercising the backtest
  engine's math (ROI, Sharpe, drawdown, CLV), not as a verified historical
  record for real capital decisions.
* Pre-match Elo ratings are rough, hand-set approximations of the teams'
  relative strength at the time, not pulled from eloratings.net or any
  other live source.
* Odds are SYNTHETIC: generated from the Elo model's own probabilities plus
  a fixed bookmaker margin and deterministic random noise (seeded), so that
  edges appear and disappear realistically. They are NOT real historical
  sportsbook lines. Replace this module with real historical odds data
  (e.g. exported closing lines) before drawing any production conclusions
  from backtest output.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from wcbet.models.elo import EloModel


@dataclass
class HistoricalMatch:
    date: str
    home: str
    away: str
    home_goals: int
    away_goals: int
    elo_home: float
    elo_away: float
    neutral: bool
    home_odds: float
    draw_odds: float
    away_odds: float
    closing_home_odds: float
    closing_draw_odds: float
    closing_away_odds: float


# (date, home, away, home_goals, away_goals, elo_home, elo_away, neutral)
_RAW_2022_MD1 = [
    ("2022-11-20", "Qatar", "Ecuador", 0, 2, 1608, 1793, True),
    ("2022-11-21", "England", "Iran", 6, 2, 1929, 1636, True),
    ("2022-11-21", "Senegal", "Netherlands", 0, 2, 1747, 1919, True),
    ("2022-11-21", "United States", "Wales", 1, 1, 1785, 1791, True),
    ("2022-11-22", "Argentina", "Saudi Arabia", 1, 2, 2043, 1567, True),
    ("2022-11-22", "Denmark", "Tunisia", 0, 0, 1858, 1637, True),
    ("2022-11-22", "Mexico", "Poland", 0, 0, 1780, 1799, True),
    ("2022-11-22", "France", "Australia", 4, 1, 1993, 1710, True),
    ("2022-11-23", "Morocco", "Croatia", 0, 0, 1730, 1913, True),
    ("2022-11-23", "Germany", "Japan", 1, 2, 1937, 1738, True),
    ("2022-11-23", "Spain", "Costa Rica", 7, 0, 1963, 1670, True),
    ("2022-11-23", "Belgium", "Canada", 1, 0, 1821, 1738, True),
    ("2022-11-24", "Switzerland", "Cameroon", 1, 0, 1846, 1592, True),
    ("2022-11-24", "Uruguay", "South Korea", 0, 0, 1873, 1786, True),
    ("2022-11-24", "Portugal", "Ghana", 3, 2, 1975, 1568, True),
    ("2022-11-24", "Brazil", "Serbia", 2, 0, 2010, 1745, True),
]

_BOOK_MARGIN = 1.06  # ~6% overround, typical for a 3-way soccer market


def _build_history() -> list[HistoricalMatch]:
    rng = np.random.default_rng(seed=20221120)
    elo = EloModel()
    matches: list[HistoricalMatch] = []
    for date, home, away, hg, ag, elo_h, elo_a, neutral in _RAW_2022_MD1:
        p_home, p_draw, p_away = elo.match_probabilities(elo_h, elo_a, neutral_site=neutral)

        # Add noise so the "true" market disagrees with the Elo model by a
        # realistic amount in either direction (this is what lets edges show
        # up in the sample backtest at all).
        noise = rng.normal(loc=0.0, scale=0.035, size=3)
        market_probs = np.clip(np.array([p_home, p_draw, p_away]) + noise, 0.02, 0.95)
        market_probs = market_probs / market_probs.sum()
        opening_odds = (market_probs * _BOOK_MARGIN) ** -1

        # Simulate modest closing-line movement.
        move = rng.normal(loc=0.0, scale=0.02, size=3)
        closing_probs = np.clip(market_probs + move, 0.02, 0.95)
        closing_probs = closing_probs / closing_probs.sum()
        closing_odds = (closing_probs * _BOOK_MARGIN) ** -1

        matches.append(
            HistoricalMatch(
                date=date, home=home, away=away, home_goals=hg, away_goals=ag,
                elo_home=elo_h, elo_away=elo_a, neutral=neutral,
                home_odds=round(float(opening_odds[0]), 2),
                draw_odds=round(float(opening_odds[1]), 2),
                away_odds=round(float(opening_odds[2]), 2),
                closing_home_odds=round(float(closing_odds[0]), 2),
                closing_draw_odds=round(float(closing_odds[1]), 2),
                closing_away_odds=round(float(closing_odds[2]), 2),
            )
        )
    return matches


SAMPLE_HISTORY: list[HistoricalMatch] = _build_history()
