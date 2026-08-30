# LL.md — Lessons Learned & Gotchas

**Repository:** `SocrateAI-Numeric-DualScale-Solver`  
**Updated:** 2026-08-30  

---

## 1. Mathematical & Computational Gotchas

### LL-01: Float vs Exact Rational Arithmetic in Epistemic Gates
- **Gotcha**: Testing $R_{\text{eff}}(R)$ with Python standard floats (`float64`) can cause subtle round-off deviations near $\sqrt{\alpha'}$ (e.g. $10^{-16}$ differences), corrupting identity checks.
- **Rule**: All Tier B verification harnesses must use `fractions.Fraction` or exact integer lattices.

### LL-02: 2/3 Rule Dealiasing in Pseudo-Spectral Navier-Stokes
- **Gotcha**: Evaluating non-linear advection $(u \cdot \nabla) u$ directly via FFT on an $N \times N$ grid produces aliasing errors when high-frequency modes fold into lower modes.
- **Rule**: Apply the Orszag $2/3$-dealiasing filter: zero out all Fourier modes with $|k_i| > \frac{2}{3} \frac{N}{2}$ before and after non-linear product evaluation.

### LL-03: Leray-Helmholtz Incompressibility Condition
- **Gotcha**: Standard time-stepping without projection allows numerical compressibility errors to accumulate over time.
- **Rule**: Apply the exact projection $\hat{u}(k) \gets \hat{u}(k) - \frac{k (k \cdot \hat{u}(k))}{|k|^2}$ at every RK4 sub-step to maintain machine-precision divergence-free state ($\nabla \cdot u = 0$).

### LL-04: Dyadic Shell Triad Antisymmetry
- **Gotcha**: The Katz-Pavlović dyadic shell model requires exact antisymmetry in inter-shell energy transfer ($\sum_n \dot{u}_n u_n = 0$) in the inviscid limit.
- **Rule**: Ensure the coupling coefficient $\lambda = 2$ exactly matches the backward shell index shift so that $u_n (k_n u_{n-1}^2 - k_n \lambda u_n u_{n+1})$ telescopes over all shells.
