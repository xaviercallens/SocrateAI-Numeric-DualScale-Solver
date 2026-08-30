# CLAUDE.md

This file provides guidance to Claude Code and AI assistants when working with code in this repository.

## What this repository is

**SocrateAI-Numeric-DualScale-Solver** is the computational and numerical dual-scale PDE solver engine within the SocrateAI ecosystem. It implements:
1. Exact rational arithmetic invariants for T-duality scale regularization ($R_{\text{eff}}(R) = \max(R, \alpha'/R)$).
2. Multi-scale dyadic shell cascade simulations (Katz-Pavlović model) with dual-scale ultraviolet bounce regularization.
3. 2D/3D pseudo-spectral Navier-Stokes solvers with Orszag 2/3 dealiasing and exact Leray-Helmholtz divergence-free projection.
4. Automated Tier B/A certificate generation with JSON schema validation and negative controls.

## Epistemic Tier System

- **Tier A**: Formal proofs compiled by Lean 4 / Mathlib (zero sorry, zero custom axioms).
- **Tier B**: Exact rational arithmetic (`fractions.Fraction` or `int`), algebraic invariants, with explicit **negative controls** that are demonstrated to fail when falsified.
- **Tier C**: Floating-point numerical solvers (`float64`, FFT, RK4, ODE/PDE integrators).

## Key Commands

Run the full two-gate verification:
```bash
./scripts/verify.sh
```

Run test suite:
```bash
pytest -v tests/
```

Run exact rational checks:
```bash
python3 -m tests.test_exact_tduality
```

Run benchmark simulations:
```bash
python3 scripts/run_benchmarks.py
```

CLI entry point:
```bash
python3 -m dualscale_solver.cli --help
```

## Architecture & Code Guidelines

- **`src/dualscale_solver/exact/`**: No floats allowed. Use `fractions.Fraction` and exact algebra.
- **`src/dualscale_solver/numeric/`**: High-performance NumPy / SciPy numerical implementations with clean vectorized operations.
- **`src/dualscale_solver/cert/`**: Machine-verifiable audit certificates conforming to `schema.json`.
- **`tests/`**: Every test module must include positive verification and negative control assertions.
