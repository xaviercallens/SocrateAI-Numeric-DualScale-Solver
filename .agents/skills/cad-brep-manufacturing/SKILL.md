---
name: cad-brep-manufacturing
description: >-
  Workflows and algorithmic guidelines for converting 2D frustration-minimized flow solutions into watertight 3D B-Rep solid CAD geometries
  (STEP AP214 / IGES 5.3) using the OpenCASCADE kernel. Enforces the Euler-Poincaré topological characteristic V - E + F = 2(1 - g)
  and prepares manufacturing-grade 5-axis CNC milling toolpath geometries.
version: 1.0
updated: 2026-08-31
---

# CAD B-Rep Manufacturing Skill (Phase 8 — H46)

> **CRITICAL RULE**: All exported CAD models must adhere strictly to ISO-10303-21 text syntax, maintain watertight manifold topologies, pass the Euler-Poincaré invariant ($\chi = 2$), and feature SHA-256 cryptographic provenance.

## 1. OpenCASCADE 3D Solid Lofting Workflow

1. **Camber Ingestion**: Ingest 2D optimized camber arrays $y_c(x)$ minimizing Triadic Frustration Index $\mathcal{D}(M)$.
2. **Thickness Distribution**: Apply continuous 4-digit airfoil thickness envelope $y_t(x)$.
3. **Spanwise Lofting**: Generate $N_{\text{span}}$ sectional cross-sections along the span $z \in [0, L_{\text{span}}]$.
4. **B-Rep Shell Assembly**: Form quadrilateral lofted faces and seal root/tip planar end-caps.
5. **Topological Euler-Poincaré Verification**:
   $$\chi(M) = V - E + F = 2(1 - g) = \mathbf{2} \quad (\text{for genus } g=0)$$
6. **Enclosed Volume Calculation**:
   $$V_{\text{solid}} = \frac{1}{6} \sum_{f \in F} \left( v_{1,f} \cdot (v_{2,f} \times v_{3,f}) \right) > 0$$

## 2. Hardness Gate H46 & Negative Control NC-P8-02

- **Verification Gate**: Confirms ISO-10303-21 schema compliance, non-negative enclosed volume ($0.2040\,\text{m}^3$), $\chi = 2$, and SHA-256 provenance hash.
- **Epistemic Negative Control**: `NC-P8-02` — Non-manifold edges, open seams ($\chi \ne 2$), or negative volume triggers deterministic rejection.
