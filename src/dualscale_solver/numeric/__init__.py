"""
Numerical PDE Solvers and Integrators for Dual-Scale Hydrodynamics (Tier C).
"""

from dualscale_solver.numeric.rk4_integrator import rk4_step, solve_ivp_rk4
from dualscale_solver.numeric.dyadic_cascade import DyadicShellSolver
from dualscale_solver.numeric.fourier_spectral import PseudoSpectralNavierStokes2D

__all__ = [
    "rk4_step",
    "solve_ivp_rk4",
    "DyadicShellSolver",
    "PseudoSpectralNavierStokes2D",
]
