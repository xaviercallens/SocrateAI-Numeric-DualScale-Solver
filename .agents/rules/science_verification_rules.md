# Science Verification & Epistemic Governance Rules

## 1. Epistemic Tier Gating
- **Tier A**: Formal Lean 4 / Mathlib proofs (zero sorry, zero custom axioms).
- **Tier B**: Exact rational arithmetic (`fractions.Fraction` or `int`), algebraic verification with demonstrated negative controls.
- **Tier C**: Floating-point numerical simulations (`float64`, FFT, ODE/PDE integrators).

## 2. Mandatory Verification Protocols
- All Tier B verification scripts in `src/dualscale_solver/exact/` and `tests/test_exact_*.py` must operate over `fractions.Fraction` or exact integer lattices.
- Every verifier must include a negative control proving that falsified data triggers a hard failure.
- Solver runs generating certificates must conform to `src/dualscale_solver/cert/schema.json`.
- When using Google DeepMind Science Skills, clearly differentiate experimental empirical records from deep-learning predictions.
