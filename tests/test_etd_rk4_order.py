"""
Test: Empirical Convergence Order for ETD-RK4 Integrator.

Lesson LL-08: The ETD-RK4 stage 3 uses exact integrating factor coefficients.
HARDNESS Invariant: H4 (Non-Vacuity) & H5 (Enstrophy Boundedness).
"""

import numpy as np
import pytest
from dualscale_solver.numeric.dyadic_cascade import DyadicShellSolver


def _run_etd_cascade_decay(n_shells: int, nu: float, dt: float, t_end: float):
    """
    Run dyadic cascade with pure viscous dissipation (no nonlinear term, no forcing).
    Initial condition: single-mode u0[0] = 1.0, all others zero.
    For shell 0: du_0/dt = -D_0 * u_0 where D_0 = nu * k0^2.
    Exact solution: u_0(t) = exp(-nu * k0^2 * t).
    """
    solver = DyadicShellSolver(
        n_shells=n_shells,
        k0=1.0,
        nu=nu,
        alpha_prime=None,   # Standard dissipation
        forcing_amp=0.0,
    )
    u0 = np.zeros(n_shells)
    u0[0] = 1.0  # Single-mode initial condition

    result = solver.solve((0.0, t_end), u0, dt=dt)
    return float(result["trajectory"][-1][0])


def test_etd_rk4_convergence_order():
    """
    Verify ETD-RK4 achieves exact exponential integrating factor accuracy (< 1e-13)
    or convergence order >= 3.5 on viscous decay problem.
    """
    nu = 1.0
    k0 = 1.0
    t_end = 0.5
    lam = nu * k0**2
    u_exact = np.exp(-lam * t_end)

    dts = [0.1, 0.05, 0.025]
    errors = []
    for dt in dts:
        u_num = _run_etd_cascade_decay(n_shells=1, nu=nu, dt=dt, t_end=t_end)
        errors.append(abs(u_num - u_exact))

    # Because ETD-RK4 solves linear dissipation via integrating factor exactly,
    # errors are already at machine precision (< 1e-14)
    all_machine_precision = all(e < 1e-13 for e in errors)
    if not all_machine_precision:
        orders = [
            np.log2(errors[i] / errors[i + 1]) for i in range(len(errors) - 1)
        ]
        assert all(o >= 3.5 for o in orders), f"Order below 3.5: {orders}"
    else:
        assert all_machine_precision, f"Errors exceeded machine precision: {errors}"


def test_etd_rk4_inviscid_energy_conservation():
    """
    Verify that energy is conserved to < 1e-3 relative drift in the
    inviscid limit (nu=0) over short time.
    """
    solver = DyadicShellSolver(n_shells=12, k0=1.0, nu=0.0, alpha_prime=None)
    u0 = np.zeros(12)
    u0[0] = 1.0
    u0[1] = 0.5

    result = solver.solve((0.0, 0.05), u0, dt=5e-4)
    E0 = result["energy"][0]
    Ef = result["energy"][-1]
    rel_drift = abs(Ef - E0) / E0
    assert rel_drift < 1e-3, (
        f"Inviscid energy drift too large: {rel_drift:.2e} > 1e-3\n"
        f"Initial energy={E0:.6f}, Final energy={Ef:.6f}"
    )


def test_dualscale_enstrophy_bounded():
    """
    Verify that dual-scale regularization keeps max enstrophy <= 1/alpha'.
    This is HARDNESS H5 — the core singularity prevention invariant.
    """
    alpha_prime = 0.01
    solver = DyadicShellSolver(n_shells=16, nu=1e-3, alpha_prime=alpha_prime)
    u0 = np.zeros(16)
    u0[0] = 1.0
    u0[1] = 0.8

    result = solver.solve((0.0, 1.0), u0, dt=0.001)
    max_enstrophy = float(np.max(result["enstrophy"]))
    bound = 1.0 / alpha_prime

    assert max_enstrophy <= bound, (
        f"Enstrophy bound violated: max_enstrophy={max_enstrophy:.4f} > 1/alpha'={bound:.1f}"
    )
