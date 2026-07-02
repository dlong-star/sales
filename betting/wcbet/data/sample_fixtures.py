"""Illustrative sample fixtures with players, conditions and market odds.

All odds/roster figures below are hand-authored for demonstration -- swap in
a real ``OddsDataSource`` / ``PlayerDataSource`` (see ``sources.py``) for a
production deployment.
"""
from __future__ import annotations

from wcbet.data.models import Fixture, MatchConditions, MarketOdds, Player

_ARG_PLAYERS = [
    Player(
        name="L. Messi", team="Argentina", position="FW", is_projected_starter=True,
        goals_season=18, assists_season=14, xg_season=15.2, xa_season=11.8,
        shots_per90=3.8, shots_on_target_per90=2.1, key_passes_per90=2.9,
        progressive_carries_per90=5.1, defensive_actions_per90=0.6,
        minutes_played_season=2450, minutes_last_5_matches=420, fatigue_index=0.42,
        injury_status="healthy", suspension_status="available",
        club_form_rating=88, international_form_rating=91, market_value_eur_m=35,
        xg_involvement_share=0.30,
    ),
    Player(
        name="J. Alvarez", team="Argentina", position="FW", is_projected_starter=True,
        goals_season=22, assists_season=6, xg_season=19.0, xa_season=5.5,
        shots_per90=3.2, shots_on_target_per90=1.7, key_passes_per90=1.4,
        progressive_carries_per90=3.6, defensive_actions_per90=1.1,
        minutes_played_season=2700, minutes_last_5_matches=450, fatigue_index=0.38,
        injury_status="healthy", suspension_status="available",
        club_form_rating=85, international_form_rating=82, market_value_eur_m=70,
        xg_involvement_share=0.24,
    ),
    Player(
        name="E. Martinez", team="Argentina", position="GK", is_projected_starter=True,
        goals_season=0, assists_season=0, xg_season=0.0, xa_season=0.0,
        shots_per90=0.0, shots_on_target_per90=0.0, key_passes_per90=0.1,
        progressive_carries_per90=0.1, defensive_actions_per90=2.0,
        minutes_played_season=2790, minutes_last_5_matches=450, fatigue_index=0.30,
        injury_status="healthy", suspension_status="available",
        club_form_rating=80, international_form_rating=88, market_value_eur_m=22,
        xg_involvement_share=0.0,
    ),
]

_FRA_PLAYERS = [
    Player(
        name="K. Mbappe", team="France", position="FW", is_projected_starter=True,
        goals_season=27, assists_season=8, xg_season=22.5, xa_season=7.0,
        shots_per90=4.5, shots_on_target_per90=2.6, key_passes_per90=2.0,
        progressive_carries_per90=6.2, defensive_actions_per90=0.7,
        minutes_played_season=2600, minutes_last_5_matches=430, fatigue_index=0.45,
        injury_status="healthy", suspension_status="available",
        club_form_rating=90, international_form_rating=93, market_value_eur_m=180,
        xg_involvement_share=0.32,
    ),
    Player(
        name="O. Dembele", team="France", position="FW", is_projected_starter=True,
        goals_season=12, assists_season=10, xg_season=9.8, xa_season=8.9,
        shots_per90=2.6, shots_on_target_per90=1.2, key_passes_per90=2.7,
        progressive_carries_per90=5.4, defensive_actions_per90=1.0,
        minutes_played_season=2200, minutes_last_5_matches=380, fatigue_index=0.50,
        injury_status="doubtful", suspension_status="available",
        club_form_rating=79, international_form_rating=74, market_value_eur_m=50,
        xg_involvement_share=0.16,
    ),
    Player(
        name="M. Maignan", team="France", position="GK", is_projected_starter=True,
        goals_season=0, assists_season=0, xg_season=0.0, xa_season=0.0,
        shots_per90=0.0, shots_on_target_per90=0.0, key_passes_per90=0.1,
        progressive_carries_per90=0.1, defensive_actions_per90=1.8,
        minutes_played_season=2650, minutes_last_5_matches=450, fatigue_index=0.33,
        injury_status="healthy", suspension_status="available",
        club_form_rating=83, international_form_rating=85, market_value_eur_m=30,
        xg_involvement_share=0.0,
    ),
]

FIXTURE_ARG_FRA = Fixture(
    fixture_id="WC2026-FINAL-ARG-FRA",
    date="2026-07-19",
    home_team="Argentina",
    away_team="France",
    neutral_site=True,
    conditions=MatchConditions(
        stadium="MetLife Stadium, New Jersey",
        temperature_c=27.0, humidity_pct=65.0, wind_kph=12.0, rain_probability_pct=20.0,
        altitude_m=30.0, travel_distance_km=6800.0, timezone_shift_hours=5.0,
        home_rest_days=4, away_rest_days=4,
        referee_name="S. Marciniak", referee_cards_per_match=4.1, referee_penalties_per_match=0.22,
        crowd_home_pct=52.0, tournament_stage="Final",
    ),
    odds=MarketOdds(
        book="Sample Book", home=2.55, draw=3.40, away=2.80,
        over_2_5=1.95, under_2_5=1.90, btts_yes=1.72, btts_no=2.05,
        opening_home=2.70, opening_draw=3.30, opening_away=2.65,
        closing_home=2.50, closing_draw=3.45, closing_away=2.85,
        public_bet_pct_home=61.0, public_money_pct_home=48.0,
    ),
    home_players=_ARG_PLAYERS,
    away_players=_FRA_PLAYERS,
)

FIXTURE_BRA_ENG = Fixture(
    fixture_id="WC2026-QF-BRA-ENG",
    date="2026-07-10",
    home_team="Brazil",
    away_team="England",
    neutral_site=True,
    conditions=MatchConditions(
        stadium="AT&T Stadium, Arlington",
        temperature_c=33.0, humidity_pct=40.0, wind_kph=8.0, rain_probability_pct=5.0,
        altitude_m=180.0, travel_distance_km=9500.0, timezone_shift_hours=6.0,
        home_rest_days=5, away_rest_days=3,
        referee_name="F. Zwayer", referee_cards_per_match=3.6, referee_penalties_per_match=0.18,
        crowd_home_pct=58.0, tournament_stage="Quarterfinal",
    ),
    odds=MarketOdds(
        book="Sample Book", home=2.15, draw=3.30, away=3.60,
        over_2_5=2.05, under_2_5=1.80, btts_yes=1.85, btts_no=1.95,
        opening_home=2.05, opening_draw=3.35, opening_away=3.75,
        closing_home=2.20, closing_draw=3.25, closing_away=3.50,
        public_bet_pct_home=70.0, public_money_pct_home=55.0,
    ),
    home_players=[],
    away_players=[],
)

SAMPLE_FIXTURES: list[Fixture] = [FIXTURE_ARG_FRA, FIXTURE_BRA_ENG]
