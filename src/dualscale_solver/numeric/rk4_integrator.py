"""
High-Precision Runge-Kutta (RK4) Time Integration for Multiscale PDE Systems.
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
    Single classical 4th-order Runge-Kutta step with optional state projection
    (e.g., Leray divergence-free projection).
    """
    k1 = f(t, y)
    
    y_k2 = y + 0.5 * dt * k1
    if projector is not None:
        y_k2 = projector(y_k2)
    k2 = f(t + 0.5 * dt, y_k2)
    
    y_k3 = y + 0.5 * dt * k2
    if projector is not None:
        y_k3 = projector(y_k3)
    k3 = f(t + 0.5 * dt, y_k3)
    
    y_k4 = y + dt * k3
    if projector is not None:
        y_k4 = projector(y_k4)
    k4 = f(t + dt, y_k4)
    
    y_next = y + (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
    if projector is not None:
        y_next = projector(y_next)
    
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
    
    Returns:
        times: 1D array of time stamps
        trajectory: 2D array of state history of shape (n_steps, *y0.shape)
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
            callback(times[i+1], curr_y)
            
    return times, np.array(trajectory)
