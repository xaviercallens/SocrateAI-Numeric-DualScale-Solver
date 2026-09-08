---
name: climate-weatherbench-evaluation
description: >-
  Workflows and algorithmic guidelines for evaluating the LeanFlow Dual-Scale 
  PDE simulator against Earth System Digital Twin and HuggingFace WeatherBench 
  baselines (e.g., google/weatherbench2). Enforces statistical integrity, 
  enstrophy conservation validation, and autonomous generation of model cards.
version: 1.0
updated: 2026-09-08
---

# Climate & WeatherBench Evaluation Skill

## 1. Scope & Objective
This skill orchestrates the evaluation of atmospheric fluid dynamics using the LeanFlow solver.
It focuses on the dual-scale coupling of macro-level jet streams and micro-level turbulence,
validating computational speedup and invariant conservation against standard weather models (IFS, WRF).

## 2. Epistemic Mandates (Derived from AGENTS.md)
1. **No Surrogate Inflation:** Do not label $N=32^3$ grids as "production forecasting" without caveats. Call it a "surrogate validation."
2. **Statistical Rigor:** All empirical speedup comparisons must be actually measured (`_measured: true`).
3. **Buzzword Ban:** Do not use banned terms (e.g., "Rulial Inversion"). Use "Dual-Scale Preconditioner."
4. **Invariant Tracking:** You MUST log and verify the conservation of Enstrophy and the Weak Energy Condition ($\rho + p > 0$).

## 3. Autonomous Execution Protocol
When the orchestrator triggers this skill:
1. Parse the subset dataset (e.g., netCDF subset or generated mock for CI/CD).
2. Execute the Rust engine (`rusty-SUNDIALS/examples/weatherbench_climate.rs`).
3. Extract latency (ms), residual errors, and invariant validation markers.
4. Auto-generate the final `weatherbench_leanflow_paper.md` structured for HuggingFace submission.

## 4. Output Contract
The final evaluation must output a structured JSON status containing:
`{"status": "SUCCESS|FAILED", "benchmark_result": {"speedup": X, "residual": Y}, "grid_n": N, "_measured": true}`
