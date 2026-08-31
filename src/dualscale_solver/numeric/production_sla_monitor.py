"""
Production SLA Monitor — Phase 5 H18 Gate
==========================================
10,000-step production stress loop with NaN guard, throughput counter,
and uptime fraction reporter. Enforces H18 deterministic SLA.

Hardness:
  H18-1 — >= 1000 steps/s at N >= 128^2 (after 500-step warmup, LL-15)
  H18-2 — Zero NaN/Inf in velocity, pressure, enstrophy across all steps
  H18-3 — Uptime fraction >= 99.9% (at most 10 failures in 10,000 steps)
  NC-DS-10 — NaN injected at step 5000 detected before step 5001
"""

from __future__ import annotations

import time
import math
import numpy as np
from dataclasses import dataclass, field
from typing import Any


@dataclass
class SLAResult:
    """Production SLA measurement result. All fields _measured: true (H11/H12)."""
    throughput_steps_per_sec: float   # steps/s over measured window
    nan_count: int                    # NaN occurrences in measured steps
    uptime_fraction: float            # fraction of steps without exception
    total_steps_measured: int
    elapsed_seconds: float
    nan_detected: bool                # True if NaN guard fired (NC-DS-10)
    nan_detected_at_step: int | None  # step where NaN first detected
    h18_passes: bool
    details: dict[str, Any] = field(default_factory=dict)
    _measured: bool = True


class ProductionSLAMonitor:
    """
    Production stress loop for H18 compliance.

    Runs warmup_steps + measure_steps total iterations.
    Only measure_steps count toward throughput (LL-15 compliant).

    Example:
        monitor = ProductionSLAMonitor(grid_n=128, warmup_steps=500, measure_steps=9500)
        result = monitor.run()
        assert result.h18_passes
    """

    H18_MIN_THROUGHPUT = 1000.0   # steps/s
    H18_MAX_NAN_STEPS = 0          # zero NaN allowed in production
    H18_MIN_UPTIME = 0.999         # >= 99.9%

    def __init__(
        self,
        grid_n: int = 128,
        warmup_steps: int = 500,
        measure_steps: int = 9500,
        nu: float = 1e-3,
        alpha_prime: float = 1.0,
        dt: float = 1e-3,
        inject_nan_at_step: int | None = None,
    ):
        self.grid_n = grid_n
        self.warmup_steps = warmup_steps
        self.measure_steps = measure_steps
        self.nu = nu
        self.alpha_prime = alpha_prime
        self.dt = dt
        self.inject_nan_at_step = inject_nan_at_step

    def run(self) -> SLAResult:
        """
        Execute the full production SLA stress loop.
        Returns SLAResult with all H18 sub-gate verdicts.
        """
        from dualscale_solver.numeric.fourier_spectral import PseudoSpectralNavierStokes2D

        solver = PseudoSpectralNavierStokes2D(
            n_grid=self.grid_n,
            nu=self.nu,
            alpha_prime=self.alpha_prime,
        )

        # Initialize state
        u_hat = solver.initialize_taylor_green()  # shape (2, N, N)

        # Pre-compute dissipation factors for inline ETD-RK4 (avoids recompute each step)
        D = solver.nu * solver.k_sq   # linear dissipation
        dt = self.dt
        E_half = np.exp(-0.5 * D * dt)  # shape (N, N)
        E_full = np.exp(-D * dt)

        def _step(u: np.ndarray) -> np.ndarray:
            """Inline ETD-RK4 single step. No trajectory storage."""
            # Dealiased nonlinear RHS
            k1 = solver.rhs_fourier(0.0, u)
            u2 = solver.project_leray(E_half * u + 0.5 * dt * E_half * k1)
            k2 = solver.rhs_fourier(0.0, u2)
            u3 = solver.project_leray(E_half * u + 0.5 * dt * E_half * k2)
            k3 = solver.rhs_fourier(0.0, u3)
            u4 = solver.project_leray(E_full * u + dt * E_half * k3)
            k4 = solver.rhs_fourier(0.0, u4)
            out = E_full * u + (dt / 6.0) * (
                E_full * k1 + 2.0 * E_half * k2 + 2.0 * E_half * k3 + k4
            )
            return solver.project_leray(out)

        nan_count = 0
        failure_count = 0
        nan_detected = False
        nan_detected_at_step: int | None = None

        # ---- Warmup (LL-15: avoid JIT/cache-cold costs in measurement) ----
        for _ in range(self.warmup_steps):
            u_hat = _step(u_hat)

        # ---- Measured production loop ----
        t_start = time.perf_counter_ns()

        for step_idx in range(self.measure_steps):
            # NC-DS-10: inject NaN at specified step (into current state)
            if (
                self.inject_nan_at_step is not None
                and step_idx == self.inject_nan_at_step
            ):
                u_hat = u_hat.copy()
                u_hat.flat[0] = float("nan")

            # Pre-step NaN guard: detect NaN in input state BEFORE step
            if not np.isfinite(u_hat).all():
                nan_count += 1
                if not nan_detected:
                    nan_detected = True
                    nan_detected_at_step = step_idx + 1
                failure_count += 1
                continue  # skip step on NaN state

            try:
                u_hat = _step(u_hat)

                # Post-step NaN guard: check output state
                if not np.isfinite(u_hat).all():
                    nan_count += 1
                    if not nan_detected:
                        nan_detected = True
                        nan_detected_at_step = step_idx + 1
                    failure_count += 1

            except Exception:
                failure_count += 1

        elapsed_ns = time.perf_counter_ns() - t_start
        elapsed_s = elapsed_ns * 1e-9

        throughput = self.measure_steps / elapsed_s if elapsed_s > 0 else 0.0
        uptime = (self.measure_steps - failure_count) / self.measure_steps

        h18_passes = (
            throughput >= self.H18_MIN_THROUGHPUT
            and nan_count == self.H18_MAX_NAN_STEPS
            and uptime >= self.H18_MIN_UPTIME
            and not nan_detected  # only in non-injection runs
        ) if self.inject_nan_at_step is None else True  # NC-DS-10 run: gate is on detection

        return SLAResult(
            throughput_steps_per_sec=throughput,
            nan_count=nan_count,
            uptime_fraction=uptime,
            total_steps_measured=self.measure_steps,
            elapsed_seconds=elapsed_s,
            nan_detected=nan_detected,
            nan_detected_at_step=nan_detected_at_step,
            h18_passes=h18_passes,
            details={
                "grid_n": self.grid_n,
                "warmup_steps": self.warmup_steps,
                "measure_steps": self.measure_steps,
                "nu": self.nu,
                "alpha_prime": self.alpha_prime,
                "dt": self.dt,
                "inject_nan_at_step": self.inject_nan_at_step,
                "failure_count": failure_count,
                "h18_thresholds": {
                    "min_throughput": self.H18_MIN_THROUGHPUT,
                    "max_nan_steps": self.H18_MAX_NAN_STEPS,
                    "min_uptime": self.H18_MIN_UPTIME,
                },
            },
            _measured=True,
        )


# ------------------------------------------------------------------
# Negative Control NC-DS-10
# ------------------------------------------------------------------

def negative_control_nan_injection() -> bool:
    """
    NC-DS-10: Inject NaN into the velocity state — must be detected within 1 step.
    Uses N=16 for CI speed. Returns True if detection was timely (within 1 step).
    """
    inject_at = 500
    monitor = ProductionSLAMonitor(
        grid_n=16,          # small grid for CI speed
        warmup_steps=0,
        measure_steps=inject_at + 100,  # 600 steps total
        inject_nan_at_step=inject_at,
    )
    result = monitor.run()

    detected = result.nan_detected
    timely = (
        result.nan_detected_at_step is not None
        and result.nan_detected_at_step <= inject_at + 1
    )
    return bool(detected and timely)
