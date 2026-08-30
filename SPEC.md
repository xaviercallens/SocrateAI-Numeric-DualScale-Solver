# SPEC.md — Dual-Scale Numerical Solver Specification

**Status:** NORMATIVE  
**Epistemic Standard:** Tier A / B / C Gated  
**Target Repository:** `SocrateAI-Numeric-DualScale-Solver`  
**Date:** 2026-08-30  

---

## 1. Executive Summary

This repository implements the **Dual-Scale Numerical Solver** architecture for multiscale fluid dynamics, hydrodynamic energy cascades, and non-linear partial differential equations. The core mathematical principle is the **T-Dual Effective Scale Regularization**:

$$R_{\text{eff}}(R) = \max\left(R, \frac{\alpha'}{R}\right)$$

where $\alpha' > 0$ represents the fundamental crossover / regularization scale.

The dual-scale framework guarantees:
1. **Singularity Avoidance**: $R_{\text{eff}}(R) \ge \sqrt{\alpha'}$ for all $R > 0$.
2. **Dual-Scale Bounce Regime**: For $R < \sqrt{\alpha'}$, $R_{\text{eff}}(R) = \frac{\alpha'}{R}$ (ultraviolet modes mirror to infrared effective scales).
3. **Inertial Continuum Regime**: For $R \ge \sqrt{\alpha'}$, $R_{\text{eff}}(R) = R$ (standard macroscopic PDE mechanics).
4. **T-Duality Invariance**: $R_{\text{eff}}\left(\frac{\alpha'}{R}\right) = R_{\text{eff}}(R)$.
5. **Universal Enstrophy Boundedness**: The associated effective dissipation / enstrophy density $\Omega_{\text{eff}} \le \frac{1}{\alpha'}$ is unconditionally bounded.

---

## 2. Solver Architecture

The solver is divided into three functional pillars:

```
SocrateAI-Numeric-DualScale-Solver/
├── src/dualscale_solver/
│   ├── exact/                     # [Tier B] Exact rational arithmetic & invariants
│   │   ├── t_duality.py           # Rational Reff, bounce law, symmetric square locks
│   │   └── cascade_invariants.py  # Telescoping dyadic shell energy-enstrophy invariants
│   ├── numeric/                   # [Tier C] High-performance numerical PDE engines
│   │   ├── dyadic_cascade.py      # Katz-Pavlović dyadic shell model with dual-scale bounce
│   │   ├── fourier_spectral.py    # 2D/3D pseudo-spectral NS solver with 2/3 dealiasing & Leray projection
│   │   └── rk4_integrator.py      # Symplectic / SSP-RK4 time integrator with adaptive CFL
│   ├── cert/                      # [Tier B/A] Verification & audit certificate pipeline
│   │   ├── certificate_generator.py # Audit certificate producer & validator
│   │   └── schema.json            # Machine-readable JSON schema
│   └── cli.py                     # Unified CLI entry point
```

---

## 3. Mathematical Formulations

### 3.1 Dyadic Shell Cascade (Katz–Pavlović Model)

The dyadic shell model decomposes velocity into shell amplitudes $u_n(t)$ at wavenumbers $k_n = k_0 \lambda^n$ (with inter-shell ratio $\lambda = 2$ or golden ratio):

$$\frac{d u_n}{dt} = k_n \left( u_{n-1}^2 - \lambda u_n u_{n+1} \right) - \nu k_n^2 u_n + f_n$$

Under standard Navier-Stokes cascade, energy flux transfers to $n \to \infty$, potentially triggering finite-time enstrophy blow-up as $u_n$ scales. Under **Dual-Scale Regularization**, the effective wavenumber $\kappa_n$ or dissipation operator is replaced by:

$$\kappa_n = \min\left(k_n, \frac{1}{\sqrt{\alpha'}}\right) \quad \text{or} \quad \nu_{\text{eff}}(n) = \nu k_n^2 \max\left(1, \alpha' k_n^2\right)$$

which enforces the bounce condition at $k_n > k_* = 1/\sqrt{\alpha'}$.

### 3.2 2D/3D Incompressible Navier-Stokes Pseudo-Spectral Solver

$$\frac{\partial u}{\partial t} + (u \cdot \nabla) u = -\nabla p + \nu \nabla^2 u + f, \quad \nabla \cdot u = 0$$

In Fourier space:
1. **Leray-Helmholtz Projector**:
   $$\mathcal{P}_{ij}(k) = \delta_{ij} - \frac{k_i k_j}{|k|^2}, \quad \mathcal{P}(k) \hat{u}(k) \implies k \cdot \hat{u}(k) \equiv 0$$
2. **Dealiasing**: Orszag $2/3$ rule truncating modes with $|k_i| > \frac{2}{3} k_{\text{max}}$.
3. **Dual-Scale Dissipation**:
   $$\hat{\mathcal{D}}(k) = -\nu |k|^2 \left[ 1 + \alpha' |k|^2 \right]$$

---

## 4. Epistemic Gates & Verification

- **Gate 1 (Unit & Exact Invariants)**: All tests in `tests/` execute with 0 failures; exact rational invariants verify over $\mathbb{Q}$.
- **Gate 2 (Audit Certificates & Negative Controls)**: Generated certificates must pass strict JSON schema validation, and all negative controls must trigger certified verification rejections.
