"""Model 2: Expected-goals engine.

Converts each team's attack/defense process metrics (xG for/against,
recency-weighted) into expected goals for a specific fixture, the way a
Dixon-Coles-style attack/defense strength model does, before any Poisson
scoreline math is applied (that's Model 3, in ``poisson_model.py``).
"""
from __future__ import annotations

from wcbet.data.models import TeamStats

LEAGUE_AVG_GOALS_PER_TEAM = 1.35  # ~2.7 combined goals/match, typical for intl./WC play
DEFAULT_HOME_ADVANTAGE_PCT = 0.10

# Recency weighting: season sample, then progressively shorter/more recent windows.
_RECENCY_WEIGHTS = {"season": 0.40, "last20": 0.30, "last10": 0.20, "last5": 0.10}


def blended_xg(team: TeamStats) -> tuple[float, float]:
    """Recency-weighted blend of a team's attack/defense xG rate."""
    attack = (
        _RECENCY_WEIGHTS["season"] * team.xg_for_per90
        + _RECENCY_WEIGHTS["last20"] * team.last20_xg_for
        + _RECENCY_WEIGHTS["last10"] * team.last10_xg_for
        + _RECENCY_WEIGHTS["last5"] * team.last5_xg_for
    )
    defense = (
        _RECENCY_WEIGHTS["season"] * team.xg_against_per90
        + _RECENCY_WEIGHTS["last20"] * team.last20_xg_against
        + _RECENCY_WEIGHTS["last10"] * team.last10_xg_against
        + _RECENCY_WEIGHTS["last5"] * team.last5_xg_against
    )
    return attack, defense


class GoalExpectancyModel:
    def __init__(
        self,
        league_avg_goals: float = LEAGUE_AVG_GOALS_PER_TEAM,
        home_advantage_pct: float = DEFAULT_HOME_ADVANTAGE_PCT,
        min_lambda: float = 0.05,
    ) -> None:
        self.league_avg_goals = league_avg_goals
        self.home_advantage_pct = home_advantage_pct
        self.min_lambda = min_lambda

    def team_strengths(self, team: TeamStats) -> tuple[float, float]:
        """Return (attack_strength, defense_strength), both centered on 1.0."""
        atk_for, atk_against = blended_xg(team)
        return atk_for / self.league_avg_goals, atk_against / self.league_avg_goals

    def expected_goals(
        self, home: TeamStats, away: TeamStats, neutral: bool = False
    ) -> tuple[float, float]:
        home_attack, home_defense = self.team_strengths(home)
        away_attack, away_defense = self.team_strengths(away)

        lambda_home = self.league_avg_goals * home_attack * away_defense
        lambda_away = self.league_avg_goals * away_attack * home_defense

        if not neutral:
            lambda_home *= 1 + self.home_advantage_pct
            lambda_away *= 1 - self.home_advantage_pct * 0.5

        return max(lambda_home, self.min_lambda), max(lambda_away, self.min_lambda)
