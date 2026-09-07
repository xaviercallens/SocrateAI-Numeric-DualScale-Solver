"""
Unit & Integration Tests for Enterprise Edition Autonomous Workflow (Phases E1–E4)
==================================================================================

Validates:
1. All 7 Enterprise execution benchmarks (Arena, DAE, Telemetry, PolarQuant, Stencil, FGMRES, TPU/RVV).
2. All 8 Epistemic negative controls (NC-ENT-01 to NC-ENT-08).
3. 8-Agent Enterprise Workflow Orchestrator and H26 JSON contract adherence.
4. Sealed Certificate Generation (`certs/CERT-ENTERPRISE-V3.3.0.json`).
5. CLI `enterprise-workflow` subcommand execution.
"""

import json
import os
import pytest
from pathlib import Path

from dualscale_solver.numeric.enterprise_models import (
    run_memory_arena_benchmark,
    negative_control_nc_ent_01,
    run_dae_incompressible_benchmark,
    negative_control_nc_ent_02,
    run_lockfree_telemetry_benchmark,
    negative_control_nc_ent_03,
    run_polarquant_compression_benchmark,
    negative_control_nc_ent_04,
    run_stencil_cache_tiling_benchmark,
    negative_control_nc_ent_05,
    run_chebyshev_fgmres_benchmark,
    negative_control_nc_ent_06,
    run_tpu_rvv_dispatch_benchmark,
    negative_control_nc_ent_07,
    negative_control_nc_ent_08,
)
from dualscale_solver.agents.enterprise_workflow_orchestrator import (
    EnterpriseWorkflowOrchestrator,
    run_enterprise_workflow,
)
from dualscale_solver.cli import cmd_enterprise_workflow
import argparse


def test_enterprise_models_individual_benchmarks():
    """Validates that all numerical execution benchmarks pass with _measured: true."""
    # 1. Memory Arena
    arena = run_memory_arena_benchmark(n_steps=100)
    assert arena["status"] == "PASSED"
    assert arena["alignment_bytes"] == 64
    assert arena["fragmentation_pct"] == 0.0
    assert arena["_measured"] is True

    # 2. Monolithic DAE Solenoidal Solver
    dae = run_dae_incompressible_benchmark(n_dof=32, n_steps=20)
    assert dae["status"] == "PASSED"
    assert dae["max_divergence_inf"] < 1e-10
    assert dae["splitting_error"] == 0.0
    assert dae["_measured"] is True

    # 3. Wait-Free Telemetry Ring
    telemetry = run_lockfree_telemetry_benchmark(n_events=1000)
    assert telemetry["status"] == "PASSED"
    assert telemetry["is_monotonic"] is True
    assert telemetry["throughput_eps"] > 10000.0
    assert telemetry["_measured"] is True

    # 4. PolarQuant 4-Bit Compression
    pq = run_polarquant_compression_benchmark(n_samples=2000)
    assert pq["status"] == "PASSED"
    assert pq["compression_ratio"] >= 4.0
    assert pq["mean_relative_l2_error"] < 0.15
    assert pq["_measured"] is True

    # 5. MLGO 3D Stencil Tiling
    stencil = run_stencil_cache_tiling_benchmark(nx=32, ny=32, nz=32)
    assert stencil["status"] == "PASSED"
    assert stencil["fits_l1"] is True
    assert stencil["cache_miss_reduction_pct"] > 65.0
    assert stencil["_measured"] is True

    # 6. Mixed-Precision Chebyshev FGMRES
    fgmres = run_chebyshev_fgmres_benchmark(n_grid=16)
    assert fgmres["status"] == "PASSED"
    assert fgmres["iterations"] <= 15
    assert fgmres["residual_reduction"] >= 1e8
    assert fgmres["converged"] is True
    assert fgmres["_measured"] is True

    # 7. Hardware Dispatch (SpacemiT RVV 1.0 & Cloud TPU StableHLO)
    dispatch = run_tpu_rvv_dispatch_benchmark()
    assert dispatch["status"] == "PASSED"
    assert dispatch["rvv_step_latency_ms"] <= 1.0
    assert dispatch["rvv_ram_usage_bytes"] <= 64 * 1024
    assert dispatch["_measured"] is True


def test_enterprise_negative_controls():
    """Validates that all 8 epistemic negative controls catch and reject invalid states."""
    assert negative_control_nc_ent_01() is True, "NC-ENT-01 failed to reject arena overflow/misalignment"
    assert negative_control_nc_ent_02() is True, "NC-ENT-02 failed to reject divergence violation"
    assert negative_control_nc_ent_03() is True, "NC-ENT-03 failed to reject non-monotonic telemetry"
    assert negative_control_nc_ent_04() is True, "NC-ENT-04 failed to reject corrupted PolarQuant state"
    assert negative_control_nc_ent_05() is True, "NC-ENT-05 failed to reject oversized stencil tile"
    assert negative_control_nc_ent_06() is True, "NC-ENT-06 failed to reject divergent FGMRES iterations"
    assert negative_control_nc_ent_07() is True, "NC-ENT-07 failed to reject overbudget hardware latency/RAM"
    assert negative_control_nc_ent_08() is True, "NC-ENT-08 failed to reject unconstrained prose/forbidden sentinels"


def test_enterprise_workflow_orchestrator_execution(tmp_path):
    """Validates full execution of EnterpriseWorkflowOrchestrator and certificate generation."""
    cert_dir = tmp_path / "test_certs"
    orchestrator = EnterpriseWorkflowOrchestrator(cert_output_dir=str(cert_dir.name))
    cert = orchestrator.run_pipeline(workspace_root=str(tmp_path))

    assert cert["overall_status"] == "CERTIFIED"
    assert cert["epistemic_tier"] == "TIER_A_FORMAL_AND_EXACT_RATIONAL"
    assert len(cert["invariants_verified"]) == 8
    assert all(cert["invariants_verified"].values())
    assert len(cert["negative_controls"]) == 8
    assert all(cert["negative_controls"].values())
    assert len(cert["sha256_seal"]) == 64
    assert cert["_measured"] is True

    # Verify certificate file on disk
    cert_file = Path(cert["certificate_file"])
    assert cert_file.exists()
    with open(cert_file, "r", encoding="utf-8") as f:
        disk_data = json.load(f)
    assert disk_data["certificate_id"] == cert["certificate_id"]
    assert disk_data["sha256_seal"] == cert["sha256_seal"]


def test_enterprise_agent_deliverables_contract():
    """Asserts that all 8 agents return valid structured JSON conforming to H26."""
    cert = run_enterprise_workflow()
    deliverables = cert["agent_deliverables"]
    assert len(deliverables) == 8

    expected_agents = [
        "enterprise_dae_engineer",
        "memory_arena_auditor",
        "telemetry_ring_auditor",
        "polarquant_specialist",
        "stencil_cache_tiler",
        "chebyshev_fgmres_auditor",
        "tpu_accelerator_agent",
        "enterprise_certifier",
    ]

    for agent in expected_agents:
        assert agent in deliverables, f"Missing agent deliverable: {agent}"
        agent_data = deliverables[agent]
        assert agent_data.get("_measured") is True, f"Agent {agent} missing _measured: true"
        assert agent_data.get("status") in {"PASSED", "CERTIFIED"}, f"Agent {agent} failed status: {agent_data.get('status')}"


def test_cli_enterprise_workflow_command(tmp_path):
    """Validates that CLI command 'enterprise-workflow' runs and returns exit code 0."""
    out_file = tmp_path / "cli_cert.json"
    args = argparse.Namespace(output=str(out_file))
    exit_code = cmd_enterprise_workflow(args)
    assert exit_code == 0
    assert out_file.exists()
    with open(out_file, "r", encoding="utf-8") as f:
        cert_json = json.load(f)
    assert cert_json["overall_status"] == "CERTIFIED"
