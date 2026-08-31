"""
Unit tests for Phase 3 Multi-Agent Workflow Orchestrator.
"""

from pathlib import Path
import pytest
from dualscale_solver.agents.phase3_workflow_orchestrator import Phase3WorkflowOrchestrator


def test_phase3_workflow_pipeline_execution():
    """Verify full 5-agent Phase 3 pipeline execution and certificate generation."""
    repo_root = Path(__file__).resolve().parent.parent
    orchestrator = Phase3WorkflowOrchestrator(repo_root=repo_root)

    report = orchestrator.run_full_phase3_pipeline()

    assert "amg_preconditioner_synthesizer" in report
    assert "openfoam_comparison_auditor" in report
    assert "symbrain_router" in report
    assert "tensorcore_precision_verifier" in report
    assert "phase3_hardness_auditor" in report

    cert = report["phase3_hardness_auditor"]["certificate"]
    assert cert["status"] == "CERTIFIED"
    assert cert["invariants_verified"]["H15_phase3_tensorcore_openfoam_gate"] is True
    assert report["openfoam_comparison_auditor"]["h15_openfoam_supremacy_verified"] is True
