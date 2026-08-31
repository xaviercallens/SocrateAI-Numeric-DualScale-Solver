---
name: dualscale-numeric-solver
description: >-
  Expert guidelines and workflows for running, extending, and verifying dual-scale numerical PDE solvers,
  Katz-Pavlović dyadic cascades, 2D/3D pseudo-spectral Navier-Stokes simulations, exact rational T-duality invariants,
  P1/P2/P3/P5 preconditioners, JHTDB spectral validation, production SLA monitoring, and generating Tier B audit
  certificates. Activate when working with dual-scale fluid dynamics, enstrophy control, spectral dealiasing,
  Leray-Helmholtz projection, or Phase 5 production/industrial validation in this repository.
version: 3.0
updated: 2026-08-31
---

# Dual-Scale Numeric Solver Skill (v3.0 — Phase 5 Certified)

> **CRITICAL RULE**: No hardcoded performance numbers, no synthetic formulas, no fabricated figures. Every reported value must come from a real computation. See HARDNESS.md H11–H19.

## 1. Mathematical Principles

The dual-scale regularization is governed by:

$$R_{\text{eff}}(R) = \max\left(R, \frac{\alpha'}{R}\right)$$

where $\alpha' > 0$ defines the crossover scale:
- **Macro Continuum Regime ($R \ge \sqrt{\alpha'}$)**: Standard Navier-Stokes advection-diffusion.
- **Micro Bounce Regime ($R < \sqrt{\alpha'}$)**: Ultraviolet modes bounce back; dissipation bounded by $\Omega_{\text{eff}} \le 1/\alpha'$.
- **T-Duality Invariance**: $R_{\text{eff}}(\alpha'/R) = R_{\text{eff}}(R)$.

## 2. Solver & Preconditioner Modules

### P1 Spectral Fourier Gate Preconditioner (`dualscale_solver.numeric.preconditioner_p1`)
- Implements Fourier-space inverse Rulial symbol: $P_1(k) = \max(k^2, \alpha' k^4)$.
- Applied in $\mathcal{O}(N \log N)$ operations via FFT.
- Guarantees preconditioned condition number $\kappa(P_1^{-1} A) \le 10^3$ (H14).

### P2 Multilevel ILU / Flexible GMRES (`dualscale_solver.numeric.preconditioner_p2`)
- Incomplete LU factorization for non-symmetric convective operators with cross-scale shell couplings.
- Preconditioned GMRES with exact residual vector tracking $\|r_k\|_2 / \|r_0\|_2 \le 10^{-8}$.

### P3 FP8 TensorCore AMG (`dualscale_solver.numeric.preconditioner_p3`)
- Algebraic Multigrid (AMG) V-Cycle with mixed-precision quantization emulation.
- Demonstrates real measured iteration reduction $\ge 5\times$ to $256\times$ vs OpenFOAM DIC/CG baselines (H15).
- Coarse operator regularized: $A_c \leftarrow A_c + 10^{-5} I_{n_c}$ (LL-12).

### Phase 4 Embedded Real-Time Target (`dualscale_solver.runtimes.embedded_target`)
- `no_std` zero-heap allocation static buffer execution kernel (STM32 Cortex-M, SpacemiT K1 RISC-V RVV, RunuX kernel).
- Enforces $\le 64\text{ KB}$ RAM budget and deterministic sub-millisecond step latency (H16).
- Validates photobioreactor oxygen mass transfer $k_L a = 115.89/\text{s}$ yielding $\ge 3.0\times$ algal yield multiplier.

### Phase 5 JHTDB Spectral Auditor (`dualscale_solver.numeric.jhtdb_client`)
- Fetches or generates a statistically-consistent $1024^3$ HIT snapshot.
- Computes 1D energy spectrum $E(k) = \frac{1}{2}\sum_{k-\frac{1}{2} \le |p| < k+\frac{1}{2}} |\hat{u}(p)|^2$.
- Returns `_measured: true` result dict with Kolmogorov exponent fit (H17).
- **Offline fallback**: When `JHTDB_AUTH_TOKEN` is absent, uses local synthetic-but-statistically-valid HIT snapshot (LL-14).

### Phase 5 Production SLA Monitor (`dualscale_solver.numeric.production_sla_monitor`)
- 10,000-step production stress loop (500 warmup + 9,500 measured).
- NaN/Inf guard on every step; uptime counter; throughput in steps/s (H18, LL-15).

### Phase 5 Spectral Energy Auditor (`dualscale_solver.numeric.spectral_energy_auditor`)
- Computes $L^2$ relative spectral error vs JHTDB reference.
- Fits Kolmogorov scaling exponent via log-log regression on inertial range (H17).

## 3. Epistemic Negative Controls (Tier B Mandatory)

Every verifier must pass its negative control:
```python
assert negative_control_singularity_violation()      # NC-DS-01
assert negative_control_symmetry_violation()         # NC-DS-02
assert negative_control_p1_spectral_distortion()     # NC-DS-05
assert negative_control_p2_singular_matrix()         # NC-DS-06
assert negative_control_p3_amg_coarsening()          # NC-DS-07
assert negative_control_embedded_memory_overflow()   # NC-DS-08
assert negative_control_white_noise_spectrum()       # NC-DS-09 (Phase 5, H17)
assert negative_control_nan_injection()              # NC-DS-10 (Phase 5, H18)
```

## 4. Autonomous Workflow Execution

```bash
# Execute End-to-End Master Protocol (Phases 1–5)
./scripts/run_all_phases_autonomous.sh

# Execute Phase 5 only
./scripts/run_phase5_autonomous.sh

# Run Phase 5 standalone script
python3 scripts/run_phase5_experimental_protocol.py
```

## 5. H17–H19 Quick Reference (Phase 5 Gates)

| Gate | Invariant | Threshold | NC |
|---|---|---|---|
| Spectral Fidelity | H17 | $L^2$ error $< 2\%$, exponent $\in [-1.8, -1.6]$ | NC-DS-09 |
| Production SLA | H18 | $\ge 1000$ steps/s, uptime $\ge 99.9\%$ | NC-DS-10 |
| Frustration Monotonicity | H19 | $\mathcal{D}(M)$ non-decreasing for $Re_\lambda > 100$ | Laminar regime exemption |

## 6. Phase 6c Cloud-Production Readiness (H33–H34)

When advancing industrial PoCs to cloud-production (Phase 6c), you must adhere to the following strict operational guidelines:

### 6.1. Secure Vault Integration (H33)
- **Do NOT** rely on plain environment variables (`GEMINI_API_KEY`) for agentic orchestration.
- **Rule**: Agents must authenticate via a mock or real `SecretVaultAgent` to retrieve credentials. If keys are missing, the workflow must actively halt and reject the execution, preventing silent fallback to `SCAFFOLDING_ONLY`.

### 6.2. Native Cloud Telemetry (H33)
- **Do NOT** simply print critical metrics to stdout.
- **Rule**: Stream real-time edge metrics (e.g., $k_L a$ yields, shock buffet variance, latency bounds) directly to a `CloudTelemetryAgent` (BigQuery/Grafana mock endpoint).

### 6.3. Distributed JHTDB Scaling (H34)
- **Rule**: Single-node PoCs for pipeline drag reduction must be scaled to use distributed multi-node array models interfacing with the JHTDB API. 

### 6.4. Hardware-in-the-Loop (HITL) Validation
- **Rule**: Embedded edge bounds ($\le 64\,\text{KB}$ RAM, $\le 1.0\,\text{ms}$ latency) must be validated using simulated physical hardware latency profiles (e.g., ARM Cortex-M4) rather than host CPU measurements.

## 7. Phase 7 & 8 Industrialization & Productization Standards (H41–H50)

### 7.1. HIL Cycle Budget Analysis (H41 / H45)
- Micro-kernel ($N=4\times4$) must execute in $\le 1.0\,\text{ms}$ (456 cycles @ 168 MHz on STM32F407).
- Memory footprint bounded to static stack/BSS $\le 64\,\text{KB}$ with zero heap allocation.

### 7.2. Generative CAD & Topology Export (H42 / H46)
- Airfoil/blade camber lines optimized via frustration minimization must be exported to ISO-10303-21 STEP files.
- Files must feature valid `ISO-10303-21` header/footer, `B_SPLINE_CURVE_WITH_KNOTS`, and SHA-256 cryptographic traceability.

### 7.3. Live Multi-Cloud Telemetry Streaming (H43 / H47)
- Telemetry events must be monotonic in timestamp (`timestamp_ns`), schema-complete with `sequence_number`, and verified via a rolling SHA-256 stream digest with zero event loss.

### 7.4. 3D Volume Mesh FSI Co-Simulation (H44 / H44b / H48)
- Interface velocity continuity must be enforced at the fluid-solid boundary ($y=0$).
- Record `pre_enforcement_velocity_mismatch` (to guarantee non-trivial coupling $> 10^{-8}$) and `post_enforcement_residual = 0.0`.
- Verify sign-agnostic enstrophy transfer coefficient $|\eta| = |\Delta\Omega / M_b| \ge 10^{-6}$ and kinetic energy loss $< 5.0\%$.

### 7.5. Industrial Productization (Phase 8 Mandate)
- Package core solver as a standalone Python Wheel (`leanflow`), native C-ABI shared library (`libleanflow.so`), and lightweight Docker HPC appliance.

