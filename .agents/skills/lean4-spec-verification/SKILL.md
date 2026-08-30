---
name: lean4-spec-verification
description: >-
  Methodologies for running Lean 4 formal verification checks, parsing proof obligations,
  and auditing mathematical stubs (sorry) inside formal PDE specifications and kernel models.
  Activate when validating Tier A mathematical proofs against Mathlib or certifying zero-sorry status.
---

# Lean 4 Formal Specification Verification Skill

Guidance for formal mathematical verification in Lean 4 with Mathlib.

## 1. Epistemic Standard for Tier A

A Lean 4 theorem achieves **Tier A Certification** if and only if:
1. It compiles cleanly with the pinned `lean-toolchain`.
2. It contains **zero `sorry`** tactics in active proof bodies.
3. The `#print axioms` output contains only Lean's foundational axioms: `[propext, Classical.choice, Quot.sound]`.

## 2. Verification Procedure

```bash
# Check theorem axiom footprint
lake env lean --run scripts/audit_axioms.lean
```

## 3. Structural Congruence

- Ensure that definitions in `.lean` files (e.g. $R_{\text{eff}}$, Leray projectors, dyadic energy transfer) map 1-to-1 to the exact Python and Rust implementations.
