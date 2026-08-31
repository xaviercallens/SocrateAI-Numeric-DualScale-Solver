"""
Unit & Hardness Tests for Phase 7 Industrialization & Workflow 7.
================================================================

Covers:
- Coupled Aeroelastic FSI Flutter Suppression (H35)
- Coupled Bioreactor Reaction-Diffusion Kinetics (H36)
- Generative Inverse Design Frustration Minimization (H37)
- Hierarchical Edge-Cloud Swarm Synchronization (H38)
- Holographic Scale Regularization & Attractor Boundedness (H39)
- Automated Regulatory Compliance Package Packaging (H40)
- Epistemic Negative Controls (NC-P7-01 .. NC-P7-06)
- Phase 7 Multi-Agent Pipeline Execution & Hardness Auditor
- Phase 7 Production Roadmap Upgrades (H41-H44) + NC-P7-07..NC-P7-10
"""

import os
import tempfile

import pytest

from dualscale_solver.numeric.phase7_industrial_models import (
    simulate_coupled_fsi_buffet_flutter,
    simulate_coupled_bioreactor_kinetics,
    optimize_generative_geometry_frustration,
    simulate_edge_cloud_swarm_synchronization,
    compute_holographic_rg_scale_regularization,
    generate_regulatory_compliance_package,
    negative_control_nc_p7_01,
    negative_control_nc_p7_02,
    negative_control_nc_p7_03,
    negative_control_nc_p7_04,
    negative_control_nc_p7_05,
    negative_control_nc_p7_06,
)
from dualscale_solver.agents.phase7_workflow_orchestrator import (
    run_phase7_pipeline,
    _probe_gemini,
    _probe_mistral,
    _probe_ollama,
)


class TestPhase7PhysicalModels:
    """Tests for Phase 7 industrial multi-physics and optimization models."""

    def test_coupled_fsi_buffet_flutter_model(self):
        """H35: Aeroelastic flutter variance reduction must be >= 45%."""
        res = simulate_coupled_fsi_buffet_flutter(n_steps=500)
        assert res["_measured"] is True
        assert res["variance_reduction_fraction"] >= 0.45
        assert res["fsi_flutter_suppressed"] is True
        assert res["leanflow_flutter_variance"] < res["baseline_flutter_variance"]

    def test_coupled_bioreactor_kinetics_model(self):
        """H36: Bioreactor kLa >= 115/s and yield multiplier >= 3.0x."""
        res = simulate_coupled_bioreactor_kinetics(n_steps=500)
        assert res["_measured"] is True
        assert res["kla_achieved"] >= 115.0
        assert res["yield_multiplier"] >= 3.0
        assert res["meets_kinetics_criteria"] is True

    def test_generative_geometry_frustration_optimization(self):
        """H37: Generative inverse design achieves >= 20% D(M) reduction and >= 8% drag reduction."""
        res = optimize_generative_geometry_frustration(max_iterations=10)
        assert res["_measured"] is True
        assert res["dm_reduction_pct"] >= 20.0
        assert res["drag_reduction_pct"] >= 8.0
        assert res["meets_generative_criteria"] is True

    def test_edge_cloud_swarm_synchronization(self):
        """H38: Edge latency <= 1.0 ms and swarm scaling >= 85%."""
        res = simulate_edge_cloud_swarm_synchronization(swarm_nodes=16, macro_grid_size=256)
        assert res["_measured"] is True
        assert res["edge_node_latency_ms"] <= 1.0
        assert res["swarm_scaling_efficiency"] >= 0.85
        assert res["meets_edge_latency_bound"] is True
        assert res["meets_swarm_scaling"] is True

    def test_holographic_scale_regularization(self):
        """H39: R_eff >= 2*sqrt(alpha') and enstrophy is strictly bounded by Z*."""
        res = compute_holographic_rg_scale_regularization(alpha_prime=1e-4, nu=1e-3)
        assert res["_measured"] is True
        assert res["bound_satisfied"] is True
        assert res["min_r_eff_measured"] >= res["theoretical_lower_bound"] - 1e-12
        assert res["enstrophy_strictly_bounded"] is True
        assert res["simulated_peak_enstrophy"] <= res["enstrophy_attractor_z_star"]

    def test_regulatory_compliance_package(self):
        """H40: FDA 21 CFR Part 11 and DO-178C Level A audit package generated with valid SHA-256."""
        res = generate_regulatory_compliance_package()
        assert res["_measured"] is True
        assert res["compliance_fda_21_cfr_part_11"] is True
        assert res["compliance_do_178c_level_a"] is True
        assert res["proof_matrix_verified"] is True
        assert len(res["sha256_audit_hash"]) == 64


class TestPhase7NegativeControls:
    """Epistemic negative control verifications (NC-P7-01 .. NC-P7-06)."""

    def test_nc_p7_01_falsified_flutter(self):
        assert negative_control_nc_p7_01() is True

    def test_nc_p7_02_subthreshold_bioreactor(self):
        assert negative_control_nc_p7_02() is True

    def test_nc_p7_03_stagnant_frustration(self):
        assert negative_control_nc_p7_03() is True

    def test_nc_p7_04_excessive_edge_latency(self):
        assert negative_control_nc_p7_04() is True

    def test_nc_p7_05_holographic_bound_violation(self):
        assert negative_control_nc_p7_05() is True

    def test_nc_p7_06_incomplete_proof_matrix(self):
        assert negative_control_nc_p7_06() is True


class TestPhase7PipelineOrchestrator:
    """Tests for Phase 7 multi-agent workflow pipeline and hardness auditor."""

    def test_run_phase7_pipeline(self):
        res = run_phase7_pipeline()
        assert res["_measured"] is True
        assert "measurements" in res
        assert "phase7_hardness_auditor" in res

        auditor = res["phase7_hardness_auditor"]
        assert auditor["_measured"] is True
        assert auditor["certificate_id"].startswith("CERT-P7-IND-")
        assert len(auditor["sha256_hash"]) == 64
        assert auditor["overall_status"] in ("CERTIFIED", "SCAFFOLDING_ONLY")

        inv = auditor["invariants_verified"]
        assert inv["H35_fsi_aeroelastic_flutter_gate"] is True
        assert inv["H36_biopharma_reaction_kinetics_gate"] is True
        assert inv["H37_generative_inverse_design_gate"] is True
        assert inv["H38_edge_cloud_swarm_sync_gate"] is True
        assert inv["H39_holographic_scale_attractor_gate"] is True
        # Production roadmap invariants
        assert inv["H41_hil_arm_cycle_budget_gate"] is True
        assert inv["H42_cad_step_export_gate"] is True
        assert inv["H43_telemetry_stream_integrity_gate"] is True
        assert inv["H44_3d_fsi_coupling_gate"] is True

    def test_probe_helpers(self):
        assert _probe_gemini("") is False
        assert _probe_gemini("YOUR_API_KEY") is False
        assert _probe_gemini("valid_gemini_key_123456789") is True
        assert _probe_mistral("") is False
        assert isinstance(_probe_ollama(), bool)


class TestPhase7ProductionUpgrades:
    """Tests for Phase 7 Production Roadmap Upgrades (H41-H44) and NC-P7-07..NC-P7-10."""

    # --- H41: ARM Cortex-M4 HIL Cycle-Budget Testbench ---

    def test_hil_arm_cycle_budget_test(self):
        """H41: ARM Cortex-M4 cycle-budget at 168 MHz must stay within 1.0 ms."""
        from dualscale_solver.numeric.hil_arm_testbench import simulate_hil_arm_cycle_budget
        res = simulate_hil_arm_cycle_budget(n=4)
        assert res["_measured"] is True
        assert res["latency_ms"] <= 1.0
        assert res["budget_satisfied"] is True
        assert res["cycles_per_step"] > 0
        assert res["cpu_freq_hz"] == 168_000_000

    def test_nc_p7_07_over_budget_cycles_rejected(self):
        """NC-P7-07: Over-budget cycle count (latency > 1.0 ms) is rejected."""
        from dualscale_solver.numeric.hil_arm_testbench import negative_control_nc_p7_07
        assert negative_control_nc_p7_07() is True

    # --- H42: CAD / STEP AP203 Topology Exporter ---

    def test_cad_step_export(self):
        """H42: Frustration-minimized airfoil exported to valid STEP AP203 file."""
        from dualscale_solver.numeric.cad_step_exporter import (
            build_naca_camber_points, write_step_ap203, validate_step_file,
        )
        pts = build_naca_camber_points(camber=0.04, n_points=16)
        assert len(pts) == 16
        assert all(len(p) == 3 for p in pts)

        with tempfile.NamedTemporaryFile(suffix=".step", delete=False) as f:
            tmppath = f.name
        try:
            res = write_step_ap203(tmppath, pts, run_sha256="a" * 64)
            assert res["_measured"] is True
            assert res["cad_export_valid"] is True
            assert res["entity_count"] >= 5
            assert len(res["step_file_sha256"]) == 64

            val = validate_step_file(tmppath)
            assert val["valid"] is True
            assert val["has_header"] is True
            assert val["has_footer"] is True
            assert val["has_cartesian_points"] is True
            assert val["has_bspline_curve"] is True
        finally:
            if os.path.exists(tmppath):
                os.remove(tmppath)

    def test_nc_p7_08_malformed_step_rejected(self):
        """NC-P7-08: STEP file missing END-ISO-10303-21; footer is rejected."""
        from dualscale_solver.numeric.cad_step_exporter import negative_control_nc_p7_08
        assert negative_control_nc_p7_08() is True

    # --- H43: Live Multi-Cloud Telemetry Streaming ---

    def test_live_telemetry_stream_mock(self):
        """H43: Mock telemetry stream emits events with monotonic timestamps and valid integrity hash."""
        from dualscale_solver.numeric.telemetry_streamer import (
            simulate_edge_telemetry_stream, validate_telemetry_stream,
        )
        with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False) as f:
            tmppath = f.name
        try:
            res = simulate_edge_telemetry_stream(
                swarm_nodes=4, n_events_per_node=5, sink_filepath=tmppath,
            )
            assert res["_measured"] is True
            assert res["telemetry_stream_valid"] is True
            assert res["events_emitted"] > 0
            assert res["events_dropped"] == 0
            assert len(res["stream_integrity_hash"]) == 64

            val = validate_telemetry_stream(tmppath)
            assert val["valid"] is True
            assert val["monotonic_timestamps"] is True
            assert val["schema_errors"] == 0
        finally:
            if os.path.exists(tmppath):
                os.remove(tmppath)

    def test_nc_p7_09_out_of_order_timestamps_rejected(self):
        """NC-P7-09: Out-of-order timestamps are deterministically rejected."""
        from dualscale_solver.numeric.telemetry_streamer import negative_control_nc_p7_09
        assert negative_control_nc_p7_09() is True

    # --- H44: 3D Volume Mesh FSI Co-Simulation ---

    def test_3d_fsi_mesh_coupling(self):
        """H44: 3D FSI coupling on 8^3 grid verifies interface continuity and enstrophy transfer."""
        from dualscale_solver.numeric.fsi_3d_mesh_coupler import simulate_3d_volume_mesh_fsi
        res = simulate_3d_volume_mesh_fsi(n_steps=5, grid_n=8)
        assert res["_measured"] is True
        assert res["coupling_verified"] is True
        assert res["fsi_coupling_loss_pct"] < 5.0
        assert res["pre_enforcement_velocity_mismatch"] >= 0.0

    def test_nc_p7_10_interface_discontinuity_rejected(self):
        """NC-P7-10: Interface velocity discontinuity without no-slip enforcement is rejected."""
        from dualscale_solver.numeric.fsi_3d_mesh_coupler import negative_control_nc_p7_10
        assert negative_control_nc_p7_10() is True
