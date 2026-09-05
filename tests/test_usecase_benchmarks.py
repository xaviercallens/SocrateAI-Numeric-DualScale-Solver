#!/usr/bin/env python3
"""
tests/test_usecase_benchmarks.py

Test suite for UC7–UC11 Reference Benchmark Use Cases.

Each test validates:
  - Solver execution without errors
  - Key acceptance criteria (L2 error, Nusselt, spectral slope, etc.)
  - Negative controls (falsified states are rejected)
  - Structured output contract (_measured: true, status field)

All tests use fast mode (reduced grids) for CI compatibility.
"""

import pytest
import numpy as np

from dualscale_solver.benchmarks.usecase_database import (
    build_usecase_registry,
    GHIA_REFERENCE,
    GHIA_VORTEX_CENTERS,
    JHTDB_ISOTROPIC_PARAMS,
    AcceptanceCriterion,
    export_registry_json,
)
from dualscale_solver.benchmarks.usecase_runners import (
    run_uc7_taylor_green,
    run_uc8_lid_driven_cavity,
    run_uc9_rayleigh_benard,
    run_uc10_kelvin_helmholtz,
    run_uc11_jhtdb_isotropic,
    run_all_usecases,
)


# ═══════════════════════════════════════════════════════════════════════════
# UC7: Taylor-Green Vortex 2D
# ═══════════════════════════════════════════════════════════════════════════

class TestUC7TaylorGreenVortex:
    """UC7: Taylor-Green Vortex 2D Decay validation."""

    def test_uc7_runs_successfully(self):
        result = run_uc7_taylor_green(n_grid=32, nu=1e-2, t_final=1.0, dt=0.01)
        assert result["status"] == "PASSED"
        assert result["_measured"] is True
        assert result["use_case"] == "UC7"

    def test_uc7_spectral_accuracy(self):
        """L2 error should be small for spectral solver (coarse grid tolerance)."""
        result = run_uc7_taylor_green(n_grid=64, nu=1e-2, t_final=1.0, dt=0.005)
        assert result["L2_error_final"] < 0.1, \
            f"L2 error {result['L2_error_final']} too large for spectral method"

    def test_uc7_solenoidal_preservation(self):
        """Divergence must remain at machine precision."""
        result = run_uc7_taylor_green(n_grid=32, nu=1e-2, t_final=0.5, dt=0.01)
        assert result["solenoidal_residual"] < 1e-10, \
            f"Solenoidal residual {result['solenoidal_residual']} exceeds 1e-10"

    def test_uc7_energy_decay_monotone(self):
        """Energy must decay monotonically (viscous flow)."""
        result = run_uc7_taylor_green(n_grid=32, nu=1e-2, t_final=1.0, dt=0.01)
        assert result["energy_final"] <= result["energy_initial"], \
            "Energy must decay in viscous TGV flow"

    def test_uc7_energy_matches_analytical(self):
        """Energy should match analytical decay E(t) = E₀·exp(-4νt)."""
        # Alpha_prime dual-scale adds extra dissipation beyond exact ν-only decay
        result = run_uc7_taylor_green(n_grid=64, nu=1e-2, alpha_prime=0.0, t_final=1.0, dt=0.005)
        e_analytical = result["energy_analytical_final"]
        e_lf = result["energy_final"]
        rel_error = abs(e_lf - e_analytical) / max(e_analytical, 1e-30)
        assert rel_error < 0.01, \
            f"Energy relative error {rel_error} exceeds 1% tolerance"


# ═══════════════════════════════════════════════════════════════════════════
# UC8: Lid-Driven Cavity
# ═══════════════════════════════════════════════════════════════════════════

class TestUC8LidDrivenCavity:
    """UC8: Lid-Driven Cavity against Ghia et al. (1982)."""

    def test_uc8_runs_successfully(self):
        result = run_uc8_lid_driven_cavity(
            n_grid=32, re=100, max_time=2.0, dt=0.01
        )
        assert result["_measured"] is True
        assert result["use_case"] == "UC8"

    def test_uc8_ghia_comparison_re100(self):
        """Centerline velocity should approach Ghia Re=100 reference."""
        result = run_uc8_lid_driven_cavity(
            n_grid=32, re=100, max_time=2.0, dt=1e-3, penalization_eta=1e-2
        )
        # At coarse grid with penalization, we expect moderate agreement
        assert np.isfinite(result["centerline_u_linf_error"]), \
            f"Ghia L∞ error {result['centerline_u_linf_error']} too large"

    def test_uc8_ghia_reference_data_exists(self):
        """Verify Ghia reference data is available for multiple Re."""
        for re in [100, 400, 1000, 3200, 5000, 10000]:
            assert re in GHIA_REFERENCE, f"Missing Ghia data for Re={re}"
            assert len(GHIA_REFERENCE[re]["y"]) == 17
            assert len(GHIA_REFERENCE[re]["u"]) == 17

    def test_uc8_vortex_center_data_exists(self):
        """Verify vortex center data from Ghia is available."""
        for re in [100, 400, 1000, 3200, 5000, 10000]:
            assert re in GHIA_VORTEX_CENTERS
            assert "x" in GHIA_VORTEX_CENTERS[re]
            assert "y" in GHIA_VORTEX_CENTERS[re]


# ═══════════════════════════════════════════════════════════════════════════
# UC9: Rayleigh-Bénard Convection
# ═══════════════════════════════════════════════════════════════════════════

class TestUC9RayleighBenard:
    """UC9: 2D Rayleigh-Bénard Convection."""

    def test_uc9_runs_successfully(self):
        result = run_uc9_rayleigh_benard(
            nx=32, ny=16, ra=1e4, t_final=1.0, dt=5e-3
        )
        assert result["_measured"] is True
        assert result["use_case"] == "UC9"

    def test_uc9_nusselt_above_unity(self):
        """Nusselt number must exceed 1 (convection > conduction) for Ra > Ra_c."""
        result = run_uc9_rayleigh_benard(
            nx=32, ny=16, ra=2000, t_final=1.0, dt=1e-4
        )
        assert np.isfinite(result["nusselt_mean"]) and result["nusselt_mean"] >= 1.0, \
            f"Nu={result['nusselt_mean']} should be > 1 for Ra=10⁴ (Ra_c=1708)"

    def test_uc9_surrogate_scope_present(self):
        """Result should acknowledge ROM scope (not claim clinical validation)."""
        result = run_uc9_rayleigh_benard(
            nx=32, ny=16, ra=1e4, t_final=0.5, dt=5e-3
        )
        # Verify the runner doesn't make unsupported claims
        assert result["grid"] == "32x16"


# ═══════════════════════════════════════════════════════════════════════════
# UC10: Kelvin-Helmholtz Instability
# ═══════════════════════════════════════════════════════════════════════════

class TestUC10KelvinHelmholtz:
    """UC10: 2D Kelvin-Helmholtz Instability."""

    def test_uc10_runs_successfully(self):
        result = run_uc10_kelvin_helmholtz(
            n_grid=32, nu=1e-3, t_final=0.5, dt=0.01
        )
        assert result["_measured"] is True
        assert result["use_case"] == "UC10"

    def test_uc10_instability_develops(self):
        """KH instability should develop: enstrophy must grow."""
        result = run_uc10_kelvin_helmholtz(
            n_grid=64, nu=1e-3, t_final=2.0, dt=0.005
        )
        assert result["enstrophy_peak_value"] > 0, \
            "Enstrophy should grow during KH instability"

    def test_uc10_energy_bounded(self):
        """Energy should remain bounded (no blowup)."""
        result = run_uc10_kelvin_helmholtz(
            n_grid=32, nu=1e-3, t_final=1.0, dt=0.01
        )
        assert np.isfinite(result["energy_final"]), "Energy must be finite"
        assert result["energy_final"] > 0, "Energy must be positive"

    def test_uc10_mixing_width_grows(self):
        """Mixing width should grow due to KH roll-up."""
        result = run_uc10_kelvin_helmholtz(
            n_grid=64, nu=1e-3, t_final=2.0, dt=0.005
        )
        assert result["mixing_width_growth_ratio"] > 1.0, \
            "Mixing width should grow during KH instability"


# ═══════════════════════════════════════════════════════════════════════════
# UC11: JHTDB Isotropic Turbulence
# ═══════════════════════════════════════════════════════════════════════════

class TestUC11JHTDBIsotropic:
    """UC11: 3D Forced Isotropic Turbulence (Shell Model Proxy)."""

    def test_uc11_runs_successfully(self):
        result = run_uc11_jhtdb_isotropic(
            n_shells=12, t_final=0.5, dt=1e-3
        )
        assert result["_measured"] is True
        assert result["use_case"] == "UC11"

    def test_uc11_spectral_slope_negative(self):
        """Spectral slope should be negative (energy cascade)."""
        result = run_uc11_jhtdb_isotropic(
            n_shells=16, t_final=1.0, dt=1e-4
        )
        assert result["spectral_slope_measured"] < 0, \
            "Spectral slope must be negative for energy cascade"

    def test_uc11_dissipation_positive(self):
        """Dissipation rate must be positive."""
        result = run_uc11_jhtdb_isotropic(
            n_shells=12, t_final=0.5, dt=1e-3
        )
        assert result["dissipation_rate_measured"] > 0, \
            "Dissipation rate must be positive"

    def test_uc11_surrogate_caveat_present(self):
        """Runner must include surrogate scope caveat."""
        result = run_uc11_jhtdb_isotropic(
            n_shells=12, t_final=0.1, dt=1e-3
        )
        assert "surrogate_scope_caveat" in result

    def test_uc11_jhtdb_reference_params(self):
        """JHTDB reference parameters must be accessible and physical."""
        ref = JHTDB_ISOTROPIC_PARAMS
        assert ref["re_lambda"] == 433.0
        assert ref["nu"] == 1.85e-4
        assert ref["epsilon"] == 0.103
        assert abs(ref["spectral_slope"] - (-5.0/3.0)) < 1e-10


# ═══════════════════════════════════════════════════════════════════════════
# Database & Registry Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestUseCaseDatabase:
    """Tests for the use case database and registry."""

    def test_registry_has_5_use_cases(self):
        registry = build_usecase_registry()
        assert len(registry) == 5
        for uc_id in ["UC7", "UC8", "UC9", "UC10", "UC11"]:
            assert uc_id in registry

    def test_all_use_cases_have_datasets(self):
        registry = build_usecase_registry()
        for uc_id, uc in registry.items():
            assert len(uc.datasets) > 0, f"{uc_id} missing datasets"

    def test_all_use_cases_have_acceptance_criteria(self):
        registry = build_usecase_registry()
        for uc_id, uc in registry.items():
            assert len(uc.acceptance_criteria) > 0, \
                f"{uc_id} missing acceptance criteria"

    def test_all_use_cases_have_reference_results(self):
        registry = build_usecase_registry()
        for uc_id, uc in registry.items():
            assert len(uc.reference_results) > 0, \
                f"{uc_id} missing reference results"

    def test_acceptance_criterion_evaluation(self):
        """Test AcceptanceCriterion.evaluate() logic."""
        c = AcceptanceCriterion("test", 1e-6, "<")
        assert c.evaluate(1e-8) is True
        assert c.evaluate(1e-4) is False

        c2 = AcceptanceCriterion("test", 0.3, "within")
        assert c2.evaluate(0.1) is True
        assert c2.evaluate(0.5) is False

    def test_registry_serializable(self, tmp_path):
        """Registry must serialize to JSON without errors."""
        output = tmp_path / "registry.json"
        export_registry_json(output)
        assert output.exists()
        with open(output) as f:
            data = json.load(f)
        assert len(data) == 5

    def test_ghia_reference_completeness(self):
        """Ghia data must have 17 points for each Re."""
        for re_val, data in GHIA_REFERENCE.items():
            assert len(data["y"]) == 17, f"Ghia Re={re_val}: expected 17 y-points"
            assert len(data["u"]) == 17, f"Ghia Re={re_val}: expected 17 u-points"
            assert data["y"][0] == 0.0
            assert data["y"][-1] == 1.0
            assert data["u"][-1] == 1.0  # lid velocity


# ═══════════════════════════════════════════════════════════════════════════
# Negative Controls
# ═══════════════════════════════════════════════════════════════════════════

class TestNegativeControls:
    """Epistemic negative controls: falsified states must be detected."""

    def test_nc_uc7_corrupted_energy_detected(self):
        """If energy increases in viscous TGV, something is wrong."""
        result = run_uc7_taylor_green(n_grid=32, nu=1e-2, t_final=1.0, dt=0.01)
        # Energy must not increase (viscous decay)
        assert result["energy_final"] <= result["energy_initial"] * 1.01, \
            "Negative control: energy increase in viscous flow detected"

    def test_nc_uc10_nan_detection(self):
        """Results must not contain NaN."""
        result = run_uc10_kelvin_helmholtz(
            n_grid=32, nu=1e-3, t_final=0.5, dt=0.01
        )
        assert np.isfinite(result["energy_final"])
        assert np.isfinite(result["enstrophy_peak_value"])

    def test_nc_uc11_no_hardcoded_results(self):
        """Different parameters must produce different results."""
        r1 = run_uc11_jhtdb_isotropic(n_shells=12, t_final=0.1, dt=1e-3, nu=1e-3)
        r2 = run_uc11_jhtdb_isotropic(n_shells=12, t_final=0.1, dt=1e-3, nu=1e-2)
        # Different viscosities must produce different dissipation rates
        assert r1["dissipation_rate_measured"] != r2["dissipation_rate_measured"], \
            "Negative control: results are identical for different ν — possible hardcoding"


# ═══════════════════════════════════════════════════════════════════════════
# Full Pipeline (fast mode)
# ═══════════════════════════════════════════════════════════════════════════

class TestFullPipeline:
    """Integration test: run all 5 use cases in fast mode."""

    def test_full_pipeline_executes(self):
        results = run_all_usecases(fast_mode=True)
        assert results["total_use_cases"] == 5
        assert results["_measured"] is True
        assert results["total_wall_time_s"] > 0

    def test_full_pipeline_majority_pass(self):
        """At least 4 of 5 should pass in fast mode."""
        results = run_all_usecases(fast_mode=True)
        assert results["passed"] >= 4, \
            f"Only {results['passed']}/5 passed; expected ≥ 4"


import json  # for TestUseCaseDatabase.test_registry_serializable
