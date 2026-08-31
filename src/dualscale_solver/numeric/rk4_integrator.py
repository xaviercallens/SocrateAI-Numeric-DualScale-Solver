"""
High-Precision Runge-Kutta (RK4) Time Integration for Multiscale PDE Systems.

W2 Fix (2026-08-30): Leray projection now applied ONLY to the final combined step
(y_next), not to intermediate RK4 stages. Projecting intermediate stages introduces
order-reduction artefacts and a non-standard constraint enforcement scheme.

The correct approach (Chorin-type projection):
  - Evolve the full RK4 step without projection.
  - Project the result once at the end.
  - The RHS function (rhs_fourier) already contains Leray projection internally,
    so intermediate states are approximately solenoidal via the dynamics.
"""

from typing import Callable, Tuple, List, Optional
import numpy as np


def rk4_step(
    f: Callable[[float, np.ndarray], np.ndarray],
    t: float,
    y: np.ndarray,
    dt: float,
    projector: Optional[Callable[[np.ndarray], np.ndarray]] = None,
) -> np.ndarray:
    """
    Single classical 4th-order Runge-Kutta step with final-step projection.

    W2 Fix: Leray projection is applied ONLY to y_next (the final combined step),
    NOT to intermediate stages y_k2, y_k3, y_k4. This preserves 4th-order accuracy.
    """
    k1 = f(t, y)

    y_k2 = y + 0.5 * dt * k1          # W2 Fix: no intermediate projection
    k2 = f(t + 0.5 * dt, y_k2)

    y_k3 = y + 0.5 * dt * k2          # W2 Fix: no intermediate projection
    k3 = f(t + 0.5 * dt, y_k3)

    y_k4 = y + dt * k3                 # W2 Fix: no intermediate projection
    k4 = f(t + dt, y_k4)

    y_next = y + (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
    if projector is not None:
        y_next = projector(y_next)     # Project only the final combined step

    return y_next


def solve_ivp_rk4(
    f: Callable[[float, np.ndarray], np.ndarray],
    t_span: Tuple[float, float],
    y0: np.ndarray,
    dt: float,
    projector: Optional[Callable[[np.ndarray], np.ndarray]] = None,
    callback: Optional[Callable[[float, np.ndarray], None]] = None,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Integrate an initial value problem using RK4 from t_span[0] to t_span[1].

    Args:
        f: RHS function f(t, y) -> dy/dt.
        t_span: (t_start, t_end).
        y0: Initial state.
        dt: Time step (actual dt may be adjusted to hit t_end exactly).
        projector: Optional constraint projector applied to y_next only (W2 Fix).
        callback: Optional function called as callback(t, y) at each step.
                  Use this to record per-step diagnostics (H6: divergence time-series).

    Returns:
        times: 1D array of time stamps.
        trajectory: Array of state history of shape (n_steps+1, *y0.shape).
    """
    t_start, t_end = t_span
    n_steps = max(1, int(np.ceil((t_end - t_start) / dt)))
    actual_dt = (t_end - t_start) / n_steps

    times = np.linspace(t_start, t_end, n_steps + 1)
    trajectory = [y0.copy()]

    curr_y = y0.copy()
    if projector is not None:
        curr_y = projector(curr_y)

    for i in range(n_steps):
        t = times[i]
        curr_y = rk4_step(f, t, curr_y, actual_dt, projector=projector)
        trajectory.append(curr_y.copy())
        if callback is not None:
            callback(times[i + 1], curr_y)

    return times, np.array(trajectory)
