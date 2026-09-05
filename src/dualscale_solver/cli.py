"""
Command Line Interface for SocrateAI Numeric Dual-Scale Solver.
"""

import argparse
import sys
from pathlib import Path
import numpy as np

from dualscale_solver.cert.certificate_generator import (
    generate_verification_certificate,
    save_certificate,
)
from dualscale_solver.numeric.dyadic_cascade import DyadicShellSolver
from dualscale_solver.numeric.fourier_spectral import PseudoSpectralNavierStokes2D


def cmd_verify(args: argparse.Namespace) -> int:
    """Run exact verification and generate audit certificate."""
    print("================================================================================")
    print(" SocrateAI Dual-Scale Solver: Tier B Exact Rational Verification")
    print("================================================================================")
    
    cert = generate_verification_certificate()
    print(f" Certificate ID : {cert['certificate_id']}")
    print(f" Epistemic Tier : {cert['epistemic_tier']}")
    print(f" Status         : {cert['status']}")
    print(f" Claims Checked : {len(cert['claims_verified'])}")
    print(f" Negative Ctrl  : {cert['negative_controls']}")

    if args.output:
        out_path = Path(args.output)
        save_certificate(cert, out_path)
        print(f" Certificate saved to: {out_path.resolve()}")

    return 0 if cert["status"] == "PASSED" else 1


def cmd_dyadic(args: argparse.Namespace) -> int:
    """Run dyadic shell cascade simulation."""
    print(f"Running Dyadic Shell Model: shells={args.shells}, nu={args.nu}, alpha_prime={args.alpha_prime}")
    solver = DyadicShellSolver(
        n_shells=args.shells,
        nu=args.nu,
        alpha_prime=args.alpha_prime,
    )
    
    u0 = np.zeros(args.shells)
    u0[0] = 1.0
    u0[1] = 0.5
    
    result = solver.solve(t_span=(0.0, args.time), u0=u0, dt=args.dt)
    e0, e_final = result["energy"][0], result["energy"][-1]
    om_max = float(np.max(result["enstrophy"]))
    
    print(f" Initial Energy   : {e0:.6e}")
    print(f" Final Energy     : {e_final:.6e}")
    print(f" Peak Enstrophy   : {om_max:.6e}")
    print(" Dyadic simulation completed successfully.")
    return 0


def cmd_spectral(args: argparse.Namespace) -> int:
    """Run 2D pseudo-spectral Taylor-Green vortex simulation."""
    print(f"Running 2D Pseudo-Spectral NS: grid={args.grid}x{args.grid}, nu={args.nu}, alpha_prime={args.alpha_prime}")
    solver = PseudoSpectralNavierStokes2D(
        n_grid=args.grid,
        nu=args.nu,
        alpha_prime=args.alpha_prime,
    )
    u0_hat = solver.initialize_taylor_green()
    
    result = solver.solve(t_span=(0.0, args.time), u_hat0=u0_hat, dt=args.dt)
    max_div = float(np.max(result["max_divergences"]))
    e0, e_final = result["energy"][0], result["energy"][-1]
    
    print(f" Max |div(u)|    : {max_div:.3e} (Machine Precision)")
    print(f" Initial Energy  : {e0:.6e}")
    print(f" Final Energy    : {e_final:.6e}")
    print(" Spectral simulation completed successfully.")
    return 0


from dualscale_solver.agents.phase8_workflow_orchestrator import run_phase8_pipeline
import json


def cmd_workflow8(args: argparse.Namespace) -> int:
    """Run Phase 8 Autonomous Industrial Productization Pipeline (Workflow 8)."""
    print("================================================================================")
    print(" SocrateAI LeanFlow: Phase 8 Industrial Workflow 8 Autonomous Pipeline")
    print("================================================================================")
    cert = run_phase8_pipeline()
    print(f" Certificate ID : {cert['certificate_id']}")
    print(f" Overall Status : {cert['overall_status']}")
    print(f" Epistemic Tier : {cert['epistemic_tier']}")
    print(f" SHA-256 Hash   : {cert['sha256_hash']}")
    print(f" Invariants     : {len(cert['invariants_verified'])} Verified")
    print(f" Negative Ctrls : {len(cert['negative_controls'])} Rejections Verified")
    
    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(cert, f, indent=2)
        print(f" Certificate saved to: {out_path.resolve()}")
        
    return 0 if cert["overall_status"] == "CERTIFIED" else 1


from dualscale_solver.agents.phase9_workflow_orchestrator import run_phase9_pipeline

def cmd_workflow9(args: argparse.Namespace) -> int:
    """Run Phase 9 Autonomic Resilience & Recursive Optimization Pipeline (Workflow 9)."""
    print("================================================================================")
    print(" SocrateAI LeanFlow: Phase 9 Autonomic Resilience & Recursive Optimization")
    print("================================================================================")
    cert = run_phase9_pipeline()
    print(f" Certificate ID : {cert['certificate_id']}")
    print(f" Overall Status : {cert['overall_status']}")
    print(f" SHA-256 Hash   : {cert['sha256_hash']}")
    print(f" Invariants     : {len(cert['invariants_verified'])} Verified")
    print(f" Negative Ctrls : {len(cert['negative_controls'])} Rejections Verified")
    
    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(cert, f, indent=2)
        print(f" Certificate saved to: {out_path.resolve()}")
        
    return 0 if cert["overall_status"] == "CERTIFIED" else 1

from dualscale_solver.agents.phase10_workflow_orchestrator import run_phase10_pipeline

def cmd_workflow10(args: argparse.Namespace) -> int:
    """Run Phase 10 Enterprise AI, Real-Time Edge & OpenFOAM Supremacy (Workflow 10)."""
    print("================================================================================")
    print(" SocrateAI LeanFlow: Phase 10 Enterprise AI & OpenFOAM Supremacy")
    print("================================================================================")
    cert = run_phase10_pipeline()
    print(f" Certificate ID : {cert['certificate_id']}")
    print(f" Overall Status : {cert['overall_status']}")
    print(f" SHA-256 Hash   : {cert['sha256_hash']}")
    print(f" Invariants     : {len(cert['invariants_verified'])} Verified")
    print(f" Negative Ctrls : {len(cert['negative_controls'])} Rejections Verified")
    
    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(cert, f, indent=2)
        print(f" Certificate saved to: {out_path.resolve()}")
        
    return 0 if cert["overall_status"] == "CERTIFIED" else 1

from dualscale_solver.agents.phase11_workflow_orchestrator import Phase11HyperscaleOrchestrator

def cmd_workflow11(args: argparse.Namespace) -> int:
    """Run Phase 11 Enterprise Hyperscale & Critical Systems (Workflow 11)."""
    orchestrator = Phase11HyperscaleOrchestrator()
    report = orchestrator.execute_workflow()
    return 0 if report["certificate"]["overall_status"] == "CERTIFIED" else 1

from dualscale_solver.agents.phase12_workflow_orchestrator import run_phase12_pipeline

def cmd_workflow12(args: argparse.Namespace) -> int:
    """Run Phase 12 Autonomous Monotonic Greedy Search Loop & Industrial Workflows (Workflow 12)."""
    print("================================================================================")
    print(" SocrateAI LeanFlow: Phase 12 Monotonic Greedy Search Loop & Industrial Workflows")
    print("================================================================================")
    report = run_phase12_pipeline()
    cert = report["certificate"]
    print(f" Certificate ID : {cert['certificate_id']}")
    print(f" Overall Status : {cert['overall_status']}")
    print(f" SHA-256 Hash   : {cert['sha256_hash']}")
    
    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        print(f" Certificate saved to: {out_path.resolve()}")
        
    return 0 if cert["overall_status"] == "CERTIFIED" else 1

def main() -> None:
    parser = argparse.ArgumentParser(
        prog="dualscale-solver",
        description="SocrateAI Numeric Dual-Scale PDE Solver and Invariant Verifier",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Subcommand: verify
    p_verify = subparsers.add_parser("verify", help="Run exact Tier B verification & produce certificate")
    p_verify.add_argument("--output", "-o", type=str, default="data/verification_cert.json", help="Path to output certificate")
    p_verify.set_defaults(func=cmd_verify)

    # Subcommand: workflow8
    p_wf8 = subparsers.add_parser("workflow8", help="Run Phase 8 Autonomous Industrial Productization Pipeline (Workflow 8)")
    p_wf8.add_argument("--output", "-o", type=str, default="data/cert_phase8_workflow.json", help="Path to output certificate")
    p_wf8.set_defaults(func=cmd_workflow8)

    # Subcommand: workflow9
    p_wf9 = subparsers.add_parser("workflow9", help="Run Phase 9 Autonomic Resilience & Recursive Optimization")
    p_wf9.add_argument("--output", "-o", type=str, default="data/cert_phase9_workflow.json", help="Path to output certificate")
    p_wf9.set_defaults(func=cmd_workflow9)

    # Subcommand: workflow10
    p_wf10 = subparsers.add_parser("workflow10", help="Run Phase 10 Enterprise AI, Real-Time Edge & OpenFOAM Supremacy")
    p_wf10.add_argument("--output", "-o", type=str, default="data/cert_phase10_workflow.json", help="Path to output certificate")
    p_wf10.set_defaults(func=cmd_workflow10)

    # Subcommand: workflow11
    p_wf11 = subparsers.add_parser("workflow11", help="Run Phase 11 Enterprise Hyperscale & Critical Systems")
    p_wf11.set_defaults(func=cmd_workflow11)

    # Subcommand: workflow12
    p_wf12 = subparsers.add_parser("workflow12", help="Run Phase 12 Autonomous Auto-Research Loop & Industrial Workflows")
    p_wf12.add_argument("--output", "-o", type=str, default="data/cert_phase12_workflow.json", help="Path to output certificate")
    p_wf12.set_defaults(func=cmd_workflow12)

    # Subcommand: dyadic
    p_dyadic = subparsers.add_parser("dyadic", help="Run dyadic shell cascade simulation")
    p_dyadic.add_argument("--shells", type=int, default=20, help="Number of dyadic shells")
    p_dyadic.add_argument("--nu", type=float, default=1e-3, help="Kinematic viscosity")
    p_dyadic.add_argument("--alpha-prime", type=float, default=0.01, help="Dual-scale cutoff alpha'")
    p_dyadic.add_argument("--time", type=float, default=1.0, help="Simulation duration")
    p_dyadic.add_argument("--dt", type=float, default=0.001, help="Time step")
    p_dyadic.set_defaults(func=cmd_dyadic)

    # Subcommand: spectral
    p_spectral = subparsers.add_parser("spectral", help="Run 2D pseudo-spectral Taylor-Green simulation")
    p_spectral.add_argument("--grid", type=int, default=64, help="Grid size N")
    p_spectral.add_argument("--nu", type=float, default=1e-3, help="Kinematic viscosity")
    p_spectral.add_argument("--alpha-prime", type=float, default=0.01, help="Dual-scale cutoff alpha'")
    p_spectral.add_argument("--time", type=float, default=0.5, help="Simulation duration")
    p_spectral.add_argument("--dt", type=float, default=0.005, help="Time step")
    p_spectral.set_defaults(func=cmd_spectral)

    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(1)

    sys.exit(args.func(args))


if __name__ == "__main__":
    main()

