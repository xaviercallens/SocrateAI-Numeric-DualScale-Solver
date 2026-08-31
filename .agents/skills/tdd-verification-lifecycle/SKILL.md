---
name: tdd-verification-lifecycle
description: >-
  Disciplined Test-Driven Development (TDD), property-based testing (Hypothesis),
  epistemic negative control design, and regression certification for mathematical physics code.
  Activate when writing new solver features, adding unit tests, or verifying invariant preservation.
  Phase 5: includes JHTDB spectral test patterns, production SLA regression, and frustration monotonicity assertions.
version: 3.0
updated: 2026-08-31
---

# TDD & Verification Lifecycle Skill (v3.0 — Phase 5 Hardened)

> **CRITICAL RULE**: Verification means running code and checking exit codes — not asserting `True` in a dictionary. See HARDNESS.md H2, H10, LL-02.

## 1. The Tri-Phase TDD Process

1. **RED (Negative & Baseline)**:
   - Write the exact invariant assertion first.
   - Write an explicit **negative control** demonstrating that an incorrect or unregularized formula fails loudly.
   - **The negative control must actually be called in a test that asserts it returns True** (i.e., proves it detected the error).

2. **GREEN (Implementation)**:
   - Implement the minimal correct algorithm (exact rational arithmetic for Tier B, or vectorized NumPy/Rust for Tier C).
   - Ensure positive checks pass and negative controls catch falsified inputs.

3. **REFACTOR (Performance & Architecture)**:
   - Optimize memory access and vectorization without changing invariant outcomes.
   - Re-run full test suite including negative controls after any refactor.

## 2. Agent QA Checklist — Live Wiring (Lesson LL-02)

The `qa_scientific_auditor` agent MUST call these live — never hardcode:

```python
# H2 — Negative Controls (call programmatically, assert result)
from dualscale_solver.exact.t_duality import (
    negative_control_singularity_violation,
    negative_control_symmetry_violation,
)
from dualscale_solver.exact.cascade_invariants import (
    negative_control_broken_energy_conservation,
)
h2_passed = (
    negative_control_singularity_violation() and
    negative_control_symmetry_violation() and
    negative_control_broken_energy_conservation()
)

# H1 — Lean 4 Zero-Sorry (call programmatically)
import subprocess
proc = subprocess.run(["lake", "build"], cwd="lean4", capture_output=True)
h1_passed = proc.returncode == 0

# H7 — Energy Monotonicity (check from actual simulation)
h7_passed = float(result["energy"][-1]) < float(result["energy"][0])
```

**Forbidden pattern** (violates H10):
```python
invariants_checked = {"H1": True, "H2": True, ...}  # ← ALL HARDCODED = INVALID
```

## 3. Property-Based Testing Guidelines

- Use `hypothesis` to fuzz test physical parameters ($\nu \in (0, 1)$, $\alpha' \in (0, 100)$, initial energy $E_0 > 0$).
- Verify universal invariants across all generated inputs:
  - Energy decay $\frac{dE}{dt} \le 0$ under viscous dissipation.
  - Divergence $|k \cdot \hat{u}| < 10^{-13}$ for arbitrary random solenoidal fields.
  - T-duality symmetry $R_{\text{eff}}(\alpha'/R) \equiv R_{\text{eff}}(R)$ over rational intervals.
- Property-based tests belong in `tests/test_properties_*.py`.

## 4. Empirical Convergence Order Testing (Lesson LL-08)

After any change to the time integrator, verify the empirical convergence order:

```python
def test_etd_rk4_order():
    """ETD-RK4 must achieve convergence order >= 3.8 on linear stiff ODE."""
    import numpy as np
    lam = 100.0
    def f(t, u): return -lam * u   # stiff linear ODE
    u_exact = lambda t: np.exp(-lam * t)

    dts = [0.01, 0.005, 0.0025]
    errors = []
    for dt in dts:
        u = np.array([1.0])
        t, T = 0.0, 0.5
        # ... integrate with ETD-RK4 ...
        errors.append(abs(u[0] - u_exact(T)))

    orders = [np.log(errors[i]/errors[i+1])/np.log(2) for i in range(len(errors)-1)]
    assert min(orders) >= 3.8, f"ETD-RK4 order too low: {orders}"
```

## 5. Peak-Time Agreement Assertion (Lesson LL-10)

Phase II Taylor-Green benchmarks must assert peak-time agreement:

```python
rel_error = abs(sim_peak_t - ref_peak_t) / max(ref_peak_t, 1e-10)
assert rel_error < 0.25, (
    f"TGV peak time mismatch: sim={sim_peak_t:.2f} vs ref={ref_peak_t:.2f} "
    f"(relative error={rel_error:.1%} > 25% threshold)"
)
```

## 6. Certificate Integrity Rules (Lesson LL-02, LL-13)

Before issuing any `CERT-P*-WF-*`:
1. Check that no result value contains `"synthetic"` or `"hardcoded"`.
2. Verify all performance claims have `_measured: true` flag.
3. Confirm `./scripts/verify.sh` exits with code 0.

## 7. Phase 5 JHTDB Spectral Test Pattern (H17)

Property-based test for Kolmogorov $k^{-5/3}$ scaling using Hypothesis:

```python
from hypothesis import given, settings
from hypothesis import strategies as st
import numpy as np
from dualscale_solver.numeric.jhtdb_client import JHTDBClient
from dualscale_solver.numeric.spectral_energy_auditor import SpectralEnergyAuditor

@given(
    nu=st.floats(min_value=1e-4, max_value=1e-2),
    alpha_prime=st.floats(min_value=0.1, max_value=10.0),
)
@settings(max_examples=5, deadline=30_000)
def test_kolmogorov_scaling_property(nu, alpha_prime):
    """H17: Kolmogorov exponent must lie in [-1.8, -1.6] for any valid HIT state."""
    client = JHTDBClient(use_local_fallback=True)
    E_k, k_vals = client.compute_energy_spectrum(nu=nu, alpha_prime=alpha_prime)
    auditor = SpectralEnergyAuditor()
    result = auditor.fit_kolmogorov_exponent(E_k, k_vals)
    assert -1.8 <= result["kolmogorov_exponent"] <= -1.6, (
        f"Kolmogorov exponent {result['kolmogorov_exponent']:.3f} outside [-1.8, -1.6]"
    )

def test_negative_control_white_noise_spectrum():
    """NC-DS-09: Random white-noise spectrum must FAIL H17 spectral L2 test."""
    client = JHTDBClient(use_local_fallback=True)
    E_ref, k_vals = client.compute_energy_spectrum()
    E_white_noise = np.random.rand(len(k_vals))  # no Kolmogorov structure
    auditor = SpectralEnergyAuditor()
    result = auditor.compute_l2_relative_error(E_white_noise, E_ref)
    assert result["l2_relative_error"] > 0.02, (
        "NC-DS-09 FAILED: white noise spectrum passed H17 (should have failed)"
    )
```

## 8. Production SLA Regression Test (H18)

10,000-step stress loop with NaN guard (LL-15 compliant — 500 warmup steps):

```python
def test_production_sla_stress():
    """H18: >= 1000 steps/s; uptime >= 99.9%; NaN guard fires on injection."""
    from dualscale_solver.numeric.production_sla_monitor import ProductionSLAMonitor
    monitor = ProductionSLAMonitor(grid_n=128, warmup_steps=500, measure_steps=9500)
    result = monitor.run()
    assert result["throughput_steps_per_sec"] >= 1000, (
        f"H18 FAILED: {result['throughput_steps_per_sec']:.1f} steps/s < 1000"
    )
    assert result["uptime_fraction"] >= 0.999, (
        f"H18 FAILED: uptime {result['uptime_fraction']:.4f} < 99.9%"
    )
    assert result["nan_count"] == 0, f"H18 FAILED: {result['nan_count']} NaN steps"

def test_negative_control_nan_injection():
    """NC-DS-10: NaN injected at step 5000 must be caught before step 5001."""
    from dualscale_solver.numeric.production_sla_monitor import ProductionSLAMonitor
    monitor = ProductionSLAMonitor(grid_n=128, warmup_steps=0, measure_steps=6000,
                                   inject_nan_at_step=5000)
    result = monitor.run()
    assert result["nan_detected"], "NC-DS-10 FAILED: NaN injection not detected"
    assert result["nan_detected_at_step"] <= 5001, (
        f"NC-DS-10 FAILED: NaN detected late at step {result['nan_detected_at_step']}"
    )
```

## 9. Frustration Monotonicity Assertion (H19)

Non-decreasing $\mathcal{D}(M)$ for turbulent states after 50-step spinup (LL-16 compliant):

```python
def test_frustration_monotonicity_turbulent():
    """H19: D(M) must be non-decreasing with M for Re_lambda > 100."""
    from dualscale_solver.numeric.dyadic_cascade import DyadicShellSolver
    solver = DyadicShellSolver(alpha_prime=1.0, nu=1e-4)  # high Re
    # 50-step spinup (LL-16: avoid cold-start ordering artifacts)
    for _ in range(50):
        solver.step(dt=1e-3)
    M_values = [4, 8, 16, 32, 64]
    d_values = [solver.compute_triadic_frustration_index(M) for M in M_values]
    for i in range(len(d_values) - 1):
        assert d_values[i] <= d_values[i + 1] * 1.05, (  # 5% tolerance
            f"H19 FAILED: D({M_values[i]})={d_values[i]:.3f} > "
            f"D({M_values[i+1]})={d_values[i+1]:.3f}"
        )
```
