"""
Mexico vs England — 2026 World Cup Round of 16 (Estadio Azteca, July 5/6 2026)
Monte Carlo simulation built from each side's actual tournament data.

Data sources (as of 2026-07-05, pre-match):
  England results:  4-2 Croatia, 0-0 Ghana, 2-0 Panama, 2-1 DR Congo (R32)
  Mexico results:   2-0 South Africa, 1-0 South Korea, 3-0 Czechia, 2-0 Ecuador (R32)
  Opta tournament averages: England 1.9 xG/gm, 72% possession, 13.3 chances/gm
                            Mexico  1.3 xG/gm, 54% possession,  8.5 chances/gm
  Venue: Azteca (2,240m altitude). Mexico unbeaten in WC games there (8W 2D),
         played 4 of 4 tournament games at altitude; England none.
  Market (for calibration only): England ~40.8%, Draw ~32.3%, Mexico ~32.3% implied.
"""

import random
import math

random.seed(20260705)

N_SIMS = 200_000

# ---------------------------------------------------------------- team data
TOURNAMENT_AVG_GOALS = 1.40  # avg goals per team per game, typical WC baseline

england = {
    "gf_per_game": 8 / 4,      # 8 scored in 4 games
    "ga_per_game": 3 / 4,      # 3 conceded
    "xg_per_game": 1.9,        # Opta
    "games": 4,
}

mexico = {
    "gf_per_game": 8 / 4,      # 8 scored in 4 games
    "ga_per_game": 0 / 4,      # 0 conceded — 4 straight clean sheets
    "xg_per_game": 1.3,        # Opta
    "games": 4,
}


def attack_rating(team):
    """Blend actual goals with xG (xG is the more stable signal),
    then shrink toward the mean — 4 games is a small sample and both
    sides fattened their numbers against sub-elite opposition."""
    blended = 0.45 * team["gf_per_game"] + 0.55 * team["xg_per_game"]
    ratio = blended / TOURNAMENT_AVG_GOALS
    return 1 + (ratio - 1) * 0.75  # 25% shrinkage


def defense_rating(team):
    """Goals allowed vs baseline, Bayesian-shrunk with a 3-game prior of
    average defense so Mexico's 0.00 GA doesn't produce an impossible 0."""
    prior_games = 3
    shrunk_ga = (team["ga_per_game"] * team["games"]
                 + TOURNAMENT_AVG_GOALS * prior_games) / (team["games"] + prior_games)
    ratio = shrunk_ga / TOURNAMENT_AVG_GOALS
    return 1 + (ratio - 1) * 0.75


ENG_ATT, ENG_DEF = attack_rating(england), defense_rating(england)
MEX_ATT, MEX_DEF = attack_rating(mexico), defense_rating(mexico)

# ------------------------------------------------------- venue adjustments
# Azteca: 2,240m altitude, 87k partisan crowd, Mexico acclimatized (4 games
# already played there / at altitude), England zero minutes at altitude this
# tournament. Historical home/altitude effects in CONMEBOL/CONCACAF data run
# ~+10-15% for the hosts and ~-10-15% for unacclimatized visitors.
MEX_HOME_BOOST = 1.13
ENG_ALTITUDE_PENALTY = 0.87

lambda_mex = TOURNAMENT_AVG_GOALS * MEX_ATT * ENG_DEF * MEX_HOME_BOOST
lambda_eng = TOURNAMENT_AVG_GOALS * ENG_ATT * MEX_DEF * ENG_ALTITUDE_PENALTY

# Knockout football is cagier than the group stage
KNOCKOUT_DAMP = 0.92
lambda_mex *= KNOCKOUT_DAMP
lambda_eng *= KNOCKOUT_DAMP


def poisson(lam):
    """Knuth sampler."""
    L, k, p = math.exp(-lam), 0, 1.0
    while True:
        p *= random.random()
        if p <= L:
            return k
        k += 1


def shootout():
    """Mexico gets a small home-crowd edge; England's recent shootout
    record is respectable, so keep it close to a coin flip."""
    return "MEX" if random.random() < 0.53 else "ENG"


def simulate_match():
    mg, eg = poisson(lambda_mex), poisson(lambda_eng)
    result_90 = "MEX" if mg > eg else "ENG" if eg > mg else "DRAW"
    if result_90 != "DRAW":
        return result_90, result_90, (mg, eg)
    # Extra time: ~1/3 of a match, altitude fatigue bites England harder
    mg_et = poisson(lambda_mex * 0.38)
    eg_et = poisson(lambda_eng * 0.30)
    if mg_et != eg_et:
        adv = "MEX" if mg_et > eg_et else "ENG"
        return "DRAW", adv, (mg + mg_et, eg + eg_et)
    return "DRAW", shootout() + "_PENS", (mg + mg_et, eg + eg_et)


# ---------------------------------------------------------------- run sims
tally_90 = {"MEX": 0, "ENG": 0, "DRAW": 0}
advance = {"MEX": 0, "ENG": 0}
pens = {"MEX": 0, "ENG": 0}
scorelines = {}

for _ in range(N_SIMS):
    r90, adv, in_ = simulate_match()
    tally_90[r90] += 1
    if adv.endswith("_PENS"):
        w = adv[:3]
        advance[w] += 1
        pens[w] += 1
    else:
        advance[adv] += 1
    scorelines[in_] = scorelines.get(in_, 0) + 1

pct = lambda n: 100 * n / N_SIMS

print(f"Model lambdas: Mexico {lambda_mex:.2f}, England {lambda_eng:.2f}\n")
print("90-minute result:")
print(f"  England win : {pct(tally_90['ENG']):5.1f}%")
print(f"  Draw        : {pct(tally_90['DRAW']):5.1f}%")
print(f"  Mexico win  : {pct(tally_90['MEX']):5.1f}%\n")
print("To advance (incl. extra time & penalties):")
print(f"  ENGLAND     : {pct(advance['ENG']):5.1f}%  (of which on pens: {pct(pens['ENG']):.1f}%)")
print(f"  MEXICO      : {pct(advance['MEX']):5.1f}%  (of which on pens: {pct(pens['MEX']):.1f}%)\n")
print("Most likely final scorelines (Mexico-England, incl. ET where played):")
for (m, e), c in sorted(scorelines.items(), key=lambda kv: -kv[1])[:6]:
    print(f"  {m}-{e} : {pct(c):4.1f}%")

# ------------------------------------------------- market-blended verdict
# The pure form model ignores squad quality priors (England's roster/Elo is
# well above Mexico's), which the betting market prices in. De-vigged
# to-advance market: England ~52%, Mexico ~48%. Blend 50/50 with the model.
mkt_mex = 0.481
blend_mex = 0.5 * (advance["MEX"] / N_SIMS) + 0.5 * mkt_mex
print("\nBlended verdict (50% form model / 50% de-vigged market):")
print(f"  MEXICO advances : {100*blend_mex:.1f}%")
print(f"  ENGLAND advances: {100*(1-blend_mex):.1f}%")
