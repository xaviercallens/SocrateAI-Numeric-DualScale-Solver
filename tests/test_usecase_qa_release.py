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


def test_qa_epistemic_nomenclature():
    """Verify Gate 7: Zero banned pseudoscientific buzzwords in core code."""
    audit = audit_epistemic_nomenclature(REPO, verbose=False)
    assert audit["passed"] is True
    assert audit["violations_count"] == 0


def test_qa_release_full_orchestration(tmp_path):
    """Run full Release QA audit suite and verify certificate generation."""
    cert_path = tmp_path / "cert_test_release.json"
    cert, passed = run_release_qa(
        release_tag="v8.1.0-rc1",
        output_path=cert_path,
        verbose=False,
    )
    assert passed is True
    assert cert["overall_status"] == "CERTIFIED"
    assert cert["certificate_id"] == "CERT-QA-RELEASE-V8.1.0-RC1"
    assert cert["_measured"] is True
    assert cert["invariants_verified"]["H2_negative_controls"] is True
    assert cert["invariants_verified"]["UC1_high_re_stiffness_gain"] is True
    assert cert["invariants_verified"]["UC2_embedded_static_ram_budget"] is True
    assert cert["invariants_verified"]["UC3_dualscale_uv_regularity"] is True
    assert cert["invariants_verified"]["UC4_ida_dae_solenoidal_manifold"] is True
    assert cert["invariants_verified"]["UC5_polarquant_8x_compression"] is True
    assert cert["invariants_verified"]["UC6_pyo3_zerocopy_memory_safety"] is True
    assert cert["invariants_verified"]["epistemic_nomenclature"] is True
    assert cert_path.exists()
