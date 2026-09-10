#!/usr/bin/env python3
"""
Test Euler Counter-Detonation Testbench.

Validates:
1. Classical Euler calibration run divergence (blow-up) at T* < 0.3 s.
2. T-Dual shield activation with k_eff metric:
   - Triadic Frustration Index D(M) explodes (D(M) > 1000) at UV wall.
   - Velocity/Vorticity alignment cos(theta) > 0.98 (Beltrami flow formation).
   - Enstrophy bounded (no finite-time singularity).
"""

import json
import subprocess
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
REPORT_JSON = REPO_ROOT / "results" / "euler_counterdetonation_results.json"


def test_euler_counterdetonation_binary_execution():
    """Run cargo testbench binary and verify execution succeeds."""
    cmd = ["cargo", "run", "--bin", "euler_counterdetonation"]
    res = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True)
    assert res.returncode == 0, f"Binary failed: {res.stderr}"
    assert "AUDIT PASSED" in res.stdout
    assert REPORT_JSON.exists(), "Report JSON was not generated"


def test_euler_counterdetonation_audit_metrics():
    """Audit the generated JSON report according to H26 contracts."""
    with open(REPORT_JSON, "r") as f:
        data = json.load(f)

    assert data["_measured"] is True
    assert data["verification_passed"] is True

    # Check Calibration Run
    cal = data["calibration_run"]
    assert cal["is_t_dual"] is False
    assert cal["outcome"] == "FiniteTimeBlowUp"
    assert cal["blow_up_time"] is not None
    assert 0.05 < cal["blow_up_time"] < 0.3
    assert cal["max_enstrophy_reached"] > cal["initial_enstrophy"] * 1e6

    # Check T-Dual Shield Run
    shield = data["t_dual_shield_run"]
    assert shield["is_t_dual"] is True
    assert shield["outcome"] == "BeltramiShieldNeutralized"
    assert shield["blow_up_time"] is None
    assert shield["max_frustration_index"] > 1000.0, f"Expected D(M) > 1000, got {shield['max_frustration_index']}"
    assert shield["final_alignment"] > 0.98, f"Expected Beltrami alignment > 0.98, got {shield['final_alignment']}"
    assert shield["max_enstrophy_reached"] < 1.0e4, f"Enstrophy not bounded: {shield['max_enstrophy_reached']}"
