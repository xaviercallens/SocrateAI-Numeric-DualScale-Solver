"""
Exact Rational Invariants & Verification Modules (Tier B).
"""

from dualscale_solver.exact.t_duality import (
    RationalDualScale,
    verify_t_duality_symmetry,
    verify_singularity_avoidance,
    negative_control_symmetry_violation,
    negative_control_singularity_violation,
)
from dualscale_solver.exact.cascade_invariants import (
    dyadic_triad_energy_transfer_exact,
    verify_telescoping_energy_conservation,
    compute_exact_enstrophy,
    compute_exact_dualscale_enstrophy,
    negative_control_broken_energy_conservation,
)

__all__ = [
    "RationalDualScale",
    "verify_t_duality_symmetry",
    "verify_singularity_avoidance",
    "negative_control_symmetry_violation",
    "negative_control_singularity_violation",
    "dyadic_triad_energy_transfer_exact",
    "verify_telescoping_energy_conservation",
    "compute_exact_enstrophy",
    "compute_exact_dualscale_enstrophy",
    "negative_control_broken_energy_conservation",
]
