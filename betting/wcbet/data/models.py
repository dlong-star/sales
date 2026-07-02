"""Core data structures for the World Cup betting intelligence system.

These are plain dataclasses so that any data source (sample, CSV, live API)
can populate them. Nothing in the modeling/value layers depends on where the
data came from -- see ``sources.py`` for the adapter interfaces.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

InjuryStatus = Literal["healthy", "doubtful", "out"]
SuspensionStatus = Literal["available", "suspended"]


@dataclass
class TeamStats:
    name: str
    fifa_ranking: int
    elo_rating: float
    spi_rating: float

    # Expected goals, per 90 minutes, trailing full sample
    xg_for_per90: float
    xg_against_per90: float
    goals_for_per90: float
    goals_against_per90: float

    # Style / process metrics
    possession_pct: float
    pass_completion_pct: float
    ppda: float  # passes allowed per defensive action; lower = more intense press
    set_piece_goal_share: float  # fraction of goals from set pieces
    counter_attack_goal_share: float  # fraction of goals from transitions

    # Schedule context
    strength_of_schedule: float  # avg Elo of opponents faced, trailing 12 months
    home_goal_diff_per90: float
    away_goal_diff_per90: float
    neutral_goal_diff_per90: float

    # Recency windows (xG for/against per90 over each window)
    last5_xg_for: float
    last5_xg_against: float
    last10_xg_for: float
    last10_xg_against: float
    last20_xg_for: float
    last20_xg_against: float

    # Tournament history
    world_cup_matches_played: int
    world_cup_win_pct: float
    tournament_history_score: float  # composite 0-100, host federation's own scouting scale


@dataclass
class Player:
    name: str
    team: str
    position: str
    is_projected_starter: bool

    goals_season: int
    assists_season: int
    xg_season: float
    xa_season: float
    shots_per90: float
    shots_on_target_per90: float
    key_passes_per90: float
    progressive_carries_per90: float
    defensive_actions_per90: float

    minutes_played_season: int
    minutes_last_5_matches: int
    fatigue_index: float  # 0 (fresh) - 1 (heavily loaded)
    injury_status: InjuryStatus
    suspension_status: SuspensionStatus

    club_form_rating: float  # 0-100
    international_form_rating: float  # 0-100
    market_value_eur_m: float

    xg_involvement_share: float  # this player's share of the team's total xG (scorer prop weighting)

    @property
    def is_available(self) -> bool:
        return self.injury_status != "out" and self.suspension_status != "suspended"


@dataclass
class MatchConditions:
    stadium: str
    temperature_c: float
    humidity_pct: float
    wind_kph: float
    rain_probability_pct: float
    altitude_m: float
    travel_distance_km: float  # away team's travel distance to venue
    timezone_shift_hours: float  # away team's timezone shift from home base
    home_rest_days: int
    away_rest_days: int
    referee_name: str
    referee_cards_per_match: float
    referee_penalties_per_match: float
    crowd_home_pct: float  # estimated share of crowd supporting home team
    tournament_stage: str  # e.g. "Group Stage", "Round of 16", "Final"


@dataclass
class MarketOdds:
    """Decimal odds for one bookmaker snapshot."""

    book: str
    home: float
    draw: float
    away: float
    over_2_5: float
    under_2_5: float
    btts_yes: float
    btts_no: float
    opening_home: float | None = None
    opening_draw: float | None = None
    opening_away: float | None = None
    closing_home: float | None = None
    closing_draw: float | None = None
    closing_away: float | None = None
    public_bet_pct_home: float | None = None  # % of tickets on home
    public_money_pct_home: float | None = None  # % of $ on home (sharp indicator vs tickets)


@dataclass
class Fixture:
    fixture_id: str
    date: str
    home_team: str
    away_team: str
    neutral_site: bool
    conditions: MatchConditions
    odds: MarketOdds
    home_players: list[Player] = field(default_factory=list)
    away_players: list[Player] = field(default_factory=list)
