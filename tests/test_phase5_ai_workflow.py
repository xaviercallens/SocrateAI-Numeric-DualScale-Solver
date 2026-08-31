"""
Tests for Phase 5 AI Preprocessing Workflow and Certification
=============================================================
Validates H20 gate, AI-driven meshing, boundary conditions, parameter tuning,
and full 6-agent autonomous pipeline under Mathesis Stream 0 Hardness rules.
"""

from dualscale_solver.agents.phase5_workflow_orchestrator import (
    agent_ai_preprocessing_validator,
    run_phase5_pipeline,
)
from dualscale_solver.ai.preprocessing import NeuroSymbolicMesher
from dualscale_solver.numeric.jhtdb_client import JHTDBClient


def test_phase5_ai_validator_agent():
    """Verify that agent_ai_preprocessing_validator executes and validates H20."""
    result = agent_ai_preprocessing_validator(grid_n=32)
    assert result["_measured"] is True
    assert result["status"] == "VALIDATED"
    assert result["h20_passes"] is True
    assert result["max_divergence_residual"] < 1e-12
    assert result["grid_n_recommended"] >= 16
    assert result["dt_recommended"] > 0.0
    assert len(result["provenance_hash"]) == 64


def test_phase5_ai_mesher_upsizing_on_turbulence():
    """Verify that the AI mesher increases resolution when enstrophy is high."""
    mesher = NeuroSymbolicMesher()
    # High enstrophy field
    u_raw = JHTDBClient.generate_local_hit_snapshot(N=32, seed=99)
    u_2d = u_raw[:2, :, :]
    
    config_turbulent = mesher.analyze_field(u_2d, nu=1e-4)  # higher Re -> smaller eta -> higher N needed
    config_laminar = mesher.analyze_field(u_2d, nu=1e-1)    # lower Re -> larger eta -> lower N needed

    assert config_turbulent.grid_n >= config_laminar.grid_n
    assert config_turbulent.k_max_eta >= 0.5


def test_phase5_ai_workflow_pipeline_full_certification():
    """Verify that run_phase5_pipeline executes all 6 agents and issues CERT-P5-WF-*."""
    pipeline = run_phase5_pipeline(grid_n=64)
    assert pipeline["_measured"] is True
    
    auditor_res = pipeline["phase5_hardness_auditor"]
    assert auditor_res["_measured"] is True
    assert auditor_res["overall_status"] == "CERTIFIED"
    assert auditor_res["certificate_id"].startswith("CERT-P5-WF-")
    assert len(auditor_res["sha256_hash"]) == 64
    assert auditor_res["invariants_verified"]["H20_phase5_ai_preprocessing_gate"] is True
