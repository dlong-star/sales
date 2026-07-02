"""Assembles and renders the 10-part per-match output format."""
from __future__ import annotations

from dataclasses import dataclass, field

from wcbet.value.edge import BetRecommendation


@dataclass
class MatchReport:
    fixture_id: str
    home_team: str
    away_team: str
    neutral_site: bool

    model_probabilities: dict[str, tuple[float, float, float]]
    ensemble_probabilities: tuple[float, float, float]
    ensemble_disagreement: float
    ml_ensemble_active: bool

    lambda_home: float
    lambda_away: float

    markets: dict[str, list[BetRecommendation]]  # "1x2", "totals_2.5", "btts"
    player_props: dict[str, dict[str, float]]  # "home_anytime_scorer", "away_anytime_scorer"

    key_supporting_factors: list[str]
    key_risk_factors: list[str]
    sensitivity: dict[str, tuple[float, float, float]]

    correct_score_top: list[tuple[tuple[int, int], float]] = field(default_factory=list)
    first_half_probabilities: tuple[float, float, float] | None = None


def render_text(report: MatchReport) -> str:
    lines: list[str] = []
    lines.append("=" * 78)
    lines.append(f"{report.home_team} vs {report.away_team}  ({report.fixture_id})")
    lines.append("=" * 78)

    lines.append("\n[1] PREDICTED PROBABILITIES (per model)")
    for name, (h, d, a) in report.model_probabilities.items():
        lines.append(f"  {name:>12}:  home {h:6.1%}   draw {d:6.1%}   away {a:6.1%}")
    eh, ed, ea = report.ensemble_probabilities
    lines.append(f"  {'ENSEMBLE':>12}:  home {eh:6.1%}   draw {ed:6.1%}   away {ea:6.1%}"
                 f"   (model spread {report.ensemble_disagreement:.1%}, "
                 f"ML meta-learner {'ACTIVE' if report.ml_ensemble_active else 'inactive'})")
    if report.first_half_probabilities:
        fh, fd, fa = report.first_half_probabilities
        lines.append(f"  {'1st half':>12}:  home {fh:6.1%}   draw {fd:6.1%}   away {fa:6.1%}")

    lines.append(f"\n  Expected goals: {report.home_team} {report.lambda_home:.2f} - "
                 f"{report.lambda_away:.2f} {report.away_team}")

    if report.correct_score_top:
        top = ", ".join(f"{h}-{a} ({p:.1%})" for (h, a), p in report.correct_score_top[:5])
        lines.append(f"  Most likely scorelines: {top}")

    for market_name, recs in report.markets.items():
        lines.append(f"\n[2-7] MARKET: {market_name.upper()}")
        header = f"  {'selection':<10}{'model%':>9}{'implied%':>10}{'edge':>8}{'fair odds':>11}" \
                 f"{'book odds':>11}{'EV':>8}{'kelly%':>8}{'conf':>7}{'risk':>7}  bet?"
        lines.append(header)
        for rec in recs:
            lines.append(
                f"  {rec.selection:<10}{rec.model_prob:>9.1%}{rec.implied_prob:>10.1%}{rec.edge:>+8.1%}"
                f"{rec.fair_odds:>11.2f}{rec.decimal_odds:>11.2f}{rec.expected_value:>+8.1%}"
                f"{rec.kelly_stake_pct:>8.1%}{rec.confidence:>7.0f}{rec.risk:>7.0f}"
                f"  {'BET' if rec.recommended else 'no'}"
            )
            if rec.recommended:
                lines.append(f"      -> recommended wager: {rec.kelly_stake_pct:.1%} of bankroll on {rec.selection} "
                             f"@ {rec.decimal_odds:.2f} ({rec.reason})")
            elif rec.edge > 0:
                lines.append(f"      -> no bet: {rec.reason}")

    if report.player_props:
        lines.append("\n[PLAYER PROPS] Anytime goalscorer probability (Monte Carlo)")
        for side, probs in report.player_props.items():
            if not probs:
                continue
            lines.append(f"  {side}:")
            for name, p in sorted(probs.items(), key=lambda x: -x[1]):
                lines.append(f"    {name:<16}{p:6.1%}")

    lines.append("\n[8] KEY SUPPORTING FACTORS")
    for f in report.key_supporting_factors:
        lines.append(f"  + {f}")

    lines.append("\n[9] KEY RISK FACTORS")
    if report.key_risk_factors:
        for r in report.key_risk_factors:
            lines.append(f"  - {r}")
    else:
        lines.append("  (none flagged)")

    lines.append("\n[10] SENSITIVITY ANALYSIS (home win probability by scenario)")
    baseline = report.sensitivity.get("baseline")
    for name, (h, d, a) in report.sensitivity.items():
        marker = "  <- baseline" if name == "baseline" else ""
        delta = f" ({h - baseline[0]:+.1%})" if baseline and name != "baseline" else ""
        lines.append(f"  {name:<18} home {h:6.1%}{delta}{marker}")

    return "\n".join(lines)
