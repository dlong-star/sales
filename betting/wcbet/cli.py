"""Command-line entry point.

    python -m wcbet analyze [--sims N] [--fixture ID]
    python -m wcbet backtest
"""
from __future__ import annotations

import argparse

from wcbet.backtest.engine import backtest
from wcbet.data.sample_history import SAMPLE_HISTORY
from wcbet.data.sources import SampleDataSource
from wcbet.pipeline import analyze_fixture
from wcbet.report import render_text


def cmd_analyze(args: argparse.Namespace) -> None:
    source = SampleDataSource()
    fixture_ids = [args.fixture] if args.fixture else source.list_fixtures()

    for fid in fixture_ids:
        fixture = source.get_fixture(fid)
        home = source.get_team(fixture.home_team)
        away = source.get_team(fixture.away_team)
        report = analyze_fixture(fixture, home, away, n_sims=args.sims, seed=args.seed)
        print(render_text(report))
        print()


def cmd_backtest(args: argparse.Namespace) -> None:
    result = backtest(SAMPLE_HISTORY, staking=args.staking, min_edge=args.min_edge)
    print("BACKTEST RESULT (sample dataset -- see wcbet/data/sample_history.py caveats)")
    print("=" * 78)
    print(f"  Bets placed:       {result.n_bets}")
    print(f"  ROI per bet:       {result.roi:+.2%}")
    print(f"  Win rate:          {result.win_rate:.1%}")
    print(f"  Sharpe (per-bet):  {result.sharpe:.2f}")
    print(f"  Max drawdown:      {result.max_drawdown:.1%}")
    print(f"  Avg CLV:           {result.avg_clv:+.2%}")
    print(f"  Ending bankroll:   {result.ending_bankroll:.2f} (started at 100.00)")


def main() -> None:
    parser = argparse.ArgumentParser(prog="wcbet", description="World Cup betting intelligence system")
    sub = parser.add_subparsers(dest="command", required=True)

    p_analyze = sub.add_parser("analyze", help="Run the full model pipeline on sample fixtures")
    p_analyze.add_argument("--fixture", default=None, help="Specific fixture id to analyze (default: all)")
    p_analyze.add_argument("--sims", type=int, default=100_000, help="Monte Carlo simulations per match (>= 100000)")
    p_analyze.add_argument("--seed", type=int, default=None, help="RNG seed for reproducibility")
    p_analyze.set_defaults(func=cmd_analyze)

    p_backtest = sub.add_parser("backtest", help="Backtest the value-detection rule on the sample historical dataset")
    p_backtest.add_argument("--staking", choices=["kelly", "flat"], default="kelly")
    p_backtest.add_argument("--min-edge", type=float, default=0.05, dest="min_edge")
    p_backtest.set_defaults(func=cmd_backtest)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
