---
name: enterprise-productization
description: >-
  Expert workflows and standards for commercial enterprise productization of LeanFlow dual-scale PDE solvers,
  including universal Python binary wheels (PyPI), zero-dependency native C-ABI shared libraries (libleanflow.so),
  ANSI C99/C++17 headers (leanflow.h), standalone Rust CLI binaries, and lightweight OCI/Docker HPC container appliances (< 150 MB).
  Activate when packaging, compiling, or validating commercial software distributions for Phase 8.
version: 1.0
updated: 2026-08-31
---

# Enterprise Productization Skill (Phase 8 — H49)

> **CRITICAL RULE**: All distributed libraries, binary wheels, and container images must be verified for zero unresolved dynamic symbols, cross-platform ABI stability, and exact memory layouts. No synthetic build artifacts or unmeasured binary sizes.

## 1. Productization Packaging Standards

### 1.1 Universal Python Binary Wheels (`pip install leanflow`)
- Target tags: `manylinux2014_x86_64`, `macos_arm64`, `win_amd64`.
- Pre-compiled SIMD AVX-512, AVX2, and ARM NEON acceleration routines.
- Compressed wheel package size strictly $< 25\,\text{MB}$ (target: $\approx 12.4\,\text{MB}$).
- Automated PyO3 bindings exposing both high-level Python solver classes and low-level zero-copy NumPy buffer pointers.

### 1.2 Zero-Dependency Native C-ABI (`libleanflow.so` / `leanflow.h`)
- Strict ANSI C99 / C++17 compatible header [`leanflow.h`](file:///home/xavkal/xdev/SocrateAI-Numeric-DualScale-Solver/SocrateAI-Numeric-DualScale-Solver/src/dualscale_solver/deploy/package_enterprise.py).
- Exported C-ABI symbols:
  - `leanflow_solver_create(grid_n, alpha_prime, nu)`
  - `leanflow_solver_destroy(solver)`
  - `leanflow_solve_step(solver, dt)`
  - `leanflow_compute_enstrophy(solver)`
  - `leanflow_enforce_leray_projection(solver)`
  - `leanflow_compute_triadic_frustration(solver, m_order)`
  - `leanflow_fsi_couple_step(solver, p_int, v_int)`
  - `leanflow_stream_telemetry(solver, grpc_endpoint)`
  - `leanflow_verify_license_token(ed25519_token, org_id)`
- Zero unresolved external dependencies (statically linked standard runtime).

### 1.3 Lightweight OCI / Docker Container Appliance
- Base image: `alpine:latest` or `rockylinux:9-minimal`.
- Includes optimized BLAS/LAPACK, SUNDIALS CVODE, OpenMPI, and CUDA/ROCm hooks.
- Total compressed image size strictly $< 150\,\text{MB}$ (target: $\approx 118.5\,\text{MB}$).

## 2. Hardness Gate H49 & Negative Control NC-P8-05

- **Verification Gate**: `package_enterprise.py` verifies all 9 C-ABI symbols, checks C header syntax, and asserts Docker compressed size $< 150\,\text{MB}$.
- **Epistemic Negative Control**: `NC-P8-05` — Deliberately inject missing C symbols or bloated container image size ($> 250\,\text{MB}$). Must trigger hard rejection.
