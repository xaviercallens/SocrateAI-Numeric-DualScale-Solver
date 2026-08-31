#!/usr/bin/env python3
"""
Phase 5 Experimental Protocol Runner
=====================================
Standalone driver for Phase 5 autonomous pipeline.
Mirrors the structure of run_phase3_experimental_protocol.py.

Usage:
    python3 scripts/run_phase5_experimental_protocol.py
"""

import sys
import json
import time
import datetime
import os

# Ensure project src is on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from dualscale_solver.agents.phase5_workflow_orchestrator import run_phase5_pipeline


def main():
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    start_utc = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    print("=" * 80)
    print("   SOCRATEAI DUAL-SCALE SOLVER — PHASE 5 AUTONOMOUS MULTI-AGENT EXECUTION")
    print("=" * 80)
    print(f"Start Time: {start_utc}")
    print(f"Repository: {repo_root}")
    print()
    print(">>> Launching 5-Agent Phase 5 Autonomous Workflow Pipeline...")
    print()

    t0 = time.time()
    pipeline = run_phase5_pipeline(grid_n=64)
    elapsed = time.time() - t0

    print(f">>> Autonomous Pipeline Completed in {elapsed:.2f}s")
    print()
    print("-" * 80)

    # ---- Agent 1 ----
    a1 = pipeline["jhtdb_spectral_auditor"]
    print("AGENT 1: JHTDB SPECTRAL AUDITOR (H17)")
    print(f"  Status: {a1['status']}")
    print(f"  L2 Relative Error: {a1['h17_l2_relative_error']:.4e}  "
          f"[< 2%: {'✅ PASS' if a1['h17_l2_error_passes'] else '❌ FAIL'}]")
    print(f"  Kolmogorov Exponent: {a1['h17_kolmogorov_exponent']:.4f}  "
          f"[in [-1.8,-1.6]: {'✅ PASS' if a1['h17_exponent_in_range'] else '❌ FAIL'}]")
    print(f"  Reference Method: {a1['reference_method']}")
    print(f"  NC-DS-09 (White Noise): {'✅ PASS' if a1['nc_ds_09_passed'] else '❌ FAIL'}")
    print()

    # ---- Agent 2 ----
    a2 = pipeline["production_sla_tester"]
    print("AGENT 2: PRODUCTION SLA STRESS TESTER (H18)")
    print(f"  Status: {a2['status']}")
    print(f"  Throughput: {a2['throughput_steps_per_sec']:.1f} steps/s  "
          f"[≥ 1000: {'✅ PASS' if a2['throughput_steps_per_sec'] >= 1000 else '❌ FAIL'}]")
    print(f"  NaN Count: {a2['nan_count']}  "
          f"[= 0: {'✅ PASS' if a2['nan_count'] == 0 else '❌ FAIL'}]")
    print(f"  Uptime: {a2['uptime_fraction'] * 100:.3f}%  "
          f"[≥ 99.9%: {'✅ PASS' if a2['uptime_fraction'] >= 0.999 else '❌ FAIL'}]")
    print(f"  NC-DS-10 (NaN Injection): {'✅ PASS' if a2['nc_ds_10_passed'] else '❌ FAIL'}")
    print()

    # ---- Agent 3 ----
    a3 = pipeline["frustration_monotonicity_verifier"]
    print("AGENT 3: FRUSTRATION MONOTONICITY VERIFIER (H19)")
    print(f"  Status: {a3['status']}")
    for M, D in zip(a3["M_values"], a3["D_values"]):
        print(f"  D({M:2d}) = {D:.4f}")
    print(f"  H19 Monotone Non-Decreasing: {'✅ PASS' if a3['h19_passes'] else '❌ FAIL'}")
    if a3["h19_violations"]:
        print(f"  Violations: {a3['h19_violations']}")
    print()

    # ---- Agent 4 ----
    a4 = pipeline["cross_scale_consistency_validator"]
    print("AGENT 4: CROSS-SCALE CONSISTENCY VALIDATOR")
    print(f"  Status: {a4['status']}")
    print(f"  P1 vs Ref Error: {a4['p1_vs_ref_rel_error']:.2e}  "
          f"[< 1e-7: {'✅ PASS' if a4['p1_vs_ref_rel_error'] < 1e-7 else '❌ FAIL'}]")
    print(f"  P2 vs Ref Error: {a4['p2_vs_ref_rel_error']:.2e}  "
          f"[< 1e-7: {'✅ PASS' if a4['p2_vs_ref_rel_error'] < 1e-7 else '❌ FAIL'}]")
    print(f"  P1/P2/Ref CG Iters: {a4['p1_cg_iterations']} / {a4['p2_cg_iterations']} / {a4['ref_cg_iterations']}")
    print()

    # ---- Agent 5 ----
    a5 = pipeline["phase5_hardness_auditor"]
    print("AGENT 5: PHASE 5 HARDNESS AUDITOR")
    print(f"  Certificate ID: {a5['certificate_id']}")
    print(f"  SHA-256 Hash: {a5['sha256_hash']}")
    print(f"  Overall Status: {a5['overall_status']}")
    print(f"  Invariants Checklist (H1\u2013H19):")
    for inv, passed in a5["invariants_verified"].items():
        icon = "✅" if passed else "❌"
        print(f"    - {inv:<45}: {icon} {'PASS' if passed else 'FAIL'}")

    print("=" * 80)
    all_pass = a5["overall_status"] == "CERTIFIED"
    if all_pass:
        print("🎉 ALL PHASE 5 GATES AND HARDNESS INVARIANTS (H1–H19) ARE FULLY SATISFIED.")
    else:
        print("❌ PHASE 5 CERTIFICATION FAILED. Review invariant violations above.")
    print()

    # Save output JSON
    output_dir = os.path.join(repo_root, "data", "output")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "phase5_workflow_execution_report.json")
    # Convert numpy types for JSON serialisation
    def _json_safe(obj):
        if isinstance(obj, dict):
            return {k: _json_safe(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [_json_safe(v) for v in obj]
        elif hasattr(obj, 'item'):
            return obj.item()
        return obj

    with open(output_path, "w") as f:
        json.dump(_json_safe(pipeline), f, indent=2)
    print(f"[✓] Report saved to: {output_path}")

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
