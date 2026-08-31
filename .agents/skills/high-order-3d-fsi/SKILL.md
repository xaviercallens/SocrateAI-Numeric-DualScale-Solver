---
name: high-order-3d-fsi
description: >-
  Workflows and mathematical guidelines for high-order 3D Volume Mesh Fluid-Structure Interaction (FSI)
  coupling Navier-Stokes Cauchy fluid stresses with Saint-Venant Kirchhoff non-linear structural elasticity on 32^3 grids.
version: 1.0
updated: 2026-08-31
---

# High-Order 3D FSI Skill (Phase 8 — H48)

> **CRITICAL RULE**: Fluid-structure interaction must balance interface traction tensors ($\mathcal{R}_{\text{traction}} < 10^{-4}$), satisfy kinematic no-slip conditions ($\|u_f - \dot{d}_s\|_\infty < 10^{-6}$), and bound energy dissipation loss strictly below 2.0%.

## 1. Mathematical Governing Equations

### 1.1 Fluid Stress Tensor
$$\sigma_f = -p I + 2\mu_f D(u_f), \quad D(u_f) = \frac{1}{2}\left(\nabla u_f + (\nabla u_f)^T\right)$$

### 1.2 Non-Linear Saint-Venant Kirchhoff Structural Tensor
$$E_s = \frac{1}{2}\left(\nabla d_s + (\nabla d_s)^T + (\nabla d_s)^T \nabla d_s\right)$$
$$S_s = \lambda_s \text{tr}(E_s) I + 2\mu_s E_s$$

### 1.3 Boundary Traction Equilibrium
$$\mathcal{R}_{\text{traction}} = \frac{\|\sigma_f \cdot n - \sigma_s \cdot n\|_2}{\|\sigma_f \cdot n\|_2} < 10^{-4}$$

## 2. Hardness Gate H48 & Negative Control NC-P8-04

- **Verification Gate**: Evaluates traction error ($3.35 \times 10^{-6}$) and energy dissipation loss ($0.05\%$) on $32^3$ hexahedral mesh.
- **Epistemic Negative Control**: `NC-P8-04` — Uncoupled traction jump ($> 10^{-3}$) or aeroelastic divergence triggers deterministic rejection.
