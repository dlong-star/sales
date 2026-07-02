import pytest

from wcbet.models.ensemble import EnsembleModel, MLEnsemble, ModelEstimate


def test_combine_normalizes_to_one():
    estimates = [
        ModelEstimate("elo", 0.4, 0.3, 0.3),
        ModelEstimate("poisson", 0.45, 0.25, 0.30),
        ModelEstimate("bayesian", 0.42, 0.28, 0.30),
        ModelEstimate("monte_carlo", 0.43, 0.27, 0.30),
    ]
    result = EnsembleModel().combine(estimates)
    assert result.home + result.draw + result.away == pytest.approx(1.0)


def test_combine_falls_between_component_extremes():
    estimates = [ModelEstimate("elo", 0.6, 0.2, 0.2), ModelEstimate("poisson", 0.2, 0.3, 0.5)]
    result = EnsembleModel(weights={"elo": 0.5, "poisson": 0.5}).combine(estimates)
    assert 0.2 < result.home < 0.6


def test_disagreement_is_zero_when_models_agree():
    estimates = [ModelEstimate("elo", 0.5, 0.25, 0.25), ModelEstimate("poisson", 0.5, 0.25, 0.25)]
    result = EnsembleModel().combine(estimates)
    assert result.disagreement == pytest.approx(0.0)


def test_disagreement_is_positive_when_models_diverge():
    estimates = [ModelEstimate("elo", 0.7, 0.15, 0.15), ModelEstimate("poisson", 0.3, 0.35, 0.35)]
    result = EnsembleModel().combine(estimates)
    assert result.disagreement > 0.1


def test_ml_ensemble_refuses_to_fit_on_too_little_data():
    ml = MLEnsemble()
    with pytest.raises(ValueError):
        ml.fit([[0.5, 0.3, 0.2] * 4] * 10, [0] * 10)
    assert not ml.is_trained


def test_ml_ensemble_fits_and_predicts_on_sufficient_synthetic_data():
    import numpy as np

    rng = np.random.default_rng(0)
    n = 300
    # Feature = [elo_h, elo_d, elo_a, poisson_h, poisson_d, poisson_a, bayes_h, bayes_d, bayes_a, mc_h, mc_d, mc_a]
    # Make a synthetic but learnable relationship: outcome mostly follows elo_h vs elo_a.
    rows, outcomes = [], []
    for _ in range(n):
        home_strength = rng.uniform(0.2, 0.7)
        row = [home_strength] * 12
        outcome = 0 if home_strength > 0.5 else (2 if home_strength < 0.35 else 1)
        rows.append(row)
        outcomes.append(outcome)

    ml = MLEnsemble()
    ml.fit(rows, outcomes)
    assert ml.is_trained
    probs = ml.predict_proba([0.65] * 12)
    assert probs is not None
    assert sum(probs) == pytest.approx(1.0, abs=1e-6)
