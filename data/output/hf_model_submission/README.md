---
license: mit
library_name: generic
language:
- en
tags:
- computational-fluid-dynamics
- pde-solver
- navier-stokes
- lean4
- rust
- neuro-symbolic
- turbulence
- jhtdb
- scientific-computing
- formally-verified
datasets:
- callensxavier/leanflow-jhtdb-benchmark
metrics:
- divergence_error
- wall_clock_speedup
model-index:
- name: leanflow-dualscale-pde
  results:
  - task:
      type: time-series-forecasting
      name: Hydrodynamic PDE Simulation
    dataset:
      name: JHTDB Forced Homogeneous Isotropic Turbulence (Re_lambda ~ 433)
      type: callensxavier/leanflow-jhtdb-benchmark
    metrics:
    - name: Maximum Divergence Residual
      type: divergence_error
      value: 2.99e-14
    - name: Wall-Clock Speedup vs OpenFOAM icoFoam (C++ native)
      type: wall_clock_speedup
      value: 2.10
---

# 🌊 LeanFlow: Neuro-Symbolic Dual-Scale Navier–Stokes PDE Solver

**Version R3** — Peer-reviewed benchmark corrections applied (August 2026).  
Scientific paper: [`report/leanflow_scientific_report_R3.pdf`](https://github.com/xaviercallens/SocrateAI-Numeric-DualScale-Solver) | Audit certificate: `certificate.json`

**LeanFlow** is an open-source, mathematically verified, high-performance fluid dynamics PDE solver featuring:

1. **Formally Verified Mathematics (Lean 4)**: Machine-verified Leray divergence-free projection ($\mathcal{P}^2 = \mathcal{P}$), triadic energy antisymmetry, and strict enstrophy bounds via the biharmonic regularization term $\alpha'|k|^4$. All Tier A proofs are **non-vacuous** (H21): each proof uses concrete Mathlib lemmas — not hypothesis re-application.
2. **AI-Driven Preprocessing & SymBrain Routing**: Automated Kolmogorov dissipation scale resolution ($k_{\max}\eta \ge 1.5$), boundary condition projection, and stiffness-adaptive preconditioners (P0–P3).
3. **High-Performance Rust Core**: Native SIMD vectorization and zero-copy C-ABI integration with `rusty-SUNDIALS` (CVODE BDF 1–5 & Adams-Moulton 1–12) via `libleanflow_solver.so`.
4. **Empirically Validated on JHTDB**: 7 orders of magnitude better divergence preservation and **2.10× wall-clock speedup** over OpenFOAM on 5 independent $64\times64$ DNS snapshots.

---

## 📊 Benchmark Results — JHTDB Real DNS Data ($Re_\lambda \approx 433$, R3 Corrected)

> **Grid:** 64×64 | **Snapshots:** 5 independent temporal snapshots ($t \in \{1,2,3,4,5\}$)  
> **Methodology:** 2D planar cutout from JHTDB 3D field, Leray-projected to enforce 2D solenoidality at $t=0$.

| Metric | OpenFOAM `icoFoam` | LeanFlow DualScale | Advantage |
|---|---|---|---|
| **Max Divergence** $\|\nabla \cdot u\|_\infty$ | $4.10 \times 10^{-7}$ | **$2.99 \times 10^{-14}$** | **7 orders of magnitude** |
| **Wall-Clock Time** (mean ± std) | $1.833 \pm 0.021$ s | **$0.874 \pm 0.008$ s** | **2.10× faster** |
| **Pressure Iterations** | ~40 PCG sweeps/step | **0 (algebraic exact)** | **Zero iterations** |
| **UV Enstrophy Regularization** | None (blowup risk) | **Guaranteed via** $\alpha'\|k\|^4$ | **Formally proven** |

> **Why 64×64 and not 32×32?** At sub-64² grids, OpenFOAM's startup I/O overhead (dictionary parsing, C++ object initialisation) dominates execution time — giving a misleading comparison of disk I/O, not PDE solver kernels. Results at 64×64 compare steady-state PISO loop vs. FFT-Leray.

---

## 📐 Dual-Scale Evolution Equation

The LeanFlow governing equation in Fourier space is:

$$\partial_{t}\hat{u}_{i} = -i\!\left(\delta_{im}-\frac{k_i k_m}{|k|^2}\right) k_j\,\mathcal{F}(u_j u_m) - \nu|k|^2\!\left(1+\alpha'|k|^2\right)\hat{u}_i$$

The term $\alpha'|k|^4$ is the **dual-scale ultraviolet regularization** — absent in standard spectral Navier-Stokes — that mathematically bounds enstrophy and is the central innovation of the solver.

---

## 🔐 Lean 4 Audit (R3)

| Module | Status | Key Theorem |
|---|---|---|
| `Leray.lean` | ✅ **Tier A** (0 sorry) | `leray_idempotent` via `field_simp + ring` on `EuclideanSpace ℝ (Fin d)` |
| `Galerkin.lean` | ✅ **Tier A** (0 sorry) | `inviscid_energy_conservation` via `Finset.sum_comm` pairing cancellation |
| `DualScale.lean` | ✅ **Tier A** (0 sorry) | T-duality invariants |
| `FrustrationMonotonicity.lean` | ⚠️ **Tier C** (4 sorry — H19 stub) | `frustration_index_ge_one` (Tier A ✅); monotonicity conjecture open |

---

## 🚀 Quickstart

```python
from pipeline import LeanFlowPipeline
import numpy as np

pipe = LeanFlowPipeline.from_pretrained(".")

x = np.linspace(0, 2 * np.pi, 64, endpoint=False)
X, Y = np.meshgrid(x, x, indexing="ij")
u_init = np.array([np.sin(X) * np.cos(Y), -np.cos(X) * np.sin(Y)])

result = pipe(u_init, n_steps=200, nu=1e-3, cfl=0.4)
print(f"Final Divergence Residual : {result['final_divergence']:.2e}")
print(f"Wall Time                  : {result['wall_time_sec']:.4f} s")
```

---

## 📜 Citation

```bibtex
@article{callens2026leanflow,
  title   = {LeanFlow: A Formally Verified Dual-Scale Pseudo-Spectral Navier-Stokes Solver},
  author  = {Callens, Xavier and SocrateAI Research},
  journal = {arXiv preprint},
  year    = {2026},
  note    = {Revision 3. \url{https://huggingface.co/callensxavier/leanflow-dualscale-pde}}
}
```

Audit Certificate: `CERT-HF-MODEL-R3-2026-08-31`
