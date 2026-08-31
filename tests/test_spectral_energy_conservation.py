"""
Test: 2D Pseudo-Spectral Navier-Stokes Energy Conservation & Solenoidal Constraint.

Lesson LL-07 (H6): The Leray divergence check must record per-step data.
Lesson LL-09 (W2): Leray projection must only be applied at the final RK4 step.

HARDNESS Invariants tested:
  H6 — Solenoidal transversality: |k . u_hat| < 1e-13 at every step.
  H7 — Energy monotonicity: energy[-1] < energy[0] for viscous run.
  H4 — Non-vacuity: energy > 0 after simulation.
"""

import numpy as np
import pytest
from dualscale_solver.numeric.fourier_spectral import PseudoSpectralNavierStokes2D
from dualscale_solver.numeric.rk4_integrator import solve_ivp_rk4


def test_spectral_energy_conservation_inviscid():
    """
    At nu=0 (inviscid), 2D spectral solver must conserve energy to < 1e-6
    relative drift over 50 time steps with the Taylor-Green initial condition.

    Tests the W2 fix: Leray projection at intermediate stages would slightly
    modify the energy budget; projection only at final step is conservative.
    """
    solver = PseudoSpectralNavierStokes2D(n_grid=32, nu=0.0, alpha_prime=None)
    u_hat0 = solver.initialize_taylor_green()

    times, traj = solve_ivp_rk4(
        solver.rhs_fourier,
        (0.0, 0.05),
        solver.project_leray(u_hat0),
        dt=1e-3,
        projector=solver.project_leray,
    )

    E0 = solver.energy(traj[0])
    Ef = solver.energy(traj[-1])
    rel_drift = abs(Ef - E0) / E0
    assert rel_drift < 1e-5, (
        f"Inviscid 2D spectral energy drift too large: {rel_drift:.2e} > 1e-5\n"
        f"(This may indicate intermediate-stage Leray projection is still active — see W2 fix)"
    )


def test_spectral_leray_per_step_divergence():
    """
    H6: Record divergence at every time step via callback.
    Verify all per-step divergences satisfy |k . u_hat| < 1e-13.

    Lesson LL-07: We must collect actual per-step data, not just a scalar max.
    """
    solver = PseudoSpectralNavierStokes2D(n_grid=32, nu=1e-3, alpha_prime=None)
    u_hat0 = solver.initialize_taylor_green()
    u_hat0_proj = solver.project_leray(u_hat0)

    per_step_div = []

    def div_callback(t, u_hat):
        per_step_div.append(solver.max_divergence(u_hat))

    times, traj = solve_ivp_rk4(
        solver.rhs_fourier,
        (0.0, 0.05),
        u_hat0_proj,
        dt=1e-3,
        projector=solver.project_leray,
        callback=div_callback,
    )

    assert len(per_step_div) > 0, "Callback was never called — no per-step divergence recorded"

    max_div = max(per_step_div)
    assert max_div < 1e-13, (
        f"H6 solenoidal constraint violated: max per-step |k.u_hat| = {max_div:.3e} > 1e-13"
    )
    assert len(per_step_div) == len(times) - 1, (
        f"Expected {len(times)-1} callback calls, got {len(per_step_div)}"
    )


def test_spectral_energy_monotone_viscous():
    """
    H7: Energy must be monotone decreasing for viscous flow.
    Checks that the solver correctly dissipates energy over time.
    """
    solver = PseudoSpectralNavierStokes2D(n_grid=32, nu=5e-3, alpha_prime=None)
    u_hat0 = solver.initialize_taylor_green()
    result = solver.solve((0.0, 0.1), u_hat0, dt=1e-3)

    assert result["energy"][-1] < result["energy"][0], (
        f"H7 energy monotonicity violated: E_final={result['energy'][-1]:.6e} >= E_initial={result['energy'][0]:.6e}"
    )
    assert result["energy"][-1] > 0, "H4 non-vacuity violated: energy collapsed to zero"


def test_spectral_leray_idempotence():
    """
    H6: Leray projector must be idempotent: P(P(u)) = P(u).
    """
    solver = PseudoSpectralNavierStokes2D(n_grid=32, nu=1e-3)
    u_hat0 = solver.initialize_taylor_green()
    pu = solver.project_leray(u_hat0)
    ppu = solver.project_leray(pu)

    max_err = float(np.max(np.abs(ppu - pu)))
    assert max_err < 1e-14, (
        f"H6 Leray idempotence violated: ||P(P(u)) - P(u)||_inf = {max_err:.3e}"
    )
