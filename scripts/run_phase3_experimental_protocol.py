#!/usr/bin/env python3
"""
Phase 3 Autonomous Experimental Protocol & OpenFOAM Supremacy Driver.

Executes the 5-agent Phase 3 workflow:
1. AMG Preconditioner Synthesizer (P3: FP8 TensorCore AMG)
2. OpenFOAM Comparison Auditor (Real speedup benchmark on identical Poisson grids)
3. SymBrain Router Agent (Adaptive neural mesh order & preconditioner dispatch)
4. TensorCore Precision Verifier (Quantization fidelity & energy conservation)
5. Phase 3 Hardness Auditor (Invariants H1-H15, negative controls, SHA-256 certificate)
"""

import sys
import json
import time
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo_root / "src"))

from dualscale_solver.agents.phase3_workflow_orchestrator import Phase3WorkflowOrchestrator


def main():
    print("=" * 80)
    print("   SOCRATEAI DUAL-SCALE SOLVER — PHASE 3 AUTONOMOUS MULTI-AGENT EXECUTION")
    print("=" * 80)
    print(f"Start Time: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}")
    print(f"Repository: {repo_root}")
    print()

    orchestrator = Phase3WorkflowOrchestrator(repo_root=repo_root)

    print(">>> Launching 5-Agent Phase 3 Autonomous Workflow Pipeline...")
    t0 = time.perf_counter()
    report = orchestrator.run_full_phase3_pipeline()
    elapsed = time.perf_counter() - t0

    print(f"\n>>> Autonomous Pipeline Completed in {elapsed:.2f}s\n")

    amg = report["amg_preconditioner_synthesizer"]
    of = report["openfoam_comparison_auditor"]
    sym = report["symbrain_router"]
    prec = report["tensorcore_precision_verifier"]
    audit = report["phase3_hardness_auditor"]
    cert = audit["certificate"]

    print("-" * 80)
    print("AGENT 1: AMG PRECONDITIONER SYNTHESIZER")
    print(f"  Status: {amg['status']}")
    print(f"  Hierarchy Levels: {amg['p3_amg_levels']} (dims: {amg['coarse_dimensions']})")
    print(f"  FP8 TensorCore Emulation: {amg['fp8_tensorcore_emulation']}")

    print("\nAGENT 2: OPENFOAM COMPARISON AUDITOR")
    print(f"  Status: {of['status']}")
    for grid_name, metrics in of["benchmarks"].items():
        print(f"  [{grid_name}] OpenFOAM DIC/CG: {metrics['openfoam_dic_cg_iterations']} iters ({metrics['openfoam_dic_cg_time_ms']:.2f} ms) | "
              f"LeanFlow P3: {metrics['leanflow_p3_amg_iterations']} iters ({metrics['leanflow_p3_amg_time_ms']:.2f} ms) "
              f"[Iter Gain: {metrics['iteration_reduction_ratio']:.1f}x, Speedup: {metrics['wall_clock_speedup']:.2f}x]")

    print("\nAGENT 3: SYMBRAIN ROUTER AGENT")
    print(f"  Status: {sym['status']}")
    for dec in sym["routing_decisions"]:
        print(f"  [M={dec['truncation_order_M']}] D(M)={dec['triadic_frustration_D_M']:.2f} -> "
              f"Dispatch: {dec['dispatched_preconditioner']} (Action: {dec['adaptive_mesh_action']})")

    print("\nAGENT 4: TENSORCORE PRECISION VERIFIER")
    print(f"  Status: {prec['status']}")
    print(f"  FP8 Relative Quantization Error: {prec['fp8_relative_quantization_error']:.2e} (Tol <= 1e-5: {'PASS' if prec['quantization_within_tolerance'] else 'FAIL'})")
    print(f"  FP8 Max Residual: {prec['fp8_max_residual']:.2e}")

    print("\nAGENT 5: PHASE 3 HARDNESS AUDITOR")
    print(f"  Certificate ID: {cert['certificate_id']}")
    print(f"  SHA-256 Hash: {cert['sha256_hash']}")
    print(f"  Overall Status: {cert['status']}")
    print("  Invariants Checklist (H1–H15):")
    for inv, passed in cert["invariants_verified"].items():
        print(f"    - {inv:38s}: {'✅ PASS' if passed else '❌ FAIL'}")

    print("=" * 80)

    if cert["status"] == "CERTIFIED":
        print("🎉 ALL PHASE 3 GATES AND HARDNESS INVARIANTS (H1–H15) ARE FULLY SATISFIED.")
        sys.exit(0)
    else:
        print("❌ PHASE 3 VERIFICATION REJECTED BY AUDITOR.")
        sys.exit(1)


if __name__ == "__main__":
    main()
