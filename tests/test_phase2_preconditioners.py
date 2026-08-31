"""
Unit tests for Phase 2 P1 and P2 Preconditioners and Epistemic Negative Controls.
"""

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla
import pytest

from dualscale_solver.numeric.preconditioner_p1 import (
    SpectralFourierGatePreconditioner,
    build_p1_fourier_gate,
    build_multiscale_fourier_system,
    compute_spectral_condition_number,
    negative_control_p1_spectral_distortion,
)
from dualscale_solver.numeric.preconditioner_p2 import (
    MultilevelILUPreconditioner,
    solve_fgmres_p2,
    negative_control_p2_singular_matrix,
)


def test_p1_fourier_gate_1d_and_2d():
    """Verify P1 construction and matvec application in 1D and 2D."""
    p1_1d = build_p1_fourier_gate(grid_size=64, alpha_prime=0.01, ndim=1)
    assert p1_1d.shape == (64, 64)
    v1 = np.ones(64)
    res1 = p1_1d.matvec(v1)
    assert res1.shape == (64,)
    assert not np.isnan(res1).any()

    p1_2d = build_p1_fourier_gate(grid_size=16, alpha_prime=0.01, ndim=2)
    assert p1_2d.shape == (256, 256)
    v2 = np.ones(256)
    res2 = p1_2d.matvec(v2)
    assert res2.shape == (256,)
    assert not np.isnan(res2).any()


def test_p1_condition_number_reduction():
    """Verify P1 reduces condition number on multiscale Fourier system."""
    n = 32
    A, _ = build_multiscale_fourier_system((n, n), alpha_prime=0.01)
    p1 = build_p1_fourier_gate(grid_size=n, alpha_prime=0.01, ndim=2)

    cond_raw = compute_spectral_condition_number(A, precond=None, grid_shape=(n, n))
    cond_p1 = compute_spectral_condition_number(A, precond=p1, grid_shape=(n, n))

    assert cond_p1["condition_number"] <= 1.0e3
    assert cond_p1["condition_number"] < cond_raw["condition_number"]


def test_p2_multilevel_ilu_fgmres():
    """Verify P2 ILU factorization and FGMRES convergence."""
    n = 32
    h = 1.0 / n
    diag = np.full(n, 2.0 / h**2)
    off = np.full(n - 1, -1.0 / h**2)
    A = sp.diags([off, diag, off], [-1, 0, 1], format="csc")
    b = np.arange(1, n + 1, dtype=np.float64)
    b -= b.mean()

    precond = MultilevelILUPreconditioner(A, drop_tol=1e-4)
    res = solve_fgmres_p2(A, b, precond=precond, tol=1e-8, maxiter=20)

    assert res["converged"] is True
    assert res["final_residual"] < 1e-6


def test_negative_controls_p1_p2():
    """Verify epistemic negative controls for P1 and P2."""
    assert negative_control_p1_spectral_distortion() is True
    assert negative_control_p2_singular_matrix() is True
