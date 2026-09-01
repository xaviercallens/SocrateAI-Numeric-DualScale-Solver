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

**Enterprise Edition v1.0 | Certificate: `CERT-P12-AUTORESEARCH-D9A32D92F82E44B5`**

This dataset contains the full experimental results, certification JSON, compiled PDF report,
and reproducible code snapshot for the **LeanFlow Dual-Scale Navier--Stokes Solver**
applied to 5 industrial PDE problems via the **Karpathy Ratchet Auto-Research Loop**.

## Overview

The LeanFlow solver applies a spectral biharmonic regularisation parameter α' satisfying
R_eff ≥ 2√α', guaranteeing unconditional enstrophy boundedness regardless of parameter values.
This mathematical shield enables an LLM-driven Karpathy Ratchet to explore extreme parameter
regimes safely — impossible with standard CFD solvers that produce NaN blowups.

## 3 HuggingFace Datasets Used for Ground Truth Calibration

| Dataset | Problem | Calibration Use |
|---------|---------|-----------------|
| [`angioinsight/single-vessel-flow`](https://huggingface.co/datasets/angioinsight/single-vessel-flow) | H67 — Medical VAD Rotor | Blood viscosity ν = 3.5×10⁻³ Pa·s |
| [`polymathic-ai/MHD_64`](https://huggingface.co/datasets/polymathic-ai/MHD_64) | H70 — Tokamak Disruption | Plasma β, Mach=0.7, Ms=0.5 turbulence |
| [`pdebench/PDEBench`](https://huggingface.co/datasets/pdebench/PDEBench) | H66 — Scramjet SBLI | Compressible Euler Mach=2.0 (fallback: synthetic) |

## Results Summary

### 4 Certified Performance Gains

| Gain | Baseline | LeanFlow | Factor |
|------|----------|----------|--------|
| **G1: Compute Speed** (Scramjet) | 12.0 ms | 0.8 ms | **15×** |
| **G2: MHD Stability** (Tokamak) | 0.8 ms horizon | 16.0 ms | **20×** |
| **G3: Energy Yield** (Wind+BTMS) | +3.5% | +17.8% | **5.1×** |
| **G4: Biomedical Safety** (VAD) | 260 Pa | 137.9 Pa | **47% reduction** |

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
├── leanflow_phase12_report.pdf  # 4-page technical report (LaTeX compiled)
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

# 3. Verify with test suite
pytest tests/test_phase12_autoresearch.py -v
# Expected: 25/25 passed in ~2s

# 4. Lean 4 build check
cd lean4 && lake build
```

## Certificate

```json
{
  "certificate_id": "CERT-P12-AUTORESEARCH-D9A32D92F82E44B5",
  "overall_status": "CERTIFIED",
  "sha256_hash": "d9a32d92f82e44b5e0ddb2061129ac8733fa84589bb676e7c5f2e495ddc132a7",
  "schema_version": "P12-v2",
  "solver_commit": "6467643f689ba0de",
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
  note    = {Enterprise Edition v1.0, Phase 12},
  url     = {https://github.com/xaviercallens/SocrateAI-Numeric-DualScale-Solver}
}
```

## License

Apache 2.0 — see [LICENSE](https://github.com/xaviercallens/SocrateAI-Numeric-DualScale-Solver/blob/main/LICENSE)
