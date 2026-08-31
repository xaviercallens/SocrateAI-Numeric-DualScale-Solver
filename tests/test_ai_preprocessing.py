"""
Tests for LeanFlow AI Preprocessing Module
==========================================
Validates mesh estimation, boundary condition inference, parameter tuning,
and negative controls under Mathesis Stream 0 Hardness guidelines (H11, H12, H13).
"""

import math
import numpy as np
import pytest

from dualscale_solver.ai.preprocessing import (
    NeuroSymbolicMesher,
    BoundaryConditionInference,
    ParameterTuner,
    ZeroShotFluidSurrogate,
    run_ai_preprocessing_pipeline,
)


def _generate_synthetic_tgv(n: int = 32) -> np.ndarray:
    """Generate 2D Taylor-Green velocity field for testing."""
    x = np.linspace(0, 2 * np.pi, n, endpoint=False)
    y = np.linspace(0, 2 * np.pi, n, endpoint=False)
    X, Y = np.meshgrid(x, y, indexing="ij")
    u = np.sin(X) * np.cos(Y)
    v = -np.cos(X) * np.sin(Y)
    return np.array([u, v])


def test_neurosymbolic_mesher_resolution_kolmogorov():
    """Verify that the AI mesher selects a grid resolving the Kolmogorov scale."""
    u_tgv = _generate_synthetic_tgv(32)
    mesher = NeuroSymbolicMesher(domain_length=2.0 * math.pi)
    
    config = mesher.analyze_field(u_tgv, nu=1e-3)
    
    assert config._measured is True
    assert config.grid_n >= 32
    assert config.k_max_eta >= 0.5
    assert config.kinetic_energy > 0.0
    assert config.enstrophy > 0.0
    assert config.dissipation_rate > 0.0
    assert config.alpha_prime > 0.0


def test_solenoidal_boundary_condition_projection():
    """Verify that Fourier Leray projection eliminates divergence to machine precision."""
    # Create non-solenoidal field (u = grad(phi))
    n = 32
    x = np.linspace(0, 2 * np.pi, n, endpoint=False)
    X, Y = np.meshgrid(x, x, indexing="ij")
    u_nonsolenoidal = np.array([np.sin(2 * X), np.cos(2 * Y)])  # div = 2*cos(2X) - 2*sin(2Y) != 0

    u_proj, config = BoundaryConditionInference.enforce_solenoidal_projection(u_nonsolenoidal)

    assert config._measured is True
    assert config.is_solenoidal is True
    assert config.max_divergence_residual < 1e-12
    assert config.leray_projected is True


def test_parameter_tuner_stiffness_and_cfl():
    """Verify that parameter tuning respects CFL and detects stiffness regime."""
    u_tgv = _generate_synthetic_tgv(32)
    mesher = NeuroSymbolicMesher()
    mesh_config = mesher.analyze_field(u_tgv, nu=1e-3)

    tuning = ParameterTuner.tune(mesh_config, u_max=1.0, cfl_target=0.4)

    assert tuning._measured is True
    assert tuning.dt_recommended > 0.0
    assert tuning.dt_recommended < 0.1
    assert tuning.cfl_target == 0.4
    assert tuning.recommended_time_scheme in [
        "rusty_sundials_cvode_bdf",
        "rusty_sundials_cvode_adams",
    ]


def test_zero_shot_surrogate_spectrum():
    """Verify that the zero-shot surrogate computes valid Kolmogorov spectrum."""
    k_vals = np.array([1.0, 2.0, 4.0, 8.0, 16.0])
    e_k = ZeroShotFluidSurrogate.predict_spectrum(k_vals, epsilon=1e-2, nu=1e-3)

    assert len(e_k) == len(k_vals)
    # Energy should decay monotonically with wavenumber k
    assert np.all(np.diff(e_k) < 0)
    assert np.all(e_k > 0)


def test_negative_control_nc_ds_11_unphysical_enstrophy_rejected():
    """
    Negative Control NC-DS-11:
    Ensure field with zero or NaN values does not produce zero/negative grid size.
    """
    zero_field = np.zeros((2, 32, 32))
    mesher = NeuroSymbolicMesher()
    config = mesher.analyze_field(zero_field, nu=1e-3)

    # Must safely fallback to minimum grid resolution, not crash or return 0
    assert config.grid_n >= 16
    assert config.enstrophy >= 1e-12
    assert config.alpha_prime > 0.0


def test_end_to_end_ai_preprocessing_pipeline():
    """Verify full AI preprocessing pipeline execution time and output consistency."""
    u_tgv = _generate_synthetic_tgv(32)
    u_proj, result = run_ai_preprocessing_pipeline(u_tgv, nu=1e-3, cfl_target=0.35)

    assert result._measured is True
    assert result.elapsed_ms < 200.0  # fast preprocessing < 200ms
    assert len(result.provenance_hash) == 64
    assert result.boundary.is_solenoidal is True
    assert result.mesh.grid_n in [16, 32, 64, 128, 256]
    
    d = result.to_dict()
    assert d["_measured"] is True
    assert "mesh" in d
    assert "tuning" in d
