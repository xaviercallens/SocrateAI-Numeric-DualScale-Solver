"""
Unit tests for the OpenFOAM benchmark comparison results.
"""

from pathlib import Path
import json
import pytest


def test_openfoam_comparison_data_and_gain():
    repo_root = Path(__file__).parent.parent
    report_path = repo_root / "data" / "output" / "openfoam_comparison_results.json"
    figure_path = repo_root / "figures" / "openfoam_solver_comparison.png"

    assert report_path.exists(), "Benchmark output report must exist"
    assert figure_path.exists(), "Benchmark figure plot must exist"

    with open(report_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 1. Verify iteration gain is at least 10x
    gain = data["dyadic_cascade_benchmark"]["iteration_reduction_ratio"]
    assert gain >= 10.0, f"Expected at least 10x iteration gain, got {gain}"

    # 2. Verify enstrophy bound holds
    lean_res = data["dyadic_cascade_benchmark"]["dualscale_leanflow"]
    assert lean_res["max_enstrophy"] <= lean_res["enstrophy_upper_bound"]

    # 3. Verify machine-precision divergence
    div_err = data["spectral_benchmark"]["divergence_max_error"]
    assert div_err < 1e-13
