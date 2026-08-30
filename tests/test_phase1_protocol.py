"""
Unit tests for the Phase 1 multi-agent workflow and experimental protocol execution.
"""

from pathlib import Path
import json
import pytest
from dualscale_solver.agents import Phase1WorkflowOrchestrator


def test_phase1_workflow_orchestrator():
    repo_root = Path(__file__).parent.parent
    orchestrator = Phase1WorkflowOrchestrator(repo_root)
    report = orchestrator.run_full_phase1_pipeline()

    # 1. Math Review Step
    assert report["math_reviewer"]["status"] == "APPROVED"
    assert report["math_reviewer"]["t_duality_symmetry"] is True

    # 2. Dev Engineer Step
    assert report["dev_engineer"]["status"] == "OPERATIONAL"

    # 3. Experimenter Step (Protocol Phases I, II, III & Performance Comparison)
    exp = report["experimenter"]["protocol_results"]
    assert exp["phase_1_divergence"]["solenoidal_tolerance_satisfied"] is True
    assert exp["phase_2_taylor_green"]["bound_satisfied"] is True
    assert exp["phase_3_jhtdb_hit"]["high_frustration_confirmed"] is True
    assert exp["solver_performance_comparison"]["goal_20pct_reduction_achieved"] is True
    assert exp["solver_performance_comparison"]["iteration_reduction_ratio"] >= 10.0

    # 4. QA Auditor Step
    qa = report["qa_scientific_auditor"]
    assert qa["status"] == "CERTIFIED"
    assert all(qa["invariants_verified"].values())

    # 5. Output Figure & JSON artifact existence
    report_file = repo_root / "data" / "output" / "phase1_workflow_execution_report.json"
    figure_file = repo_root / "figures" / "phase1_experimental_protocol.png"
    assert report_file.exists()
    assert figure_file.exists()
