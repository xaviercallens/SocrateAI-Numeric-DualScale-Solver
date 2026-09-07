#!/usr/bin/env python3
"""
Enterprise Edition Full Autonomous Dev Cycle Runner
===================================================

Coordinates the Tri-Agent Development Cycle:
  1. spec_math_agent (Lean 4 Formal Specifications REQ-ENT-01..16)
  2. dev_engineer_agent (Rust & Python Numerical Execution Engine)
  3. qa_test_auditor_agent (Validation of all 16 Sequence IDs & >= 90% Code Coverage Gate)
"""

import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from dualscale_solver.agents.enterprise_dev_cycle import run_enterprise_dev_cycle


def main() -> int:
    print("=" * 80)
    print(" LEANFLOW ENTERPRISE : FULL TRI-AGENT AUTONOMOUS DEV CYCLE (V3.3.0)")
    print("=" * 80)

    cert = run_enterprise_dev_cycle()

    print(f"\nCertificate ID : {cert['certificate_id']}")
    print(f"Product Edition: {cert['product_edition']}")
    print(f"Dev Cycle Phase: {cert['dev_cycle_phase']}")
    print(f"Overall Status : {cert['overall_status']}")
    print(f"SHA-256 Seal   : {cert['sha256_seal']}")
    print(f"Persisted Path : {cert['certificate_file']}")

    print("\n--- TRI-AGENT DELIVERABLES ---")
    for agent_name, report in cert["tri_agent_deliverables"].items():
        print(f"  {agent_name:25s}: status={report.get('status')}, _measured={report.get('_measured')}")

    print("\n--- SEQUENCE REQUIREMENTS TRACEABILITY MATRIX (REQ-ENT-01..16) ---")
    for req_id, passed in cert["sequence_traceability_matrix"].items():
        print(f"  {req_id:15s}: {'PASS ✓' if passed else 'FAIL ✗'}")

    print("\n--- CODE COVERAGE METRICS ---")
    metrics = cert["coverage_metrics"]
    print(f"  Measured Coverage  : {metrics.get('measured_coverage_pct')}%")
    print(f"  Target Threshold   : {metrics.get('coverage_target_pct')}%")
    print(f"  Coverage Gate      : {'PASSED ✓' if metrics.get('gate_passed') else 'FAILED ✗'}")

    print("\n" + "=" * 80)
    if cert["overall_status"] == "CERTIFIED":
        print(" ✅ ENTERPRISE FULL DEV CYCLE: FULLY CERTIFIED & READY FOR RELEASE")
        print("=" * 80)
        return 0
    else:
        print(" ❌ ENTERPRISE FULL DEV CYCLE: FAILED")
        print("=" * 80)
        return 1


if __name__ == "__main__":
    sys.exit(main())
