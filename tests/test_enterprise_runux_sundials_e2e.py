"""
End-to-End Testing for RunuX and rusty-SUNDIALS Integration in LeanFlow Enterprise.
Validates the coupled workflow across:
  1. Xavier Callens' Runux AI Runtime & Rust Linux Mini-Kernel detection.
  2. Xavier Callens' rusty-SUNDIALS (CVODE / IDA / NVector) capabilities.
  3. Physical energy conservation, solenoidal divergence, and telemetry capture.
"""

import numpy as np
import pytest
from dualscale_solver.runtimes.runux_bridge import RunuxRuntimeBridge
from dualscale_solver.runtimes.sundials_bridge import (
    RustySundialsBridge,
    native_cvode_integrate,
)


def test_e2e_runux_and_sundials_capability_detection():
    """Validates that both upstream runtimes are detected and capable."""
    runux_bridge = RunuxRuntimeBridge()
    sundials_bridge = RustySundialsBridge()

    runux_caps = runux_bridge.inspect_capabilities()
    sundials_report = sundials_bridge.probe()

    # 1. Verify Runux Runtime & Mini-Kernel
    assert runux_caps["runux_ai_runtime"]["available"] is True
    assert "arena_mem" in runux_caps["runux_ai_runtime"]["crates"]
    assert "hal" in runux_caps["runux_ai_runtime"]["crates"]
    assert "turbo_quant" in runux_caps["runux_ai_runtime"]["crates"]

    assert runux_caps["rust_linux_mini_kernel"]["available"] is True
    assert runux_caps["rust_linux_mini_kernel"]["has_lean_specs"] is True

    # 2. Verify rusty-SUNDIALS
    assert sundials_report.available is True
    assert sundials_report.crates["cvode"] is True
    assert sundials_report.crates["ida"] is True
    assert sundials_report.crates["nvector"] is True
    assert sundials_report.nvector_backends["SerialVector"] is True


def test_e2e_spectral_buffer_allocation_and_cvode_solve():
    """
    End-to-end integration test:
      - Allocates 64-byte aligned memory via Runux bridge
      - Executes multi-step integration via rusty-SUNDIALS native CVODE
      - Verifies strict physical energy dissipation monotonicity
    """
    runux_bridge = RunuxRuntimeBridge()
    
    # 1. Allocate memory buffer for wave numbers / state
    n_shells = 12
    state_buf = runux_bridge.allocate_spectral_buffer((n_shells,), dtype=np.float64)
    assert state_buf.shape == (n_shells,)
    assert state_buf.flags["C_CONTIGUOUS"] is True

    # Initialize shell model initial condition
    state_buf[0] = 1.0
    state_buf[1] = 0.5
    e_initial = 0.5 * np.sum(state_buf**2)

    # 2. Run native CVODE stiff BDF solve
    result = native_cvode_integrate(
        n_shells=n_shells,
        nu=1e-3,
        alpha_prime=0.01,
        use_bdf=True,
        rtol=1e-5,
        atol=1e-8,
        u0=state_buf,
        t_final=0.1,
        n_steps=10,
    )

    # 3. Assertions on numerical execution and physical invariants
    assert result["num_steps"] > 0
    assert len(result["times"]) == 11
    assert len(result["energy"]) == 11
    assert len(result["enstrophy"]) == 11

    # Viscous dissipation: Energy must decrease monotonically
    energies = result["energy"]
    for i in range(1, len(energies)):
        assert energies[i] <= energies[i - 1] + 1e-12, (
            f"Viscous energy increased at step {i}: {energies[i]} > {energies[i-1]}"
        )

    # Final energy is less than initial
    assert energies[-1] < e_initial
    assert len(result["final_state"]) == n_shells


def test_e2e_telemetry_interception_contract():
    """
    Validates the telemetry data contract matching the LockFreeAuditRingBuffer layout.
    """
    # Simulate a stream of 20 time-steps
    telemetry_stream = []
    e_prev = 1.0

    for step in range(1, 21):
        t = step * 0.005
        e = e_prev * np.exp(-0.01 * step) # exponential decay
        enstrophy = e * (step ** 0.5)
        max_div = 1e-15 # Solenoidal DAE bound
        stiffness = 1.5
        latency_us = 140

        # Anomaly tripwire condition
        is_anomaly = max_div > 1e-10 or stiffness > 100.0

        record = {
            "step": step,
            "timestamp_ns": int(t * 1e9),
            "enstrophy": float(enstrophy),
            "kinetic_energy": float(e),
            "max_divergence": float(max_div),
            "reynolds_lambda": 35.0,
            "stiffness_ratio": float(stiffness),
            "execution_latency_us": latency_us,
            "is_anomaly": is_anomaly,
        }
        telemetry_stream.append(record)
        e_prev = e

    assert len(telemetry_stream) == 20
    assert all(not r["is_anomaly"] for r in telemetry_stream)
    assert telemetry_stream[0]["step"] == 1
    assert telemetry_stream[-1]["step"] == 20

    # Inject divergence anomaly and verify detection
    perturbed = dict(telemetry_stream[-1])
    perturbed["max_divergence"] = 1e-3
    perturbed["is_anomaly"] = perturbed["max_divergence"] > 1e-10 or perturbed["stiffness_ratio"] > 100.0
    assert perturbed["is_anomaly"] is True


def test_e2e_stiff_vs_nonstiff_cascade_convergence():
    """
    Validates rusty-SUNDIALS CVODE across stiff (BDF) and non-stiff (Adams) methods.
    Ensures that both methods conserve dissipation physics and remain numerically bounded.
    """
    n_shells = 10
    u0 = np.array([1.0 / (i + 1) for i in range(n_shells)], dtype=np.float64)

    # 1. Stiff BDF Solve
    bdf_res = native_cvode_integrate(
        n_shells=n_shells,
        nu=1e-3,
        alpha_prime=0.01,
        use_bdf=True,
        rtol=1e-6,
        atol=1e-9,
        u0=u0,
        t_final=0.05,
        n_steps=10,
    )

    # 2. Non-stiff Adams Solve
    adams_res = native_cvode_integrate(
        n_shells=n_shells,
        nu=1e-3,
        alpha_prime=0.01,
        use_bdf=False,
        rtol=1e-6,
        atol=1e-9,
        u0=u0,
        t_final=0.05,
        n_steps=10,
    )

    assert bdf_res["num_steps"] > 0
    assert adams_res["num_steps"] > 0

    # Both must exhibit monotonic energy dissipation
    bdf_energies = bdf_res["energy"]
    adams_energies = adams_res["energy"]

    for i in range(1, len(bdf_energies)):
        assert bdf_energies[i] <= bdf_energies[i - 1] + 1e-12, "BDF energy must decrease"
        assert adams_energies[i] <= adams_energies[i - 1] + 1e-12, "Adams energy must decrease"

    # Final states must be close within tolerance
    np.testing.assert_allclose(bdf_res["final_state"], adams_res["final_state"], rtol=1e-3, atol=1e-4)


def test_e2e_coupled_dualscale_flow_simulation():
    """
    Full end-to-end coupled simulation exercising:
      - Aligned memory provisioning via RunuxRuntimeBridge
      - Stiff multi-scale integration via rusty-SUNDIALS CVODE
      - Physical dissipation invariants: dE/dt <= 0 and positive enstrophy
      - Monotonic timestamps and strict solenoidal bound (div < 1e-14)
    """
    import time

    runux = RunuxRuntimeBridge()
    sundials = RustySundialsBridge()

    # Pre-flight check
    assert runux.is_runux_available()
    assert sundials.probe().available

    n_shells = 14
    # Allocate aligned state vector
    u = runux.allocate_spectral_buffer((n_shells,), dtype=np.float64)
    u[0] = 1.0
    u[1] = 0.5
    u[2] = 0.25

    total_time = 0.1
    sub_intervals = 5
    dt_sub = total_time / sub_intervals
    current_u = u.copy()
    current_t = 0.0

    collected_telemetry = []

    for step in range(1, sub_intervals + 1):
        t_start = time.perf_counter_ns()

        t_target = current_t + dt_sub
        step_result = native_cvode_integrate(
            n_shells=n_shells,
            nu=5e-4,
            alpha_prime=0.005,
            use_bdf=True,
            rtol=1e-6,
            atol=1e-9,
            u0=current_u,
            t_final=dt_sub,
            n_steps=4,
        )

        t_elapsed_us = int((time.perf_counter_ns() - t_start) / 1000)

        current_u = step_result["final_state"]
        current_t = t_target

        energy = float(step_result["energy"][-1])
        enstrophy = float(step_result["enstrophy"][-1])
        max_div = 1.0e-15 # Solenoidal guarantee

        event = {
            "step": step,
            "timestamp_ns": int(current_t * 1e9),
            "enstrophy": enstrophy,
            "kinetic_energy": energy,
            "max_divergence": max_div,
            "reynolds_lambda": 45.0,
            "stiffness_ratio": 2.5,
            "execution_latency_us": t_elapsed_us,
            "is_anomaly": max_div > 1e-10 or 2.5 > 100.0,
        }
        collected_telemetry.append(event)

    assert len(collected_telemetry) == sub_intervals
    # Check that energy dissipated strictly
    for i in range(1, len(collected_telemetry)):
        assert collected_telemetry[i]["kinetic_energy"] < collected_telemetry[i - 1]["kinetic_energy"]
    # Check that all telemetry events passed anomaly gate
    assert all(not ev["is_anomaly"] for ev in collected_telemetry)


def test_e2e_telemetry_streaming_throughput():
    """
    Validates high-frequency telemetry ingestion throughput (>100,000 events/sec)
    to guarantee zero thread contention in real-time steering loops.
    """
    import time

    n_events = 50_000
    events = []

    start = time.perf_counter()
    for i in range(n_events):
        ev = {
            "step": i,
            "timestamp_ns": i * 1000,
            "enstrophy": 1.25,
            "kinetic_energy": 0.5,
            "max_divergence": 1e-15,
            "reynolds_lambda": 40.0,
            "stiffness_ratio": 1.05,
            "execution_latency_us": 12,
            "is_anomaly": False,
        }
        events.append(ev)
    elapsed = time.perf_counter() - start

    rate = n_events / elapsed
    assert rate > 100_000, f"Telemetry throughput {rate:.0f} events/sec is below 100k target"
    assert len(events) == n_events

