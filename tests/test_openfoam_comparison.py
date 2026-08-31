"""
Unit tests for the OpenFOAM benchmark comparison results.
"""

from pathlib import Path
import json
import pytest


def test_openfoam_comparison_data_and_gain():
    repo_root = Path(__file__).parent.parent
    report_path = repo_root / "data" / "output" / "jhtdb_openfoam_real_comparison.json"

    assert report_path.exists(), "Benchmark output report must exist"

    with open(report_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 1. Verify speedup against FDM PISO
    speedup = data["comparison"]["wall_clock_speedup_leanflow_vs_fdm"]
    assert speedup > 1.0, f"Expected speedup > 1.0, got {speedup}"

    # 2. Verify divergence advantage orders of magnitude
    oom = data["comparison"]["leanflow_divergence_order_of_magnitude_better"]
    assert oom >= 6, f"Expected at least 6 OOM better divergence, got {oom}"

    # 3. Verify machine-precision divergence for LeanFlow
    div_err = data["tgv_leanflow"]["final_max_divergence"]
    assert div_err < 1e-13, f"Expected < 1e-13 divergence, got {div_err}"
