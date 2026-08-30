"""
2D Pseudo-Spectral Navier-Stokes Solver with Exact Dealiasing and Leray Projection.
"""

from typing import Tuple, Dict, Any, Optional
import numpy as np
from dualscale_solver.numeric.rk4_integrator import solve_ivp_rk4


class PseudoSpectralNavierStokes2D:
    """
    2D Incompressible Navier-Stokes Solver in a periodic box [0, 2pi)^2.
    
    du/dt + (u . grad)u = -grad p + nu * Laplacian(u) + D_dual(u)
    div(u) = 0
    
    Features:
      - Orszag 2/3 dealiasing rule
      - Machine-precision Leray divergence-free projection: k . u_hat = 0
      - Dual-scale ultraviolet dissipation regularization
    """

    def __init__(
        self,
        n_grid: int = 64,
        nu: float = 1e-3,
        alpha_prime: Optional[float] = None,
    ):
        self.n = n_grid
        self.nu = nu
        self.alpha_prime = alpha_prime

        # 1D wavenumbers in [-N/2, N/2 - 1]
        kx_1d = np.fft.fftfreq(self.n, d=1.0 / self.n)
        ky_1d = np.fft.fftfreq(self.n, d=1.0 / self.n)
        self.kx, self.ky = np.meshgrid(kx_1d, ky_1d, indexing="ij")
        
        self.k_sq = self.kx**2 + self.ky**2
        self.k_sq[0, 0] = 1.0 # Avoid division by zero at k=(0,0)
        self.k_sq_inv = 1.0 / self.k_sq
        self.k_sq[0, 0] = 0.0
        self.k_sq_inv[0, 0] = 0.0

        # Orszag 2/3 dealiasing mask
        k_cutoff = (2.0 / 3.0) * (self.n / 2.0)
        self.dealias_mask = (np.abs(self.kx) < k_cutoff) & (np.abs(self.ky) < k_cutoff)

    def project_leray(self, u_hat: np.ndarray) -> np.ndarray:
        """
        Leray-Helmholtz projection:
        P(k) u_hat = u_hat - (k . u_hat) * k / |k|^2
        u_hat has shape (2, N, N) representing (u_hat_x, u_hat_y).
        """
        u_hat_proj = u_hat.copy()
        # Divergence in Fourier space: i * (kx * u_hat_x + ky * u_hat_y)
        k_dot_u = self.kx * u_hat[0] + self.ky * u_hat[1]
        
        u_hat_proj[0] -= k_dot_u * self.kx * self.k_sq_inv
        u_hat_proj[1] -= k_dot_u * self.ky * self.k_sq_inv
        
        # Zero-mean mode
        u_hat_proj[0, 0, 0] = 0.0
        u_hat_proj[1, 0, 0] = 0.0
        
        # Dealias
        u_hat_proj[0] *= self.dealias_mask
        u_hat_proj[1] *= self.dealias_mask
        
        return u_hat_proj

    def max_divergence(self, u_hat: np.ndarray) -> float:
        """Compute maximum absolute divergence in Fourier space."""
        div_hat = 1j * (self.kx * u_hat[0] + self.ky * u_hat[1])
        return float(np.max(np.abs(div_hat)))

    def rhs_fourier(self, t: float, u_hat: np.ndarray) -> np.ndarray:
        """
        Compute time derivative d(u_hat)/dt in Fourier space.
        """
        # 1. Transform velocity to physical space
        u_x = np.fft.ifft2(u_hat[0]).real
        u_y = np.fft.ifft2(u_hat[1]).real

        # 2. Compute spatial gradients in Fourier space and transform to physical space
        # du_x/dx, du_x/dy, du_y/dx, du_y/dy
        dux_dx = np.fft.ifft2(1j * self.kx * u_hat[0]).real
        dux_dy = np.fft.ifft2(1j * self.ky * u_hat[0]).real
        duy_dx = np.fft.ifft2(1j * self.kx * u_hat[1]).real
        duy_dy = np.fft.ifft2(1j * self.ky * u_hat[1]).real

        # 3. Non-linear advection in physical space: (u . grad)u
        adv_x = u_x * dux_dx + u_y * dux_dy
        adv_y = u_x * duy_dx + u_y * duy_dy

        # 4. Transform advection back to Fourier space
        adv_x_hat = np.fft.fft2(adv_x)
        adv_y_hat = np.fft.fft2(adv_y)

        # 5. Dissipation operator
        if self.alpha_prime is not None and self.alpha_prime > 0:
            diss_op = -self.nu * self.k_sq * (1.0 + self.alpha_prime * self.k_sq)
        else:
            diss_op = -self.nu * self.k_sq

        # 6. Unprojected RHS: -adv_hat + diss_op * u_hat
        rhs_x = -adv_x_hat + diss_op * u_hat[0]
        rhs_y = -adv_y_hat + diss_op * u_hat[1]

        rhs_hat = np.array([rhs_x, rhs_y])

        # 7. Apply Leray projection to eliminate pressure gradient and enforce div(du/dt) = 0
        return self.project_leray(rhs_hat)

    def energy(self, u_hat: np.ndarray) -> float:
        """Total kinetic energy: E = 0.5 * sum (|u_x|^2 + |u_y|^2) / N^4."""
        # By Parseval's theorem:
        return 0.5 * float(np.sum(np.abs(u_hat[0])**2 + np.abs(u_hat[1])**2)) / (self.n**4)

    def enstrophy(self, u_hat: np.ndarray) -> float:
        """Total enstrophy: Omega = 0.5 * sum (|omega|^2) / N^4."""
        vort_hat = 1j * (self.kx * u_hat[1] - self.ky * u_hat[0])
        return 0.5 * float(np.sum(np.abs(vort_hat)**2)) / (self.n**4)

    def initialize_taylor_green(self) -> np.ndarray:
        """
        Initialize standard 2D Taylor-Green vortex:
        u_x(x, y) = sin(x) * cos(y)
        u_y(x, y) = -cos(x) * sin(y)
        """
        x_1d = np.linspace(0, 2 * np.pi, self.n, endpoint=False)
        y_1d = np.linspace(0, 2 * np.pi, self.n, endpoint=False)
        x, y = np.meshgrid(x_1d, y_1d, indexing="ij")

        ux = np.sin(x) * np.cos(y)
        uy = -np.cos(x) * np.sin(y)

        ux_hat = np.fft.fft2(ux)
        uy_hat = np.fft.fft2(uy)

        u_hat0 = np.array([ux_hat, uy_hat], dtype=np.complex128)
        return self.project_leray(u_hat0)

    def solve(
        self,
        t_span: Tuple[float, float],
        u_hat0: np.ndarray,
        dt: float,
    ) -> Dict[str, Any]:
        """Solve 2D pseudo-spectral Navier-Stokes over t_span."""
        u_hat0_proj = self.project_leray(u_hat0)
        
        times, traj = solve_ivp_rk4(
            self.rhs_fourier,
            t_span,
            u_hat0_proj,
            dt,
            projector=self.project_leray,
        )
        
        energies = np.array([self.energy(state) for state in traj])
        enstrophies = np.array([self.enstrophy(state) for state in traj])
        max_divs = np.array([self.max_divergence(state) for state in traj])
        
        return {
            "times": times,
            "trajectory": traj,
            "energy": energies,
            "enstrophy": enstrophies,
            "max_divergences": max_divs,
            "nu": self.nu,
            "alpha_prime": self.alpha_prime,
            "n_grid": self.n,
        }
