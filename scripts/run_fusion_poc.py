#!/usr/bin/env python3
"""
Fusion Proof of Concept Execution Runner
========================================

Executes the PoC workflows, verifying both the Enterprise Core Dev Cycle
and the Fusion PoC targets (speedup, residuals).
"""

import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from dualscale_solver.agents.fusion_poc_workflow import run_fusion_poc_workflow


def main() -> int:
    print("=" * 80)
    print(" LEANFLOW ENTERPRISE : FUSION PoC WORKFLOW EXECUTION")
    print("=" * 80)

    cert = run_fusion_poc_workflow()

    print(f"\nCertificate ID : {cert.get('certificate_id')}")
    print(f"Product Edition: {cert.get('product_edition', 'N/A')}")
    print(f"Overall Status : {cert.get('overall_status')}")
    print(f"Dev Cycle Cert : {cert.get('dev_cycle_certificate', 'N/A')}")
    print(f"SHA-256 Seal   : {cert.get('sha256_seal', 'N/A')}")
    if "certificate_file" in cert:
        print(f"Persisted Path : {cert['certificate_file']}")
    else:
        print(f"Reason         : {cert.get('reason', 'N/A')}")

    if "poc_benchmarks" in cert:
        print("\n--- PoC BENCHMARKS (v12_poc_results.json) ---")
        poc = cert["poc_benchmarks"]
        print(f"  Max DOF         : {poc.get('max_dof')}")
        print(f"  CPU Time (ms)   : {poc.get('max_cpu_ms')}")
        print(f"  GPU Total (ms)  : {poc.get('max_gpu_ms')}")
        print(f"  Speedup         : {poc.get('max_speedup'):.2f}x")
        print(f"  Final FP8 Res   : {poc.get('final_fp8_res')}")
        print(f"  Final FP64 Res  : {poc.get('final_fp64_res')}")
        
        print("\n--- TARGETS MET ---")
        for target, passed in poc.get("targets_met", {}).items():
            print(f"  {target:20s}: {'PASS ✓' if passed else 'FAIL ✗'}")

    print("\n" + "=" * 80)
    if cert["overall_status"] == "CERTIFIED":
        print(" ✅ FUSION PoC WORKFLOW: FULLY CERTIFIED")
        print("=" * 80)
        return 0
    else:
        print(" ❌ FUSION PoC WORKFLOW: FAILED")
        print("=" * 80)
        return 1


if __name__ == "__main__":
    sys.exit(main())
