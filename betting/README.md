# Dave and Nubs Soccer Retirement Plan (`wcbet`)

A quantitative framework for estimating *true* match probabilities and
comparing them against sportsbook-implied probabilities, so that bets are
only ever recommended when a statistically defensible edge exists. The goal
is long-run expected value, not picking winners.

> **This is a research/decision-support engine, not a live trading system.**
> It ships with hand-authored sample data and synthetic historical odds (see
> [Data and limitations](#data-and-limitations)) so it runs and is fully
> testable out of the box. Wire in real data sources before using it to size
> real bets. Sports betting is illegal or regulated in many jurisdictions —
> you are responsible for complying with local law, and for your own
> bankroll/risk management. Nothing here is financial advice.

## Quick start

```bash
cd betting
pip install -e .          # or: pip install -r requirements.txt
python -m pytest -q       # 55 tests covering the model math
python -m wcbet analyze --sims 100000        # full report on both sample fixtures
python -m wcbet analyze --fixture WC2026-FINAL-ARG-FRA --seed 42
python -m wcbet backtest --staking kelly --min-edge 0.05
```

## Architecture

```
wcbet/
  data/
    models.py            TeamStats, Player, MatchConditions, MarketOdds, Fixture
    sources.py            Abstract TeamDataSource/PlayerDataSource/OddsDataSource
                           + SampleDataSource (reference impl over sample data)
    sample_teams.py        Illustrative team dataset (Elo, SPI, xG, form, ...)
    sample_fixtures.py     Illustrative fixtures with rosters, odds, conditions
    sample_history.py      Illustrative historical dataset for backtesting

  models/
    elo.py                 Model 1: Elo-based prediction engine
    goal_expectancy.py      Model 2: xG engine -> (lambda_home, lambda_away)
    poisson_model.py        Model 3: Poisson / Dixon-Coles scoreline matrix
                             -> 1X2, totals, BTTS, correct score, first half
    bayesian.py              Model 4: Gamma-Poisson Bayesian model with
                             posterior-predictive credible intervals
    monte_carlo.py           Model 6: >=100,000-sim Monte Carlo, incl.
                             player-level anytime-goalscorer probabilities
    ensemble.py               Model 5: weighted-average ensemble +
                             optional ML (logistic regression) meta-learner

  value/
    odds_math.py            Implied probability, vig removal, fair odds
    edge.py                  Edge %, EV, Kelly sizing, confidence/risk score,
                             and the bet/no-bet recommendation rule

  backtest/
    engine.py                ROI, win rate, Sharpe, max drawdown, CLV

  pipeline.py                 Orchestrates all 6 models -> ensemble -> value
                             detection -> sensitivity analysis for a fixture
  report.py                   Assembles/renders the 10-part output format
  cli.py                      `wcbet analyze` / `wcbet backtest`

tests/                        55 unit + smoke tests (pytest)
```

Nothing in `models/`, `value/`, `backtest/`, or `pipeline.py` imports a
concrete data provider — everything reads `TeamStats` / `Player` / `Fixture`
objects. That boundary is `data/sources.py`: implement `TeamDataSource`,
`PlayerDataSource`, and `OddsDataSource` against a real provider (an odds
API, a paid Elo/SPI/FIFA feed, your own warehouse) and pass instances into
the pipeline instead of `SampleDataSource`. No pipeline code changes.

## The six models

1. **Elo** (`models/elo.py`) — standard logistic Elo win expectancy with a
   home-advantage offset, extended to three outcomes via a Gaussian draw
   curve centered on evenly matched teams. Also implements the
   goal-difference-weighted rating update used to progress ratings match by
   match (used by the backtester).
2. **xG engine** (`models/goal_expectancy.py`) — converts each team's
   recency-weighted attack/defense xG rate (season / last20 / last10 / last5,
   weighted 0.4/0.3/0.2/0.1) into `(lambda_home, lambda_away)` for the
   fixture, Dixon-Coles style.
3. **Poisson / Dixon-Coles** (`models/poisson_model.py`) — builds the full
   scoreline probability matrix from the two lambdas, with the low-score
   correlation correction from Dixon & Coles (1997). Every derived market
   (1X2, totals, BTTS, correct score, first half) is read directly off this
   matrix.
4. **Bayesian** (`models/bayesian.py`) — treats attack/defense goal rates as
   Gamma-distributed with a conjugate prior centered on the league average,
   updated with each team's trailing-20-match sample. Sampling from the
   posterior and pushing each sample through the Poisson outcome formula
   yields both a point estimate and a genuine credible interval on the
   *probability itself* (parameter uncertainty) — separate from Monte Carlo
   simulation noise.
5. **Ensemble** (`models/ensemble.py`) — `EnsembleModel` is a transparent
   weighted average of the four probability-producing models plus a
   disagreement diagnostic (used by the "multiple models agree" rule).
   `MLEnsemble` is a logistic-regression meta-learner that stacks the same
   features and *learns* the combination from historical outcomes, but it
   refuses to fit on fewer than 150 historical matches — the bundled sample
   history (16 matches) is intentionally far below that floor, so the
   pipeline reports `ML meta-learner inactive` and falls back to the
   weighted average. Feed it a real multi-thousand-match dataset to activate
   it.
6. **Monte Carlo** (`models/monte_carlo.py`) — >= 100,000 simulations per
   match (enforced: the simulator raises if asked for fewer), applying the
   same Dixon-Coles correction via importance-weighted resampling. Cross-
   validates the analytic Poisson solution (see
   `tests/test_monte_carlo.py::test_converges_to_analytic_poisson...`), gives
   simulation-based standard errors on every market, and is the only model
   that produces player-level props (anytime goalscorer, via multinomial
   attribution of each simulated team goal by the scorer's share of team xG
   involvement).

## Value detection

`value/edge.py::evaluate_market` is a pure function of model probability,
market odds, de-vigged implied probability, and model disagreement/CI width.
It has **no parameter for "is this team favored" or "did the line move"** —
that's structural, not just a convention (see
`tests/test_edge_kelly.py::test_recommendation_never_takes_favorite_or_line_movement_signals`).
A bet is only ever recommended when *all* of the following hold:

- Edge (model probability − de-vigged implied probability) exceeds 5%
- Expected value is positive
- Confidence score (penalizes model disagreement and Bayesian CI width)
  clears 55/100
- Models agree (disagreement spread ≤ 8 percentage points)
- Kelly stake (quarter-Kelly, capped at 5% of bankroll) is positive

All thresholds are named constants at the top of `edge.py` — tune them for
your own risk tolerance, but don't remove the structural guarantee above.

**Underdog risk policy.** Once (and only once) a selection has already
cleared every gate above on its own merits, `evaluate_market` sizes it more
aggressively if the market's de-vigged implied probability is below 40%
(`UNDERDOG_IMPLIED_PROB_THRESHOLD`): the Kelly fraction doubles (quarter- →
half-Kelly) and the stake cap doubles (5% → 10% of bankroll). This is a
deliberate policy to press harder into value the market has under-priced on
longshots than a sportsbook would ever risk on its own book — it changes
*how big* an already-qualified underdog bet is, never *whether* one
qualifies. Underdog status alone still can't manufacture a recommendation
(see `tests/test_edge_kelly.py::test_underdog_policy_does_not_bypass_recommendation_gates`).

## Backtesting

`backtest/engine.py::backtest` replays a historical dataset match-by-match,
applies the same edge/EV filter, stakes Kelly or flat, and reports ROI, win
rate, Sharpe ratio, max drawdown, and average closing-line value (CLV). It
uses Elo alone (not the full 6-model stack) for backtest throughput, since
that's the one model that only needs pre-match ratings, not trailing xG/form
data that the sample historical rows don't carry.

## Data and limitations

**This environment has no credentials for any live sports-data or odds
provider**, so nothing here polls a real feed. Three sample datasets stand
in for it, and each carries an explicit caveat in its module docstring:

- `data/sample_teams.py` / `data/sample_fixtures.py` — hand-authored,
  illustrative Elo/SPI/xG/roster/odds figures for demonstration and testing.
  Not live data.
- `data/sample_history.py` — match **scores** reflect the author's best
  recollection of 2022 World Cup group-stage (matchday 1) results, not
  re-verified against an authoritative source in this session. Pre-match
  Elo ratings are rough approximations. **Odds are synthetic** (generated
  from the Elo model's own output plus noise and a fixed bookmaker margin),
  not real historical sportsbook lines.

Consequences of this:

- The 16-row backtest is a demonstration of the *math* (ROI/Sharpe/drawdown/
  CLV compute correctly and behave sensibly), not a claim about real-world
  strategy performance. Treat any ROI/Sharpe number from it as illustrative
  only — real backtesting needs real closing-line history across thousands
  of matches.
- The ML ensemble meta-learner never activates on the bundled data by
  design (150-match floor vs. 16 available rows).
- "Continuously update" data collection (the spec's DATA COLLECTION section)
  is implemented as an interface (`data/sources.py`), not a running service —
  there's nothing here to poll on a schedule without real API credentials.

To move to production: implement `TeamDataSource` / `PlayerDataSource` /
`OddsDataSource` against real providers (e.g., a paid Elo/SPI feed, an odds
API with opening/closing snapshots, your own scouting database), backfill
`sample_history.py`-shaped rows with real historical results and closing
odds (ideally thousands of matches across multiple tournaments/competitions
per the spec's BACKTESTING section), and re-check whether `MLEnsemble` should
be trained and activated once the training floor is met.

## Critical rules (enforced by design, not just convention)

- Never recommend a wager solely because a team is favored — `evaluate_market`
  never receives that signal.
- Never recommend a wager solely because odds moved — line movement/public
  betting % appear only as *risk factors* in the report (see
  `pipeline.py::_key_risk_factors`), never as recommendation inputs.
- Always compare true (model) probability vs. de-vigged implied probability —
  every market evaluation goes through `odds_math.devig_market` first.
- Multiple models must agree before a bet is recommended (see the ensemble
  disagreement gate above).
