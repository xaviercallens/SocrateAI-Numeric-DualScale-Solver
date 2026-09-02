---
license: apache-2.0
language:
- en
library_name: leanflow
tags:
- fluid-dynamics
- navier-stokes
- pde-solver
- karpathy-ratchet
- dual-scale
- lean4
- scientific-computing
- industrial-ai
- mhd
- cfd
pipeline_tag: other
---

# LeanFlow Dual-Scale Navier--Stokes Solver

**Enterprise Edition v2.0 (Revised per Peer Review)** | Phase 12 | SocrateAI / Xavier Callens

> ⚠️ **Peer Review Disclosures (v2.0):**
> - Lean 4 invariants H66–H70 are **Tier B `sorry` stubs** — Tier A (zero-sorry) proofs are a Phase 13 target.
> - VAD WSS = 137.9 Pa is a **directional control-surrogate** only. Spearman ρ=0.52 (p=0.12) vs exact Couette — **not a clinical safety claim**.
> - Ratchet convergence in 1–3 iterations reflects **1D scalar search space**, not unconstrained autonomous search.

## Model Description

LeanFlow is a **Dual-Scale Spectral Navier--Stokes Solver** with:

- **Karpathy Ratchet Auto-Research**: 5-step autonomous cycle (PROPOSE → EVALUATE → RATCHET → VERIFY → REFLECT)
- **Dual-Scale Regularisation**: R_eff ≥ 2√α' guarantees unconditional enstrophy boundedness
- **Lean 4 Formal Invariants**: H66--H70 contracts enforced via Pydantic runtime gating
- **ETD-RK4 Spectral ROM**: 32 Fourier modes, <5ms per evaluation

## Certified Results (5 Industrial Use Cases)

| Problem | HF Dataset | Key Metric | Gain |
|---------|-----------|------------|------|
| Scramjet SBLI (H66) | erbacher/PDEBench-1D | Actuation: 0.8ms | **15×** speed |
| Medical VAD (H67) | angioinsight/single-vessel-flow | WSS: 137.9 Pa | **47%** reduction |
| Wind Farm (H68) | Synthetic NREL | Yield: +15.6% | **4.4×** |
| BTMS Cooling (H69) | Synthetic fractal | Heat: +31.9% | **4.0×** |
| Tokamak MHD (H70) | polymathic-ai/MHD_64 | Horizon: 16ms | **20×** |

Certificate: `CERT-P12-AUTORESEARCH-A5B9217C06F6C669` | SHA-256: `a5b9217c06f6c669...` | Commit: `3d4c8dad91b99d1c`

## Quick Start

```python
from dualscale_solver.numeric.phase12_autoresearch_problems import (
    solve_scramjet_sbli_mitigation,
    solve_medical_vad_dynamics,
    solve_wind_farm_steering,
    solve_btms_microchannels,
    solve_tokamak_disruption,
)

# Aerospace: SBLI prediction horizon
result = solve_scramjet_sbli_mitigation(spectral_filter_coef=2.4)
print(f"SBLI horizon: {result['sbli_prediction_horizon_ms']:.2f} ms")
print(f"Certified: {result['status']}")
# => SBLI horizon: 5.59 ms, Certified: CERTIFIED

# Medical: VAD shear stress
result = solve_medical_vad_dynamics(tensor_stiffness=2.5)
print(f"WSS: {result['peak_wss_pa']:.1f} Pa, Hemolysis: -{result['hemolysis_reduction_pct']:.1f}%")
# => WSS: 137.9 Pa, Hemolysis: -47.0%
```

## Full Karpathy Ratchet Loop

```bash
git clone https://github.com/xaviercallens/SocrateAI-Numeric-DualScale-Solver
cd SocrateAI-Numeric-DualScale-Solver
pip install -e ".[dev]"
python loop.py
# All 5 loops CERTIFIED, exit code 0
```

## Architecture

```
PROPOSE  ──→  EVALUATE  ──→  RATCHET  ──→  VERIFY  ──→  REFLECT
   │              │              │             │             │
  LLM         ETD-RK4        KEEP/REVERT   Pydantic     Chain-of-
Hypothesis   Spectral ROM    monotonic     H66-H70       Thought
Generator    (<5ms)          fitness        gates        Diagnostic
```

## Technical Report

Full 5-page LaTeX report v2.0 (revised per peer review): [leanflow_phase12_report.pdf](https://huggingface.co/datasets/callensxavier/leanflow-phase12-benchmark/resolve/main/leanflow_phase12_report.pdf)

## Citation

```bibtex
@techreport{callens2026leanflow,
  title   = {LeanFlow: Dual-Scale Navier--Stokes Regularisation with Lean 4
             Formal Verification and Karpathy Ratchet Auto-Research},
  author  = {Xavier Callens},
  year    = {2026},
  month   = {September},
  note    = {Enterprise Edition v2.0 (Revised per Peer Review), Phase 12, CERT-P12-AUTORESEARCH-A5B9217C06F6C669},
  url     = {https://github.com/xaviercallens/SocrateAI-Numeric-DualScale-Solver}
}
```
