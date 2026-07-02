"""Backtesting harness: apply the value-detection rule match-by-match over a
historical dataset and report ROI, win rate, Sharpe ratio, max drawdown, and
closing-line value (CLV) performance.

The harness only needs an Elo snapshot per match (fast enough to run over
thousands of historical rows) rather than the full model stack -- this is a
deliberate simplification for backtesting throughput. Swapping in the full
ensemble per historical row is possible but requires trailing xG/form data
for every historical match, which the sample dataset doesn't carry.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from wcbet.data.sample_history import HistoricalMatch
from wcbet.models.elo import EloModel
from wcbet.value.edge import DEFAULT_MIN_EDGE, kelly_fraction
from wcbet.value.odds_math import decimal_to_implied_prob, remove_vig_multiplicative


@dataclass
class BacktestResult:
    n_bets: int
    roi: float
    win_rate: float
    sharpe: float
    max_drawdown: float
    avg_clv: float
    ending_bankroll: float
    equity_curve: list[float] = field(default_factory=list)


def backtest(
    matches: list[HistoricalMatch],
    elo_model: EloModel | None = None,
    staking: str = "kelly",
    flat_stake_pct: float = 0.01,
    min_edge: float = DEFAULT_MIN_EDGE,
    starting_bankroll: float = 100.0,
) -> BacktestResult:
    elo_model = elo_model or EloModel()
    bankroll = starting_bankroll
    equity_curve = [bankroll]
    bet_returns: list[float] = []
    clv_list: list[float] = []

    for m in matches:
        p_home, p_draw, p_away = elo_model.match_probabilities(m.elo_home, m.elo_away, neutral_site=m.neutral)
        implied = remove_vig_multiplicative(
            [decimal_to_implied_prob(o) for o in (m.home_odds, m.draw_odds, m.away_odds)]
        )

        selections = [
            ("home", p_home, m.home_odds, implied[0], m.closing_home_odds, m.home_goals > m.away_goals),
            ("draw", p_draw, m.draw_odds, implied[1], m.closing_draw_odds, m.home_goals == m.away_goals),
            ("away", p_away, m.away_odds, implied[2], m.closing_away_odds, m.home_goals < m.away_goals),
        ]

        for _sel, model_p, odds, implied_p, closing_odds, won in selections:
            edge = model_p - implied_p
            ev = model_p * odds - 1
            if edge <= min_edge or ev <= 0:
                continue

            stake_pct = kelly_fraction(model_p, odds) if staking == "kelly" else flat_stake_pct
            if stake_pct <= 0:
                continue
            stake = bankroll * stake_pct
            pnl = stake * (odds - 1) if won else -stake
            bankroll += pnl
            bet_returns.append(pnl / stake)
            equity_curve.append(bankroll)

            closing_implied = decimal_to_implied_prob(closing_odds)
            clv_list.append(closing_implied - implied_p)  # positive = we beat the closing price

    returns = np.array(bet_returns)
    n_bets = len(returns)
    roi = float(returns.mean()) if n_bets else 0.0
    win_rate = float((returns > 0).mean()) if n_bets else 0.0
    sharpe = float(returns.mean() / returns.std()) if n_bets > 1 and returns.std() > 0 else 0.0

    equity = np.array(equity_curve)
    running_max = np.maximum.accumulate(equity)
    drawdowns = (equity - running_max) / running_max
    max_drawdown = float(drawdowns.min()) if len(drawdowns) else 0.0

    avg_clv = float(np.mean(clv_list)) if clv_list else 0.0

    return BacktestResult(
        n_bets=n_bets, roi=roi, win_rate=win_rate, sharpe=sharpe,
        max_drawdown=max_drawdown, avg_clv=avg_clv, ending_bankroll=float(bankroll),
        equity_curve=equity_curve,
    )
