"""
Exact Rational T-Duality and Dual-Scale Invariants (Tier B).

All computations in this module use exact rational arithmetic (fractions.Fraction)
and exact integers. Floats are strictly prohibited.
"""

from fractions import Fraction
from typing import List, Tuple, Dict, Any


class RationalDualScale:
    """
    Exact rational representation of the Dual-Scale metric and scale map:
    R_eff(R) = max(R, alpha_prime / R)
    """

    def __init__(self, alpha_prime: Fraction):
        if not isinstance(alpha_prime, Fraction):
            raise TypeError("alpha_prime must be a fractions.Fraction")
        if alpha_prime <= 0:
            raise ValueError("alpha_prime must be strictly positive")
        self.alpha_prime = alpha_prime

    def r_eff(self, r: Fraction) -> Fraction:
        """Compute R_eff(R) = max(R, alpha_prime / R) in exact rational arithmetic."""
        if not isinstance(r, Fraction):
            raise TypeError(f"r must be Fraction, got {type(r)}")
        if r <= 0:
            raise ValueError("Radius r must be strictly positive")
        t_dual = self.alpha_prime / r
        return max(r, t_dual)

    def is_inertial(self, r: Fraction) -> bool:
        """Check if scale r is in inertial continuum regime (r^2 >= alpha_prime)."""
        return (r * r) >= self.alpha_prime

    def is_bounce(self, r: Fraction) -> bool:
        """Check if scale r is in bounce regime (r^2 < alpha_prime)."""
        return (r * r) < self.alpha_prime

    def effective_enstrophy_bound(self) -> Fraction:
        """
        Exact upper bound for 1 / R_eff^2 = 1 / alpha_prime.
        For any R > 0, 1 / (R_eff(R))^2 <= 1 / alpha_prime.
        """
        return Fraction(1, 1) / self.alpha_prime

    def simulate_rational_cascade(self, r0: Fraction, contraction: Fraction, steps: int) -> List[Tuple[int, Fraction, Fraction]]:
        """
        Simulate an exact rational geometric collapse cascade:
        r_{n+1} = r_n * contraction
        Returns list of (step, r_n, r_eff_n).
        """
        if contraction <= 0 or contraction >= 1:
            raise ValueError("contraction ratio must be in (0, 1)")
        
        trajectory = []
        curr = r0
        for n in range(steps + 1):
            trajectory.append((n, curr, self.r_eff(curr)))
            curr = curr * contraction
        return trajectory


def verify_t_duality_symmetry(alpha_prime: Fraction, sample_radii: List[Fraction]) -> Dict[str, Any]:
    """
    Verify the exact identity R_eff(alpha' / R) == R_eff(R) for all sample radii.
    """
    ds = RationalDualScale(alpha_prime)
    verified = 0
    for r in sample_radii:
        r_eff_direct = ds.r_eff(r)
        r_dual = alpha_prime / r
        r_eff_dual = ds.r_eff(r_dual)
        if r_eff_direct != r_eff_dual:
            raise AssertionError(f"T-Duality symmetry failed for R={r}: {r_eff_direct} != {r_eff_dual}")
        verified += 1
    return {
        "status": "PASSED",
        "samples_tested": verified,
        "alpha_prime": str(alpha_prime),
    }


def verify_singularity_avoidance(alpha_prime: Fraction, sample_radii: List[Fraction]) -> Dict[str, Any]:
    """
    Verify that R_eff(R)^2 >= alpha_prime for all R in exact rational arithmetic.
    """
    ds = RationalDualScale(alpha_prime)
    verified = 0
    for r in sample_radii:
        r_eff = ds.r_eff(r)
        r_eff_sq = r_eff * r_eff
        if r_eff_sq < alpha_prime:
            raise AssertionError(f"Singularity avoidance violated for R={r}: R_eff^2={r_eff_sq} < alpha'={alpha_prime}")
        verified += 1
    return {
        "status": "PASSED",
        "samples_tested": verified,
        "min_bound_squared": str(alpha_prime),
    }


# Negative Controls
def negative_control_symmetry_violation() -> bool:
    """
    Negative control NC-DS-02:
    Demonstrates that an asymmetric perturbed scale function violates T-duality symmetry.
    Must return True (successfully caught).
    """
    alpha_prime = Fraction(1, 4)
    r = Fraction(1, 10)
    # Perturbed fake metric: R_fake = R + 1/100
    def fake_r_eff(rad: Fraction) -> Fraction:
        return max(rad + Fraction(1, 100), alpha_prime / rad)

    r_eff_dir = fake_r_eff(r)
    r_eff_dual = fake_r_eff(alpha_prime / r)
    if r_eff_dir == r_eff_dual:
        raise RuntimeError("Negative control failed: asymmetric metric falsely claimed symmetric!")
    return True


def negative_control_singularity_violation() -> bool:
    """
    Negative control NC-DS-01:
    Demonstrates that an unregularized linear scale can penetrate below sqrt(alpha_prime).
    Must return True (successfully caught).
    """
    alpha_prime = Fraction(1, 16) # sqrt(alpha') = 1/4
    r_small = Fraction(1, 64)
    # Unregularized metric R_eff = R
    if (r_small * r_small) < alpha_prime:
        return True # Successfully detected singularity penetration
    raise RuntimeError("Negative control failed: unregularized scale was not detected penetrating below sqrt(alpha')")
