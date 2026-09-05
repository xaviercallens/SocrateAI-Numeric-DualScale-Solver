---
name: scientific-deep-think
description: >-
  Systematic methodology and execution guidelines for leveraging Gemini 3.1 Pro (High)
  with Deep Think (Ultra subscription) for Tier 2 Mathematical Physics Judgment,
  Navier-Stokes singularity analysis, nonlinear transfer balance, and Lean 4 formalization.
version: 1.0
tier: T2
target_model: gemini-3.1-pro
reasoning_budget: deep_think
---

# Scientific Deep Think: Mathematical Physics & Formalization

This skill formalizes the deep reasoning protocols required for **Tier 2 Mathematical Physics Judgment** using **Gemini 3.1 Pro (High)** in extended **Deep Think** mode.

Tier 2 tasks demand exhaustive mathematical scrutiny, formal rigor, and epistemic modesty. Hand-waving, intuitive heuristics, and unverified assumptions are strictly prohibited.

---

## Deep Think Operational Workflow

When engaged on mathematical derivations, PDE formulations, or Lean 4 specifications, execute the following four-phase cognitive protocol:

```
┌────────────────────────────────────────────────────────┐
│  Phase 1: Scale Analysis & Epistemic Boundary Setting  │
└──────────────────────────┬─────────────────────────────┘
                           │
┌──────────────────────────▼─────────────────────────────┐
│  Phase 2: Nonlinear Transfer & Dissipation Balance     │
└──────────────────────────┬─────────────────────────────┘
                           │
┌──────────────────────────▼─────────────────────────────┐
│  Phase 3: Negative Control & Perturbation Derivation   │
└──────────────────────────┬─────────────────────────────┘
                           │
┌──────────────────────────▼─────────────────────────────┐
│  Phase 4: Formal Proof Specification (Lean 4)          │
└────────────────────────────────────────────────────────┘
```

---

## Phase 1: Scale Analysis & Epistemic Boundary Setting

1. **Dimensional Consistency**:
   Verify physical units and dimensions for all variables across every term:
   $$[\nu] = \text{m}^2/\text{s}, \quad [\Omega] = \text{s}^{-2}, \quad [\alpha'] = \text{m}^4/\text{s}$$
2. **Surrogate Scope Demarcation**:
   - Explicitly identify the spatial discretization mode count ($N$), boundary conditions (e.g. periodic vs wall-bounded), and dimensionality (1D/2D/3D).
   - If using a Reduced-Order Model (ROM, e.g. $N=32$), enforce the rule: **Never claim numerical smoothing as real physical or clinical flow stabilization without full Navier-Stokes validation**.

---

## Phase 2: Nonlinear Transfer vs Dissipation Balance

When analyzing enstrophy or energy evolution equations, never evaluate linear dissipation in isolation.

1. **Full Enstrophy Evolution**:
   For the velocity field $u$ with biharmonic regularizer $-\alpha' \Delta^2 u$:
   $$\frac{d\Omega}{dt} = -2\nu \sum_k k^2 |\omega_k|^2 - 2\alpha' \sum_k k^4 |\omega_k|^2 + T_\Omega(t)$$
   where $T_\Omega(t) = \int_{\mathbb{T}^d} \omega \cdot (\omega \cdot \nabla u)\,dx$ represents the **nonlinear vortex stretching / enstrophy cascade term**.
2. **Critical Balance Check**:
   - In 2D: Vortex stretching is identically zero ($T_\Omega(t) = 0$), so $-2\alpha' \sum k^4 |\omega_k|^2 \le 0$ provides unconditional monotonicity.
   - In 3D: Vortex stretching can be positive ($T_\Omega(t) > 0$). You must determine whether the scale thresholding $\alpha' \ge \alpha_{\text{crit}}$ guarantees that hyper-dissipation dominates the supremum of vortex stretching:
     $$2\alpha' \sum_k k^4 |\omega_k|^2 \ge \sup |T_\Omega(t)|$$
   - Any claim omitting $T_\Omega(t)$ in a 3D context violates epistemic integrity and must be rejected.

---

## Phase 3: Negative Control & Perturbation Derivation

Under `HARDNESS.md` Invariant `H2`, a mathematical theorem or verifier is invalid unless accompanied by a deterministic negative control.

1. **Falsification Hypothesis**:
   Construct an explicit state or parameter perturbation that violates the theorem's premises:
   - Example: Setting $\alpha' \to 0$ or injecting non-divergence-free velocity perturbations ($k \cdot \hat{u} \ne 0$).
2. **Rejection Guarantee**:
   Verify that the negative control deterministically triggers a non-zero exit code or certificate rejection (`overall_status = "REJECTED"`).

---

## Phase 4: Formal Proof Specification (Lean 4)

1. **Axiom Fingerprinting**:
   Audit the Lean 4 proof environment. Permitted axioms are strictly limited to standard Mathlib foundations:
   `[propext, Classical.choice, Quot.sound]`
2. **Sorry-Free Distinction**:
   - Modules containing `sorry` stubs MUST be designated:
     `"status": "FORMAL SPECIFICATION ROADMAP (Tier B)"`
   - Only proofs verified by `lake build` with zero non-exempt `sorry` stubs may receive:
     `"status": "VERIFIED"`
