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
