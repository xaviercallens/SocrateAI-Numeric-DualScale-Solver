---
name: dualscale-numeric-solver
description: >-
  Expert guidelines and workflows for running, extending, and verifying dual-scale numerical PDE solvers,
  Katz-Pavlović dyadic cascades, 2D/3D pseudo-spectral Navier-Stokes simulations, exact rational T-duality invariants,
  and generating Tier B audit certificates. Activate when working with dual-scale fluid dynamics, enstrophy control,
  spectral dealiasing, or Leray-Helmholtz projection in this repository.
---

# Dual-Scale Numeric Solver Skill

This skill provides operational and mathematical guidance for working with the **Dual-Scale Numerical Solver** system.

## 1. Mathematical Principles

The dual-scale regularization is governed by:

$$R_{\text{eff}}(R) = \max\left(R, \frac{\alpha'}{R}\right)$$

where $\alpha' > 0$ defines the crossover scale:
- **Macro Continuum Regime ($R \ge \sqrt{\alpha'}$)**: Standard Navier-Stokes advection-diffusion.
- **Micro Bounce Regime ($R < \sqrt{\alpha'}$)**: Ultraviolet modes bounce back to effective infrared scales, bounding dissipation $\Omega_{\text{eff}} \le 1/\alpha'$.
- **T-Duality Invariance**: $R_{\text{eff}}(\alpha'/R) = R_{\text{eff}}(R)$.

## 2. Solver Modules

- **Exact Rational Invariants (`dualscale_solver.exact`)**:
  - Use `RationalDualScale` with `fractions.Fraction` only. Floats are prohibited in Tier B checks.
  - Mandatory negative controls: `negative_control_singularity_violation()`, `negative_control_symmetry_violation()`, `negative_control_broken_energy_conservation()`.

- **Dyadic Shell Cascade (`dualscale_solver.numeric.dyadic_cascade.DyadicShellSolver`)**:
  - Uses integrating factor RK4 (ETD-RK4) for stiff linear dissipation $D_n = \nu k_n^2 \max(1, \alpha' k_n^2)$.
  - Exact triad energy conservation in inviscid limit ($\nu = 0$).

- **2D/3D Pseudo-Spectral NS (`dualscale_solver.numeric.fourier_spectral.PseudoSpectralNavierStokes2D`)**:
  - Exact Orszag $2/3$-dealiasing filter applied to velocity and advective products.
  - Exact Leray projector $\mathcal{P}_{ij}(k) = \delta_{ij} - \frac{k_i k_j}{|k|^2}$ ensuring $|k \cdot \hat{u}| < 10^{-13}$.

## 3. Workflow Procedures

### Running Verification Protocol
```bash
./scripts/verify.sh
```

### Generating Audit Certificate
```bash
python3 -m dualscale_solver.cli verify --output data/verification_cert.json
```

### Running Simulations
```bash
# Dyadic cascade
python3 -m dualscale_solver.cli dyadic --shells 20 --nu 1e-4 --alpha-prime 0.01 --time 1.0

# 2D Pseudo-spectral Taylor-Green
python3 -m dualscale_solver.cli spectral --grid 64 --nu 1e-3 --alpha-prime 0.01 --time 0.5
```
