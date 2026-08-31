#!/usr/bin/env python3
"""
Phase 6b Industrial PoC Experimental Protocol Runner
====================================================
Standalone driver for the Phase 6b Industrial Proof of Concept Pipeline.
Evaluates:
- Bioreactor k_L a mass transfer enhancement (H29)
- Transonic shock buffet oscillation suppression (H30)
- Embedded real-time execution bounds (H31)
- Multi-backend AI execution parity (H32)
"""

import sys
import json
import time
import datetime
import os

# Ensure project src is on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from dualscale_solver.agents.phase6b_workflow_orchestrator import run_phase6b_pipeline


def main():
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    start_utc = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    print("=" * 80)
    print("   SOCRATEAI DUAL-SCALE SOLVER — PHASE 6B INDUSTRIAL POC EXECUTION")
    print("   Powered by Google Antigravity SDK & Multi-Sector Physics Engines")
    print("=" * 80)
    print(f"Start Time: {start_utc}")
    print(f"Repository: {repo_root}")

    # Discover available backends
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
        print(f">>> Launching 5-Agent Phase 6b Industrial Pipeline... [Backend: {backend.upper()}]")
        print("=" * 80 + "\n")

        t0 = time.time()
        pipeline = run_phase6b_pipeline(force_backend=backend)
        elapsed = time.time() - t0

        print(f"\n>>> Industrial Pipeline Completed in {elapsed:.2f}s")
        print("-" * 80)

        # Print Agent Summaries
        for name, label in [
            ("industrial_domain_expert", "AGENT 1: INDUSTRIAL DOMAIN EXPERT"),
            ("bioreactor_kla_optimizer", "AGENT 2: BIOREACTOR KLA OPTIMIZER (H29)"),
            ("aerospace_buffet_controller", "AGENT 3: AEROSPACE BUFFET CONTROLLER (H30)"),
            ("edge_latency_auditor", "AGENT 4: EDGE LATENCY AUDITOR (H31)"),
        ]:
            a = pipeline[name]
            print(label)
            print(f"  Status: {a.get('status')}")
            print(f"  Details: {a.get('details', 'N/A')}\n")

        # Hardness Auditor
        a5 = pipeline["phase6b_hardness_auditor"]
        print("PHASE 6B INDUSTRIAL HARDNESS AUDIT")
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
            print(f"🎉 ALL PHASE 6B INDUSTRIAL GATES (H29-H32) SATISFIED FOR {backend.upper()}.")
        elif is_scaffolding:
            print("⚠️  SCAFFOLDING_ONLY — SDK/model backend not yet live. Not a CI failure.")
            if overall_exit_code == 0:
                overall_exit_code = 2
        else:
            print(f"❌ PHASE 6B CERTIFICATION REJECTED FOR {backend.upper()}.")
            overall_exit_code = 1
        print()

        # Save output JSON
        output_dir = os.path.join(repo_root, "data", "output")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"phase6b_workflow_execution_report_{backend}.json")
        with open(output_path, "w") as f:
            json.dump(pipeline, f, indent=2)
        print(f"[✓] Report saved to: {output_path}")

    return overall_exit_code


if __name__ == "__main__":
    sys.exit(main())
