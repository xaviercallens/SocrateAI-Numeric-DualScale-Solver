#!/usr/bin/env python3
"""
Phase 6c Cloud-Production PoC Autonomous Workflow
=================================================
Runs the 5-agent pipeline incorporating Vault Security and Cloud Telemetry.
"""

import json
import logging
import os
import sys

from dualscale_solver.agents.phase6c_workflow_orchestrator import (
    run_phase6c_pipeline,
    _detect_live_backend,
    HAS_ANTIGRAVITY
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")

def main():
    print("================================================================================")
    print("   SOCRATEAI DUAL-SCALE SOLVER — PHASE 6C CLOUD-PRODUCTION AUTONOMOUS WORKFLOW")
    print("   Powered by Google Antigravity SDK & Vault Integration")
    print("================================================================================")

    import datetime
    print(f"Start Time: {datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"Repository: {os.getcwd()}")
    
    if os.environ.get("ANTIGRAVITY_API_KEY"):
        print("[Info] Detected ANTIGRAVITY_API_KEY. Orchestrator telemetry is authenticated natively.\n")

    if not HAS_ANTIGRAVITY:
        print("\n[WARNING] google-antigravity SDK not installed. Running in SCAFFOLDING mode.")
    else:
        backend = _detect_live_backend()
        print(f"Discovered active backend: {backend}\n")
        if backend == "none":
            print("[ERROR] No valid GEMINI_API_KEY, MISTRAL_API_KEY found, and Ollama is not running.")
            print("[ERROR] Phase 6c Vault Enforces strict authentication.")
        else:
            print(f"================================================================================")
            print(f">>> Launching 5-Agent Phase 6c Cloud-Production Pipeline... [Backend: {backend.upper()}]")
            print(f"================================================================================\n")

    res = run_phase6c_pipeline()

    print(json.dumps(res, indent=2))
    
    auditor = res.get("phase6c_hardness_auditor", {})
    status = auditor.get("overall_status", "UNKNOWN")
    
    print("\n================================================================================")
    if status == "CERTIFIED":
        print(f" ✅ PHASE 6C WORKFLOW CERTIFIED")
        print(f"    Certificate: {auditor.get('certificate_id')}")
        print(f"    SHA-256:     {auditor.get('sha256_hash')}")
        sys.exit(0)
    elif status == "SCAFFOLDING_ONLY":
        print(f" ⚠️ PHASE 6C WORKFLOW COMPLETED IN SCAFFOLDING_ONLY MODE")
        print(f"    Certificate: {auditor.get('certificate_id')}")
        print("    (Missing actual LLM backend keys or running outside Antigravity)")
        sys.exit(0)
    else:
        print(f" ❌ PHASE 6C WORKFLOW REJECTED")
        print("    Hardness invariants were violated or agents returned forbidden statuses.")
        sys.exit(1)

if __name__ == "__main__":
    main()
