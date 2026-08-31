"""
Unit tests for Phase 3 P3 FP8 TensorCore AMG Preconditioner and Negative Controls.
"""

import numpy as np
import scipy.sparse as sp
import pytest

from dualscale_solver.numeric.preconditioner_p3 import (
    AlgebraicMultigridPreconditioner,
    build_p3_amg_preconditioner,
    solve_cg_p3,
    negative_control_p3_amg_coarsening,
)


def test_p3_amg_hierarchy_construction():
    """Verify P3 AMG 3-level V-cycle hierarchy construction."""
    n = 64
    h = 1.0 / n
    diag = np.full(n, 2.0 / h**2)
    off = np.full(n - 1, -1.0 / h**2)
    A = sp.diags([off, diag, off], [-1, 0, 1], format="csr")

    p3 = build_p3_amg_preconditioner(A, levels=3, use_fp8=True)
    assert len(p3.A_levels) == 3
    assert len(p3.R_levels) == 2
    assert len(p3.P_levels) == 2
    assert p3.A_levels[0].shape == (64, 64)
    assert p3.A_levels[1].shape == (32, 32)
    assert p3.A_levels[2].shape == (16, 16)


def test_p3_amg_cg_solve():
    """Verify P3 AMG preconditioned solve convergence."""
    n = 64
    h = 1.0 / n
    diag = np.full(n, 2.0 / h**2)
    off = np.full(n - 1, -1.0 / h**2)
    A = sp.diags([off, diag, off], [-1, 0, 1], format="csr")
    b = np.arange(1, n + 1, dtype=np.float64)
    b -= b.mean()

    # Test FP8 TensorCore accelerated solve
    p3_fp8 = build_p3_amg_preconditioner(A, levels=3, use_fp8=True)
    res_fp8 = solve_cg_p3(A, b, precond=p3_fp8, tol=1e-8, maxiter=50)

    assert res_fp8["converged"] is True
    assert res_fp8["final_residual"] < 1e-4

    # Test FP64 solve
    p3_fp64 = build_p3_amg_preconditioner(A, levels=3, use_fp8=False)
    res_fp64 = solve_cg_p3(A, b, precond=p3_fp64, tol=1e-8, maxiter=50)

    assert res_fp64["converged"] is True
    assert res_fp64["final_residual"] < 1e-4
    assert res_fp64["residual_reduction"] < 1e-4


def test_negative_control_p3_amg():
    """Verify epistemic negative control for P3 AMG."""
    assert negative_control_p3_amg_coarsening() is True
