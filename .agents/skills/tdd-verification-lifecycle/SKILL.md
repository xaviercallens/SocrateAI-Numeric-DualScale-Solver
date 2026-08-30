---
name: tdd-verification-lifecycle
description: >-
  Disciplined Test-Driven Development (TDD), property-based testing (Hypothesis),
  epistemic negative control design, and regression certification for mathematical physics code.
  Activate when writing new solver features, adding unit tests, or verifying invariant preservation.
---

# TDD & Verification Lifecycle Skill

Enforces strict test-driven development and dual-phase (positive + negative control) verification for scientific software.

## 1. The Tri-Phase TDD Process

1. **RED (Negative & Baseline)**:
   - Write the exact invariant assertion first.
   - Write an explicit **negative control** demonstrating that an incorrect or unregularized formula fails loudly.
2. **GREEN (Implementation)**:
   - Implement the minimal correct algorithm (in exact rational arithmetic for Tier B, or vectorized NumPy/Rust for Tier C).
   - Ensure positive checks pass and negative controls catch falsified inputs.
3. **REFACTOR (Performance & Architecture)**:
   - Optimize memory access and vectorization without changing invariant outcomes.

## 2. Property-Based Testing Guidelines

- Use `hypothesis` to fuzz test physical parameters ($\nu \in (0, 1)$, $\alpha' \in (0, 100)$, initial energy $E_0 > 0$).
- Verify universal invariants across all generated inputs:
  - Energy decay $\frac{dE}{dt} \le 0$ under viscous dissipation.
  - Divergence $|k \cdot \hat{u}| < \epsilon$ for arbitrary random solenoidal fields.
  - T-duality symmetry $R_{\text{eff}}(\alpha'/R) \equiv R_{\text{eff}}(R)$ over rational intervals.
