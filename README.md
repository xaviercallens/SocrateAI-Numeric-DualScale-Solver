# SocrateAI Numeric Dual-Scale Solver

[![CI Verification Protocol](https://github.com/xaviercallens/SocrateAI-Numeric-DualScale-Solver/actions/workflows/ci.yml/badge.svg)](https://github.com/xaviercallens/SocrateAI-Numeric-DualScale-Solver/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Epistemic Tier: Tier B Certified](https://img.shields.io/badge/Epistemic%20Tier-Tier%20B%20Verified-success)](SPEC.md)

**SocrateAI-Numeric-DualScale-Solver** is the computational and numerical dual-scale PDE engine within the SocrateAI ecosystem. It implements multiscale fluid dynamics, dyadic energy cascade simulations, and 2D/3D pseudo-spectral Navier–Stokes solvers governed by exact **T-Dual Effective Scale Regularization**:

$$R_{\text{eff}}(R) = \max\left(R, \frac{\alpha'}{R}\right)$$

---

## Key Capabilities

1. **Exact Rational Invariant Verification (Tier B)**:
   - Zero floating-point roundoff verification over $\mathbb{Q}$ using `fractions.Fraction`.
   - Proof of singularity lower bound $R_{\text{eff}}(R) \ge \sqrt{\alpha'}$.
   - Exact T-duality symmetry: $R_{\text{eff}}(\alpha'/R) = R_{\text{eff}}(R)$.
   - Automated generation of machine-verifiable JSON audit certificates with strict schema validation and negative controls.

2. **Dyadic Shell Cascade Engine (Katz–Pavlović Model)**:
   - High-precision inter-shell non-linear energy transfer $\frac{du_n}{dt} = k_n (u_{n-1}^2 - \lambda u_n u_{n+1})$.
   - Integrating factor Runge–Kutta (ETD-RK4) for stiff dual-scale ultraviolet dissipation.
   - Exact telescoping inviscid energy conservation.

3. **2D/3D Pseudo-Spectral Navier–Stokes Solver**:
   - Machine-precision Leray–Helmholtz divergence-free projection $\mathcal{P}_{ij}(k) = \delta_{ij} - \frac{k_i k_j}{|k|^2}$ ($|k \cdot \hat{u}| < 10^{-13}$).
   - Exact Orszag $2/3$-dealiasing filter eliminating high-frequency aliasing errors.
   - Dual-scale regularized Laplacian dissipation: $\hat{\mathcal{D}}(k) = -\nu |k|^2 \left[ 1 + \alpha' |k|^2 \right]$.

---

## Epistemic Tier Governance

This repository adheres to the SocrateAI epistemic tier framework:

| Epistemic Tier | Formal Standard | Implementation in this Repo |
|---|---|---|
| **Tier A** | Machine-checked Lean 4 formal math (zero sorry, zero custom axioms) | Mapped via [SPEC.md](SPEC.md) to SocrateAI formal certificates. |
| **Tier B** | Exact rational arithmetic ($\mathbb{Q}$) with mandatory negative controls | `src/dualscale_solver/exact/` and `tests/test_exact_*.py`. |
| **Tier C** | High-performance numerical simulation (`float64`, FFT, RK4) | `src/dualscale_solver/numeric/` and benchmark pipelines. |

> [!IMPORTANT]
> Every Tier B verification harness includes an explicit **negative control** (`NC-DS-01`, `NC-DS-02`, `NC-DS-04`) designed to fail if mathematical assumptions or physical conservation laws are broken.

---

## Quick Start

### 1. Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/xaviercallens/SocrateAI-Numeric-DualScale-Solver.git
cd SocrateAI-Numeric-DualScale-Solver
pip install -e ".[dev]"
```

### 2. Run the Two-Gate Verification Protocol

Execute the full verification protocol (Gate 1 unit/exact tests + Gate 2 certificate audit):

```bash
./scripts/verify.sh
```

### 3. CLI Usage

Generate an exact Tier B audit certificate:
```bash
python3 -m dualscale_solver.cli verify --output data/verification_cert.json
```

Run a dyadic shell turbulence cascade simulation:
```bash
python3 -m dualscale_solver.cli dyadic --shells 20 --nu 1e-4 --alpha-prime 0.01 --time 1.0
```

Run a 2D pseudo-spectral Taylor–Green vortex simulation:
```bash
python3 -m dualscale_solver.cli spectral --grid 64 --nu 1e-3 --alpha-prime 0.01 --time 0.5
```

---

## Benchmark Results

Run the full benchmark suite to generate figures and JSON summaries:

```bash
python3 scripts/run_benchmarks.py
```

- **Cascade Enstrophy Boundedness**: Demonstrates that the dual-scale ultraviolet bounce operator unconditionally suppresses finite-time enstrophy spikes while preserving macroscopic inertial cascades.
- **Taylor–Green Incompressibility**: Maintains divergence-free velocity $\nabla \cdot u = 0$ to $< 10^{-13}$ throughout continuous viscous decay.

---

## Project Structure

```
SocrateAI-Numeric-DualScale-Solver/
├── .github/workflows/ci.yml       # GitHub Actions CI workflow
├── src/dualscale_solver/
│   ├── exact/                     # Tier B exact rational invariants
│   │   ├── t_duality.py           # Rational Reff, bounce law, negative controls
│   │   └── cascade_invariants.py  # Telescoping dyadic shell energy bounds
│   ├── numeric/                   # Tier C numerical PDE solvers
│   │   ├── rk4_integrator.py      # Integrating factor & SSP-RK4 integrators
│   │   ├── dyadic_cascade.py      # Katz-Pavlović dyadic shell model
│   │   └── fourier_spectral.py    # 2D pseudo-spectral Navier-Stokes
│   ├── cert/                      # Audit certificate generator & JSON schema
│   │   ├── certificate_generator.py
│   │   └── schema.json
│   └── cli.py                     # Unified CLI entry point
├── tests/                         # Test suite with 100% negative control coverage
├── scripts/
│   ├── verify.sh                  # Two-gate verification script
│   └── run_benchmarks.py          # Benchmark runner
├── figures/                       # Benchmark visualization artifacts
├── SPEC.md                        # Formal specification
├── LEDGER.md                      # Claims and theorems ledger
├── PLAN.md                        # Task cards and Definition of Done
├── LL.md                          # Lessons learned and numerical gotchas
├── NAMING_POLICY.md               # Scientific naming rules
├── pyproject.toml                 # Build configuration
└── LICENSE                        # MIT License
```

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
