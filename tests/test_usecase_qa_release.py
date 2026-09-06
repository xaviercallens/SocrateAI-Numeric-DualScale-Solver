"""
tests/test_usecase_qa_release.py

End-to-End Regression Test Suite for Major Release QA
======================================================
Tests the 3 canonical use cases and 3 Phase E2 enterprise extensions,
verifying release gating protocol defined in:
.agents/skills/usecase-qa-release-verification/SKILL.md
"""

import sys
import pytest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "target" / "release"))

from scripts.usecase_qa_release_verifier import (
    run_release_qa,
    verify_use_case_1,
    verify_use_case_2,
    verify_use_case_3,
    verify_use_case_4_ida_dae,
    verify_use_case_5_polarquant,
    verify_use_case_6_pyo3_zerocopy,
    verify_use_case_7_taylor_green,
    verify_use_case_8_lid_driven_cavity,
    verify_use_case_9_rayleigh_benard,
    verify_use_case_10_kelvin_helmholtz,
    verify_use_case_11_jhtdb_isotropic,
    verify_use_case_12_burgers,
    verify_use_case_13_poiseuille,
    verify_use_case_14_double_shear_layer,
    verify_use_case_15_vortex_merger,
    verify_use_case_16_hartmann_mhd,
    run_negative_controls,
    audit_epistemic_nomenclature,
)


def test_qa_negative_controls():
    """Verify that all epistemic negative controls catch violations (H2)."""
    nc_results, all_passed = run_negative_controls(verbose=False)
    assert all_passed is True
    assert nc_results["nc_energy_growth_caught"] is True
    assert nc_results["nc_ram_overflow_caught"] is True
    assert nc_results["nc_enstrophy_inversion_caught"] is True
    assert nc_results["nc_banned_buzzwords_caught"] is True
    assert nc_results["nc_ida_dae_divergence_caught"] is True
    assert nc_results["nc_polarquant_distortion_caught"] is True
    assert nc_results["nc_memory_slice_overflow_caught"] is True
    assert nc_results["nc_uc7_divergence_caught"] is True
    assert nc_results["nc_uc8_cavity_deviation_caught"] is True
    assert nc_results["nc_uc9_unphysical_nusselt_caught"] is True
    assert nc_results["nc_uc10_mixing_collapse_caught"] is True
    assert nc_results["nc_uc11_anti_cascade_slope_caught"] is True
    assert nc_results["nc_uc12_shock_divergence_caught"] is True
    assert nc_results["nc_uc13_poiseuille_profile_caught"] is True
    assert nc_results["nc_uc14_shear_layer_suppression_caught"] is True
    assert nc_results["nc_uc15_vortex_merger_repulsion_caught"] is True
    assert nc_results["nc_uc16_hartmann_mhd_deviation_caught"] is True



def test_qa_gate1_stiff_cascade():
    """Verify Gate 1: Stiff dyadic cascade achieves required speedup and reduction."""
    metrics = verify_use_case_1(verbose=False)
    assert metrics["status"] == "PASSED"
    assert metrics["step_reduction_factor"] >= 500.0
    assert metrics["wall_time_speedup_factor"] >= 1000.0
    assert metrics["energy_monotone"] is True
    assert metrics["energy_dissipated_pct"] > 0.0


def test_qa_gate2_embedded_realtime():
    """Verify Gate 2: Zero-allocation embedded kernel within 64 KB RAM budget."""
    metrics = verify_use_case_2(verbose=False)
    assert metrics["status"] == "PASSED"
    assert metrics["static_ram_bytes"] <= 65536
    assert metrics["ram_budget_margin_pct"] >= 90.0  # > 90% margin
    assert metrics["max_state_deviation"] <= 1e-8
    assert metrics["energy_monotone"] is True


def test_qa_gate3_dualscale_regularity():
    """Verify Gate 3: Dual-scale dissipation enhances UV enstrophy damping."""
    metrics = verify_use_case_3(verbose=False)
    assert metrics["status"] == "PASSED"
    assert metrics["enstrophy_suppression_ratio"] >= 1.5
    assert metrics["energy_dissipated_dual"] >= metrics["energy_dissipated_classical"]
    assert metrics["energy_monotone"] is True


def test_qa_gate4_ida_dae_solenoidal():
    """Verify Gate 4: Coupled Incompressible Navier-Stokes DAE Solenoidal Projection."""
    metrics = verify_use_case_4_ida_dae(verbose=False)
    assert metrics["status"] == "PASSED"
    assert metrics["div_residual"] <= 1e-2
    assert metrics["is_solenoidal"] is True
    assert metrics["energy"] > 0.0


def test_qa_gate5_polarquant_compression():
    """Verify Gate 5: PolarQuant 8x Telemetry Compression & Bounded Distortion."""
    metrics = verify_use_case_5_polarquant(verbose=False)
    assert metrics["status"] == "PASSED"
    assert metrics["compression_ratio"] >= 4.0
    assert metrics["energy_distortion_pct"] < 20.0
    assert metrics["compressed_bytes"] < metrics["original_bytes"]


def test_qa_gate6_pyo3_zerocopy():
    """Verify Gate 6: PyO3 Zero-Copy Native Integration & Memory Safety."""
    metrics = verify_use_case_6_pyo3_zerocopy(verbose=False)
    assert metrics["status"] == "PASSED"
    assert metrics["is_zerocopy"] is True
    assert metrics["lean4_memory_invariant_verified"] is True


def test_qa_gate7_taylor_green():
    """Verify Gate 7: Taylor-Green Vortex 2D Decay against PDEBench analytical reference."""
    metrics = verify_use_case_7_taylor_green(verbose=False)
    assert metrics["status"] == "PASSED"
    assert metrics["solenoidal_residual"] < 1e-12
    assert metrics["energy_monotone"] is True
    assert metrics["l2_error"] < 0.1


def test_qa_gate8_lid_driven_cavity():
    """Verify Gate 8: 2D Lid-Driven Cavity Flow against Ghia et al. reference table."""
    metrics = verify_use_case_8_lid_driven_cavity(verbose=False)
    assert metrics["status"] == "PASSED"
    assert metrics["centerline_u_linf_error"] < 1.0
    assert metrics["centerline_points_checked"] == 17


def test_qa_gate9_rayleigh_benard():
    """Verify Gate 9: 2D Rayleigh-Bénard Convection against Dedalus reference."""
    metrics = verify_use_case_9_rayleigh_benard(verbose=False)
    assert metrics["status"] == "PASSED"
    assert metrics["nusselt_mean"] >= 1.0
    assert metrics["surrogate_scope_caveat_verified"] is True


def test_qa_gate10_kelvin_helmholtz():
    """Verify Gate 10: 2D Kelvin-Helmholtz Instability against Athena++ reference."""
    metrics = verify_use_case_10_kelvin_helmholtz(verbose=False)
    assert metrics["status"] == "PASSED"
    assert metrics["mixing_width_growth_ratio"] > 1.0
    assert metrics["enstrophy_peak_value"] > 0.0


def test_qa_gate11_jhtdb_isotropic():
    """Verify Gate 11: 3D Forced Isotropic Turbulence Proxy against JHTDB DNS reference."""
    metrics = verify_use_case_11_jhtdb_isotropic(verbose=False)
    assert metrics["status"] == "PASSED"
    assert metrics["spectral_slope_measured"] < 0.0
    assert metrics["dissipation_rate_measured"] > 0.0
    assert metrics["surrogate_scope_caveat_verified"] is True


def test_qa_gate12_burgers():
    """Verify Gate 12: 1D Viscous Burgers Shock Formation & Decay against PyClaw reference."""
    metrics = verify_use_case_12_burgers(verbose=False)
    assert metrics["status"] == "PASSED"
    assert metrics["l2_error"] < 0.08
    assert metrics["energy_monotone"] is True


def test_qa_gate13_poiseuille():
    """Verify Gate 13: 2D Poiseuille Channel Flow against OpenFOAM reference."""
    metrics = verify_use_case_13_poiseuille(verbose=False)
    assert metrics["status"] == "PASSED"
    assert metrics["centerline_u_relative_error"] < 0.08
    assert metrics["wall_shear_stress"] > 0.0


def test_qa_gate14_double_shear_layer():
    """Verify Gate 14: 2D Double Shear Layer Roll-Up against AMReX reference."""
    metrics = verify_use_case_14_double_shear_layer(verbose=False)
    assert metrics["status"] == "PASSED"
    assert metrics["enstrophy_peak_value"] > 5.0
    assert metrics["solenoidal_residual"] < 1e-12


def test_qa_gate15_vortex_merger():
    """Verify Gate 15: 2D Co-Rotating Vortex Merging against Spectral-DNS reference."""
    metrics = verify_use_case_15_vortex_merger(verbose=False)
    assert metrics["status"] == "PASSED"
    assert metrics["vortex_separation_ratio"] <= 1.05


def test_qa_gate16_hartmann_mhd():
    """Verify Gate 16: 3D Hartmann Channel Duct (MHD) against Athena++ reference."""
    metrics = verify_use_case_16_hartmann_mhd(verbose=False)
    assert metrics["status"] == "PASSED"
    assert metrics["hartmann_profile_linf_error"] < 0.15
    assert metrics["lorentz_damping_ratio"] > 1.2
    assert metrics["surrogate_scope_caveat_verified"] is True


def test_qa_epistemic_nomenclature():
    """Verify Epistemic Gate: Zero banned pseudoscientific buzzwords in core code."""
    audit = audit_epistemic_nomenclature(REPO, verbose=False)
    assert audit["passed"] is True
    assert audit["violations_count"] == 0


def test_qa_release_full_orchestration(tmp_path):
    """Run full Release QA audit suite across all 16 gates and verify certificate generation."""
    cert_path = tmp_path / "cert_test_release.json"
    cert, passed = run_release_qa(
        release_tag="v8.3.0-extended-usecases",
        output_path=cert_path,
        verbose=False,
    )
    assert passed is True
    assert cert["overall_status"] == "CERTIFIED"
    assert cert["certificate_id"] == "CERT-QA-RELEASE-V8.3.0-EXTENDED-USECASES"
    assert cert["_measured"] is True
    assert cert["invariants_verified"]["H2_negative_controls"] is True
    assert cert["invariants_verified"]["UC1_high_re_stiffness_gain"] is True
    assert cert["invariants_verified"]["UC2_embedded_static_ram_budget"] is True
    assert cert["invariants_verified"]["UC3_dualscale_uv_regularity"] is True
    assert cert["invariants_verified"]["UC4_ida_dae_solenoidal_manifold"] is True
    assert cert["invariants_verified"]["UC5_polarquant_8x_compression"] is True
    assert cert["invariants_verified"]["UC6_pyo3_zerocopy_memory_safety"] is True
    assert cert["invariants_verified"]["UC7_taylor_green_spectral_decay"] is True
    assert cert["invariants_verified"]["UC8_lid_driven_cavity_ghia"] is True
    assert cert["invariants_verified"]["UC9_rayleigh_benard_convection"] is True
    assert cert["invariants_verified"]["UC10_kelvin_helmholtz_instability"] is True
    assert cert["invariants_verified"]["UC11_jhtdb_isotropic_turbulence"] is True
    assert cert["invariants_verified"]["UC12_burgers_shock_decay"] is True
    assert cert["invariants_verified"]["UC13_poiseuille_channel_flow"] is True
    assert cert["invariants_verified"]["UC14_double_shear_layer_rollup"] is True
    assert cert["invariants_verified"]["UC15_vortex_merger_dynamics"] is True
    assert cert["invariants_verified"]["UC16_hartmann_mhd_channel"] is True
    assert cert["invariants_verified"]["epistemic_nomenclature"] is True
    assert cert_path.exists()

