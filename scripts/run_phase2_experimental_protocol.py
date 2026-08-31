#!/usr/bin/env python3
"""
Phase 2 Autonomous Experimental Protocol & Preconditioner Verification Driver.

Executes the 5-agent Phase 2 workflow:
1. Preconditioner Synthesizer (P1 Fourier Gate & P2 Multilevel ILU)
2. Spectral Gate Verifier (Condition number kappa <= 10^3 on multiscale grids)
3. Krylov Convergence Auditor (Exact residual history, 7-run wall-clock timing)
4. DualScale Cross Validator (Lean 4 Galerkin bound vs Rust ETD-RK4 simulation)
5. Epistemic Hardness Auditor (H1-H14 compliance, negative controls, SHA-256 certificate)
"""

import sys
import json
import time
from pathlib import Path

# Add src to python path
repo_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo_root / "src"))

from dualscale_solver.agents.phase2_workflow_orchestrator import Phase2WorkflowOrchestrator


def main():
    print("=" * 80)
    print("   SOCRATEAI DUAL-SCALE SOLVER — PHASE 2 AUTONOMOUS MULTI-AGENT EXECUTION")
    print("=" * 80)
    print(f"Start Time: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}")
    print(f"Repository: {repo_root}")
    print()

    orchestrator = Phase2WorkflowOrchestrator(repo_root=repo_root)

    print(">>> Launching 5-Agent Phase 2 Autonomous Workflow Pipeline...")
    t0 = time.perf_counter()
    report = orchestrator.run_full_phase2_pipeline()
    elapsed = time.perf_counter() - t0

    print(f"\n>>> Autonomous Pipeline Completed in {elapsed:.2f}s\n")

    # Extract sub-agent metrics
    syn = report["preconditioner_synthesizer"]
    spec = report["spectral_gate_verifier"]
    kry = report["krylov_convergence_auditor"]
    cross = report["dualscale_cross_validator"]
    audit = report["epistemic_hardness_auditor"]
    cert = audit["certificate"]

    print("-" * 80)
    print("AGENT 1: PRECONDITIONER SYNTHESIZER")
    print(f"  Status: {syn['status']}")
    print(f"  P1 Operators: {list(syn['p1_fourier_gate'].keys())}")
    print(f"  P2 Multilevel ILU: {syn['p2_multilevel_ilu']['operator_type']} (shape: {syn['p2_multilevel_ilu']['shape']})")

    print("\nAGENT 2: SPECTRAL GATE VERIFIER")
    print(f"  Status: {spec['status']}")
    for grid_name, metrics in spec["spectral_metrics"].items():
        print(f"  [{grid_name}] Unpreconditioned kappa: {metrics['unpreconditioned_condition_number']:.2e} | "
              f"P1 kappa: {metrics['p1_preconditioned_condition_number']:.2f} "
              f"(Reduction: {metrics['condition_number_reduction_factor']:.1f}x) "
              f"[H14 Gate: {'PASS' if metrics['h14_kappa_bound_satisfied'] else 'FAIL'}]")

    print("\nAGENT 3: KRYLOV CONVERGENCE AUDITOR")
    print(f"  Status: {kry['status']}")
    print(f"  System Dimension: {kry['benchmark_system_dimension']}")
    print(f"  Unpreconditioned CG: {kry['unpreconditioned_cg_iterations']} iters, {kry['unpreconditioned_cg_time_sec']*1000:.2f} ms")
    print(f"  P1 Preconditioned CG: {kry['p1_preconditioned_cg_iterations']} iters, {kry['p1_preconditioned_cg_time_sec']*1000:.2f} ms")
    print(f"  Iteration Reduction Ratio: {kry['iteration_reduction_ratio']:.2f}x (Target >= 5x: {'ACHIEVED' if kry['goal_5x_iteration_reduction_achieved'] else 'NOT MET'})")
    print(f"  Wall-Time Gain: {kry['wall_time_reduction_pct']:.1f}%")
    print(f"  P2 FGMRES Residual: {kry['p2_fgmres_final_residual']:.2e} (iters: {kry['p2_fgmres_iterations']})")

    print("\nAGENT 4: DUAL-SCALE CROSS VALIDATOR")
    print(f"  Status: {cross['status']}")
    print(f"  Exact Rational T-Duality: {'PASS' if cross['rational_t_duality_passed'] else 'FAIL'}")
    print(f"  Singularity Avoidance: {'PASS' if cross['rational_singularity_avoidance_passed'] else 'FAIL'}")
    print(f"  Energy Monotonicity: {'VERIFIED' if cross['energy_monotonicity_verified'] else 'VIOLATED'}")
    print(f"  Max Observed Enstrophy: {cross['max_enstrophy_observed']:.2f} (Bound <= {cross['enstrophy_bound_1_over_alpha']})")

    print("\nAGENT 5: EPISTEMIC HARDNESS AUDITOR")
    print(f"  Certificate ID: {cert['certificate_id']}")
    print(f"  SHA-256 Hash: {cert['sha256_hash']}")
    print(f"  Overall Status: {cert['status']}")
    print("  Invariants Checklist (H1–H14):")
    for inv, passed in cert["invariants_verified"].items():
        print(f"    - {inv:35s}: {'✅ PASS' if passed else '❌ FAIL'}")

    print("\n  Negative Controls Checklist:")
    for nc, passed in audit["negative_controls"].items():
        if nc != "all_negative_controls_rejected_falsified_states":
            print(f"    - {nc:35s}: {'🛡️ REJECTED FALSIFICATION (PASS)' if passed else '⚠️ FAILED TO REJECT'}")

    print("=" * 80)

    if cert["status"] == "CERTIFIED":
        print("🎉 ALL PHASE 2 GATES AND HARDNESS INVARIANTS (H1–H14) ARE FULLY SATISFIED.")
        sys.exit(0)
    else:
        print("❌ PHASE 2 VERIFICATION REJECTED BY AUDITOR.")
        sys.exit(1)


if __name__ == "__main__":
    main()
