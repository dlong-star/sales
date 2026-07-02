"""Illustrative sample team dataset.

These numbers are hand-authored approximations for demonstration and testing
purposes -- they are NOT pulled from a live Elo/SPI/FIFA feed. Replace this
module with a real ``TeamDataSource`` implementation (see ``sources.py``) to
run the system on live data.
"""
from __future__ import annotations

from wcbet.data.models import TeamStats

SAMPLE_TEAMS: dict[str, TeamStats] = {
    "Argentina": TeamStats(
        name="Argentina", fifa_ranking=1, elo_rating=2105, spi_rating=88.9,
        xg_for_per90=1.95, xg_against_per90=0.85, goals_for_per90=1.90, goals_against_per90=0.75,
        possession_pct=58.0, pass_completion_pct=87.5, ppda=9.8,
        set_piece_goal_share=0.22, counter_attack_goal_share=0.20,
        strength_of_schedule=1920, home_goal_diff_per90=1.4, away_goal_diff_per90=0.7, neutral_goal_diff_per90=1.05,
        last5_xg_for=2.05, last5_xg_against=0.70, last10_xg_for=1.98, last10_xg_against=0.80,
        last20_xg_for=1.90, last20_xg_against=0.88,
        world_cup_matches_played=87, world_cup_win_pct=0.55, tournament_history_score=92,
    ),
    "France": TeamStats(
        name="France", fifa_ranking=2, elo_rating=2075, spi_rating=87.5,
        xg_for_per90=2.05, xg_against_per90=0.95, goals_for_per90=2.0, goals_against_per90=0.90,
        possession_pct=54.0, pass_completion_pct=85.0, ppda=10.5,
        set_piece_goal_share=0.18, counter_attack_goal_share=0.28,
        strength_of_schedule=1900, home_goal_diff_per90=1.3, away_goal_diff_per90=0.8, neutral_goal_diff_per90=1.10,
        last5_xg_for=2.20, last5_xg_against=0.90, last10_xg_for=2.10, last10_xg_against=0.95,
        last20_xg_for=2.00, last20_xg_against=1.00,
        world_cup_matches_played=73, world_cup_win_pct=0.53, tournament_history_score=90,
    ),
    "Brazil": TeamStats(
        name="Brazil", fifa_ranking=3, elo_rating=2070, spi_rating=87.0,
        xg_for_per90=1.90, xg_against_per90=0.80, goals_for_per90=1.85, goals_against_per90=0.75,
        possession_pct=60.0, pass_completion_pct=88.0, ppda=10.0,
        set_piece_goal_share=0.16, counter_attack_goal_share=0.24,
        strength_of_schedule=1890, home_goal_diff_per90=1.5, away_goal_diff_per90=0.6, neutral_goal_diff_per90=1.0,
        last5_xg_for=1.85, last5_xg_against=0.85, last10_xg_for=1.88, last10_xg_against=0.82,
        last20_xg_for=1.92, last20_xg_against=0.78,
        world_cup_matches_played=114, world_cup_win_pct=0.63, tournament_history_score=98,
    ),
    "England": TeamStats(
        name="England", fifa_ranking=4, elo_rating=2040, spi_rating=85.8,
        xg_for_per90=1.85, xg_against_per90=0.90, goals_for_per90=1.80, goals_against_per90=0.85,
        possession_pct=56.0, pass_completion_pct=86.0, ppda=10.8,
        set_piece_goal_share=0.24, counter_attack_goal_share=0.18,
        strength_of_schedule=1880, home_goal_diff_per90=1.2, away_goal_diff_per90=0.6, neutral_goal_diff_per90=0.85,
        last5_xg_for=1.75, last5_xg_against=0.95, last10_xg_for=1.80, last10_xg_against=0.92,
        last20_xg_for=1.83, last20_xg_against=0.88,
        world_cup_matches_played=68, world_cup_win_pct=0.51, tournament_history_score=78,
    ),
    "Spain": TeamStats(
        name="Spain", fifa_ranking=5, elo_rating=2060, spi_rating=86.9,
        xg_for_per90=2.10, xg_against_per90=0.75, goals_for_per90=2.05, goals_against_per90=0.70,
        possession_pct=64.0, pass_completion_pct=90.5, ppda=9.5,
        set_piece_goal_share=0.14, counter_attack_goal_share=0.14,
        strength_of_schedule=1885, home_goal_diff_per90=1.5, away_goal_diff_per90=0.9, neutral_goal_diff_per90=1.20,
        last5_xg_for=2.25, last5_xg_against=0.65, last10_xg_for=2.15, last10_xg_against=0.72,
        last20_xg_for=2.05, last20_xg_against=0.78,
        world_cup_matches_played=71, world_cup_win_pct=0.52, tournament_history_score=80,
    ),
    "Portugal": TeamStats(
        name="Portugal", fifa_ranking=6, elo_rating=2010, spi_rating=84.9,
        xg_for_per90=1.80, xg_against_per90=0.85, goals_for_per90=1.75, goals_against_per90=0.80,
        possession_pct=55.0, pass_completion_pct=86.5, ppda=10.2,
        set_piece_goal_share=0.20, counter_attack_goal_share=0.22,
        strength_of_schedule=1860, home_goal_diff_per90=1.1, away_goal_diff_per90=0.55, neutral_goal_diff_per90=0.80,
        last5_xg_for=1.95, last5_xg_against=0.80, last10_xg_for=1.85, last10_xg_against=0.83,
        last20_xg_for=1.78, last20_xg_against=0.87,
        world_cup_matches_played=27, world_cup_win_pct=0.48, tournament_history_score=62,
    ),
    "Germany": TeamStats(
        name="Germany", fifa_ranking=7, elo_rating=1990, spi_rating=83.8,
        xg_for_per90=1.90, xg_against_per90=1.05, goals_for_per90=1.85, goals_against_per90=1.00,
        possession_pct=59.0, pass_completion_pct=87.0, ppda=9.9,
        set_piece_goal_share=0.19, counter_attack_goal_share=0.16,
        strength_of_schedule=1875, home_goal_diff_per90=1.0, away_goal_diff_per90=0.45, neutral_goal_diff_per90=0.65,
        last5_xg_for=1.80, last5_xg_against=1.10, last10_xg_for=1.85, last10_xg_against=1.05,
        last20_xg_for=1.88, last20_xg_against=1.00,
        world_cup_matches_played=112, world_cup_win_pct=0.60, tournament_history_score=95,
    ),
    "Netherlands": TeamStats(
        name="Netherlands", fifa_ranking=8, elo_rating=2000, spi_rating=84.5,
        xg_for_per90=1.75, xg_against_per90=0.80, goals_for_per90=1.70, goals_against_per90=0.75,
        possession_pct=57.0, pass_completion_pct=87.0, ppda=10.6,
        set_piece_goal_share=0.23, counter_attack_goal_share=0.19,
        strength_of_schedule=1855, home_goal_diff_per90=1.15, away_goal_diff_per90=0.55, neutral_goal_diff_per90=0.75,
        last5_xg_for=1.70, last5_xg_against=0.75, last10_xg_for=1.72, last10_xg_against=0.78,
        last20_xg_for=1.74, last20_xg_against=0.82,
        world_cup_matches_played=52, world_cup_win_pct=0.56, tournament_history_score=76,
    ),
    "Morocco": TeamStats(
        name="Morocco", fifa_ranking=13, elo_rating=1920, spi_rating=79.5,
        xg_for_per90=1.35, xg_against_per90=0.75, goals_for_per90=1.30, goals_against_per90=0.65,
        possession_pct=47.0, pass_completion_pct=81.0, ppda=8.9,
        set_piece_goal_share=0.21, counter_attack_goal_share=0.33,
        strength_of_schedule=1790, home_goal_diff_per90=0.9, away_goal_diff_per90=0.35, neutral_goal_diff_per90=0.55,
        last5_xg_for=1.45, last5_xg_against=0.55, last10_xg_for=1.40, last10_xg_against=0.65,
        last20_xg_for=1.32, last20_xg_against=0.72,
        world_cup_matches_played=13, world_cup_win_pct=0.38, tournament_history_score=48,
    ),
    "Croatia": TeamStats(
        name="Croatia", fifa_ranking=9, elo_rating=1960, spi_rating=81.6,
        xg_for_per90=1.55, xg_against_per90=0.90, goals_for_per90=1.50, goals_against_per90=0.85,
        possession_pct=53.0, pass_completion_pct=85.5, ppda=11.0,
        set_piece_goal_share=0.20, counter_attack_goal_share=0.21,
        strength_of_schedule=1830, home_goal_diff_per90=0.95, away_goal_diff_per90=0.40, neutral_goal_diff_per90=0.60,
        last5_xg_for=1.60, last5_xg_against=0.85, last10_xg_for=1.58, last10_xg_against=0.88,
        last20_xg_for=1.53, last20_xg_against=0.90,
        world_cup_matches_played=27, world_cup_win_pct=0.48, tournament_history_score=58,
    ),
}
