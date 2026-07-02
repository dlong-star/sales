"""Model 1: Elo-based prediction engine.

Uses the standard logistic Elo win expectancy (as popularized by
eloratings.net for international football) with a home-advantage offset,
extended to three outcomes (home/draw/away) via a Gaussian draw-probability
curve centered on evenly matched teams. This is a documented heuristic, not
a fitted model -- swap in an empirically fitted draw curve if you have
enough historical data to estimate one.
"""
from __future__ import annotations

import math

DEFAULT_HOME_ADVANTAGE = 60.0  # Elo points
DEFAULT_DRAW_BASE = 0.26  # draw probability when teams are exactly even
DEFAULT_DRAW_SIGMA = 200.0  # how quickly draw probability decays with rating gap


class EloModel:
    def __init__(
        self,
        home_advantage: float = DEFAULT_HOME_ADVANTAGE,
        draw_base: float = DEFAULT_DRAW_BASE,
        draw_sigma: float = DEFAULT_DRAW_SIGMA,
    ) -> None:
        self.home_advantage = home_advantage
        self.draw_base = draw_base
        self.draw_sigma = draw_sigma

    def match_probabilities(
        self, elo_home: float, elo_away: float, neutral_site: bool = False
    ) -> tuple[float, float, float]:
        """Return (p_home, p_draw, p_away)."""
        adv = 0.0 if neutral_site else self.home_advantage
        diff = (elo_home + adv) - elo_away

        p_home_no_draw = 1.0 / (1.0 + 10.0 ** (-diff / 400.0))
        draw_prob = self.draw_base * math.exp(-(diff**2) / (2 * self.draw_sigma**2))
        draw_prob = min(max(draw_prob, 0.05), 0.40)

        p_home = p_home_no_draw * (1 - draw_prob)
        p_away = (1 - p_home_no_draw) * (1 - draw_prob)
        p_draw = draw_prob

        total = p_home + p_draw + p_away
        return p_home / total, p_draw / total, p_away / total

    def update_ratings(
        self,
        elo_home: float,
        elo_away: float,
        home_goals: int,
        away_goals: int,
        k: float = 20.0,
        neutral_site: bool = False,
    ) -> tuple[float, float]:
        """World-Football-Elo-style rating update after a result is known."""
        adv = 0.0 if neutral_site else self.home_advantage
        diff = (elo_home + adv) - elo_away
        expected_home = 1.0 / (1.0 + 10.0 ** (-diff / 400.0))

        if home_goals > away_goals:
            actual_home = 1.0
        elif home_goals == away_goals:
            actual_home = 0.5
        else:
            actual_home = 0.0

        goal_diff = abs(home_goals - away_goals)
        if goal_diff <= 1:
            g = 1.0
        elif goal_diff == 2:
            g = 1.5
        else:
            g = (11 + goal_diff) / 8.0

        delta = k * g * (actual_home - expected_home)
        return elo_home + delta, elo_away - delta
