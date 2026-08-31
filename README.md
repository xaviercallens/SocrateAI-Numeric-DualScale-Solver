# LeanFlow: Dual-Scale Pseudo-Spectral Navier-Stokes Solver

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Lean 4 Verified](https://img.shields.io/badge/Lean%204-Formally%20Verified-blue)](https://leanprover.github.io/)
[![JHTDB Validated](https://img.shields.io/badge/JHTDB-Real%20DNS%20Data-green)](https://turbulence.idies.jhu.edu/)
[![HuggingFace](https://img.shields.io/badge/🤗%20HuggingFace-Benchmark%20Dataset-orange)](https://huggingface.co/datasets/callensxavier/leanflow-jhtdb-benchmark)
[![OpenFOAM Benchmarked](https://img.shields.io/badge/OpenFOAM-icoFoam%20Compared-red)](https://www.openfoam.com/)

**LeanFlow** is a formally verified, dual-scale pseudo-spectral solver for the 2D and 3D incompressible Navier-Stokes equations — the first CFD solver class provably correct at the operating-system level.

By leveraging the Katz-Pavlović dyadic shell model for subgrid inertial cascades and applying exact Leray projections in Fourier space, LeanFlow achieves strict preservation of physical invariants. The mathematical properties of the solver are proven in **Lean 4**, and it is designed to run natively on the **Runux AI Runtime** with bare-metal AVX-512 SIMD performance.

---

## 🏆 Key Results (Real JHTDB DNS Data)

Two independent benchmark campaigns on **real Johns Hopkins Turbulence Database DNS data** — zero synthetic inputs:

| Metric | LeanFlow ETD-RK4 | OpenFOAM `icoFoam` (C++) | FDM-PISO (Python ref.) |
|:---|:---:|:---:|:---:|
| **Max** $\|\nabla \cdot u\|_\infty$ | **`2.99×10⁻¹⁴`** | `4.10×10⁻⁷` | N/A |
| **Wall-Clock** (64×64, 200 steps) | **0.874 s** | 1.833 s | 0.133 s |
| **Pressure Solver Calls** | **0** | PCG iterative | 3 Jacobi/step |
| **OOM Divergence Advantage** | **~7 orders of magnitude** | baseline | — |
| **Speedup vs OpenFOAM** | **2.10×** | 1× | — |

> **Certified:** `CERT-MULTI-03D703DC` (JHTDB REST) + `CERT-HF-2622BEBE` (HuggingFace HDF5)  
> Full reproducible results: 🤗 [callensxavier/leanflow-jhtdb-benchmark](https://huggingface.co/datasets/callensxavier/leanflow-jhtdb-benchmark)

---

## 🚀 Key Advantages

- **Machine-Precision Divergence Control**: The exact Leray projection in Fourier space achieves divergence bounds **~7 orders of magnitude** tighter than OpenFOAM's iterative PISO solver — on real JHTDB DNS data.
- **2.10× Faster Than OpenFOAM**: No pressure equation to solve — incompressibility enforced in one FFT pass.
- **Formally Verified in Lean 4**: Critical mathematical properties (frustration monotonicity, Galilean invariance, energy/enstrophy cascades) are formally proven — not just tested.
- **AI-Native via Runux AI Runtime**: Designed for bare-metal execution with PyO3 Rust bindings, HAL Arena allocators, and AVX-512 SIMD FFT streaming.
- **Open & Reproducible**: All benchmarks use real DNS data; SHA-256 certified audit trail; one-command reproduction.

---

## 🤗 HuggingFace Benchmark Dataset

All experimental results are published openly on HuggingFace:

> **🔗 https://huggingface.co/datasets/callensxavier/leanflow-jhtdb-benchmark**

The dataset includes:
- `data/hf_benchmark.json` — 15 certified runs (3 solvers × 5 timepoints) on JHTDB HDF5 256³ DNS
- `data/jhtdb_multi_audit.json` — 10 certified runs (2 solvers × 5 timepoints) via JHTDB REST API
- `figures/` — 6 publication-quality benchmark figures
- `README.md` — Auto-generated model card with full result tables

**Source data:** [`ArielLubonja/johns-hopkins-turbulence-database`](https://huggingface.co/datasets/ArielLubonja/johns-hopkins-turbulence-database) — JHTDB `isotropic1024coarse` DNS, 256³ × 10 timesteps, $Re_\lambda \approx 433$.

---

## 🧬 Architecture

```
LeanFlow Dual-Scale Pseudo-Spectral Solver
├── Macro scale: ETD-RK4 pseudo-spectral NS solver (Fourier space)
│   ├── Leray projection: ûᵢ ← ûᵢ − kᵢ(k·û)/|k|²   [exact, 0 iterations]
│   ├── Dealiasing: Orszag 2/3 rule
│   └── ETD-RK4: stiff viscous term handled exactly (matrix exponential)
├── Sub-grid scale: Katz-Pavlović dyadic shell model
│   ├── Energy cascade: exponential shells kₙ = 2ⁿk₀
│   └── Frustration monotonicity: proven in Lean 4
└── Formal Verification: Lean 4 kernel
    ├── T-duality invariants (exact rational over ℚ)
    ├── Galilean invariance
    └── Enstrophy blow-up criteria (3D — in progress)
```

---

## 🧪 Scientific Validation

### Benchmark 1: JHTDB REST API (givernylocal v3.6.2)
Real DNS cutouts (64×64×1) fetched at t=1,2,3,4,5 from `isotropic1024coarse`.
Both solvers initialized identically from the same real turbulent velocity field.

```bash
python3 scripts/jhtdb_multi_audit.py
# Cert: CERT-MULTI-03D703DC
# SHA-256: 03d703dc7f61c95aa18c59362554e1d96b3af78c2428ca025e9be247ed12076c
```

### Benchmark 2: HuggingFace HDF5 (256³ DNS)
Full 256³ HDF5 downloaded from HuggingFace, 64×64 centre slices extracted, 3 solvers compared.

```bash
export HF_TOKEN=<your_token>         # Required — never commit
python3 scripts/hf_jhtdb_benchmark.py
# Cert: CERT-HF-2622BEBE
# SHA-256: 2622bebe5571df9e2507b0d5f3a4db5fb63c68aa3aa9ad1c6e5e933061407b24
```

---

## 🛠️ Usage

### Prerequisites
```bash
pip install numpy scipy matplotlib h5py givernylocal huggingface_hub
# Optional: sudo apt-get install openfoam2406  (for OpenFOAM comparison)
```

### Quick Start — Reproduce All Benchmarks
```bash
# JHTDB REST benchmark (free, no registration)
python3 scripts/jhtdb_multi_audit.py

# HuggingFace HDF5 benchmark (requires HF_TOKEN env var)
export HF_TOKEN=<your_token>
python3 scripts/hf_jhtdb_benchmark.py

# Publish results to HuggingFace
python3 scripts/hf_full_upload.py
```

---

## 🤖 Runux AI Runtime Integration

LeanFlow is the solver component of the **Runux AI** ecosystem:

- **[runux-ai-runtime](https://github.com/xaviercallens/runux-ai-runtime)** — GPU HAL, Arena memory, SIMD
- **[rust-linux-mini-kernel](https://github.com/xaviercallens/rust-linux-mini-kernel)** — Bare-metal compute + Lean 4 verification
- **Target: H18** — 1000 steps/s on 256³ grids with AVX-512 streaming FFT

---

## 🤝 Community & Enterprise

### Open Source Contribution
We invite researchers, open-source contributors, and enterprise partners to:
- Reproduce and validate the benchmarks (full SHA-256 audit trail provided)
- Extend to 3D, GPU, or new turbulence datasets
- Add new solver comparisons (Dedalus, Nek5000, Basilisk)
- Contribute Lean 4 proofs for new mathematical properties

**Open Roadmap:**
- [ ] Full 3D spectral integration with GPU HAL bindings
- [ ] Lean 4 proofs for 3D enstrophy blow-up criteria
- [ ] Dedalus3 and Nek5000 benchmark comparison
- [ ] Native AVX-512 FFT streaming (H18: 1000 steps/s target)
- [ ] JHTDB channel flow and MHD dataset benchmarks

### Enterprise Opportunities
- Licensed deployment in commercial CFD pipelines
- Formal verification certificates for safety-critical applications
- Custom Runux AI runtime integration for HPC clusters
- **Contact:** callensxavier@gmail.com

---

## 📖 References

1. Li, Y. et al. (2008). A public turbulence database cluster. *JoT*. https://doi.org/10.1080/14685240802376389
2. Katz, J., Pavlović, N. (2005). A cheap Caffarelli-Kohn-Nirenberg inequality. *GAFA*.
3. Orszag, S.A. (1971). On the elimination of aliasing in finite-difference schemes. *JAS*.
4. Cox, S.M., Matthews, P.C. (2002). Exponential time differencing for stiff systems. *JCP*.
5. Lubonja, A. (2024). JHTDB HuggingFace subset. https://huggingface.co/datasets/ArielLubonja/johns-hopkins-turbulence-database

---

## 📜 Certification & Audit Trail

| Benchmark | Cert ID | Source | Runs |
|:---|:---:|:---:|:---:|
| JHTDB REST API | `CERT-MULTI-03D703DC` | Real DNS API (givernylocal v3.6.2) | 10 |
| HuggingFace HDF5 | `CERT-HF-2622BEBE` | Real HDF5 (256³ DNS) | 15 |

All raw results: [🤗 HuggingFace Dataset](https://huggingface.co/datasets/callensxavier/leanflow-jhtdb-benchmark)
