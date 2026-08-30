"""
Unit Tests for Dyadic Shell Model & Telescoping Invariants.
"""

from fractions import Fraction
import numpy as np
import pytest

from dualscale_solver.exact.cascade_invariants import (
    verify_telescoping_energy_conservation,
    compute_exact_enstrophy,
    compute_exact_dualscale_enstrophy,
    negative_control_broken_energy_conservation,
)
from dualscale_solver.numeric.dyadic_cascade import DyadicShellSolver


def test_exact_telescoping_conservation():
    u_amps = [Fraction(1, 1), Fraction(1, 2), Fraction(1, 4), Fraction(1, 8)]
    k_waves = [Fraction(1, 1), Fraction(2, 1), Fraction(4, 1), Fraction(8, 1)]
    result = verify_telescoping_energy_conservation(u_amps, k_waves)
    assert result["is_conservative"] is True
    assert result["status"] == "PASSED"


def test_negative_control_nc_ds_04():
    """Negative control: Broken triad coupling leaks energy."""
    assert negative_control_broken_energy_conservation() is True


def test_exact_enstrophy_bounds():
    u_amps = [Fraction(1, 2), Fraction(1, 4), Fraction(1, 8)]
    k_waves = [Fraction(1, 1), Fraction(2, 1), Fraction(16, 1)]
    alpha_prime = Fraction(1, 16) # k_max = 4, k_max_sq = 16

    std_enstrophy = compute_exact_enstrophy(u_amps, k_waves)
    reg_enstrophy = compute_exact_dualscale_enstrophy(u_amps, k_waves, alpha_prime)

    assert reg_enstrophy <= std_enstrophy
    assert reg_enstrophy > 0


def test_numerical_dyadic_solver_inviscid_conservation():
    """Test that with nu=0, energy is conserved to high accuracy over short times."""
    solver = DyadicShellSolver(
        n_shells=12,
        k0=1.0,
        nu=0.0, # Inviscid
        alpha_prime=None,
    )
    u0 = np.zeros(12)
    u0[0] = 1.0
    u0[1] = 0.5

    result = solver.solve(t_span=(0.0, 0.05), u0=u0, dt=0.0005)
    e_initial = result["energy"][0]
    e_final = result["energy"][-1]
    
    # Energy drift should be very small for RK4 inviscid integration
    rel_drift = abs(e_final - e_initial) / e_initial
    assert rel_drift < 1e-4


def test_numerical_dyadic_dualscale_boundedness():
    """Test that dual-scale regularized solver stably damps high-k modes."""
    solver_reg = DyadicShellSolver(
        n_shells=16,
        nu=1e-3,
        alpha_prime=0.05,
    )
    u0 = np.zeros(16)
    u0[0] = 1.0
    u0[1] = 0.8

    result = solver_reg.solve(t_span=(0.0, 0.5), u0=u0, dt=0.001)
    assert result["energy"][-1] < result["energy"][0]
    assert np.all(np.isfinite(result["enstrophy"]))
