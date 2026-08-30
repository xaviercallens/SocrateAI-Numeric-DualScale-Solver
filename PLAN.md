# PLAN.md — Execution Plan & Task Routing

**Project:** `SocrateAI-Numeric-DualScale-Solver`  
**Current Milestone:** Milestone 1 — Core Architecture, Dual-Scale Solvers, Exact Verification  
**Updated:** 2026-08-30  

---

## 1. Task Card Summary

| Task ID | Component | Description | Tier | Status |
|---|---|---|---|---|
| `TSK-01` | Governance & Config | Scaffolding (`pyproject.toml`, `.gitignore`, `LICENSE`, `SPEC`, `LEDGER`, `PLAN`, `LL`, `CLAUDE`, `AGENTS`) | T0 | ✅ Complete |
| `TSK-02` | Exact Arithmetic | Implement `exact/t_duality.py` and `exact/cascade_invariants.py` with exact rational arithmetic | T1 | In Progress |
| `TSK-03` | Numerical Solvers | Implement `numeric/rk4_integrator.py`, `numeric/dyadic_cascade.py`, `numeric/fourier_spectral.py` | T1 | In Progress |
| `TSK-04` | Certificate Pipeline | Implement `cert/certificate_generator.py` and `cert/schema.json` | T0 | In Progress |
| `TSK-05` | Verification Suite | Implement test suite in `tests/` with negative controls and `scripts/verify.sh` | T0 | In Progress |
| `TSK-06` | CLI & Benchmarks | Implement `cli.py` and `scripts/run_benchmarks.py` with reproducible outputs | T0 | In Progress |
| `TSK-07` | CI/CD Integration | Create GitHub Actions `.github/workflows/ci.yml` | T0 | In Progress |

---

## 2. Definition of Done (DoD)

A task is marked **DONE** only when:
1. All relevant source code is implemented with docstrings, type annotations, and error handling.
2. Unit tests covering both normal execution and explicit **negative controls** pass with 100% success.
3. Two-gate verification (`./scripts/verify.sh`) executes cleanly without error.
4. Git state is clean and all files are tracked.

---

## 3. Escalation Rules

Stop and escalate when:
- An exact invariant over $\mathbb{Q}$ fails algebraic verification.
- A numerical solver diverges under CFL $\le 0.5$.
- A negative control unexpectedly passes.
