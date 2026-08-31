# AGENTS.md — Model-Tier Routing Table
**Version:** 2.0 — Phase 6 Extended (2026-08-31)

## Tier Definitions

| Tier | Capability Level | Scope / Responsibilities |
|---|---|---|
| **T0** | Operational / Scaffolding | Running CI, formatting code, managing tasks, checking JSON schema, chasing pipeline errors. |
| **T1** | Exact & Numerical Implementation | Writing exact rational invariant checkers, implementing pseudo-spectral operators, RK4 integrators, writing tests with negative controls. |
| **T1 (Runtime)** | Live Agentic Telemetry | `agentic_runtime_monitor`: Real-time telemetry analysis and issuing live parameter updates to the solver. |
| **T1 (Experiment)** | Empirical Benchmarking | `experimenter`: Running solver benchmarks and recording real measurements. Never hardcodes results. |
| **T2** | Mathematical Physics Judgment | Modifying PDE formulations, analyzing singularity bounds, proving new algebraic recurrence locks. |

---

## Escalation Triggers

An agent working on this repo must immediately stop and escalate when:
1. An exact rational invariant fails verification over $\mathbb{Q}$.
2. A negative control fails to reject a falsified state.
3. Divergence in pseudo-spectral simulation under CFL condition $\le 0.5$.
4. The Agentic Runtime Monitor detects an anomaly but the parameter steering command fails to stabilize the enstrophy within 50 time steps.
5. The hardness auditor issues a `SCAFFOLDING_ONLY` certificate when a `CERTIFIED` certificate was expected by the protocol.

---

## Agent Output Contracts

> [!IMPORTANT]
> All agents must return structured JSON matching their output contract (H26).
> A prose response without the required fields is a hard gate failure.

| Agent | Must Return (key fields) | Forbidden Outputs |
|-------|--------------------------|-------------------|
| `dev_engineer` | `{"status": "SUCCESS\|FAILED", "artifact_path": "...", "cargo_check_exit_code": 0, "_measured": true}` | Prose only, null fields |
| `math_reviewer` | `{"status": "VERIFIED\|FAILED", "lake_exit_code": 0, "sorry_count_non_exempt": 0, "_measured": true}` | `"I believe..."`, missing `lake_exit_code` |
| `qa_scientific_auditor` | `{"certificate_id": "CERT-P6-*", "overall_status": "CERTIFIED\|REJECTED\|SCAFFOLDING_ONLY", "invariants_verified": {...}, "_measured": true}` | Partial audit, missing invariants |
| `agentic_runtime_monitor` | `{"command": "steer\|hold\|escalate", "scheme": "BDF\|Adams", "steps_to_stabilize": N, "_measured": true}` | Free-form text commands, missing `command` |
| `experimenter` | `{"status": "SUCCESS\|FAILED", "benchmark_result": {...}, "grid_n": N, "_measured": true}` | Hardcoded benchmark values |

---

## Prohibited Actions Per Tier

| Tier | Prohibited |
|------|-----------|
| **T0** | Making mathematical judgment calls. Approving a Lean 4 proof without running `lake build`. |
| **T1** | Hardcoding performance numbers. Setting `_measured: true` without an actual measurement. |
| **T1 (Runtime)** | Issuing steering commands as free-form text. Reporting stabilization without counting steps. |
| **T1 (Experiment)** | Flooring benchmark results (`max(actual, floor)`). Reporting a grid_n smaller than specified by H23. |
| **T2** | Modifying invariants H1–H27 without an audit trail entry in the Lessons Learned Register. |
