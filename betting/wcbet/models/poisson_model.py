"""Model 3: Poisson goal model with a Dixon-Coles low-score correction.

Given (lambda_home, lambda_away) from the xG engine, builds the full
scoreline probability matrix and derives every standard market from it:
1X2, totals, BTTS, correct score, and first-half probabilities.

Matrix convention: ``matrix[i, j] = P(home scores i, away scores j)``.
"""
from __future__ import annotations

import numpy as np
from scipy.stats import poisson

DEFAULT_DIXON_COLES_RHO = -0.08
DEFAULT_MAX_GOALS = 10
DEFAULT_FIRST_HALF_SHARE = 0.44  # empirically first halves see slightly fewer goals than an even split


class PoissonModel:
    def __init__(self, max_goals: int = DEFAULT_MAX_GOALS, dixon_coles_rho: float | None = DEFAULT_DIXON_COLES_RHO):
        self.max_goals = max_goals
        self.rho = dixon_coles_rho

    def _dc_tau(self, i: int, j: int, lam_h: float, lam_a: float, rho: float) -> float:
        if i == 0 and j == 0:
            return 1 - lam_h * lam_a * rho
        if i == 0 and j == 1:
            return 1 + lam_h * rho
        if i == 1 and j == 0:
            return 1 + lam_a * rho
        if i == 1 and j == 1:
            return 1 - rho
        return 1.0

    def score_matrix(self, lambda_home: float, lambda_away: float) -> np.ndarray:
        n = self.max_goals + 1
        home_probs = poisson.pmf(np.arange(n), lambda_home)
        away_probs = poisson.pmf(np.arange(n), lambda_away)
        matrix = np.outer(home_probs, away_probs)

        if self.rho:
            for i in range(min(2, n)):
                for j in range(min(2, n)):
                    matrix[i, j] *= self._dc_tau(i, j, lambda_home, lambda_away, self.rho)

        matrix = np.clip(matrix, 0, None)
        return matrix / matrix.sum()

    @staticmethod
    def outcome_probs(matrix: np.ndarray) -> tuple[float, float, float]:
        n = matrix.shape[0]
        i_idx, j_idx = np.indices((n, n))
        home_win = matrix[i_idx > j_idx].sum()
        draw = matrix[i_idx == j_idx].sum()
        away_win = matrix[i_idx < j_idx].sum()
        return float(home_win), float(draw), float(away_win)

    @staticmethod
    def over_under(matrix: np.ndarray, line: float = 2.5) -> tuple[float, float]:
        n = matrix.shape[0]
        i_idx, j_idx = np.indices((n, n))
        total_goals = i_idx + j_idx
        over = matrix[total_goals > line].sum()
        return float(over), float(1 - over)

    @staticmethod
    def btts(matrix: np.ndarray) -> tuple[float, float]:
        n = matrix.shape[0]
        i_idx, j_idx = np.indices((n, n))
        yes = matrix[(i_idx >= 1) & (j_idx >= 1)].sum()
        return float(yes), float(1 - yes)

    @staticmethod
    def correct_scores(matrix: np.ndarray, top_n: int = 10) -> list[tuple[tuple[int, int], float]]:
        n = matrix.shape[0]
        scores = [((i, j), float(matrix[i, j])) for i in range(n) for j in range(n)]
        scores.sort(key=lambda item: -item[1])
        return scores[:top_n]

    def first_half_outcome_probs(
        self, lambda_home: float, lambda_away: float, fh_share: float = DEFAULT_FIRST_HALF_SHARE
    ) -> tuple[float, float, float]:
        fh_matrix = self.score_matrix(lambda_home * fh_share, lambda_away * fh_share)
        return self.outcome_probs(fh_matrix)
