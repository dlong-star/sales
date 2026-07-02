"""Value detection: edge, expected value, Kelly sizing, confidence and risk
scoring, and the bet/no-bet recommendation rule.

Design note (CRITICAL RULES from the spec): the recommendation function
below is a pure function of (model probability, market odds, implied
probability, model disagreement, uncertainty width). It has no parameter
for "is this team favored" or "did the line move" -- those signals
structurally cannot influence the recommendation because they are never
passed in. A team being favored, or odds moving, is only ever a byproduct
of a real edge/EV signal, never a substitute for one.
"""
from __future__ import annotations

from dataclasses import dataclass

from wcbet.value.odds_math import fair_odds_from_prob

DEFAULT_MIN_EDGE = 0.05
DEFAULT_MIN_CONFIDENCE = 55.0
DEFAULT_KELLY_FRACTION = 0.25  # quarter-Kelly, for variance control
DEFAULT_KELLY_CAP = 0.05  # never stake more than 5% of bankroll on one bet
DEFAULT_MAX_DISAGREEMENT = 0.08  # max allowed stddev across model probabilities to call it "agreement"

# Underdog risk policy: once a selection has already cleared every
# recommendation gate (edge, EV, confidence, model agreement) on its own
# merits, size it more aggressively if the market prices it as the
# longshot. This does NOT relax the recommendation gates above and does NOT
# let "is an underdog" substitute for a real edge -- it only changes how
# hard we press a already-qualified underdog bet vs. an already-qualified
# favorite bet. Vegas books shade lines to protect against longshot bettors'
# behavioral bias; this policy deliberately takes on more variance than a
# book would, betting bigger into value the market has under-priced on dogs.
UNDERDOG_IMPLIED_PROB_THRESHOLD = 0.40  # devigged implied prob below this = "underdog" for this selection
UNDERDOG_KELLY_FRACTION_MULTIPLIER = 2.0  # quarter-Kelly -> half-Kelly on qualifying underdogs
UNDERDOG_KELLY_CAP_MULTIPLIER = 2.0  # 5% cap -> 10% cap on qualifying underdogs


def edge_pct(model_prob: float, implied_prob: float) -> float:
    return model_prob - implied_prob


def expected_value(model_prob: float, decimal_odds: float) -> float:
    """EV per unit staked, e.g. 0.08 means +8% expected return on stake."""
    return model_prob * decimal_odds - 1.0


def kelly_fraction(
    model_prob: float,
    decimal_odds: float,
    fraction: float = DEFAULT_KELLY_FRACTION,
    cap: float = DEFAULT_KELLY_CAP,
) -> float:
    b = decimal_odds - 1.0
    if b <= 0:
        return 0.0
    full_kelly = (model_prob * b - (1 - model_prob)) / b
    if full_kelly <= 0:
        return 0.0
    return min(full_kelly * fraction, cap)


def confidence_score(disagreement: float, ci_width: float) -> float:
    """0-100 heuristic: penalizes model disagreement and wide credible intervals."""
    disagreement_penalty = min(disagreement * 4.0, 1.0)
    ci_penalty = min(ci_width * 2.0, 1.0)
    score = 100.0 * (1 - disagreement_penalty) * (1 - ci_penalty)
    return max(0.0, min(100.0, score))


def risk_score(
    disagreement: float, ci_width: float, kelly_stake: float, data_completeness: float = 1.0,
    kelly_cap: float = DEFAULT_KELLY_CAP,
) -> float:
    """0-100 heuristic risk score (higher = riskier)."""
    score = 100.0 * (
        0.40 * min(disagreement * 5.0, 1.0)
        + 0.30 * min(ci_width * 2.0, 1.0)
        + 0.20 * min(kelly_stake / kelly_cap, 1.0)
        + 0.10 * (1 - data_completeness)
    )
    return max(0.0, min(100.0, score))


@dataclass
class BetRecommendation:
    market: str
    selection: str
    model_prob: float
    implied_prob: float
    edge: float
    decimal_odds: float
    fair_odds: float
    expected_value: float
    kelly_stake_pct: float
    confidence: float
    risk: float
    model_agreement: bool
    is_underdog: bool
    recommended: bool
    reason: str


def evaluate_market(
    market: str,
    selection: str,
    model_prob: float,
    decimal_odds: float,
    implied_prob: float,
    disagreement: float,
    ci_width: float = 0.0,
    data_completeness: float = 1.0,
    min_edge: float = DEFAULT_MIN_EDGE,
    min_confidence: float = DEFAULT_MIN_CONFIDENCE,
    max_disagreement: float = DEFAULT_MAX_DISAGREEMENT,
    kelly_fraction_: float = DEFAULT_KELLY_FRACTION,
    kelly_cap: float = DEFAULT_KELLY_CAP,
) -> BetRecommendation:
    is_underdog = implied_prob < UNDERDOG_IMPLIED_PROB_THRESHOLD
    if is_underdog:
        kelly_fraction_ = kelly_fraction_ * UNDERDOG_KELLY_FRACTION_MULTIPLIER
        kelly_cap = kelly_cap * UNDERDOG_KELLY_CAP_MULTIPLIER

    edge = edge_pct(model_prob, implied_prob)
    ev = expected_value(model_prob, decimal_odds)
    conf = confidence_score(disagreement, ci_width)
    kelly = kelly_fraction(model_prob, decimal_odds, kelly_fraction_, kelly_cap)
    risk = risk_score(disagreement, ci_width, kelly, data_completeness, kelly_cap)
    fair = fair_odds_from_prob(model_prob)
    agreement = disagreement <= max_disagreement

    reasons = []
    if edge <= min_edge:
        reasons.append(f"edge {edge:+.1%} <= required {min_edge:.0%}")
    if ev <= 0:
        reasons.append(f"EV {ev:+.1%} is not positive")
    if conf < min_confidence:
        reasons.append(f"confidence {conf:.0f} < required {min_confidence:.0f}")
    if not agreement:
        reasons.append(f"models disagree (spread {disagreement:.1%} > {max_disagreement:.0%})")
    if kelly <= 0:
        reasons.append("Kelly stake is zero")

    recommended = len(reasons) == 0
    reason = "Edge, EV, confidence and model agreement all clear threshold" if recommended else "; ".join(reasons)
    if recommended and is_underdog:
        reason += f" (underdog risk policy: {kelly_fraction_:.0%}-Kelly, {kelly_cap:.0%} cap)"

    return BetRecommendation(
        market=market, selection=selection, model_prob=model_prob, implied_prob=implied_prob,
        edge=edge, decimal_odds=decimal_odds, fair_odds=fair, expected_value=ev,
        kelly_stake_pct=kelly, confidence=conf, risk=risk, model_agreement=agreement,
        is_underdog=is_underdog, recommended=recommended, reason=reason,
    )
