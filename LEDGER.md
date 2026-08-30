# LEDGER.md — Claim & Invariant Inventory

**Status:** CANONICAL CLAIM INVENTORY  
**Rule:** A claim not listed in this ledger has no tier and may not be cited.  
**Last Updated:** 2026-08-30  

---

## 1. Inventory Summary

| Claim ID | Description | Epistemic Tier | Primary File | Negative Control Verified |
|---|---|---|---|---|
| `CLM-DS-01` | $R_{\text{eff}}(R) \ge \sqrt{\alpha'}$ for all $R \in \mathbb{Q}_{>0}$ | **Tier B** | `src/dualscale_solver/exact/t_duality.py` | ✅ Yes (`NC-DS-01`) |
| `CLM-DS-02` | $R_{\text{eff}}(\alpha'/R) = R_{\text{eff}}(R)$ (T-Duality symmetry) | **Tier B** | `src/dualscale_solver/exact/t_duality.py` | ✅ Yes (`NC-DS-02`) |
| `CLM-DS-03` | Enstrophy density bound $\Omega_{\text{eff}} \le 1/\alpha'$ | **Tier B** | `src/dualscale_solver/exact/cascade_invariants.py` | ✅ Yes (`NC-DS-03`) |
| `CLM-DS-04` | Dyadic shell energy conservation in inviscid limit ($\nu=0, f=0$) | **Tier C** / **Tier B** check | `src/dualscale_solver/numeric/dyadic_cascade.py` | ✅ Yes (`NC-DS-04`) |
| `CLM-DS-05` | Exact Leray divergence-free condition $|k \cdot \hat{u}| < 10^{-14}$ | **Tier C** / **Numeric** | `src/dualscale_solver/numeric/fourier_spectral.py` | ✅ Yes (`NC-DS-05`) |
| `CLM-DS-06` | Dual-scale dissipation suppresses finite-time dyadic enstrophy blowup | **Tier C** | `src/dualscale_solver/numeric/dyadic_cascade.py` | ✅ Yes (`NC-DS-06`) |

---

## 2. Negative Controls Catalog

- **`NC-DS-01` (Singularity Penetration)**: Inject a candidate $R_{\text{fake}} < \sqrt{\alpha'}$ with claims that $R_{\text{eff}} < \sqrt{\alpha'}$. Must raise `AssertionError`.
- **`NC-DS-02` (Asymmetry Violation)**: Perturb $R_{\text{eff}}(\alpha'/R) \neq R_{\text{eff}}(R)$ with asymmetric metric $R_{\text{fake}} = R + \epsilon$. Must fail symmetry test.
- **`NC-DS-03` (Enstrophy Overflow)**: Claim $\Omega_{\text{eff}} > 1/\alpha'$ for $R_{\text{eff}} \ge \sqrt{\alpha'}$. Must be rejected algebraically.
- **`NC-DS-04` (Energy Leak Detection)**: Introduce non-antisymmetric triad coupling $(u_{n-1}^2 - 2 u_n u_{n+1})$. Verifier must flag $\frac{dE}{dt} \ne 0$.
- **`NC-DS-05` (Compressibility Leak)**: Introduce non-divergence-free velocity field without projection. Projector verifier must report non-zero divergence before projection and zero after.
- **`NC-DS-06` (Unregularized Cascade Blowup Baseline)**: Compare regularized dual-scale shell cascade against unregularized Euler cascade demonstrating finite-time enstrophy spike.
