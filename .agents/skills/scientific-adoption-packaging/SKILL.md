---
name: scientific-adoption-packaging
description: >-
  Workflows, packaging standards, and benchmarking protocols for maximizing scientific and industrial adoption
  of dual-scale PDE solvers: ISO-10303-21 STEP CAD generation, JHTDB spectral validation, zero-dependency C-ABI
  bindings (libleanflow.so), ANSI C99 headers, PyPI wheels, and lightweight Docker containers.
version: 1.0
tier: T1/T0
target_model: gemini-3.8-flash
reasoning_budget: high
---

# Scientific & Industrial Adoption Packaging

To achieve widespread scientific adoption across academic research groups and aerospace/biomedical engineering enterprises, numerical solver artifacts must be transparent, modular, mathematically standardized, and interoperable with existing industrial toolchains.

---

## 4 Pillars of Scientific & Industrial Adoption

```
┌────────────────────────────────────────────────────────┐
│  Pillar 1: Standard CAD / Manufacturing Export         │
│  - Watertight ISO-10303-21 STEP AP203/AP214 solids     │
└──────────────────────────┬─────────────────────────────┘
                           │
┌──────────────────────────▼─────────────────────────────┐
│  Pillar 2: Standard Reference Benchmarking             │
│  - Johns Hopkins Turbulence Database (JHTDB) & OpenFOAM│
└──────────────────────────┬─────────────────────────────┘
                           │
┌──────────────────────────▼─────────────────────────────┐
│  Pillar 3: Zero-Dependency Native C-ABI Interface      │
│  - ANSI C99/C++17 headers (leanflow.h) & libleanflow.so│
└──────────────────────────┬─────────────────────────────┘
                           │
┌──────────────────────────▼─────────────────────────────┐
│  Pillar 4: Reproducible Container & PyPI Distribution   │
│  - Universal wheels + slim OCI containers (< 150 MB)   │
└────────────────────────────────────────────────────────┘
```

---

## Pillar 1: CAD & Computational Geometry (STEP AP203/AP214)

Industrial adoption requires converting numerical flow optima into physical hardware without manual geometric translation.

1. **OpenCASCADE Solid Kernel Integration**:
   - Construct B-Spline camber curves via `B_SPLINE_CURVE_WITH_KNOTS` with continuous second derivatives ($C^2$).
   - Loft 2D camber profiles into 3D B-Rep manifold volumes satisfying the Euler-Poincaré topological formula:
     $$V - E + F = 2(1 - g)$$
2. **Deterministic Provenance Sealing**:
   - Every generated STEP model must embed the SHA-256 digest of the simulation optimization in the ISO-10303-21 header:
     ```
     /* ISO-10303-21;
        HEADER;
        FILE_DESCRIPTION(('LeanFlow DualScale Solid Blade'),'2;1');
        FILE_NAME('blade_opt.step','2026-09-03',('SocrateAI'),('IndustrialDesign'),'OpenCASCADE 7.7','LeanFlow','SHA256:...');
     */
     ```

---

## Pillar 2: Reference Validation Benchmarking (JHTDB & OpenFOAM)

Scientific credibility depends on reproducible comparisons against community gold standards.

1. **Johns Hopkins Turbulence Database (JHTDB)**:
   - Validate dual-scale spectral velocity fields against the $1024^3$ isotropic turbulence dataset at $Re_\lambda \approx 433$.
   - Confirm Kolmogorov energy spectrum scaling:
     $$E(k) \propto \varepsilon^{2/3} k^{-5/3} f_L(k L) f_\eta(k \eta)$$
   - Calculate Kolmogorov dissipation cutoff satisfaction: $k_{\max} \eta \ge 1.5$.
2. **OpenFOAM / SU2 Cross-Validation**:
   - Provide standard OpenFOAM test case dictionaries (`system/controlDict`, `constant/transportProperties`) comparing wall-shear stress and velocity profiles with dual-scale surrogate predictions.

---

## Pillar 3: Zero-Dependency C-ABI Bindings (`libleanflow.so`)

Enterprise adopters require seamless embedding into legacy Fortran, C, C++, or Python simulation pipelines.

1. **ANSI C99 / C++17 Header (`leanflow.h`)**:
   - Strictly avoid proprietary compiler extensions.
   - Provide clear opaque handles (`leanflow_solver_t*`) and thread-safe error reporting.
2. **Symbol Verification**:
   - Ensure `nm -D libleanflow.so` exhibits zero undefined symbols (`U`) for core computational math routines.

---

## Pillar 4: Appliance Packaging & Reproducibility

1. **PyPI Binary Wheels**:
   - Build `manylinux_2_28_x86_64` and `manylinux_2_28_aarch64` wheels with zero external shared library dependencies.
2. **OCI Appliance Container**:
   - Keep final compressed Docker image size strictly below 150 MB.
   - Enforce reproducible multi-stage builds (`debian:bookworm-slim` or `alpine`).
