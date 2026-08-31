"""
Unit tests for Phase 4 Multi-Agent Workflow Orchestrator.
"""

from pathlib import Path
import pytest
from dualscale_solver.agents.phase4_workflow_orchestrator import Phase4WorkflowOrchestrator


def test_phase4_workflow_pipeline_execution():
    """Verify full 5-agent Phase 4 pipeline execution and certificate generation."""
    repo_root = Path(__file__).resolve().parent.parent
    orchestrator = Phase4WorkflowOrchestrator(repo_root=repo_root)

    report = orchestrator.run_full_phase4_pipeline()

    assert "embedded_kernel_synthesizer" in report
    assert "static_memory_auditor" in report
    assert "realtime_latency_auditor" in report
    assert "industrial_bioreactor_validator" in report
    assert "phase4_hardness_auditor" in report

    cert = report["phase4_hardness_auditor"]["certificate"]
    assert cert["status"] == "CERTIFIED"
    assert cert["invariants_verified"]["H16_phase4_embedded_zero_alloc_gate"] is True
    assert report["static_memory_auditor"]["h16_memory_budget_satisfied"] is True
    assert report["realtime_latency_auditor"]["h16_deterministic_sub_ms_satisfied"] is True
    assert report["industrial_bioreactor_validator"]["yield_3x_goal_achieved"] is True
