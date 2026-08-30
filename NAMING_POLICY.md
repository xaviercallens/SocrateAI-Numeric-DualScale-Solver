# Naming Policy — SocrateAI-Numeric-DualScale-Solver

**Effective:** 2026-08-30  
**Rules:** RES-1 (Reserved Scientific Terms) + N-1 (Structural & Invariant Claims)  
**Status:** ENFORCED — violations in this repo block verification and CI

---

## 1. Scope & Intent

This repository develops numerical, exact rational, and pseudo-spectral solvers for **Dual-Scale Regularized PDEs** (hydrodynamic cascades, Navier-Stokes, dyadic shell models, and multiscale energy-enstrophy systems).

All claims, architectures, and algorithms must adhere to the standard three-tier epistemic system:
- **Tier A (Established Formal Math)**: Machine-checked Lean 4 proofs (zero-sorry, zero custom axioms).
- **Tier B (Exact Checkable Numerics)**: Exact rational arithmetic (`fractions.Fraction` or `int`), algebraic verification with demonstrated negative controls.
- **Tier C (Floating-Point / Empirical Solver / Heuristic)**: Standard floating-point (`float64`, PDE approximations), clearly designated as numerical simulations or heuristic exploration.

---

## 2. Reserved Terms & Definitions

| Term | Required Definition / Criterion | Permitted Usage | Prohibited Usage |
|---|---|---|---|
| **Dual-Scale Regularization** | Scale mapping $R_{\text{eff}}(R) = \max(R, \alpha'/R)$ satisfying $R_{\text{eff}} \ge \sqrt{\alpha'}$ and T-duality $R_{\text{eff}}(\alpha'/R) = R_{\text{eff}}(R)$. | In exact arithmetic modules, dyadic shell regularizers, and modified viscous dissipation operators. | Labeling ad-hoc numerical smoothing without the T-dual bounce symmetry. |
| **Exact Rational Invariant** | Quantity proved using exact rational fractions ($\mathbb{Q}$) with zero floating-point roundoff. | `dualscale_solver/exact/` and `tests/test_exact_*.py`. | Floating-point assertions labeled as "exact". |
| **Divergence-Free** | Velocity field satisfying $k \cdot \hat{u}(k) = 0$ via exact Leray projection in Fourier space. | Pseudo-spectral Navier-Stokes velocity state $u$. | Approximate velocity fields without projection. |
| **Negative Control** | A test case designed mathematically to violate a condition, required to fail the verifier. | In every Tier B verification harness. | Omission of negative controls in verification suites. |

---

## 3. Epistemic Gating Rules

1. **Floats banned from Tier B harnesses**: All Tier B verification scripts in `dualscale_solver/exact/` and `tests/test_exact_*.py` must operate over `fractions.Fraction` or integer lattices.
2. **Negative Controls are Mandatory**: Every verifier must include a negative control proving that falsified data triggers a hard failure.
3. **Audit Certificates**: Solver runs generating certificates must conform to `src/dualscale_solver/cert/schema.json`.
