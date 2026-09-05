# Epistemic Memory & Cross-Agent Operational Guardrails

**Repository:** `SocrateAI-Numeric-DualScale-Solver`  
**Standard:** Enterprise Edition v3.0 (Post-Peer Review Remediation)  
**Authority:** Derived from `LL.md` (LL-01 through LL-42) and `AGENTS.md`  

---

## 1. Core Mathematical & Statistical Mandates

### 1.1. Statistical Significance Rule (LL-38)
- **Hard Rule**: NEVER claim "directional control utility", "monotone trend", or "surrogate ranking consistency" if Spearman rank correlation $p \ge 0.05$.
- **Sample Size**: Testing rank correlation on $n=3$ points (especially with clamped outputs) cannot mathematically reject the null hypothesis ($p=0.12$). All correlation sweeps MUST use $n \ge 20$ points across the continuous operational domain (`couette_spearman_sweep(n_points=20)`).
- **Remediation**: If an existing text asserts directional utility despite $p \ge 0.05$, the assertion MUST be retracted in print.

### 1.2. Nonlinear Enstrophy Dissipation Accounting (LL-40)
- **Hard Rule**: In Fourier pseudo-spectral Navier-Stokes ROMs, enstrophy evolution is governed by:
  $$\frac{d\Omega}{dt} = T(t) - 2\nu \sum_k k^4 |\hat{u}|^2 - 2\alpha' \sum_k k^6 |\hat{u}|^2$$
  where $T(t) = \sum_k k^2 \text{Re}[\hat{u}_k^* \hat{N}_k]$ is the nonlinear Galerkin transfer term.
- **Formulation**: Label this as a `Proposition` (Linear Enstrophy Bound), NOT an unconditional theorem. Universal monotonicity $\Omega(t) \le \Omega(0)$ is conditional on $T(t) \le 0$ (net forward cascade), which is numerically validated for truncated spectral modes but unproven for arbitrary initial conditions.

---

## 2. Terminology & Nomenclature Policy (LL-39)

All agents MUST reject and eliminate pseudoscientific buzzwords. Use established classical numerical and optimization terms:

| Banned Term | Approved Replacement | Context |
|---|---|---|
| `"Karpathy Ratchet Auto-Research Loop"` | `"Monotonic Greedy Line Search with Backtracking"` | 1D parameter optimization with state reversion |
| `"Rulial Inversion"` | `"Wavenumber-Dependent Scale Thresholding"` | $R_{\text{eff}}(k) = \max(k^{-1}, \alpha' k)$ |
| `"Holographic Regularisation"` | `"Empirical Disruption Threshold"` | Tokamak MHD stability boundary $\Omega < 250 R_{\text{eff}}^2$ |
| `"Biomedical Safety Gain"` | `"Surrogate Shear Reduction"` | $N=32$ ROM wall shear stress output |
| `"Formal Verification"` (for `sorry` stubs) | `"Formal Specification Roadmap"` | Lean 4 modules where theorem bodies use `sorry` |

---

## 3. Lean 4 Formal Verification Epistemic Tiers (LL-19, LL-41)

- **Tier A (Certified Formal Verification)**:
  - `lake build` exit code `0`.
  - Zero non-exempt `sorry` stubs.
  - `#print axioms` output contains only `[propext, Classical.choice, Quot.sound]`.
  - Proof is non-tautological (H21 / LL-19).
- **Tier B (Formal Specification Roadmap / Runtime Enforced)**:
  - Formal Lean 4 signatures exist, but bodies use `sorry`.
  - Validated by runtime Pydantic schema contracts on numerical instances.
  - **MANDATORY**: Must be disclosed explicitly as a specification roadmap, never as completed formal verification.

---

## 4. Surrogate-Model Scope & Clinical/Industrial Caveats (LL-42)

- **Hard Rule**: A 1D periodic Fourier reduced-order model ($N=32$) with heavy biharmonic damping ($-\alpha' k^4$) artificially smooths velocity gradients near boundaries.
- Any reported drop in Wall Shear Stress (WSS), drag, or heat flux is an optimization within the surrogate's own mathematical metric space.
- All reports, tables, and agent outputs must include the mandatory caveat:
  > *"ROM outputs are control-surrogate indicators only. They cannot be cited as clinical or regulatory safety claims without 3D CFD cross-validation against high-resolution solvers (Nek5000, OpenFOAM) on patient-specific geometries."*
