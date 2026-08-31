#!/usr/bin/env python3
"""
Phase 6 Experimental Protocol Runner
=====================================
Standalone driver for Phase 6 autonomous pipeline.
Uses the Google Antigravity SDK to spawn multi-agent workflows.

Usage:
    python3 scripts/run_phase6_experimental_protocol.py
"""

import sys
import json
import time
import datetime
import os

# Ensure project src is on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from dualscale_solver.agents.phase6_workflow_orchestrator import run_phase6_pipeline


def main():
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    start_utc = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    print("=" * 80)
    print("   SOCRATEAI DUAL-SCALE SOLVER — PHASE 6 AUTONOMOUS MULTI-AGENT EXECUTION")
    print("   Powered by Google Antigravity SDK")
    print("=" * 80)
    print(f"Start Time: {start_utc}")
    print(f"Repository: {repo_root}")
    print()
    print(">>> Launching 4-Agent Phase 6 Autonomous Workflow Pipeline...")
    print()

    t0 = time.time()
    pipeline = run_phase6_pipeline(grid_n=64)
    elapsed = time.time() - t0

    print(f">>> Autonomous Pipeline Completed in {elapsed:.2f}s")
    print()
    print("-" * 80)

    # ---- Agent 1 ----
    a1 = pipeline["dev_engineer"]
    print("AGENT 1: DEV ENGINEER")
    print(f"  Status: {a1.get('status')}")
    print(f"  Details: {a1.get('details', 'N/A')}")
    print()

    # ---- Agent 2 ----
    a2 = pipeline["math_reviewer"]
    print("AGENT 2: MATH REVIEWER")
    print(f"  Status: {a2.get('status')}")
    print(f"  Details: {a2.get('details', 'N/A')}")
    print()

    # ---- Agent 3 ----
    a3 = pipeline["agentic_runtime_monitor"]
    print("AGENT 3: AGENTIC RUNTIME MONITOR (H24 Intercept Gate)")
    print(f"  Status: {a3.get('status')}")
    print(f"  Details: {a3.get('details', 'N/A')}")
    print()

    # ---- Agent 4 ----
    a4 = pipeline["qa_scientific_auditor"]
    print("AGENT 4: QA SCIENTIFIC AUDITOR (H24 / H25)")
    print(f"  Status: {a4.get('status')}")
    print(f"  Details: {a4.get('details', 'N/A')}")
    print()

    # ---- Hardness Auditor ----
    a5 = pipeline["phase6_hardness_auditor"]
    print("PHASE 6 HARDNESS AUDIT")
    print(f"  Certificate ID: {a5['certificate_id']}")
    print(f"  SHA-256 Hash: {a5['sha256_hash']}")
    print(f"  Overall Status: {a5['overall_status']}")
    print(f"  Invariants Verified:")
    for inv, passed in a5["invariants_verified"].items():
        icon = "✅" if passed else "❌"
        print(f"    - {inv:<45}: {icon} {'PASS' if passed else 'FAIL'}")

    print("=" * 80)
    all_pass = a5["overall_status"] == "CERTIFIED"
    is_scaffolding = a5["overall_status"] == "SCAFFOLDING_ONLY"
    if all_pass:
        print("🎉 ALL PHASE 6 GATES (H24, H25, H26, H27) ARE FULLY SATISFIED.")
    elif is_scaffolding:
        print("⚠️  SCAFFOLDING_ONLY — SDK/model backend not yet live. Not a CI failure.")
        print("   To reach CERTIFIED: pip install -e '.[agentic]' + set GEMINI_API_KEY or start Ollama.")
    else:
        print("❌ PHASE 6 CERTIFICATION REJECTED. Review invariant violations above.")
    print()

    # Save output JSON
    output_dir = os.path.join(repo_root, "data", "output")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "phase6_workflow_execution_report.json")
    
    with open(output_path, "w") as f:
        json.dump(pipeline, f, indent=2)
    print(f"[✓] Report saved to: {output_path}")

    # Exit codes: 0=CERTIFIED, 2=SCAFFOLDING_ONLY (incomplete, not an error), 1=REJECTED
    if all_pass:
        return 0
    elif is_scaffolding:
        return 2
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
