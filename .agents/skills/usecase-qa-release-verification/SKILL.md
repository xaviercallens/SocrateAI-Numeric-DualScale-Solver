---
name: usecase-qa-release-verification
description: >-
  End-to-end Quality Assurance (QA) certification and release gating workflow based on the 3 canonical LeanFlow solver use cases:
  (1) High-Re Stiff Cascade (CVODE BDF vs. CFL explicit RK4 speedup >= 1000x),
  (2) Real-Time Embedded Kernel (zero dynamic allocation, static RAM <= 64 KB, machine-precision agreement <= 1e-8),
  (3) Dual-Scale UV Regularization (enstrophy suppression ratio >= 1.5x vs. classical Navier-Stokes).
  Enforces H2 negative controls, strict energy dissipation monotonicity, epistemic nomenclature compliance (zero banned buzzwords),
  and emits signed JSON audit certificates (CERT-QA-RELEASE-*). Activate prior to tagging, releasing, or deploying any major version.
version: 1.0
tier: T1 (QA) / T2 (Audit)
updated: 2026-09-05
---

# Use-Case QA & Major Release Verification Skill

This skill defines the non-negotiable Quality Assurance (QA) and release gating protocol for all major, minor, and patch releases of the **LeanFlow Multiscale Navier-Stokes Enterprise Solver**.

Every software release candidate (Python wheels, Docker appliances, C-ABI shared library `libleanflow.so`, and Rust crates) **must pass all 4 verification gates** and demonstrate active negative control verification (H2) before tagging, publication, or deployment.

---

## 1. The 6 Mandatory Release Verification Gates

```
┌────────────────────────────────────────────────────────────────────────┐
│  Gate 1: High-Re Stiff Cascade & Speedup Certification (Use Case 1)    │
│  - CVODE BDF variable-order vs. CFL explicit RK4                       │
│  - Step count reduction >= 500x | Extrapolated speedup >= 1000x        │
│  - Monotonic energy dissipation: E(t+dt) <= E(t) + 1e-10               │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│  Gate 2: Real-Time Embedded & Zero-Allocation Determinism (Use Case 2) │
│  - Embedded static RAM <= 64 KB (measured 1.31 KB / 1344 bytes)        │
│  - Zero heap allocations in inner integration loop                     │
│  - Numerical agreement against high-order reference <= 1e-8            │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│  Gate 3: Dual-Scale UV Regularization & Enstrophy Damping (Use Case 3) │
│  - Theoretical crossover wavenumber k_* = 1 / sqrt(alpha')             │
│  - UV enstrophy suppression ratio >= 1.5x vs. classical Kolmogorov    │
│  - Dissipated energy (Dual-Scale) >= Dissipated energy (Classical)     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│  Gate 4: Coupled Navier-Stokes DAE Solenoidal Projection (Phase E2)    │
│  - Solves F(t, y, y') = 0 on constraint manifold via rusty-SUNDIALS IDA│
│  - Divergence residual |div(u)| <= 1e-2 (solenoidal transversality)    │
│  - Lean 4 formal verification: satisfiesDaeResidual (ida_dae_step)     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│  Gate 5: PolarQuant 8x Telemetry Compression & Bounded Distortion      │
│  - Orthogonal Householder rotation + 4-bit scalar block quantization   │
│  - Bandwidth reduction ratio >= 4.0x (targets 8.0x at 4-bit)           │
│  - Energy distortion < 20.0% (Lean 4: totalVectorDistortionBound)      │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│  Gate 6: PyO3 Zero-Copy Native Integration & Memory Safety             │
│  - Non-copying strided array views (is_zerocopy is True)               │
│  - Zero heap copies on NumPy array ingestion and return                │
│  - Lean 4 Memory Slice capacity invariant isWithinCapacity             │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│  Gate 7: Epistemic Nomenclature & Release Hardness Audit               │
│  - Zero banned pseudoscientific buzzwords across codebase               │
│  - Cryptographic SHA-256 rolling digest across all verified states     │
│  - Structured JSON Certificate: CERT-QA-RELEASE-<TAG>                  │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Gate Specifications & Invariant Thresholds

### Gate 1: High-Re Stiff Cascade (Use Case 1)
- **Physical Context**: Sabra shell model of hydrodynamic turbulence at $\text{Re} \sim 10^4$ ($N=16$ shells, $\nu=10^{-4}$, $\alpha'=0.05$).
- **The Stiffness Barrier**: In explicit schemes (e.g. OpenFOAM standard explicit RK4), the viscous CFL limit restricts the time step to $\Delta t_{\text{CFL}} \le 0.4 \frac{\nu}{k_{\max}^2} \sim 10^{-7}\text{ s}$, requiring **millions of fixed steps** to reach macroscopic timescales ($t=0.5$).
- **LeanFlow Enterprise Advantage**: Variable-order, variable-step CVODE BDF dynamically adapts time-steps based on local truncation error estimates.
- **Pass Thresholds**:
  - `step_reduction_factor >= 500.0x` (typical measured: $\sim 1793\times$)
  - `wall_time_speedup_factor >= 1000.0x` (typical measured: $\sim 50,000\times$)
  - Strict energy dissipation monotonicity: $E(t_{n+1}) \le E(t_n) + 10^{-10}$.

### Gate 2: Real-Time Embedded & Zero-Allocation (Use Case 2)
- **Physical Context**: High-frequency hardware-in-the-loop (HIL) fluid control loops (e.g., STM32F407 ARM Cortex-M4 @ 168 MHz or SpacemiT K1 RISC-V RVV 1.0).
- **Embedded Constraints**:
  - Hard real-time cycle budget: step latency $\le 1.0\text{ ms}$ at $\Delta t = 1\text{ ms}$.
  - Static memory budget: strictly $\le 64\text{ KB}$ RAM.
  - Zero dynamic heap allocation (`malloc`/`free` or `Vec::push` in inner loop) to eliminate memory fragmentation and latency jitter.
- **Pass Thresholds**:
  - `static_ram_bytes <= 65536` (measured: 1344 bytes $\approx 1.31\text{ KB}$, giving a $>97\%$ safety margin).
  - Agreement with high-order reference trajectory: $\max |u_{\text{embedded}} - u_{\text{ref}}| \le 10^{-8}$.
  - Strict energy decay: $E_{\text{final}} < E_{\text{initial}}$.

### Gate 3: Dual-Scale UV Regularization (Use Case 3)
- **Physical Context**: Verification of the mathematical dual-scale ultraviolet dissipation operator:
  $$D(k) = \nu k^2 \max(1, \alpha' k^2)$$
  versus the classical Kolmogorov dissipation $D_{\text{classical}}(k) = \nu k^2$.
- **Mechanism**: Past the crossover scale $k_* = 1/\sqrt{\alpha'}$, the effective dissipation scales as $\nu \alpha' k^4$, acting as a rigorous spectral hyperviscosity that prevents finite-time enstrophy blow-up.
- **Pass Thresholds**:
  - Crossover scale match: $k_* = 1/\sqrt{\alpha'}$.
  - UV enstrophy damping ratio: $\frac{\Omega_{\text{classical}}(t_{\text{final}})}{\Omega_{\text{dual}}(t_{\text{final}})} \ge 1.5\text{x}$ (typical measured: $\sim 2.8\text{x}$).
  - Total dissipated energy $\Delta E_{\text{dual}} \ge \Delta E_{\text{classical}}$.

### Gate 4: Coupled Navier-Stokes DAE Solenoidal Projection (Phase E2)
- **Physical Context**: Coupled Incompressible Navier-Stokes differential-algebraic formulation:
  $$F(t, y, y') = \begin{bmatrix} y'_i - (N_i(u) - D(k_i) u_i - \text{Grad}_i(p)) \\ y'_n + \text{Div}(u) \end{bmatrix} = 0$$
- **Mechanism**: Enforces incompressibility directly on the algebraic constraint manifold using `rusty-SUNDIALS` IDA without decoupling or iterative projection errors.
- **Pass Thresholds**:
  - Residual bound: $|\text{div}(u)| \le 10^{-2}$ (measured: $\approx 1.4 \times 10^{-4}$).
  - Manifold invariant: `is_solenoidal = True`.
  - Lean 4 theorem: `satisfiesDaeResidual (ida_dae_step s diss h)`.

### Gate 5: PolarQuant 8× Telemetry State Compression (Phase E2)
- **Physical Context**: High-throughput telemetry streaming across Xavier Callens' lock-free audit ring buffer.
- **Mechanism**: Integrates `runux-ai-runtime/crates/turbo_quant`. Applies orthogonal Householder polar rotation $Q$ to distribute energy variance, followed by 4-bit uniform block quantization.
- **Pass Thresholds**:
  - Bandwidth reduction: `compression_ratio >= 4.0x` (typical measured: **$8.00\times$** at 4-bit).
  - Bounded Euclidean energy distortion: $< 20.0\%$ (typical measured: $17.8\%$).
  - Lean 4 theorem: `polar_rotation_preserves_energy` and `distortion_scales_with_dim`.

### Gate 6: PyO3 Zero-Copy Native Integration (Phase E2)
- **Physical Context**: High-frequency Python/Rust interface replacing ctypes pointer indirection.
- **Mechanism**: NumPy array memory buffers passed directly to Rust via `PyReadonlyArray1<f64>` and returned via `IntoPyArray` without intermediate heap copies.
- **Pass Thresholds**:
  - Zero memory copies: `is_zerocopy = True`.
  - Non-aliasing buffer capacity verified: `offset + length <= capacity` per Lean 4 `isWithinCapacity`.

### Gate 7: Epistemic Nomenclature & Release Hardness Audit
Per `AGENTS.md` Guardrail 2 and `NAMING_POLICY.md`:
- **Banned Terms**: `"Rulial Inversion"`, `"Holographic Regularisation"`, `"Karpathy Ratchet Auto-Research"`.
- All production code, headers, documentation, and agent certificates must be automatically scanned.
- Rolling SHA-256 digest computed across release metadata and physical metrics to guarantee tamper-proof audit trails.

---

## 3. Negative Controls Protocol (H2 Mandate)

> [!CRITICAL]
> **Hardness Invariant H2**: A test or QA gate without an active negative control is **scientifically void**.
> The QA suite must execute negative controls programmatically and assert each returns `True` (proving the detector catches violations).

| Negative Control Identifier | Falsified Input Tested | Expected Result |
|---|---|---|
| `nc_energy_growth_caught` | Perturbed energy trajectory with $\Delta E > 0$ | Detector raises error / returns `True` |
| `nc_ram_overflow_caught` | Falsified state allocation of $128\text{ KB}$ | Detector flags violation ($> 64\text{ KB}$) |
| `nc_enstrophy_inversion_caught`| Falsified suppression ratio $< 1.5\text{x}$ | Detector rejects non-regularized state |
| `nc_banned_buzzwords_caught` | Injected banned pseudoscientific buzzword | Scanner flags file / raises violation |

---

## 4. How to Execute Release Verification

### Automated CLI Execution
Run the Release QA script with the target release tag:

```bash
# Standard major release verification
python3 scripts/usecase_qa_release_verifier.py --release v8.0.0

# Enterprise release with custom certificate destination
python3 scripts/usecase_qa_release_verifier.py --release v8.1.0-enterprise \
    --output results/release_qa_v8.1.0-enterprise.json
```

### Pytest Integration
The verification suite is integrated into CI/CD pipelines via `pytest`:

```bash
pytest -v tests/test_usecase_qa_release.py
```

---

## 5. Agent Structured Output Contract (H26)

When acting as the `qa_scientific_auditor`, the agent must emit a structured JSON response matching the schema below. Any prose response lacking these fields is a **hard gate failure**:

```json
{
  "certificate_id": "CERT-QA-RELEASE-V8.0.0",
  "release_tag": "v8.0.0",
  "timestamp": "2026-09-05T16:28:59.123456Z",
  "overall_status": "CERTIFIED",
  "audit_duration_seconds": 1.95,
  "invariants_verified": {
    "H2_negative_controls": true,
    "UC1_high_re_stiffness_gain": true,
    "UC2_embedded_static_ram_budget": true,
    "UC3_dualscale_uv_regularity": true,
    "epistemic_nomenclature": true
  },
  "use_cases": {
    "use_case_1_turbulent_cascade": {
      "status": "PASSED",
      "step_reduction_factor": 1793.35,
      "wall_time_speedup_factor": 52827.0,
      "energy_dissipated_pct": 28.2071,
      "energy_monotone": true,
      "_measured": true
    },
    "use_case_2_embedded_realtime": {
      "status": "PASSED",
      "static_ram_bytes": 1344,
      "static_ram_budget_bytes": 65536,
      "ram_budget_margin_pct": 97.95,
      "max_state_deviation": 0.0,
      "energy_monotone": true,
      "_measured": true
    },
    "use_case_3_dualscale_regularity": {
      "status": "PASSED",
      "k_star_crossover": 4.4721,
      "final_enstrophy_dual": 25.6814,
      "final_enstrophy_classical": 72.2033,
      "enstrophy_suppression_ratio": 2.81,
      "energy_monotone": true,
      "_measured": true
    }
  },
  "negative_controls": {
    "nc_energy_growth_caught": true,
    "nc_ram_overflow_caught": true,
    "nc_enstrophy_inversion_caught": true,
    "nc_banned_buzzwords_caught": true
  },
  "nomenclature_audit": {
    "passed": true,
    "violations_count": 0
  },
  "sha256_digest": "e0667fe9655e3ec9c6dbbbda5ea6e680a618d36eb31a89c83693e50772733979",
  "_measured": true
}
```

---

## 6. Release Checklist for Release Engineers

Before signing off on any major release:
1. [ ] Run `python3 scripts/usecase_qa_release_verifier.py --release <TAG>`.
2. [ ] Verify `overall_status == "CERTIFIED"`.
3. [ ] Verify `_measured == true` with no synthetic values.
4. [ ] Confirm `CERT-QA-RELEASE-<TAG>.json` is checked into `results/` or attached to GitHub Release.
5. [ ] Ensure all 4 negative controls reported `True`.
6. [ ] Cross-check Lean 4 specification builds clean via `lake build`.
