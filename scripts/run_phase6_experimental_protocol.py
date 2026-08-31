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
    
    # Discover all available backends from environment variables
    available_backends = []
    if os.environ.get("GEMINI_API_KEY"):
        available_backends.append("gemini")
    if os.environ.get("MISTRAL_API_KEY"):
        available_backends.append("mistral")
    
    if not available_backends:
        available_backends.append("none")
        
    if os.environ.get("ANTIGRAVITY_API_KEY"):
        print(f"[Info] Detected ANTIGRAVITY_API_KEY. Orchestrator telemetry is authenticated natively.")

    print(f"\nDiscovered backends to evaluate: {', '.join(available_backends)}")
    
    overall_exit_code = 0

    for backend in available_backends:
        print("\n" + "=" * 80)
        print(f">>> Launching 4-Agent Phase 6 Autonomous Workflow Pipeline... [Backend: {backend.upper()}]")
        print("=" * 80 + "\n")

        t0 = time.time()
        pipeline = run_phase6_pipeline(grid_n=64, force_backend=backend)
        elapsed = time.time() - t0

        print(f"\n>>> Autonomous Pipeline Completed in {elapsed:.2f}s")
        print("-" * 80)

        # ---- Agent 1 ----
        a1 = pipeline["dev_engineer"]
        print("AGENT 1: DEV ENGINEER")
        print(f"  Status: {a1.get('status')}")
        print(f"  Details: {a1.get('details', 'N/A')}\n")

        # ---- Agent 2 ----
        a2 = pipeline["math_reviewer"]
        print("AGENT 2: MATH REVIEWER")
        print(f"  Status: {a2.get('status')}")
        print(f"  Details: {a2.get('details', 'N/A')}\n")

        # ---- Agent 3 ----
        a3 = pipeline["agentic_runtime_monitor"]
        print("AGENT 3: AGENTIC RUNTIME MONITOR (H24 Intercept Gate)")
        print(f"  Status: {a3.get('command') or a3.get('status')}")
        print(f"  Details: {a3.get('details', 'N/A')}\n")

        # ---- Agent 4 ----
        a4 = pipeline["qa_scientific_auditor"]
        print("AGENT 4: QA SCIENTIFIC AUDITOR (H24 / H25)")
        print(f"  Status: {a4.get('overall_status') or a4.get('status')}")
        print(f"  Details: {a4.get('details', 'N/A')}\n")

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
            print(f"🎉 ALL PHASE 6 GATES (H24, H25, H26, H27) ARE FULLY SATISFIED FOR {backend.upper()}.")
        elif is_scaffolding:
            print("⚠️  SCAFFOLDING_ONLY — SDK/model backend not yet live. Not a CI failure.")
            if overall_exit_code == 0: overall_exit_code = 2
        else:
            print(f"❌ PHASE 6 CERTIFICATION REJECTED FOR {backend.upper()}. Review invariant violations above.")
            overall_exit_code = 1
        print()

        # Save output JSON for this backend
        output_dir = os.path.join(repo_root, "data", "output")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"phase6_workflow_execution_report_{backend}.json")
        
        with open(output_path, "w") as f:
            json.dump(pipeline, f, indent=2)
        print(f"[✓] Report saved to: {output_path}")

    return overall_exit_code


if __name__ == "__main__":
    sys.exit(main())
