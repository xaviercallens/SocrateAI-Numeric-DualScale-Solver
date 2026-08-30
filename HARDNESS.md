# HARDNESS.md — Program-Wide Scientific Hardness & Epistemic Charter

**Program:** SocrateAI Dual-Scale & LeanFlow Multiscale Navier–Stokes Program  
**Status:** MANDATORY & NON-NEGOTIABLE INVARIANTS  
**Scope:** Applies to all mathematical proofs, exact verifiers, numerical solvers, AI preconditioners, and embedded kernels.  
**Updated:** 2026-08-30  

---

## 1. The Ten Inviolable Scientific Invariants (H1–H10)

These structural invariants define the hardness of the SocrateAI scientific program. They **never bend** under schedule pressure, token limits, or algorithmic convenience.

### `H1` : Zero-Sorry Lean 4 Formal Verification (Tier A)
All foundational algebraic and geometric theorems must compile in Lean 4 without `sorry` and with zero unvetted custom `axiom` declarations. `#print axioms <theorem_name>` must strictly output foundational Lean axioms:
```lean
[propext, Classical.choice, Quot.sound]
```

### `H2` : Negative Control is the Checker (Tier B)
Every verifier, invariant checker, and test suite must ship with an explicit negative control demonstrating that falsified states, broken symmetries, or energy leaks are deterministically caught and rejected. **A verifier without a demonstrated-to-fail negative control is invalid.**

### `H3` : Exact Rational Arithmetic Over $\mathbb{Q}$ (Tier B)
Floating-point approximations (`f32`, `f64`) are strictly forbidden in Tier B verification algorithms. Invariant checking, certificate emission, and symmetry validation must use exact rational arithmetic ($\mathbb{Q}$ via `fractions.Fraction` or integer lattices).

### `H4` : Non-Vacuity & Falsifiability
Every theorem statement, predicate, and filter must be proven non-vacuous by exhibiting:
1. At least one non-trivial instance satisfying the premise.
2. At least one explicit counter-model or perturbation violating the conclusion when premises are relaxed.

### `H5` : Strict Rulial Inversion (No Artificial Cutoffs)
Singularity prevention and scale regularization must never rely on ad-hoc empirical cutoffs or artificial smoothing, but strictly on exact **Rulial Inversions**:

$$R_{\text{eff}}(R) = \max\left(R, \frac{\alpha'}{R}\right), \quad R_{\text{eff}} \ge \sqrt{\alpha'}$$

The inverse scale $\alpha'/R$ guarantees bounded geometry at all scales without breaking microscopic conservation laws.

### `H6` : Solenoidal Transversality & Leray Idempotence
Incompressible velocity fields must maintain exact machine-precision transversality:

$$\mathcal{P}_{ij}(k) = \delta_{ij} - \frac{k_i k_j}{|k|^2}, \quad \mathcal{P}^2 = \mathcal{P}, \quad |k \cdot \hat{u}(k)| < 10^{-13}$$

### `H7` : Thermodynamic Energy Critic over Statistical Losses
In neuro-symbolic AI modules (`leanflow-ai`, `runux-ai-runtime`), models must not be trained solely on heuristic mean squared error (MSE). Loss functions and preconditioner gating must incorporate physical energy critics that penalize unphysical energy generation, enstrophy blowups ($\Omega > 1/\alpha'$), or violations of the Triadic Frustration Index bounds.

### `H8` : No Claim Outside the Machine-Checked Ledger
No result, bound, theorem, or speedup factor may be cited or relied upon unless entered into `ledger.jsonl` and `LEDGER.md` with:
- Formal unique identifier (`DS-<TIER>-<INDEX>`).
- Explicit epistemic tier ($A, B, L, C, X$).
- Provenance, verification command, and negative control reference.

### `H9` : Transitive Tier Monotonicity
A higher-tier claim cannot depend on a lower-tier assertion:

$$\text{Sound}(L) := \forall a, b. \, b \in L(a).\text{supports} \implies \text{tier}(L(a)) \le \text{tier}(L(b))$$

Where the total order is: $\text{Tier A} > \text{Tier B} > \text{Tier L} > \text{Tier C} > \text{Tier X}$.

### `H10` : Agent Self-Reports are Not Evidence
An AI agent stating *"the test passed"* or *"the invariant holds"* does not constitute verification. Verification requires running the code independently, capturing exit code 0, validating the SHA-256 certificate hash, and checking the machine ledger.

---

## 2. Epistemic Tier Calculus

```
┌──────────────────────────────────────────────────────────┐
│  Tier A: Lean 4 Kernel Verified                          │  Highest Rigor
│  (zero sorry, #print axioms [propext, choice, quot])     │
├──────────────────────────────────────────────────────────┤
│  Tier B: Exact Deterministic Rational Verifier           │
│  (Arithmetic over ℚ, negative controls mandatory)        │
├──────────────────────────────────────────────────────────┤
│  Tier L: Peer-Reviewed Literature Consensus              │
│  (Exact quoted theorem + verified citation)              │
├──────────────────────────────────────────────────────────┤
│  Tier C: Mathematical Conjecture / Physical Heuristic    │
│  (Plausible hypothesis, unproven, non-blocking)          │
├──────────────────────────────────────────────────────────┤
│  Tier X: Numerical Exploratory Simulation / AI Outputs   │  Lowest Rigor
│  (Floating point, GPU/TPU rollout, cannot gate claims)   │
└──────────────────────────────────────────────────────────┘
```

---

## 3. Mandatory Gate Verification Checklist

Before any PR, release, or milestone commit, the following command must succeed:

```bash
./scripts/verify.sh
```

| Gate | Scope | Criteria |
|---|---|---|
| **Gate 1** | Unit & Exact Invariant Tests | 100% pass rate across Python (`pytest`) and Rust (`cargo test`) suites. |
| **Gate 2** | Audit Certificate Generation | Deterministic `verification_cert.json` generated & schema-verified. |
| **Gate 3** | Mathesis Stream 0 Ledger Audit | Transitive tier monotonicity verified with zero inversions. |
