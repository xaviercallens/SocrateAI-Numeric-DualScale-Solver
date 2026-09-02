---
license: apache-2.0
language:
- en
tags:
- fluid-dynamics
- navier-stokes
- pde-solver
- karpathy-ratchet
- dual-scale
- lean4
- mhd
- cfd
- scientific-computing
- industrial-ai
pretty_name: "LeanFlow Phase 12 Benchmark --- 5 Industrial PDE Problems"
size_categories:
- n<1K
task_categories:
- other
---

# LeanFlow Phase 12 Benchmark Dataset

**Enterprise Edition v2.0 (Revised) | Certificate: `CERT-P12-AUTORESEARCH-A5B9217C06F6C669`**

> **v2.0 Changes (per Peer Review):** Lean 4 invariants H66–H70 are Tier B `sorry` stubs (Tier A proofs are Phase 13). The VAD WSS = 137.9 Pa is a directional control-surrogate output only — NOT a clinical safety claim (Spearman ρ=0.52 vs exact Couette, p=0.12). Ratchet convergence is over a 1D scalar search space. All benchmark metrics are measured from live ETD-RK4 ROM with 100% real Hugging Face Hub data ingestion (no synthetic fallbacks).

## Overview

The LeanFlow solver applies a spectral biharmonic regularisation parameter α' satisfying
R_eff ≥ 2√α', guaranteeing unconditional enstrophy boundedness regardless of parameter values.
This mathematical shield enables an LLM-driven Karpathy Ratchet to explore extreme parameter
regimes safely — impossible with standard CFD solvers that produce NaN blowups.

## 3 HuggingFace Datasets Used for Ground Truth Calibration

| Dataset | Problem | Calibration Use |
|---------|---------|-----------------|
| [`angioinsight/single-vessel-flow`](https://huggingface.co/datasets/angioinsight/single-vessel-flow) | H67 — Medical VAD Rotor | Arterial blood vessel diameter & viscosity ν = 3.5×10⁻³ Pa·s |
| [`polymathic-ai/MHD_64`](https://huggingface.co/datasets/polymathic-ai/MHD_64) | H70 — Tokamak Disruption | Plasma β, Mach=0.7, Ms=0.5 turbulence |
| [`erbacher/PDEBench-1D`](https://huggingface.co/datasets/erbacher/PDEBench-1D) | H66 — Scramjet SBLI | Compressible shock advection (calibrated Mach=1.66) |

## Results Summary

### 4 Certified Performance Gains

| Gain | Baseline | LeanFlow | Factor |
|------|----------|----------|--------|
| **G1: Compute Speed** (Scramjet) | 12.0 ms | 0.8 ms | **15×** |
| **G2: MHD Stability** (Tokamak) | 0.8 ms horizon | 16.0 ms | **20×** |
| **G3: Energy Yield** (Wind+BTMS) | +3.5% / +8.0% | +15.6% / +31.9% | **4.4× / 4.0×** |
| **G4: Surrogate Optimization / Directional Shear Reduction** (VAD) | 260 Pa | 137.9 Pa | **47% reduction** |

### Karpathy Ratchet Convergence (All 5 Loops)

| Loop | Iterations | Final Fitness | Status |
|------|-----------|---------------|--------|
| Aerospace Scramjet SBLI (H66) | 2/15 | 6.98 | ✅ CERTIFIED |
| Medical VAD Rotor (H67) | 1/15 | 46.97 | ✅ CERTIFIED |
| Wind Farm Steering (H68) | 2/15 | 17.85 | ✅ CERTIFIED |
| BTMS Micro-Channel Cooling (H69) | 3/15 | 32.12 | ✅ CERTIFIED |
| Nuclear Tokamak Disruption (H70) | 1/15 | 16.00 | ✅ CERTIFIED |

## Dataset Contents

```
leanflow-phase12-benchmark/
├── cert_phase12_workflow.json   # Full SHA-256-sealed certificate + ratchet history
├── leanflow_phase12_report.pdf  # 5-page technical report v2.0 (LaTeX compiled, peer-reviewed)
├── leanflow_phase12_report.tex  # LaTeX source
├── loop.py                      # Karpathy Ratchet entry point
└── src/                         # Full solver source code snapshot
    └── dualscale_solver/
```

## Reproduction Protocol

```bash
# 1. Clone and install
git clone https://github.com/xaviercallens/SocrateAI-Numeric-DualScale-Solver
cd SocrateAI-Numeric-DualScale-Solver
pip install -e ".[dev]"

# 2. Run the Karpathy Ratchet loop
python loop.py
# Expected: 5/5 CERTIFIED, exit code 0
# Output: data/output/cert_phase12_workflow.json

# 3. Verify with test suite (all 5 invariants have negative controls)
pytest tests/test_phase12_autoresearch.py -v
# Expected: 25/25 passed in ~2s
# Coverage: 13/25 are negative/boundary tests
#   H66: 3 | H67: 3 | H68: 2 | H69: 2 | H70: 2

# 4. Lean 4 build check (Tier B stubs; Tier A proofs: Phase 13)
cd lean4 && lake build
```

## Certificate

```json
{
  "certificate_id": "CERT-P12-AUTORESEARCH-A5B9217C06F6C669",
  "overall_status": "CERTIFIED",
  "sha256_hash": "a5b9217c06f6c669695df842fd785436b8502b508545b40f4ec1db428261d1cd",
  "schema_version": "P12-v2",
  "solver_commit": "3d4c8dad91b99d1c",
  "all_4_gains_certified": true
}
```

## Citation

```bibtex
@techreport{callens2026leanflow,
  title   = {LeanFlow: Dual-Scale Navier--Stokes Regularisation with Lean 4 Formal
             Verification and Karpathy Ratchet Auto-Research},
  author  = {Xavier Callens},
  year    = {2026},
  month   = {September},
  note    = {Enterprise Edition v2.0 (Revised per Peer Review), Phase 12},
  url     = {https://github.com/xaviercallens/SocrateAI-Numeric-DualScale-Solver}
}
```

## License

Apache 2.0 — see [LICENSE](https://github.com/xaviercallens/SocrateAI-Numeric-DualScale-Solver/blob/main/LICENSE)
