"""Model 5: Machine-learning ensemble.

Two combination strategies are provided:

* ``EnsembleModel`` -- a transparent weighted average of the other models'
  1X2 probabilities, plus a model-agreement (disagreement) diagnostic used
  downstream by the value-detection "multiple models agree" rule. This is
  the default and is robust with a handful of matches.
* ``MLEnsemble`` -- a logistic-regression meta-learner that stacks the
  same per-model probabilities and learns its own combination weights from
  historical outcomes. It refuses to fit on fewer than
  ``MIN_TRAINING_MATCHES`` rows (overfitting risk on tiny samples) and the
  pipeline falls back to ``EnsembleModel`` whenever it hasn't been trained.
  The bundled sample historical dataset is far smaller than this floor by
  design -- a real deployment needs thousands of historical matches with
  known outcomes before this meta-learner should be trusted.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


@dataclass
class ModelEstimate:
    name: str
    home: float
    draw: float
    away: float


@dataclass
class EnsembleResult:
    home: float
    draw: float
    away: float
    disagreement: float  # max stddev across models, per outcome
    components: list[ModelEstimate] = field(default_factory=list)


DEFAULT_WEIGHTS = {"elo": 0.20, "poisson": 0.30, "bayesian": 0.25, "monte_carlo": 0.25}


class EnsembleModel:
    def __init__(self, weights: dict[str, float] | None = None) -> None:
        self.weights = weights or dict(DEFAULT_WEIGHTS)

    def combine(self, estimates: list[ModelEstimate]) -> EnsembleResult:
        w = np.array([self.weights.get(e.name, 0.0) for e in estimates])
        if w.sum() == 0:
            w = np.ones(len(estimates))
        w = w / w.sum()

        homes = np.array([e.home for e in estimates])
        draws = np.array([e.draw for e in estimates])
        aways = np.array([e.away for e in estimates])

        home = float((homes * w).sum())
        draw = float((draws * w).sum())
        away = float((aways * w).sum())
        total = home + draw + away
        home, draw, away = home / total, draw / total, away / total

        disagreement = float(max(homes.std(), draws.std(), aways.std()))
        return EnsembleResult(home=home, draw=draw, away=away, disagreement=disagreement, components=estimates)


class MLEnsemble:
    """Logistic-regression meta-learner stacking per-model probabilities."""

    MIN_TRAINING_MATCHES = 150

    def __init__(self) -> None:
        self._model = None

    @property
    def is_trained(self) -> bool:
        return self._model is not None

    def fit(self, feature_rows: list[list[float]], outcomes: list[int]) -> None:
        """outcomes: 0=home win, 1=draw, 2=away win."""
        if len(feature_rows) < self.MIN_TRAINING_MATCHES:
            raise ValueError(
                f"MLEnsemble needs >= {self.MIN_TRAINING_MATCHES} historical matches to fit safely; "
                f"got {len(feature_rows)}. Use EnsembleModel's weighted average until more data is available."
            )
        from sklearn.linear_model import LogisticRegression

        model = LogisticRegression(max_iter=1000)
        model.fit(feature_rows, outcomes)
        self._model = model

    def predict_proba(self, feature_row: list[float]) -> tuple[float, float, float] | None:
        if self._model is None:
            return None
        proba = self._model.predict_proba([feature_row])[0]
        classes = list(self._model.classes_)
        ordered = [proba[classes.index(c)] if c in classes else 0.0 for c in (0, 1, 2)]
        return tuple(ordered)  # type: ignore[return-value]
