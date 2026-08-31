"""
Unit tests for Phase 2 Multi-Agent Workflow Orchestrator.
"""

from pathlib import Path
import pytest
from dualscale_solver.agents.phase2_workflow_orchestrator import Phase2WorkflowOrchestrator


def test_phase2_workflow_pipeline_execution():
    """Verify full 5-agent Phase 2 pipeline execution and certificate generation."""
    repo_root = Path(__file__).resolve().parent.parent
    orchestrator = Phase2WorkflowOrchestrator(repo_root=repo_root)

    report = orchestrator.run_full_phase2_pipeline()

    assert "preconditioner_synthesizer" in report
    assert "spectral_gate_verifier" in report
    assert "krylov_convergence_auditor" in report
    assert "dualscale_cross_validator" in report
    assert "epistemic_hardness_auditor" in report

    cert = report["epistemic_hardness_auditor"]["certificate"]
    assert cert["status"] == "CERTIFIED"
    assert cert["invariants_verified"]["H14_phase2_preconditioner_gate"] is True
    assert report["krylov_convergence_auditor"]["goal_5x_iteration_reduction_achieved"] is True
