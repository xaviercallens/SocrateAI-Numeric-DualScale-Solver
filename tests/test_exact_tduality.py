"""
Unit Tests for Exact Rational T-Duality and Dual-Scale Invariants (Tier B).
"""

from fractions import Fraction
import pytest
from dualscale_solver.exact.t_duality import (
    RationalDualScale,
    verify_t_duality_symmetry,
    verify_singularity_avoidance,
    negative_control_symmetry_violation,
    negative_control_singularity_violation,
)


def test_rational_dual_scale_initialization():
    ds = RationalDualScale(Fraction(1, 4))
    assert ds.alpha_prime == Fraction(1, 4)

    with pytest.raises(ValueError):
        RationalDualScale(Fraction(0, 1))

    with pytest.raises(ValueError):
        RationalDualScale(Fraction(-1, 2))


def test_rational_dual_scale_r_eff():
    ds = RationalDualScale(Fraction(1, 4)) # sqrt(alpha') = 1/2

    # Macroscopic inertial regime: R = 1 >= 1/2 -> R_eff = 1
    assert ds.r_eff(Fraction(1, 1)) == Fraction(1, 1)
    assert ds.is_inertial(Fraction(1, 1)) is True
    assert ds.is_bounce(Fraction(1, 1)) is False

    # Bounce regime: R = 1/8 < 1/2 -> R_eff = (1/4) / (1/8) = 2
    assert ds.r_eff(Fraction(1, 8)) == Fraction(2, 1)
    assert ds.is_bounce(Fraction(1, 8)) is True
    assert ds.is_inertial(Fraction(1, 8)) is False

    # Exact crossover point: R = 1/2 -> R_eff = 1/2
    assert ds.r_eff(Fraction(1, 2)) == Fraction(1, 2)


def test_t_duality_symmetry_positive():
    alpha_prime = Fraction(9, 16)
    sample_radii = [
        Fraction(1, 100),
        Fraction(1, 3),
        Fraction(3, 4), # sqrt(9/16)
        Fraction(2, 1),
        Fraction(50, 1),
    ]
    res = verify_t_duality_symmetry(alpha_prime, sample_radii)
    assert res["status"] == "PASSED"
    assert res["samples_tested"] == len(sample_radii)


def test_singularity_avoidance_positive():
    alpha_prime = Fraction(1, 16)
    sample_radii = [Fraction(1, 10000), Fraction(1, 10), Fraction(1, 4), Fraction(10, 1)]
    res = verify_singularity_avoidance(alpha_prime, sample_radii)
    assert res["status"] == "PASSED"


def test_negative_control_nc_ds_01():
    """Negative control: Singularity penetration in unregularized scale."""
    assert negative_control_singularity_violation() is True


def test_negative_control_nc_ds_02():
    """Negative control: Asymmetric perturbation fails T-duality."""
    assert negative_control_symmetry_violation() is True


def test_rational_cascade_trajectory():
    ds = RationalDualScale(Fraction(1, 4))
    traj = ds.simulate_rational_cascade(
        r0=Fraction(1, 1),
        contraction=Fraction(1, 2),
        steps=4,
    )
    assert len(traj) == 5
    # step 0: r=1, r_eff=1
    assert traj[0] == (0, Fraction(1, 1), Fraction(1, 1))
    # step 1: r=1/2, r_eff=1/2
    assert traj[1] == (1, Fraction(1, 2), Fraction(1, 2))
    # step 2: r=1/4, r_eff=1
    assert traj[2] == (2, Fraction(1, 4), Fraction(1, 1))
    # step 3: r=1/8, r_eff=2
    assert traj[3] == (3, Fraction(1, 8), Fraction(2, 1))
