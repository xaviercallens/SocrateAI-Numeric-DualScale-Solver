"""
Tests for Phase 6b: Industrial Proof of Concept & Autonomous Workflow.
Validates:
- Bioreactor mass transfer enhancement (H29)
- Transonic shock buffet damping (H30)
- Embedded real-time execution bounds (H31)
- Negative controls NC-IND-01, NC-IND-02, NC-IND-03
- Multi-agent orchestration pipeline
"""

import pytest
from dualscale_solver.numeric.industrial_poc import (
    simulate_transonic_buffet_damping,
    simulate_pipeline_drag_reduction,
    negative_control_nc_ind_01,
    negative_control_nc_ind_02,
    negative_control_nc_ind_03,
)
from dualscale_solver.runtimes.embedded_target import (
    simulate_bioreactor_kla_transfer,
)
from dualscale_solver.agents.phase6b_workflow_orchestrator import (
    run_phase6b_pipeline,
)


class TestIndustrialPhysicsModels:
    def test_bioreactor_mass_transfer_enhancement(self):
        """H29: kLa must exceed 100.0/s and yield multiplier >= 2.5x."""
        res = simulate_bioreactor_kla_transfer(n_steps=500, kla_target=115.89)
        assert res["_measured"] is True
        assert res["kla_achieved"] >= 100.0
        assert res["yield_multiplier"] >= 2.5
        assert res["within_64kb_ram_budget"] is True
        assert res["deterministic_latency_sub_ms"] is True

    def test_transonic_buffet_damping(self):
        """H30: Transonic shock buffet variance reduction >= 35%."""
        res = simulate_transonic_buffet_damping(n_steps=500, mach_inf=0.75, reynolds=1e6)
        assert res["_measured"] is True
        assert res["amplitude_reduction_fraction"] >= 0.35
        assert res["buffet_suppressed"] is True

    def test_pipeline_drag_reduction(self):
        """H31: High-Re pipe turbulent drag reduction >= 10%."""
        res = simulate_pipeline_drag_reduction(reynolds_d=1e5)
        assert res["_measured"] is True
        assert res["drag_reduction_fraction"] >= 0.10
        assert res["drag_reduction_exceeds_10pct"] is True


class TestIndustrialNegativeControls:
    def test_nc_ind_01_low_kla_rejected(self):
        """NC-IND-01: Falsified sub-threshold kLa is detected and rejected."""
        assert negative_control_nc_ind_01() is True

    def test_nc_ind_02_divergent_buffet_rejected(self):
        """NC-IND-02: Falsified negative buffet reduction is rejected."""
        assert negative_control_nc_ind_02() is True

    def test_nc_ind_03_memory_overflow_rejected(self):
        """NC-IND-03: Falsified memory overflow > 64 KB is rejected."""
        assert negative_control_nc_ind_03() is True


class TestPhase6bPipelineExecution:
    def test_pipeline_runs_and_measures(self):
        """Phase 6b pipeline must complete and issue certificate."""
        pipeline = run_phase6b_pipeline()
        assert pipeline["_measured"] is True
        assert "phase6b_hardness_auditor" in pipeline

        auditor = pipeline["phase6b_hardness_auditor"]
        assert auditor["_measured"] is True
        assert "certificate_id" in auditor
        assert auditor["certificate_id"].startswith("CERT-P6B-IND-")
        assert len(auditor["sha256_hash"]) == 64
        assert auditor["overall_status"] in ("CERTIFIED", "SCAFFOLDING_ONLY")
