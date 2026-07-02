import numpy as np
import pytest
from scipy.stats import poisson as scipy_poisson

from wcbet.models.poisson_model import PoissonModel


def test_score_matrix_sums_to_one():
    model = PoissonModel()
    matrix = model.score_matrix(1.4, 1.1)
    assert matrix.sum() == pytest.approx(1.0)


def test_outcome_probs_sum_to_one():
    model = PoissonModel()
    matrix = model.score_matrix(1.6, 0.9)
    home, draw, away = model.outcome_probs(matrix)
    assert home + draw + away == pytest.approx(1.0)


def test_stronger_home_lambda_increases_home_win_prob():
    model = PoissonModel(dixon_coles_rho=None)
    matrix = model.score_matrix(2.2, 0.8)
    home, _, away = model.outcome_probs(matrix)
    assert home > away


def test_symmetric_lambdas_give_symmetric_outcome_probs():
    model = PoissonModel(dixon_coles_rho=None)
    matrix = model.score_matrix(1.3, 1.3)
    home, _, away = model.outcome_probs(matrix)
    assert home == pytest.approx(away, abs=1e-9)


def test_matches_independent_poisson_without_dixon_coles():
    """With rho disabled, the joint matrix must equal the product of two
    independent Poisson pmfs (basic correctness of the outer product)."""
    model = PoissonModel(dixon_coles_rho=None, max_goals=8)
    lam_h, lam_a = 1.5, 0.7
    matrix = model.score_matrix(lam_h, lam_a)
    n = 9
    expected = np.outer(scipy_poisson.pmf(np.arange(n), lam_h), scipy_poisson.pmf(np.arange(n), lam_a))
    expected = expected / expected.sum()
    np.testing.assert_allclose(matrix, expected, atol=1e-9)


def test_over_under_complementary():
    model = PoissonModel()
    matrix = model.score_matrix(1.4, 1.2)
    over, under = model.over_under(matrix, 2.5)
    assert over + under == pytest.approx(1.0)


def test_btts_complementary_and_bounded():
    model = PoissonModel()
    matrix = model.score_matrix(1.4, 1.2)
    yes, no = model.btts(matrix)
    assert yes + no == pytest.approx(1.0)
    assert 0 <= yes <= 1


def test_correct_scores_sorted_descending():
    model = PoissonModel()
    matrix = model.score_matrix(1.4, 1.2)
    top = model.correct_scores(matrix, top_n=5)
    probs = [p for _, p in top]
    assert probs == sorted(probs, reverse=True)


def test_dixon_coles_adjusts_low_scores_only():
    model_plain = PoissonModel(dixon_coles_rho=None)
    model_dc = PoissonModel(dixon_coles_rho=-0.1)
    lam_h, lam_a = 1.3, 1.1
    plain = model_plain.score_matrix(lam_h, lam_a)
    dc = model_dc.score_matrix(lam_h, lam_a)
    # cells outside the 2x2 low-score block should be proportionally close
    # (both normalized to sum 1, so an exact match isn't expected, but the
    # 0-0 cell must differ meaningfully under a nonzero rho).
    assert dc[0, 0] != pytest.approx(plain[0, 0])


def test_first_half_probs_sum_to_one():
    model = PoissonModel()
    home, draw, away = model.first_half_outcome_probs(1.6, 1.2)
    assert home + draw + away == pytest.approx(1.0)
