---
name: ai-preprocessing-mesh-bc
description: >-
  Workflows and algorithmic guidelines for Neuro-Symbolic AI Preprocessing, dynamic mesh resolution estimation,
  Kolmogorov dissipation cutoff validation, Fourier Leray solenoidal boundary condition projection, and stiffness-based
  time integrator selection (rusty-SUNDIALS BDF vs Adams). Activate when initializing simulations, analyzing flow fields,
  or testing Phase 5 AI preprocessing components.
version: 1.0
updated: 2026-08-31
---

# AI Preprocessing & Boundary Condition Skill (Phase 5)

## 1. Core Physics & Kolmogorov Resolution Law

For any turbulent or transition flow with kinematic viscosity $\nu$, kinetic energy $E$, and enstrophy $\Omega$:
1. Dissipation rate: $\epsilon = 2 \nu \Omega$
2. Kolmogorov microscale: $\eta = (\nu^3 / \epsilon)^{1/4}$
3. Taylor microscale: $\lambda = \sqrt{15 \nu u_{\text{rms}}^2 / \epsilon}$, with $Re_\lambda = u_{\text{rms}} \lambda / \nu$
4. **Resolution Gate (H20)**: $k_{\max} \eta \ge 1.5$, where $k_{\max} = N/3$ under Orszag 2/3 dealiased pseudo-spectral grids.

$$\text{Required } N \ge \frac{4.5}{\eta} \cdot \frac{L}{2\pi}$$

## 2. Boundary Condition Projection

- **Solenoidal Leray Projection**:
  $$\mathcal{P}_{ij}(k) = \delta_{ij} - \frac{k_i k_j}{|k|^2}, \quad k \cdot \mathcal{P}(k) \hat{u} \equiv 0$$
- Eliminates divergence in $\mathcal{O}(N^d \log N)$ FFT operations without iterative pressure-Poisson solving.
- Mandates $\max |\nabla \cdot u| < 10^{-12}$.

## 3. Automated Time-Integrator Tuning

- Compute stiffness ratio $\sigma = \Delta t_{\text{advective}} / \Delta t_{\text{diffusive}} = (\Delta x / u_{\max}) / (\Delta x^2 / (2 d \nu))$.
- **If $\sigma > 2.0$ or $Re_\lambda > 100$**: Select stiff CVODE BDF (orders 2–5) with Spectral Fourier Gate (P1) or TensorCore AMG (P3).
- **If $\sigma \le 2.0$**: Select Adams-Moulton (orders 2–12) with Mixed-Precision FGMRES (P2).
