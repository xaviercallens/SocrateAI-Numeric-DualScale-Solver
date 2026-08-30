# HARDNESS.md — Structural Invariants

*The rules that do not bend under schedule pressure. Inherited from `SocrateAI-Scientific-Mathesis` Stream 0 and adapted for the Dual-Scale Numerical Solver.*

An invariant differs from a preference in one way: **there is a mechanical check that fails when it is violated.** Every entry below names its check.

---

## H1 — Zero-sorry Verification (Tier A)
Every Tier A claim is Lean 4 kernel-compiled with zero `sorry` and an axiom footprint matching strictly Lean's foundational axioms `[propext, Classical.choice, Quot.sound]`.
- *Enforced by:* `#print axioms` inspection in Lean formalization audits.

## H2 — The Negative Control is the Checker (Tier B)
Every Tier B harness ships a control that is **demonstrated to fail**, and verification fails if the control passes. A checker that cannot fail is not a checker.
- *Enforced by:* `scripts/verify.sh` Gate 1 & Gate 2 (`NC-DS-01`, `NC-DS-02`, `NC-DS-04`).

## H3 — Exact Rational Arithmetic in Certified Paths (Tier B)
`fractions.Fraction` and `int` only. Floats are banned from `src/dualscale_solver/exact/` and `tests/test_exact_*.py`. Floating-point code is strictly confined to numerical PDE approximations and exploratory simulations under `# TIER X / TIER C`.
- *Enforced by:* Gate 1 exact rational test suite.

## H4 — Non-Vacuity
Every definition ships a witness; every theorem ships an example instantiating its hypotheses; every predicate ships **both** a satisfying and a violating instance.
- *Enforced by:* Positive verifiers and negative controls in `tests/`.

## H5 — No Claim Outside the Ledger
A claim absent from `LEDGER.md` and `ledger.jsonl` has no tier and may not be cited. The machine-readable `ledger.jsonl` and human-readable `LEDGER.md` must name the identical identifiers.
- *Enforced by:* `scripts/verify.sh` Gate 3 ledger audit.

## H6 — Tier Monotonicity
No claim is filed at a tier above anything it rests on, **transitively**:
$$\text{Sound}(L) := \forall a, b, \quad b \in (L(a)).\text{supports} \implies \text{tier}(L(a)) \le \text{tier}(L(b))$$
- *Enforced by:* `src/dualscale_solver/cert/ledger_checker.py`.

## H7 — Agent Self-Reports are Not Evidence
Independently re-run the compiler or test harness on the exact artifact before committing. Never trust unchecked summaries.
- *Enforced by:* Autonomous CI execution (`./scripts/verify.sh`).
