# LEDGER.md — Canonical Claim & Invariant Inventory

**Status:** CANONICAL CLAIM INVENTORY  
**Epistemic Standard:** Mathesis Stream 0 5-Tier Calculus ($A > B > L > C > X$)  
**Soundness Condition:** $\forall a, b. \, b \in L(a).\text{supports} \implies \text{tier}(L(a)) \le \text{tier}(L(b))$  
**Last Updated:** 2026-08-30  

---

## 1. Inventory Summary

| Claim ID | Tier | Description | Evidence Kind | Artifact / Citation |
|---|---|---|---|---|
| `DS-A-0001` | **A** | $R_{\text{eff}}(R) = \max(R, \alpha/R) \ge \sqrt{\alpha}$ for all $R > 0$ | `lean_axioms` | `lean4/HoloEngine/DualScale.lean:Reff_ge_sqrt` |
| `DS-B-0001` | **B** | Exact rational $R_{\text{eff}}(R)^2 \ge \alpha$ for all $R \in \mathbb{Q}_{>0}$ | `exact_harness` | `src/dualscale_solver/exact/t_duality.py` (`NC-DS-01`) |
| `DS-B-0002` | **B** | Exact rational T-duality symmetry $R_{\text{eff}}(\alpha/R) \equiv R_{\text{eff}}(R)$ over $\mathbb{Q}$ | `exact_harness` | `src/dualscale_solver/exact/t_duality.py` (`NC-DS-02`) |
| `DS-B-0003` | **B** | Dyadic triad energy transfer telescopes to zero in inviscid limit | `exact_harness` | `src/dualscale_solver/exact/cascade_invariants.py` (`NC-DS-04`) |
| `DS-L-0001` | **L** | Ladyzhenskaya 2D Navier–Stokes global regularity theorem | `citation` | Ladyzhenskaya (1969), *Math. Theory Viscous Incompressible Flow*, Thm 1 |
| `DS-C-0001` | **C** | Dual-scale ultraviolet dissipation bounds 3D enstrophy blowup | `numeric` | `src/dualscale_solver/numeric/dyadic_cascade.py` |
| `DS-X-0001` | **X** | Pseudo-spectral 2D Taylor–Green vortex monotonic dissipation | `numeric` | `src/dualscale_solver/numeric/fourier_spectral.py` |

---

## 2. Negative Controls Catalog

- **`NC-DS-01` (Singularity Penetration)**: Inject unregularized scale $R_{\text{fake}} < \sqrt{\alpha'}$. Must trigger hard failure.
- **`NC-DS-02` (T-Duality Asymmetry)**: Inject asymmetric perturbation $R_{\text{fake}} = R + \epsilon$. Must fail symmetry check.
- **`NC-DS-04` (Energy Leak)**: Perturb triad coupling ratio $\lambda \ne 2$. Must flag $\frac{dE}{dt} \ne 0$.
