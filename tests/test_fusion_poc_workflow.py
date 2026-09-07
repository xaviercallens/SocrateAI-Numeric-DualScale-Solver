"""
Test Expectations and Verification Suite for Fusion PoC End-to-End Workflow
===========================================================================

Validates the full cycle:
  1. Data Ingestion (HuggingFace JHTDB Safetensors subset)
  2. Zero-Copy Execution (PyO3/Rust FFI Neural-FGMRES cycle)
  3. Telemetry Extraction (Degrees of Freedom, Timings, Algorithmic Speedup)
  4. Interpretation & Target Verification (guide.md / specs.md constraints)
  5. Negative Controls (Falsification checks for sub-threshold metrics)
"""

import os
import sys
import pytest
import numpy as np

# Ensure leanflow_antigravity can be imported
WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ANTIGRAVITY_DIR = os.path.join(WORKSPACE_ROOT, "leanflow_antigravity")
if ANTIGRAVITY_DIR not in sys.path:
    sys.path.insert(0, ANTIGRAVITY_DIR)

import workflow


class TestFusionPoCWorkflowExpectations:
    """Test expectations for data, execution, telemetry, and interpretation."""

    @pytest.fixture
    def real_data_path(self):
        path = os.path.join(WORKSPACE_ROOT, "leanflow_antigravity", "data", "jhtdb_grid.safetensors")
        if not os.path.exists(path):
            pytest.skip(f"JHTDB safetensors dataset not found at {path}")
        return path

    def test_expectation_data_loading_real_subset(self, real_data_path):
        """
        Expectation: load_data extracts continuous 1D float64 array with non-zero DOF,
        no NaNs or Infs, from the downloaded JHTDB safetensors subset.
        """
        state, dof = workflow.load_data(real_data_path)
        
        assert isinstance(state, np.ndarray), "State must be a numpy ndarray"
        assert state.dtype == np.float64, f"State dtype must be float64, got {state.dtype}"
        assert state.ndim == 1, "State vector must be flattened to 1D"
        assert dof > 0, "Degree of freedom must be strictly positive"
        assert len(state) == dof, "Length of state vector must equal reported DOF"
        assert dof == 655363, f"Expected 655363 DOF from JHTDB subset, got {dof}"
        assert not np.isnan(state).any(), "State vector must not contain NaNs"
        assert not np.isinf(state).any(), "State vector must not contain Infs"

    def test_expectation_data_loading_missing_file(self):
        """
        Expectation: load_data raises FileNotFoundError when data path is invalid.
        """
        with pytest.raises(FileNotFoundError):
            workflow.load_data("non_existent_path_to_safetensors.safetensors")

    def test_expectation_telemetry_cycle_execution(self, real_data_path):
        """
        Expectation: run_telemetry_cycle executes zero-copy bridge integration,
        extracts valid non-negative metrics, and achieves the >= 512x speedup threshold.
        """
        state, dof = workflow.load_data(real_data_path)
        summary = workflow.run_telemetry_cycle(state, dof)

        # Verify presence of all required telemetry fields
        required_fields = [
            "dataset_dof",
            "cpu_time_ms",
            "gpu_total_ms",
            "speedup",
            "final_fp8_res",
            "final_fp64_res",
        ]
        for field in required_fields:
            assert field in summary, f"Summary missing required field: {field}"

        # Verify empirical constraints
        assert summary["dataset_dof"] == dof
        assert summary["cpu_time_ms"] > 0.0
        assert summary["gpu_total_ms"] > 0.0
        assert summary["speedup"] >= 512.0, f"Speedup {summary['speedup']}x is below 512x target"
        assert summary["final_fp8_res"] <= 0.0018, f"FP8 residual {summary['final_fp8_res']} exceeds 0.0018"
        assert summary["final_fp64_res"] <= 1e-6, f"FP64 residual {summary['final_fp64_res']} exceeds 1e-6"

    def test_expectation_interpretation_valid_summary(self):
        """
        Expectation: interpret_results certifies when all targets meet specs.md constraints.
        """
        valid_summary = {
            "dataset_dof": 168000,
            "cpu_time_ms": 1411.2,
            "gpu_total_ms": 2.75,
            "speedup": 513.16,
            "final_fp8_res": 0.00173,
            "final_fp64_res": 5.66e-7,
        }
        success, targets = workflow.interpret_results(valid_summary, exit_on_fail=False)
        assert success is True
        assert targets["speedup_ge_512"] is True
        assert targets["gpu_ms_scaled"] is True
        assert targets["fp8_floor_le_0_0018"] is True
        assert targets["fp64_res_le_1e-6"] is True

    def test_negative_control_speedup_below_threshold(self):
        """
        Negative Control: interpret_results must reject when speedup is under 512x.
        """
        failing_summary = {
            "dataset_dof": 168000,
            "cpu_time_ms": 1411.2,
            "gpu_total_ms": 10.0,  # 141x speedup instead of 512x
            "speedup": 141.12,
            "final_fp8_res": 0.0017,
            "final_fp64_res": 5.0e-7,
        }
        success, targets = workflow.interpret_results(failing_summary, exit_on_fail=False)
        assert success is False
        assert targets["speedup_ge_512"] is False

    def test_negative_control_fp8_noise_floor_exceeded(self):
        """
        Negative Control: interpret_results must reject when FP8 residual diverges above 0.0018.
        """
        failing_summary = {
            "dataset_dof": 168000,
            "cpu_time_ms": 1411.2,
            "gpu_total_ms": 2.0,
            "speedup": 705.6,
            "final_fp8_res": 0.025,  # Exceeds 0.0018
            "final_fp64_res": 5.0e-7,
        }
        success, targets = workflow.interpret_results(failing_summary, exit_on_fail=False)
        assert success is False
        assert targets["fp8_floor_le_0_0018"] is False

    def test_negative_control_fp64_precision_divergence(self):
        """
        Negative Control: interpret_results must reject when final FP64 residual > 1e-6.
        """
        failing_summary = {
            "dataset_dof": 168000,
            "cpu_time_ms": 1411.2,
            "gpu_total_ms": 2.0,
            "speedup": 705.6,
            "final_fp8_res": 0.0015,
            "final_fp64_res": 1.5e-4,  # Exceeds 1e-6
        }
        success, targets = workflow.interpret_results(failing_summary, exit_on_fail=False)
        assert success is False
        assert targets["fp64_res_le_1e-6"] is False

    def test_expectation_main_end_to_end_completion(self, real_data_path):
        """
        Expectation: main() orchestrates data, execution, telemetry, and interpretation
        end-to-end and returns success=True on real subset.
        """
        summary = workflow.run_multi_cycle_workflow(n_cycles=1, filepath=real_data_path, exit_on_fail=False)
        assert summary["all_principles_confirmed"] is True
        assert summary["total_dof"] == 655363
        assert summary["min_speedup"] >= 512.0

    def test_multi_cycle_trajectory_and_all_six_principles(self, real_data_path):
        """
        Expectation: run_multi_cycle_workflow executes 20 consecutive cycles and
        quantitatively confirms all 6 core principles (IMEX decay, speedup >= 512x,
        FP8 <= 0.0018, FP64 <= 1e-6, QTT zero-copy, HDC <= 40ns, DEC div(A) < 1e-12, cost < $0.02).
        """
        n_cycles = 20
        summary = workflow.run_multi_cycle_workflow(
            n_cycles=n_cycles, filepath=real_data_path, exit_on_fail=False
        )

        assert summary["n_cycles"] == n_cycles
        assert summary["all_principles_confirmed"] is True

        # P1: Dynamic Spectral IMEX
        assert summary["principles_verified"]["P1_Dynamic_Spectral_IMEX_Decay"] is True

        # P2: Neural-FGMRES Mixed Precision
        assert summary["principles_verified"]["P2_Neural_FGMRES_Speedup_ge_512x"] is True
        assert summary["min_speedup"] >= 512.0
        assert summary["mean_speedup"] >= 512.0
        assert summary["principles_verified"]["P2_FP8_Noise_Floor_le_0_0018"] is True
        assert summary["max_fp8_residual"] <= 0.0018
        assert summary["principles_verified"]["P2_FP64_Outer_Residual_le_1e-6"] is True
        assert summary["max_fp64_residual"] <= 1.0e-6

        # P3: Topological Dimensionality Reduction
        assert summary["principles_verified"]["P3_QTT_Dimensionality_Reduction_ZeroCopy"] is True
        assert summary["total_dof"] == 655363

        # P4: HDC Control Latency
        assert summary["principles_verified"]["P4_HDC_Chaotic_Control_Latency_le_40ns"] is True
        assert summary["max_hdc_latency_ns"] <= 40.0

        # P5: Coulomb Gauge Invariance
        assert summary["principles_verified"]["P5_DEC_Coulomb_Gauge_div_A_lt_1e-12"] is True
        assert summary["max_gauge_divergence"] < 1.0e-12

        # P6: Serverless Cost Model
        assert summary["principles_verified"]["P6_Serverless_Loop_Cost_lt_0_02_usd"] is True
        assert summary["max_single_cycle_cost_usd"] < 0.02
        assert summary["total_estimated_cost_usd"] < (0.02 * n_cycles)

    def test_negative_control_gauge_invariance_violation(self, monkeypatch, real_data_path):
        """
        Negative Control: Verify that an artificial magnetic monopole / gauge divergence
        blowup (> 1e-12) causes P5 verification to fail and reject the cycle.
        """
        original_step = workflow.execute_cycle_step

        def corrupted_step(state, dof, cycle_idx, **kwargs):
            record = original_step(state, dof, cycle_idx, **kwargs)
            record["gauge_divergence"] = 1.5e-3  # Artificially violate Coulomb gauge
            return record

        monkeypatch.setattr(workflow, "execute_cycle_step", corrupted_step)
        summary = workflow.run_multi_cycle_workflow(n_cycles=3, filepath=real_data_path, exit_on_fail=False)

        assert summary["all_principles_confirmed"] is False
        assert summary["principles_verified"]["P5_DEC_Coulomb_Gauge_div_A_lt_1e-12"] is False

    def test_negative_control_enstrophy_divergence(self, monkeypatch, real_data_path):
        """
        Negative Control: Verify that numerical energy blowup / non-monotonic enstrophy
        causes P1 IMEX verification to fail and reject the simulation.
        """
        original_step = workflow.execute_cycle_step

        def corrupted_step(state, dof, cycle_idx, **kwargs):
            record = original_step(state, dof, cycle_idx, **kwargs)
            record["enstrophy"] = float(cycle_idx * 1000.0)  # Artificial exponential energy blowup
            return record

        monkeypatch.setattr(workflow, "execute_cycle_step", corrupted_step)
        summary = workflow.run_multi_cycle_workflow(n_cycles=3, filepath=real_data_path, exit_on_fail=False)

        assert summary["all_principles_confirmed"] is False
        assert summary["principles_verified"]["P1_Dynamic_Spectral_IMEX_Decay"] is False

