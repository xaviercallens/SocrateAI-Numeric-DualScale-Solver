"""
Reproducible Benchmark Runner for Dual-Scale Numerical Solvers.
"""

import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from dualscale_solver.numeric.dyadic_cascade import DyadicShellSolver
from dualscale_solver.numeric.fourier_spectral import PseudoSpectralNavierStokes2D


def run_cascade_benchmark(output_dir: Path) -> dict:
    """Benchmark dyadic shell model: standard vs dual-scale regularized."""
    print("Running Cascade Benchmark (Katz-Pavlović dyadic shells)...")
    n_shells = 18
    u0 = np.zeros(n_shells)
    u0[0] = 1.0
    u0[1] = 0.5
    
    # 1. Standard NS cascade (no dual-scale)
    solver_std = DyadicShellSolver(n_shells=n_shells, nu=1e-4, alpha_prime=None)
    res_std = solver_std.solve(t_span=(0.0, 0.5), u0=u0, dt=0.001)

    # 2. Dual-scale regularized cascade
    solver_ds = DyadicShellSolver(n_shells=n_shells, nu=1e-4, alpha_prime=0.01)
    res_ds = solver_ds.solve(t_span=(0.0, 0.5), u0=u0, dt=0.001)

    # Save comparison plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    ax1.semilogy(res_std["times"], res_std["energy"], label="Standard NS", color="#e74c3c", lw=2)
    ax1.semilogy(res_ds["times"], res_ds["energy"], label="Dual-Scale Regularized", color="#2ecc71", lw=2)
    ax1.set_xlabel("Time t")
    ax1.set_ylabel("Kinetic Energy E(t)")
    ax1.set_title("Energy Evolution in Dyadic Shells")
    ax1.grid(True, alpha=0.3)
    ax1.legend()

    ax2.semilogy(res_std["times"], res_std["enstrophy"], label="Standard NS", color="#e74c3c", lw=2)
    ax2.semilogy(res_ds["times"], res_ds["enstrophy"], label="Dual-Scale Regularized", color="#2ecc71", lw=2)
    ax2.set_xlabel("Time t")
    ax2.set_ylabel("Enstrophy Ω(t)")
    ax2.set_title("Enstrophy Control & Singularity Suppression")
    ax2.grid(True, alpha=0.3)
    ax2.legend()

    plt.tight_layout()
    plot_path = output_dir / "dyadic_cascade_benchmark.png"
    plt.savefig(plot_path, dpi=200)
    plt.close()

    return {
        "standard_final_energy": float(res_std["energy"][-1]),
        "standard_peak_enstrophy": float(np.max(res_std["enstrophy"])),
        "dualscale_final_energy": float(res_ds["energy"][-1]),
        "dualscale_peak_enstrophy": float(np.max(res_ds["enstrophy"])),
        "plot": str(plot_path.relative_to(output_dir.parent)),
    }


def run_taylor_green_benchmark(output_dir: Path) -> dict:
    """Benchmark 2D pseudo-spectral Taylor-Green vortex decay."""
    print("Running Taylor-Green 2D Pseudo-Spectral Benchmark...")
    solver = PseudoSpectralNavierStokes2D(n_grid=64, nu=1e-3, alpha_prime=0.01)
    u0_hat = solver.initialize_taylor_green()
    
    res = solver.solve(t_span=(0.0, 1.0), u_hat0=u0_hat, dt=0.005)
    
    # Save figure
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(res["times"], res["energy"], label="Dual-Scale NS (N=64, ν=1e-3)", color="#3498db", lw=2)
    ax.set_xlabel("Time t")
    ax.set_ylabel("Kinetic Energy E(t)")
    ax.set_title("2D Taylor-Green Vortex Energy Dissipation")
    ax.grid(True, alpha=0.3)
    ax.legend()

    plt.tight_layout()
    plot_path = output_dir / "taylor_green_benchmark.png"
    plt.savefig(plot_path, dpi=200)
    plt.close()

    return {
        "initial_energy": float(res["energy"][0]),
        "final_energy": float(res["energy"][-1]),
        "max_divergence": float(np.max(res["max_divergences"])),
        "plot": str(plot_path.relative_to(output_dir.parent)),
    }


def main() -> None:
    output_dir = Path("figures")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    metrics = {
        "cascade_benchmark": run_cascade_benchmark(output_dir),
        "taylor_green_benchmark": run_taylor_green_benchmark(output_dir),
    }

    metrics_path = Path("data/benchmark_results.json")
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"✅ Benchmarks completed successfully. Summary saved to {metrics_path}")


if __name__ == "__main__":
    main()
