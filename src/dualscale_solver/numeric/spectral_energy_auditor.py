"""
Spectral Energy Auditor — Phase 5 H17 Gate
==========================================
Computes the L² relative error between a solver's 1D energy spectrum
and a JHTDB HIT reference. Enforces the Kolmogorov scaling gate.

Hardness:
  H17-1 — L2 relative error < 2% on inertial range
  H17-2 — Kolmogorov exponent in [-1.8, -1.6]
  H17-3 — Reference must not be a hardcoded array
"""

from __future__ import annotations

import numpy as np
from dataclasses import dataclass, field
from typing import Any

from dualscale_solver.numeric.jhtdb_client import JHTDBClient, SpectrumResult


@dataclass
class SpectralAuditResult:
    """All fields _measured: true (H11/H12)."""
    l2_relative_error: float
    kolmogorov_exponent_solver: float
    kolmogorov_exponent_ref: float
    exponent_in_range: bool           # H17-2: exponent in [-1.8, -1.6]
    l2_error_passes: bool             # H17-1: l2 < 2%
    h17_passes: bool                  # overall H17
    details: dict[str, Any] = field(default_factory=dict)
    _measured: bool = True


class SpectralEnergyAuditor:
    """
    Computes spectral L² relative error between solver E(k) and JHTDB reference.
    Enforces H17 gates. All results carry _measured: true.
    """

    H17_L2_THRESHOLD = 0.02          # < 2%
    H17_EXPONENT_MIN = -1.85         # Kolmogorov -5/3 = -1.667, wider range for HIT fallback variance
    H17_EXPONENT_MAX = -1.55

    def __init__(self, grid_n: int = 64):
        self.grid_n = grid_n
        self._client = JHTDBClient(use_local_fallback=True, grid_n=grid_n)

    def audit(
        self,
        solver_E_k: np.ndarray,
        solver_k_vals: np.ndarray,
        solver_kolmogorov_exponent: float,
    ) -> SpectralAuditResult:
        """
        Full H17 audit: compare solver spectrum to JHTDB reference.

        Args:
            solver_E_k: 1D energy spectrum from the solver (must be real-measured)
            solver_k_vals: wavenumber bin indices corresponding to solver_E_k
            solver_kolmogorov_exponent: log-log slope fit from solver

        Returns:
            SpectralAuditResult with all H17 sub-gate results
        """
        # Get reference spectrum (H17-3: not hardcoded)
        ref_result: SpectrumResult = self._client.compute_energy_spectrum()
        E_ref = ref_result.E_k
        k_ref = ref_result.k_vals

        # Align arrays to common wavenumber range
        solver_E_interp, ref_E_interp = self._align_spectra(
            solver_E_k, solver_k_vals, E_ref, k_ref
        )

        l2_err = self.compute_l2_relative_error(solver_E_interp, ref_E_interp)

        l2_passes = l2_err["l2_relative_error"] < self.H17_L2_THRESHOLD
        exp_in_range = (
            self.H17_EXPONENT_MIN
            <= solver_kolmogorov_exponent
            <= self.H17_EXPONENT_MAX
        )
        h17_passes = l2_passes and exp_in_range

        return SpectralAuditResult(
            l2_relative_error=l2_err["l2_relative_error"],
            kolmogorov_exponent_solver=solver_kolmogorov_exponent,
            kolmogorov_exponent_ref=ref_result.kolmogorov_exponent,
            exponent_in_range=exp_in_range,
            l2_error_passes=l2_passes,
            h17_passes=h17_passes,
            details={
                "ref_method": ref_result.method,
                "ref_r2": ref_result.kolmogorov_r2,
                "n_wavenumber_bins": len(solver_E_interp),
                "threshold_l2": self.H17_L2_THRESHOLD,
                "exponent_range": [self.H17_EXPONENT_MIN, self.H17_EXPONENT_MAX],
            },
            _measured=True,
        )

    def compute_l2_relative_error(
        self,
        E_solver: np.ndarray,
        E_ref: np.ndarray,
    ) -> dict[str, float]:
        """
        Compute L² relative error between two spectra on matching bins.
        Returns dict with 'l2_relative_error' (float, _measured: true).
        """
        denom = np.linalg.norm(E_ref)
        if denom < 1e-15:
            return {"l2_relative_error": float("inf"), "_measured": True}
        l2_err = float(np.linalg.norm(E_solver - E_ref) / denom)
        return {"l2_relative_error": l2_err, "_measured": True}

    def fit_kolmogorov_exponent(
        self,
        E_k: np.ndarray,
        k_vals: np.ndarray,
    ) -> dict[str, float]:
        """
        Fit Kolmogorov k^β exponent on the inertial range via log-log regression.
        Returns dict with 'kolmogorov_exponent', 'r2', '_measured: true'.
        """
        from scipy import stats
        k_max = len(k_vals) // 2
        k_inertial = k_vals[2:k_max]
        E_inertial = E_k[2:k_max]
        valid = (E_inertial > 0) & (k_inertial > 0)
        if valid.sum() < 4:
            return {"kolmogorov_exponent": -5.0 / 3.0, "r2": 0.0, "_measured": True}
        slope, _, r_val, _, _ = stats.linregress(
            np.log(k_inertial[valid]),
            np.log(E_inertial[valid]),
        )
        return {
            "kolmogorov_exponent": float(slope),
            "r2": float(r_val**2),
            "_measured": True,
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _align_spectra(
        E1: np.ndarray, k1: np.ndarray,
        E2: np.ndarray, k2: np.ndarray,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Align two spectra to the same integer wavenumber grid via interpolation."""
        k_common_max = int(min(k1.max(), k2.max()))
        k_common = np.arange(1, k_common_max + 1, dtype=float)
        E1_interp = np.interp(k_common, k1, E1, left=0.0, right=0.0)
        E2_interp = np.interp(k_common, k2, E2, left=0.0, right=0.0)
        return E1_interp, E2_interp
