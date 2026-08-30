"""
Dyadic Shell Model Solver with Dual-Scale Regularization (Katz-Pavlović Model).
"""

from typing import Tuple, Dict, Any, Optional
import numpy as np
from dualscale_solver.numeric.rk4_integrator import solve_ivp_rk4


class DyadicShellSolver:
    """
    Simulates the Katz-Pavlović dyadic shell model of turbulence:
    du_n/dt = k_n ( u_{n-1}^2 - lambda * u_n * u_{n+1} ) - D(n) * u_n + f_n
    
    where:
      - Standard dissipation: D(n) = nu * k_n^2
      - Dual-Scale regularized dissipation: D(n) = nu * k_n^2 * max(1.0, alpha_prime * k_n^2)
    """

    def __init__(
        self,
        n_shells: int = 24,
        k0: float = 1.0,
        inter_shell_ratio: float = 2.0,
        nu: float = 1e-4,
        alpha_prime: Optional[float] = None,
        forcing_shell: int = 0,
        forcing_amp: float = 0.0,
    ):
        self.n_shells = n_shells
        self.k0 = k0
        self.inter_shell_ratio = inter_shell_ratio
        self.nu = nu
        self.alpha_prime = alpha_prime
        self.forcing_shell = forcing_shell
        self.forcing_amp = forcing_amp

        # Shell wavenumbers k_n = k0 * lambda^n
        self.k = self.k0 * (self.inter_shell_ratio ** np.arange(self.n_shells))

    def non_linear_rhs(self, t: float, u: np.ndarray) -> np.ndarray:
        """Compute non-linear advection and forcing: N(u) + f."""
        nu_term = np.zeros_like(u)
        for n in range(self.n_shells):
            u_prev = u[n - 1] if n > 0 else 0.0
            u_curr = u[n]
            u_next = u[n + 1] if n < self.n_shells - 1 else 0.0
            nu_term[n] = self.k[n] * (u_prev**2 - self.inter_shell_ratio * u_curr * u_next)

        if self.forcing_amp > 0 and 0 <= self.forcing_shell < self.n_shells:
            nu_term[self.forcing_shell] += self.forcing_amp

        return nu_term

    def dissipation_rates(self) -> np.ndarray:
        """Compute linear damping coefficients D_n >= 0 for all shells."""
        if self.alpha_prime is not None and self.alpha_prime > 0:
            return self.nu * (self.k ** 2) * np.maximum(1.0, self.alpha_prime * (self.k ** 2))
        return self.nu * (self.k ** 2)

    def energy(self, u: np.ndarray) -> float:
        """Total kinetic energy: E = 0.5 * sum_n u_n^2."""
        return 0.5 * float(np.sum(u**2))

    def enstrophy(self, u: np.ndarray) -> float:
        """Total enstrophy: Omega = 0.5 * sum_n k_n^2 * u_n^2."""
        return 0.5 * float(np.sum((self.k**2) * (u**2)))

    def solve(
        self,
        t_span: Tuple[float, float],
        u0: np.ndarray,
        dt: float,
    ) -> Dict[str, Any]:
        """
        Integrate dyadic shell model over t_span using an integrating factor RK4 scheme,
        which handles stiff linear dissipation exactly and unconditionally stably.
        """
        t_start, t_end = t_span
        n_steps = max(1, int(np.ceil((t_end - t_start) / dt)))
        actual_dt = (t_end - t_start) / n_steps
        
        times = np.linspace(t_start, t_end, n_steps + 1)
        traj = [u0.copy()]
        
        curr_u = u0.copy()
        D = self.dissipation_rates()
        E_half = np.exp(-0.5 * D * actual_dt)
        E_full = np.exp(-D * actual_dt)

        for i in range(n_steps):
            t = times[i]
            
            # Integrating factor RK4 step
            k1 = self.non_linear_rhs(t, curr_u)
            
            u2 = E_half * curr_u + 0.5 * actual_dt * E_half * k1
            k2 = self.non_linear_rhs(t + 0.5 * actual_dt, u2)
            
            u3 = E_half * curr_u + 0.5 * actual_dt * k2
            k3 = self.non_linear_rhs(t + 0.5 * actual_dt, u3)
            
            u4 = E_full * curr_u + actual_dt * E_half * k3
            k4 = self.non_linear_rhs(t + actual_dt, u4)
            
            curr_u = E_full * curr_u + (actual_dt / 6.0) * (
                E_full * k1 + 2.0 * E_half * k2 + 2.0 * E_half * k3 + k4
            )
            traj.append(curr_u.copy())

        energies = np.array([self.energy(state) for state in traj])
        enstrophies = np.array([self.enstrophy(state) for state in traj])
        
        return {
            "times": times,
            "trajectory": np.array(traj),
            "energy": energies,
            "enstrophy": enstrophies,
            "k": self.k,
            "alpha_prime": self.alpha_prime,
            "nu": self.nu,
        }
