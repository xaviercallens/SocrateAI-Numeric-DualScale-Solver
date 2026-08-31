#!/usr/bin/env python3
"""
Visualize JHTDB HIT Energy Spectrum (Phase III)
===============================================
Computes and plots the 1D energy spectrum from the JHTDB HIT dataset
(or its statistically consistent local fallback) and compares it with
the theoretical Kolmogorov -5/3 scaling.
"""

import sys
import os
from pathlib import Path

repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root / "src"))

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from dualscale_solver.numeric.jhtdb_client import JHTDBClient

def main():
    out_dir = repo_root / "data" / "output"
    fig_dir = repo_root / "figures"
    out_dir.mkdir(parents=True, exist_ok=True)
    fig_dir.mkdir(parents=True, exist_ok=True)

    print("Fetching/Generating JHTDB HIT Spectrum...")
    client = JHTDBClient(use_local_fallback=True, grid_n=256)
    result = client.compute_energy_spectrum()

    print(f"Kolmogorov Exponent: {result.kolmogorov_exponent:.4f} (R2={result.kolmogorov_r2:.4f})")
    print(f"Method used: {result.method}")

    # Plot
    fig, ax = plt.subplots(figsize=(8, 6))

    k = result.k_vals
    E_k = result.E_k

    # Filter out k=0 or E_k=0 for log-log plot
    mask = (k > 0) & (E_k > 0)
    k_plot = k[mask]
    E_plot = E_k[mask]

    ax.loglog(k_plot, E_plot, 'bo-', markersize=4, label='LeanFlow/JHTDB Spectrum E(k)')

    # Add theoretical -5/3 line in the inertial range (e.g. k=2 to k_max/2)
    k_inertial = k_plot[(k_plot >= 2) & (k_plot <= np.max(k_plot)//2)]
    if len(k_inertial) > 0:
        # Match magnitude at the start of inertial range
        A = E_plot[np.where(k_plot >= 2)[0][0]] / (k_inertial[0] ** (-5/3))
        E_kolmogorov = A * (k_inertial ** (-5/3))
        ax.loglog(k_inertial, E_kolmogorov, 'k--', linewidth=2, label=r'Kolmogorov $k^{-5/3}$ scaling')

    ax.set_xlabel('Wavenumber $k$', fontsize=12)
    ax.set_ylabel('Energy Spectrum $E(k)$', fontsize=12)
    ax.set_title('Isotropic Energy Spectrum (JHTDB HIT Validation)', fontsize=14, fontweight='bold')
    ax.grid(True, which='both', ls='--', alpha=0.5)
    ax.legend(fontsize=12)

    plot_path = fig_dir / "jhtdb_spectrum_validation.png"
    plt.tight_layout()
    plt.savefig(plot_path, dpi=300)
    print(f"[✓] Figure saved to {plot_path}")

if __name__ == "__main__":
    main()
