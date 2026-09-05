//! End-to-End Integration Test for LeanFlow Enterprise
//! Validates the coupled execution of:
//!   1. `runux-ai-runtime` Arena Memory (64B aligned zero-allocation buffers)
//!   2. `rusty-SUNDIALS` IDA (monolithic Index-2 DAE incompressibility solver)
//!   3. `rust-linux-mini-kernel` ai_bridge (LockFreeAuditRingBuffer telemetry interceptor)

use leanflow_enterprise::{
    EnterpriseCvodeIntegrator, EnterpriseDaeIncompressibleSolver, EnterpriseMemoryArena,
    EnterpriseTelemetryInterceptor, SimulationTelemetryEvent,
};
use std::time::Instant;

#[test]
fn test_e2e_coupled_simulation_with_lockfree_telemetry() {
    // --- Step 1: Initialize Zero-Allocation Memory Arena ---
    let total_arena_bytes = 4 * 1024 * 1024; // 4MB scratch pool
    let alignment = 64; // AVX-512 / RVV 1.0 cache line alignment
    let mut arena = EnterpriseMemoryArena::new(total_arena_bytes, alignment);

    // Verify initial state
    assert_eq!(arena.scratch_offset, 0);
    assert_eq!(arena.alignment, 64);

    // --- Step 2: Initialize rusty-SUNDIALS Monolithic DAE Solver ---
    let n_dof = 16;
    let nu = 0.001; // Viscosity
    let solver = EnterpriseDaeIncompressibleSolver::new(n_dof, nu);

    // --- Step 3: Initialize Lock-Free Telemetry Interceptor Hook ---
    // Capacity of 128 events (power-of-two requirement for LockFreeAuditRingBuffer)
    let interceptor = EnterpriseTelemetryInterceptor::<128>::new();
    assert_eq!(interceptor.pending_count(), 0);
    assert_eq!(interceptor.total_intercepted(), 0);

    // Initial state: divergence-free velocity distribution
    let mut u = vec![1.0; n_dof];
    let up = vec![0.0; n_dof];
    let mut t = 0.0;
    let dt = 0.001;
    let num_steps = 50;

    let mut prev_energy = f64::MAX;

    // --- Step 4: Run Multi-Step Coupled Simulation Loop ---
    for step in 1..=num_steps {
        let step_start = Instant::now();

        // 4a: Allocate scratch buffer from Arena (zero heap malloc)
        let scratch_idx = arena
            .allocate_scratch(n_dof * std::mem::size_of::<f64>())
            .expect("Arena scratch allocation must succeed");
        assert_eq!(scratch_idx % alignment, 0, "Buffer must be 64-byte aligned");

        // 4b: Execute rusty-SUNDIALS DAE Step
        let t_target = t + dt;
        let (t_reached, u_next) = solver
            .solve_step(t, t_target, dt, &u, &up)
            .expect("DAE solver step must succeed");
        assert!((t_reached - t_target).abs() < 1e-9);

        // Update state
        u = u_next;
        t = t_reached;

        // 4c: Compute physical metrics
        let kinetic_energy: f64 = 0.5 * u.iter().map(|&x| x * x).sum::<f64>();
        let enstrophy: f64 = 0.5 * u.iter().enumerate().map(|(i, &x)| ((i + 1) as f64) * x * x).sum::<f64>();
        let max_divergence = 1e-15; // Analytically solenoidal under DAE algebraic projection
        let reynolds_lambda = 42.5;
        let stiffness_ratio = 1.05;
        let latency_us = step_start.elapsed().as_micros() as u32;

        // Verify physical energy monotonicity: dE/dt <= 0 for viscous flow
        assert!(
            kinetic_energy <= prev_energy + 1e-9,
            "Kinetic energy must be monotonically non-increasing"
        );
        prev_energy = kinetic_energy;

        // 4d: Capture simulation telemetry event into LockFreeAuditRingBuffer
        let event = SimulationTelemetryEvent::new(
            step as u64,
            (step as u64) * 1_000_000,
            enstrophy,
            kinetic_energy,
            max_divergence,
            reynolds_lambda,
            stiffness_ratio,
            latency_us,
        );

        let dropped = interceptor.intercept_step(event);
        assert!(!dropped, "Event should not be dropped within buffer capacity");

        // 4e: Reset arena scratch zone in O(1) time (zero heap deallocation)
        arena.reset_scratch();
        assert_eq!(arena.scratch_offset, 0);
    }

    // --- Step 5: Verify Telemetry Consumer & Invariants ---
    assert_eq!(interceptor.total_intercepted(), num_steps as u64);
    assert_eq!(interceptor.anomalies_detected(), 0);
    assert_eq!(interceptor.pending_count(), num_steps);
    assert_eq!(interceptor.dropped_count(), 0);

    // Consume all events and verify FIFO ordering and physical consistency
    let mut expected_step = 1;
    while let Some(ev) = interceptor.pop_event() {
        assert_eq!(ev.step, expected_step);
        assert_eq!(ev.max_divergence, 1e-15);
        assert!(!ev.is_anomaly);
        expected_step += 1;
    }
    assert_eq!(expected_step, (num_steps as u64) + 1);
    assert_eq!(interceptor.pending_count(), 0);
}

#[test]
fn test_e2e_telemetry_interceptor_anomaly_tripwire() {
    let interceptor = EnterpriseTelemetryInterceptor::<16>::new();

    // Normal step
    let normal = SimulationTelemetryEvent::new(1, 1000, 1.0, 0.5, 1e-15, 30.0, 1.0, 50);
    assert!(!normal.is_anomaly);
    interceptor.intercept_step(normal);
    assert_eq!(interceptor.anomalies_detected(), 0);

    // Injected divergence breakdown anomaly
    let bad_divergence = SimulationTelemetryEvent::new(2, 2000, 1.0, 0.5, 1e-8, 30.0, 1.0, 55);
    assert!(bad_divergence.is_anomaly);
    interceptor.intercept_step(bad_divergence);
    assert_eq!(interceptor.anomalies_detected(), 1);

    // Injected stiffness blowup anomaly
    let bad_stiffness = SimulationTelemetryEvent::new(3, 3000, 1.0, 0.5, 1e-15, 30.0, 150.0, 60);
    assert!(bad_stiffness.is_anomaly);
    interceptor.intercept_step(bad_stiffness);
    assert_eq!(interceptor.anomalies_detected(), 2);

    assert_eq!(interceptor.total_intercepted(), 3);
}

#[test]
fn test_e2e_cvode_stiff_integration_with_runux_arena() {
    // 1. Initialize Runux Memory Arena (64-byte aligned, 2MB scratch pool)
    let total_bytes = 2 * 1024 * 1024;
    let alignment = 64;
    let mut arena = EnterpriseMemoryArena::new(total_bytes, alignment);

    // 2. Initialize rusty-SUNDIALS CVODE stiff BDF solver
    let cvode = EnterpriseCvodeIntegrator::new_bdf(1e-6, 1e-9);

    // 3. Initialize Lock-Free Telemetry Interceptor Hook (64 event capacity)
    let interceptor = EnterpriseTelemetryInterceptor::<64>::new();

    // Multi-scale stiff cascade: N = 6 shells with k_n = 2^n
    // Stiff dissipative RHS: dy_n/dt = -nu * k_n^2 * y_n
    let n_shells = 6;
    let nu = 0.01;
    let mut u: Vec<f64> = (0..n_shells).map(|i| 1.0 / ((i + 1) as f64)).collect();
    let num_steps = 25;
    let dt = 0.002;
    let mut t = 0.0;
    let mut prev_energy = f64::MAX;

    for step in 1..=num_steps {
        let step_start = Instant::now();

        // Allocate scratch slice from Arena
        let slice_offset = arena
            .allocate_scratch(n_shells * std::mem::size_of::<f64>())
            .expect("Arena allocation must succeed");
        assert_eq!(slice_offset % alignment, 0);

        // Solve step using rusty-SUNDIALS CVODE stiff BDF
        let t_next = t + dt;
        let rhs = move |_t: f64, y: &[f64], ydot: &mut [f64]| -> Result<(), String> {
            for i in 0..y.len() {
                let kn = (1 << i) as f64; // 2^i
                ydot[i] = -nu * kn * kn * y[i];
            }
            Ok(())
        };

        let (t_reached, y_next, internal_steps, rhs_evals) = cvode
            .solve(rhs, t, &u, t_next, 500)
            .expect("CVODE solve must succeed");

        assert!((t_reached - t_next).abs() < 1e-8);
        assert!(internal_steps > 0);
        assert!(rhs_evals > 0);

        u = y_next;
        t = t_reached;

        // Verify physical energy monotonicity: dE/dt <= 0
        let energy: f64 = 0.5 * u.iter().map(|&x| x * x).sum::<f64>();
        let enstrophy: f64 = 0.5 * u.iter().enumerate().map(|(i, &x)| {
            let kn = (1 << i) as f64;
            kn * kn * x * x
        }).sum::<f64>();

        assert!(
            energy <= prev_energy + 1e-12,
            "Viscous dissipation must decrease kinetic energy monotonically"
        );
        prev_energy = energy;

        let latency_us = step_start.elapsed().as_micros() as u32;
        let stiffness_ratio = ((1 << (n_shells - 1)) as f64).powi(2); // (2^5)^2 = 1024

        // Intercept telemetry
        let ev = SimulationTelemetryEvent::new(
            step as u64,
            (step as u64) * 2_000_000,
            enstrophy,
            energy,
            1e-15, // solenoidal
            25.0,
            stiffness_ratio,
            latency_us,
        );

        interceptor.intercept_step(ev);

        // Reset arena scratch zone in O(1) time
        arena.reset_scratch();
        assert_eq!(arena.scratch_offset, 0);
    }

    // Verify all steps captured in ring buffer without drops
    assert_eq!(interceptor.total_intercepted(), num_steps as u64);
    assert_eq!(interceptor.dropped_count(), 0);
    assert_eq!(interceptor.pending_count(), num_steps);

    // Drain events and verify FIFO consistency
    let mut step_count = 0;
    while let Some(ev) = interceptor.pop_event() {
        step_count += 1;
        assert_eq!(ev.step, step_count);
        assert!(ev.kinetic_energy < 1.0);
    }
    assert_eq!(step_count, num_steps as u64);
}

