---
name: scientific-peer-review
description: >-
  Wave-enabled scientific peer review and hardness auditor adapting antigravity-gemini-skills review workflows.
  Enforces statistical significance (p < 0.05, n >= 20), eliminates banned pseudoscientific buzzwords,
  inspects nonlinear transfer balance, audits Lean 4 proofs, and prevents surrogate scope inflation.
version: 1.0
tier: T2
target_model: gemini-3.1-pro
reasoning_budget: high
---

# Scientific Peer Review & Hardness Auditor

This skill establishes a rigorous, automated **Scientific Peer Review** protocol adapted from `antigravity-gemini-skills` for computational physics, fluid dynamics, and numerical PDE codebases.

Every pull request, manuscript draft, docstring, and audit certificate must pass this review prior to merging or publication.

---

## The 5 Scientific Gate Invariants

```
┌────────────────────────────────────────────────────────┐
│  Gate 1: Statistical Significance & Sample Size        │
│  - Enforce p < 0.05 and n >= 20 on all sweeps          │
└──────────────────────────┬─────────────────────────────┘
                           │
┌──────────────────────────▼─────────────────────────────┐
│  Gate 2: Epistemic Nomenclature & Buzzword Purge       │
│  - Zero banned pseudoscientific terminology            │
└──────────────────────────┬─────────────────────────────┘
                           │
┌──────────────────────────▼─────────────────────────────┐
│  Gate 3: Mathematical Completeness (Nonlinear Terms)   │
│  - Inclusion of vortex stretching T(t) in 3D enstrophy │
└──────────────────────────┬─────────────────────────────┘
                           │
┌──────────────────────────▼─────────────────────────────┐
│  Gate 4: Surrogate Scope Demarcation                   │
│  - ROM outputs != clinical/physical optimizations      │
└──────────────────────────┬─────────────────────────────┘
                           │
┌──────────────────────────▼─────────────────────────────┐
│  Gate 5: Lean 4 Proof Verification Integrity           │
│  - 'sorry' stubs == Roadmap, NOT 'Verified'            │
└────────────────────────────────────────────────────────┘
```

---

## Review Gate Specifications

### 1. Statistical Significance (Spearman $\rho$ and $p$-Value)
- **Hard Rule**: Any claim asserting that a reduced-order model (ROM) provides "directional utility", "rank preservation", or "monotonic parameter guidance" MUST report both Spearman rank correlation ($\rho$) and the two-tailed $p$-value with a sample size $n \ge 20$.
- **Rejection Trigger**: If $p \ge 0.05$, the correlation is statistically indistinguishable from random noise. The claim of directional utility must be **retracted or caveated as unverified**.

### 2. Epistemic Nomenclature Compliance
Per `AGENTS.md` Guardrail 2 and `NAMING_POLICY.md`, inspect all code, docstrings, commits, and reports for banned buzzwords:
- ❌ **BANNED**: `"Rulial Inversion"` $\implies$ ✅ **USE**: `"Wavenumber-Dependent Scale Thresholding"` or `"Dual-Scale Regularization"`
- ❌ **BANNED**: `"Holographic Regularisation"` $\implies$ ✅ **USE**: `"Empirical Disruption Threshold"`
- ❌ **BANNED**: `"Karpathy Ratchet Auto-Research Loop"` $\implies$ ✅ **USE**: `"Monotonic Greedy Line Search with Backtracking"`

### 3. Mathematical Completeness (Theorem 2.1 & Enstrophy Bounds)
- When bounding enstrophy growth:
  $$\frac{d\Omega}{dt} = -2\nu \sum k^2 |\omega_k|^2 - 2\alpha' \sum k^4 |\omega_k|^2 + T_\Omega(t)$$
- Ensure that derivations do not quietly drop the nonlinear production/transfer term $T_\Omega(t)$ in 3D.
- In 1D or 2D systems, explicitly state that $T_\Omega(t) = 0$ is a consequence of dimensionality (orthogonality of velocity and vorticity), not an unconditional Navier-Stokes property.

### 4. Surrogate Scope Demarcation (Modesty in Applications)
- 1D/2D Fourier spectral toy models with heavy biharmonic damping ($-\alpha' k^4$) heavily smooth high-wavenumber velocity gradients.
- **Mandatory Caveat**: Reductions in wall shear stress or enstrophy in a $N=32$ ROM must never be advertised as "clinical safety in ventricular assist devices" or "shock boundary-layer control in scramjets" without full 3D boundary-layer CFD / OpenFOAM / SU2 validation.
- All such findings must be framed with epistemic modesty: *"In the 1D/2D surrogate regime, parameter exploration demonstrates..."*

### 5. Lean 4 Formal Verification Audit
- Execute `lake build` programmatically.
- Scan for `sorry` stubs across `lean4/`.
- If any non-exempt `sorry` exists, label the file as **"Formal Specification Roadmap" (Tier B)**. Any report calling it "Formally Verified" is a hard failure.

---

## Review Output Contract (JSON)

When invoked as a subagent or review pass, return:

```json
{
  "gate_status": "PASSED | FAILED",
  "violations": [],
  "statistical_audit": {
    "sample_size_valid": true,
    "p_values_valid": true
  },
  "nomenclature_audit": {
    "banned_terms_count": 0,
    "banned_terms_found": []
  },
  "lean4_audit": {
    "lake_exit_code": 0,
    "sorry_count": 0,
    "classification": "FORMAL_SPECIFICATION_ROADMAP | VERIFIED"
  },
  "_measured": true
}
```
