"""
Unit Tests for Mathesis Ledger Soundness and Epistemic Tier Monotonicity.
"""

from pathlib import Path
import pytest
from dualscale_solver.cert.ledger_checker import (
    audit_ledger_files,
    verify_ledger_soundness,
    Tier,
)


def test_workspace_ledger_is_sound():
    repo_root = Path(__file__).parent.parent
    result = audit_ledger_files(repo_root)
    assert result["status"] == "PASSED"
    assert result["soundness"]["is_sound"] is True
    assert result["total_claims_audited"] >= 5


def test_negative_control_unsound_ledger_rejected():
    """Negative control: Tier A claim depending on Tier C claim must be rejected."""
    unsound_claims = {
        "DS-C-0001": {
            "id": "DS-C-0001",
            "tier": "C",
            "statement": "Heuristic conjecture.",
            "supports": [],
        },
        "DS-A-0001": {
            "id": "DS-A-0001",
            "tier": "A",
            "statement": "Kernel claim falsely resting on conjecture.",
            "supports": ["DS-C-0001"], # Violation: Tier A > Tier C
        },
    }
    result = verify_ledger_soundness(unsound_claims)
    assert result["is_sound"] is False
    assert len(result["violations"]) == 1
    assert "Tier monotonicity violated" in result["violations"][0]["error"]
