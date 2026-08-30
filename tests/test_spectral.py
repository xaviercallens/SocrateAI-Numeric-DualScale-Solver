"""
Unit Tests for 2D Pseudo-Spectral Navier-Stokes Solver.
"""

import numpy as np
import pytest
from dualscale_solver.numeric.fourier_spectral import PseudoSpectralNavierStokes2D


def test_leray_projector_divergence_free():
    solver = PseudoSpectralNavierStokes2D(n_grid=32, nu=1e-3)
    
    # Generate arbitrary random compressible velocity field
    np.random.seed(42)
    random_u = np.random.randn(2, 32, 32)
    random_u_hat = np.fft.fft2(random_u)

    # Before projection, divergence should be non-zero (negative control)
    div_before = solver.max_divergence(random_u_hat)
    assert div_before > 1e-2

    # After projection, divergence must be zero (machine precision)
    proj_u_hat = solver.project_leray(random_u_hat)
    div_after = solver.max_divergence(proj_u_hat)
    assert div_after < 1e-12


def test_leray_projector_idempotence():
    solver = PseudoSpectralNavierStokes2D(n_grid=32, nu=1e-3)
    random_u_hat = np.fft.fft2(np.random.randn(2, 32, 32))
    
    p1 = solver.project_leray(random_u_hat)
    p2 = solver.project_leray(p1)
    
    # Projector is idempotent: P^2 = P
    np.testing.assert_allclose(p1, p2, atol=1e-14)


def test_taylor_green_vortex_decay():
    solver = PseudoSpectralNavierStokes2D(n_grid=32, nu=0.01)
    u0_hat = solver.initialize_taylor_green()

    # Verify initial divergence
    assert solver.max_divergence(u0_hat) < 1e-14

    # Run for short duration
    result = solver.solve(t_span=(0.0, 0.1), u_hat0=u0_hat, dt=0.01)

    # Energy must decay monotonically under viscous dissipation
    energies = result["energy"]
    assert energies[-1] < energies[0]
    assert np.all(np.diff(energies) <= 1e-12)

    # Divergence remains zero at all time steps
    assert np.max(result["max_divergences"]) < 1e-13
