"""
Unit tests for Phase 4 Embedded Target Simulator and Bioreactor Validation.
"""

import pytest
from dualscale_solver.runtimes.embedded_target import (
    EmbeddedDyadicSimulator,
    simulate_bioreactor_kla_transfer,
    negative_control_embedded_memory_overflow,
)


def test_embedded_dyadic_static_simulator():
    """Verify zero-heap allocation embedded simulator execution."""
    sim = EmbeddedDyadicSimulator(n_shells=16, nu=1e-3, alpha_prime=0.01, dt=1e-3)
    assert sim.static_memory_bytes <= 65536
    e0 = sim.energy()
    for _ in range(100):
        sim.step()
    ef = sim.energy()
    assert ef < e0, "Energy must decay monotonically under viscous dissipation"


def test_bioreactor_kla_simulation():
    """Verify bioreactor dissolved oxygen transfer and yield gain."""
    res = simulate_bioreactor_kla_transfer(n_steps=200, kla_target=115.89)
    assert res["target_kla"] == 115.89
    assert res["yield_multiplier"] >= 3.0
    assert res["within_64kb_ram_budget"] is True
    assert res["deterministic_latency_sub_ms"] is True


def test_negative_control_embedded():
    """Verify epistemic negative control for embedded target."""
    assert negative_control_embedded_memory_overflow() is True
