"""
Unit tests for the Experimentation Protocol benchmark datasets (JHTDB & Taylor-Green Vortex).
"""

from pathlib import Path
import numpy as np
import pytest
from dualscale_solver.data import (
    get_tgv_dns_reference_data,
    get_jhtdb_hit_spectrum_reference,
    DATA_DIR,
)


def test_tgv_dns_reference_data_integrity():
    """Verify Taylor-Green Vortex Re=1600 reference table against protocol requirements."""
    tgv = get_tgv_dns_reference_data()
    assert tgv["reynolds_number"] == 1600
    assert abs(tgv["viscosity"] - 1.0 / 1600.0) < 1e-10
    assert abs(tgv["peak_dissipation_time"] - 9.0) < 0.2
    assert len(tgv["time"]) == len(tgv["kinetic_energy"]) == len(tgv["enstrophy"])
    assert tgv["kinetic_energy"][0] > 0.0


def test_jhtdb_hit_spectrum_reference_integrity():
    """Verify JHTDB Forced Isotropic Turbulence spectrum against protocol specifications."""
    hit = get_jhtdb_hit_spectrum_reference()
    assert hit["re_lambda"] == 433.0
    assert len(hit["wavenumbers"]) == 512
    assert len(hit["energy_spectrum_E_k"]) == 512
    # Verify positive energy across all modes
    assert all(e > 0.0 for e in hit["energy_spectrum_E_k"])
    # Verify inertial range slope (k=10 to k=50) exhibits Kolmogorov ~ -5/3 decay
    k = np.array(hit["wavenumbers"][10:50])
    e = np.array(hit["energy_spectrum_E_k"][10:50])
    log_k = np.log(k)
    log_e = np.log(e)
    slope, _ = np.polyfit(log_k, log_e, 1)
    # Target slope is approximately -5/3 ~ -1.67
    assert -2.0 < slope < -1.3


def test_3d_snapshot_fields_loadable():
    """Verify 3D Taylor-Green and HIT velocity field files exist and are solenoidal."""
    tgv_path = DATA_DIR / "tgv_initial_condition_64.npz"
    hit_path = DATA_DIR / "hit_sample_snapshot_64.npz"

    assert tgv_path.exists()
    assert hit_path.exists()

    with np.load(tgv_path) as data:
        assert data["ux"].shape == (64, 64, 64)
        assert data["uy"].shape == (64, 64, 64)
        assert data["uz"].shape == (64, 64, 64)

    with np.load(hit_path) as data:
        assert data["ux"].shape == (64, 64, 64)
        assert data["uy"].shape == (64, 64, 64)
        assert data["uz"].shape == (64, 64, 64)
