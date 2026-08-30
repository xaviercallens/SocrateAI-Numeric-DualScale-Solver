"""
SocrateAI Numeric Dual-Scale Solver
====================================
High-performance numerical PDE solvers, exact rational invariant checkers,
and verification certificate generators for dual-scale regularized fluid dynamics.
"""

__version__ = "0.1.0"
__author__ = "Xavier Callens"

from dualscale_solver.exact.t_duality import (
    RationalDualScale,
    verify_t_duality_symmetry,
    verify_singularity_avoidance,
)
from dualscale_solver.numeric.dyadic_cascade import DyadicShellSolver
from dualscale_solver.numeric.fourier_spectral import PseudoSpectralNavierStokes2D
from dualscale_solver.numeric.rk4_integrator import rk4_step, solve_ivp_rk4

__all__ = [
    "RationalDualScale",
    "verify_t_duality_symmetry",
    "verify_singularity_avoidance",
    "DyadicShellSolver",
    "PseudoSpectralNavierStokes2D",
    "rk4_step",
    "solve_ivp_rk4",
]
