"""
Exact Dyadic Cascade Invariants & Telescoping Bounds (Tier B).

Verifies energy conservation identities, dyadic triad telescoping, and exact
enstrophy upper bounds using Fraction arithmetic over Q.
"""

from fractions import Fraction
from typing import List, Tuple, Dict, Any


def dyadic_triad_energy_transfer_exact(
    u_prev: Fraction,
    u_curr: Fraction,
    u_next: Fraction,
    k_curr: Fraction,
    inter_shell_ratio: Fraction = Fraction(2, 1),
) -> Fraction:
    """
    Compute single-shell inviscid non-linear rate of change:
    du_n/dt = k_n ( u_{n-1}^2 - lambda * u_n * u_{n+1} )
    """
    return k_curr * (u_prev * u_prev - inter_shell_ratio * u_curr * u_next)


def verify_telescoping_energy_conservation(
    u_amplitudes: List[Fraction],
    k_wavenumbers: List[Fraction],
    inter_shell_ratio: Fraction = Fraction(2, 1),
) -> Dict[str, Any]:
    """
    Verify exact inviscid energy conservation:
    dE/dt = sum_{n=0}^{N-1} u_n * (du_n/dt) == 0 (with appropriate boundary fluxes).
    """
    n_shells = len(u_amplitudes)
    if len(k_wavenumbers) != n_shells:
        raise ValueError("u_amplitudes and k_wavenumbers must have identical length")
    
    # Internal shell rates (zero boundary condition u_{-1} = 0, u_N = 0)
    dE_dt = Fraction(0, 1)
    for n in range(n_shells):
        u_prev = u_amplitudes[n - 1] if n > 0 else Fraction(0, 1)
        u_curr = u_amplitudes[n]
        u_next = u_amplitudes[n + 1] if n < n_shells - 1 else Fraction(0, 1)
        k_curr = k_wavenumbers[n]

        du_dt = dyadic_triad_energy_transfer_exact(u_prev, u_curr, u_next, k_curr, inter_shell_ratio)
        dE_dt += u_curr * du_dt

    # The boundary flux at the truncation edge: - k_{N-1} * lambda * u_{N-1}^2 * u_N = 0 since u_N=0
    return {
        "status": "PASSED" if dE_dt == 0 else "FAILED",
        "dE_dt": str(dE_dt),
        "is_conservative": (dE_dt == 0),
    }


def compute_exact_enstrophy(u_amplitudes: List[Fraction], k_wavenumbers: List[Fraction]) -> Fraction:
    """
    Compute total exact dyadic enstrophy:
    Omega = sum_n k_n^2 * u_n^2
    """
    omega = Fraction(0, 1)
    for u, k in zip(u_amplitudes, k_wavenumbers):
        omega += (k * k) * (u * u)
    return omega


def compute_exact_dualscale_enstrophy(
    u_amplitudes: List[Fraction],
    k_wavenumbers: List[Fraction],
    alpha_prime: Fraction,
) -> Fraction:
    """
    Compute dual-scale regularized enstrophy where effective wavenumber is bounded:
    kappa_n^2 = min(k_n^2, 1 / alpha_prime)
    """
    k_max_sq = Fraction(1, 1) / alpha_prime
    omega_reg = Fraction(0, 1)
    for u, k in zip(u_amplitudes, k_wavenumbers):
        k_sq = k * k
        kappa_sq = min(k_sq, k_max_sq)
        omega_reg += kappa_sq * (u * u)
    return omega_reg


# Negative Controls
def negative_control_broken_energy_conservation() -> bool:
    """
    Negative control NC-DS-04:
    Demonstrates that a non-antisymmetric triad coupling coefficient (e.g. lambda = 3 instead of 2)
    causes non-zero dE/dt in inviscid shell dynamics.
    Must return True (successfully caught energy leak).
    """
    u_amps = [Fraction(1, 1), Fraction(1, 2), Fraction(1, 4)]
    k_waves = [Fraction(1, 1), Fraction(2, 1), Fraction(4, 1)]
    # Broken coupling ratio lambda = 3
    result = verify_telescoping_energy_conservation(u_amps, k_waves, inter_shell_ratio=Fraction(3, 1))
    if result["is_conservative"]:
        raise RuntimeError("Negative control failed: broken triad coupling was falsely marked conservative!")
    return True
