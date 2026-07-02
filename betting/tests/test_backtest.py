from wcbet.backtest.engine import backtest
from wcbet.data.sample_history import SAMPLE_HISTORY, HistoricalMatch


def test_backtest_runs_on_sample_history_and_returns_finite_metrics():
    result = backtest(SAMPLE_HISTORY)
    assert result.n_bets >= 0
    assert result.max_drawdown <= 0
    assert result.ending_bankroll > 0


def test_no_bets_placed_when_min_edge_is_impossibly_high():
    result = backtest(SAMPLE_HISTORY, min_edge=0.99)
    assert result.n_bets == 0
    assert result.roi == 0.0
    assert result.ending_bankroll == 100.0


def test_kelly_staking_never_bankrupts_on_a_single_loss():
    result = backtest(SAMPLE_HISTORY, staking="kelly", min_edge=0.05)
    assert result.ending_bankroll > 0
    assert min(result.equity_curve) > 0


def test_flat_staking_matches_expected_bet_count_logic():
    kelly_result = backtest(SAMPLE_HISTORY, staking="kelly", min_edge=0.05)
    flat_result = backtest(SAMPLE_HISTORY, staking="flat", min_edge=0.05)
    # same edge filter -> same number of qualifying bets regardless of staking method
    assert kelly_result.n_bets == flat_result.n_bets


def test_synthetic_match_with_known_positive_edge_produces_a_bet():
    # Elo(2200) vs Elo(1600) heavily favors home; give it deliberately long
    # underdog-style odds on the away side isn't useful here, so instead we
    # give *home* odds far richer than its true (high) win probability to
    # guarantee a mispriced, +edge home bet.
    juicy_match = HistoricalMatch(
        date="2099-01-01", home="Test A", away="Test B",
        home_goals=1, away_goals=0, elo_home=2200, elo_away=1600, neutral=True,
        home_odds=3.0, draw_odds=4.0, away_odds=8.0,
        closing_home_odds=2.8, closing_draw_odds=4.1, closing_away_odds=8.5,
    )
    result = backtest([juicy_match], min_edge=0.05)
    assert result.n_bets >= 1
