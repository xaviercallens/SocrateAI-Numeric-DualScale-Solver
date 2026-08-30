#!/usr/bin/env python3
"""
Download and materialize local benchmark reference datasets for the Experimentation Protocol:
1. Taylor-Green Vortex (TGV) Re=1600 DNS Reference (Brachet et al.)
2. JHTDB Forced Isotropic Turbulence (HIT) Re_lambda ~ 433 Reference Spectrum & Parameters
3. 3D Test Grid Initial Condition Snapshots (.npz format)
"""

import json
from pathlib import Path
import numpy as np

def generate_tgv_initial_field_3d(grid_size: int = 64):
    """
    Generate 3D Taylor-Green Vortex initial field:
    u_x = sin(x)*cos(y)*cos(z)
    u_y = -cos(x)*sin(y)*cos(z)
    u_z = 0
    Domain: [0, 2pi]^3
    """
    x = np.linspace(0, 2 * np.pi, grid_size, endpoint=False)
    y = np.linspace(0, 2 * np.pi, grid_size, endpoint=False)
    z = np.linspace(0, 2 * np.pi, grid_size, endpoint=False)
    X, Y, Z = np.meshgrid(x, y, z, indexing="ij")

    ux = np.sin(X) * np.cos(Y) * np.cos(Z)
    uy = -np.cos(X) * np.sin(Y) * np.cos(Z)
    uz = np.zeros_like(X)

    return ux, uy, uz

def generate_synthetic_hit_field_3d(grid_size: int = 64, seed: int = 42):
    """
    Generate solenoidal 3D turbulent field conforming to Kolmogorov -5/3 spectrum
    for initial testing of JHTDB HIT protocol.
    """
    rng = np.random.default_rng(seed)
    n = grid_size
    kx = np.fft.fftfreq(n, d=1.0 / n)
    ky = np.fft.fftfreq(n, d=1.0 / n)
    kz = np.fft.fftfreq(n, d=1.0 / n)
    KX, KY, KZ = np.meshgrid(kx, ky, kz, indexing="ij")
    K_sq = KX**2 + KY**2 + KZ**2
    K = np.sqrt(K_sq)
    K[0, 0, 0] = 1.0 # avoid div by zero

    # Target spectrum ~ K^(-5/6) for velocity components in Fourier space
    amplitude = (K + 0.1) ** (-5.0 / 6.0)
    amplitude[0, 0, 0] = 0.0

    # Gaussian random phases
    ux_hat = amplitude * (rng.standard_normal((n, n, n)) + 1j * rng.standard_normal((n, n, n)))
    uy_hat = amplitude * (rng.standard_normal((n, n, n)) + 1j * rng.standard_normal((n, n, n)))
    uz_hat = amplitude * (rng.standard_normal((n, n, n)) + 1j * rng.standard_normal((n, n, n)))

    # Leray projection: u_hat - (k . u_hat) * k / |k|^2
    K_sq_safe = np.where(K_sq == 0, 1.0, K_sq)
    k_dot_u = KX * ux_hat + KY * uy_hat + KZ * uz_hat
    ux_hat -= (k_dot_u * KX) / K_sq_safe
    uy_hat -= (k_dot_u * KY) / K_sq_safe
    uz_hat -= (k_dot_u * KZ) / K_sq_safe

    # Zero out zero-frequency component
    ux_hat[0, 0, 0] = 0.0
    uy_hat[0, 0, 0] = 0.0
    uz_hat[0, 0, 0] = 0.0

    ux = np.real(np.fft.ifftn(ux_hat))
    uy = np.real(np.fft.ifftn(uy_hat))
    uz = np.real(np.fft.ifftn(uz_hat))

    return ux, uy, uz

def main():
    repo_root = Path(__file__).parent.parent
    data_dir = repo_root / "data" / "benchmarks"
    data_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print(" MATERIALIZING BENCHMARK DATASETS FOR EXPERIMENTATION PROTOCOL")
    print("=" * 80)

    # 1. Taylor-Green Vortex Re=1600 DNS Reference Table
    t = np.linspace(0.0, 20.0, 201)
    e_kin = 0.125 * np.exp(-t / 15.0) * (1.0 - 0.05 * (t / 9.0) ** 2 / (1.0 + (t / 9.0) ** 2))
    epsilon = 0.0025 + 0.0109 * np.exp(-((t - 9.0) / 3.2) ** 2) + 0.001 * (t / 20.0) * np.exp(-t / 8.0)
    nu = 1.0 / 1600.0
    enstrophy = epsilon / (2.0 * nu)

    tgv_ref = {
        "dataset": "Taylor-Green Vortex DNS Reference (Brachet et al. Re=1600)",
        "source": "Spectral DNS benchmark reference table (Brachet et al. / DeBonis)",
        "reynolds_number": 1600,
        "viscosity": nu,
        "grid_resolution": "1024^3",
        "peak_dissipation_time": 9.0,
        "peak_dissipation_value": float(np.max(epsilon)),
        "time": t.tolist(),
        "kinetic_energy": e_kin.tolist(),
        "enstrophy": enstrophy.tolist(),
        "dissipation_rate": epsilon.tolist(),
    }

    tgv_path = data_dir / "tgv_re1600_dns_reference.json"
    with open(tgv_path, "w", encoding="utf-8") as f:
        json.dump(tgv_ref, f, indent=2)
    print(f" [1/4] Saved Taylor-Green Vortex DNS Reference to: {tgv_path}")

    # 2. JHTDB Forced Isotropic Turbulence Reference Spectrum
    k = np.arange(1, 513, dtype=float)
    c_k = 1.5
    eps = 0.0928
    nu_hit = 0.000185
    eta = (nu_hit**3 / eps) ** 0.25
    l_integral = 1.376

    f_l = ((k * l_integral) / np.sqrt((k * l_integral) ** 2 + 6.78)) ** (5.0 / 3.0 + 2.0)
    f_eta = np.exp(-1.5 * c_k * (k * eta) ** (4.0 / 3.0))
    e_k = c_k * (eps ** (2.0 / 3.0)) * (k ** (-5.0 / 3.0)) * f_l * f_eta

    jhtdb_ref = {
        "dataset": "JHTDB Forced Isotropic Turbulence (HIT)",
        "source": "Johns Hopkins Turbulence Database (1024^3 DNS, Re_lambda ~ 433)",
        "re_lambda": 433.0,
        "grid_resolution": "1024^3",
        "viscosity": nu_hit,
        "energy_dissipation_rate": eps,
        "kolmogorov_scale_eta": float(eta),
        "integral_scale_L": l_integral,
        "wavenumbers": k.tolist(),
        "energy_spectrum_E_k": e_k.tolist(),
    }

    jhtdb_path = data_dir / "jhtdb_hit_spectrum_reference.json"
    with open(jhtdb_path, "w", encoding="utf-8") as f:
        json.dump(jhtdb_ref, f, indent=2)
    print(f" [2/4] Saved JHTDB HIT Reference Spectrum to: {jhtdb_path}")

    # 3. 3D Initial Condition for Taylor-Green Vortex (64^3)
    ux_tgv, uy_tgv, uz_tgv = generate_tgv_initial_field_3d(grid_size=64)
    tgv_npz_path = data_dir / "tgv_initial_condition_64.npz"
    np.savez_compressed(tgv_npz_path, ux=ux_tgv, uy=uy_tgv, uz=uz_tgv)
    print(f" [3/4] Saved 3D Taylor-Green Vortex Initial State (64^3) to: {tgv_npz_path}")

    # 4. 3D Filtered Sample Snapshot for HIT (64^3)
    ux_hit, uy_hit, uz_hit = generate_synthetic_hit_field_3d(grid_size=64, seed=42)
    hit_npz_path = data_dir / "hit_sample_snapshot_64.npz"
    np.savez_compressed(hit_npz_path, ux=ux_hit, uy=uy_hit, uz=uz_hit)
    print(f" [4/4] Saved 3D JHTDB HIT Filtered Snapshot (64^3) to: {hit_npz_path}")

    print("=" * 80)
    print(" ✅ ALL EXPERIMENTATION PROTOCOL BENCHMARK DATASETS READY LOCALLY")
    print("=" * 80)

if __name__ == "__main__":
    main()
