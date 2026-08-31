# AGENTS.md — Model-Tier Routing Table
**Version:** 3.0 — Phase 7/8 Extended Industrial & Productization (2026-08-31)

## Tier Definitions

| Tier | Capability Level | Scope / Responsibilities |
|---|---|---|
| **T0** | Operational / Scaffolding / Packaging | **(Local SLM / Mistral)** Running CI, formatting code, managing tasks, checking JSON schema, packaging PyPI wheels, Docker appliances, C-ABI bindings. |
| **T1** | Exact & Numerical Implementation | **(Local SLM / Gemma 2 / Qwen Coder)** Writing exact rational invariant checkers, implementing pseudo-spectral operators, RK4 integrators, 3D volume FSI mesh couplers, writing tests with negative controls. |
| **T1 (Runtime)** | Live Agentic Telemetry & HIL | `agentic_runtime_monitor`, `hil_edge_engineer`: Real-time telemetry analysis, issuing live parameter updates to the solver, and executing cycle-accurate HIL tests on ARM / RISC-V targets. |
| **T1 (Design)** | Generative CAD & Topology | `cad_generative_designer`: B-Spline camber generation, STEP AP203/AP214 / IGES export, and OpenCASCADE B-Rep solid generation. |
| **T1 (Experiment)** | Empirical Benchmarking | `experimenter`: Running solver benchmarks, JHTDB validation, and recording real measurements. Never hardcodes results. |
| **T1 (MultiPhysics)** | Coupled FSI & Thermal numerics | `fsi_multiphysics_auditor`: Verifying 3D volume mesh fluid-structure interaction, interface velocity continuity, and enstrophy transfer coefficients. |
| **T2** | Mathematical Physics Judgment | **(Cloud Frontier Model)** Modifying PDE formulations, analyzing singularity bounds, proving new algebraic recurrence locks, auditing Lean 4 formal proofs. |

---

## Escalation Triggers

An agent working on this repo must immediately stop and escalate when:
1. An exact rational invariant fails verification over $\mathbb{Q}$.
2. A negative control fails to reject a falsified state.
3. Divergence in pseudo-spectral simulation under CFL condition $\le 0.5$.
4. The Agentic Runtime Monitor detects an anomaly but the parameter steering command fails to stabilize the enstrophy within 50 time steps.
5. The hardness auditor issues a `SCAFFOLDING_ONLY` certificate when a `CERTIFIED` certificate was expected by the protocol.
6. FSI interface velocity discontinuity persists post-enforcement ($|v_{\text{fluid}} - \dot{w}| > 0$).
7. Embedded HIL cycle budget exceeds 1.0 ms at 168 MHz for the $N=4\times4$ micro-kernel.
8. CAD/STEP entity count is $< 5$ or lacks valid ISO-10303-21 header/footer structure.

---

## Agent Output Contracts

> [!IMPORTANT]
> All agents must return structured JSON matching their output contract (H26).
> A prose response without the required fields is a hard gate failure.

| Agent | Must Return (key fields) | Forbidden Outputs |
|-------|--------------------------|-------------------|
| `dev_engineer` | `{"status": "SUCCESS\|FAILED", "artifact_path": "...", "cargo_check_exit_code": 0, "_measured": true}` | Prose only, null fields |
| `math_reviewer` | `{"status": "VERIFIED\|FAILED", "lake_exit_code": 0, "sorry_count_non_exempt": 0, "_measured": true}` | `"I believe..."`, missing `lake_exit_code` |
| `qa_scientific_auditor` | `{"certificate_id": "CERT-P[6-8]-*", "overall_status": "CERTIFIED\|REJECTED\|SCAFFOLDING_ONLY", "invariants_verified": {...}, "_measured": true}` | Partial audit, missing invariants |
| `agentic_runtime_monitor` | `{"command": "steer\|hold\|escalate", "scheme": "BDF\|Adams", "steps_to_stabilize": N, "_measured": true}` | Free-form text commands, missing `command` |
| `experimenter` | `{"status": "SUCCESS\|FAILED", "benchmark_result": {...}, "grid_n": N, "_measured": true}` | Hardcoded benchmark values |
| `hil_edge_engineer` | `{"status": "PASSED\|FAILED", "cycles": N, "clock_mhz": N, "latency_ms": N, "_measured": true}` | Synthetically estimated latency without cycle count |
| `cad_generative_designer` | `{"status": "EXPORTED\|REJECTED", "step_path": "...", "entity_count": N, "sha256_hash": "...", "_measured": true}` | Malformed STEP, missing entities |
| `fsi_multiphysics_auditor` | `{"status": "COUPLED\|DECOUPLED", "pre_enforcement_mismatch": N, "post_enforcement_residual": 0.0, "enstrophy_transfer_coeff": N, "_measured": true}` | Unchecked boundary mismatch, undefined $\eta$ |
| `cloud_telemetry_agent` | `{"status": "STREAMING\|FAILED", "throughput_eps": N, "loss_rate": 0.0, "rolling_sha256": "...", "_measured": true}` | Dropped packets, unmeasured throughput |
| `enterprise_packaging_agent` | `{"status": "PACKAGED\|FAILED", "wheel_size_mb": N, "docker_size_mb": N, "missing_symbols_count": 0, "_measured": true}` | Missing ABI symbols, Docker size $> 150\,\text{MB}$ |
| `licensing_audit_agent` | `{"status": "LOCKED\|REJECTED", "token_verified": true, "merkle_root": "...", "_measured": true}` | Unsigned license tokens, tampered audit tree |

---

## Prohibited Actions Per Tier

| Tier | Prohibited |
|------|-----------|
| **T0** | Making mathematical judgment calls. Approving a Lean 4 proof without running `lake build`. Relying on T2 frontier cloud models for Phase 8 execution. |
| **T1** | Hardcoding performance numbers. Setting `_measured: true` without an actual measurement. Relying on T2 frontier cloud models for deterministic computations. |
| **T1 (Runtime)** | Issuing steering commands as free-form text. Reporting stabilization without counting steps. |
| **T1 (Design)** | Creating dummy CAD files lacking ISO-10303-21 compliant geometry entities. |
| **T1 (MultiPhysics)** | Bypassing no-slip interface verification or ignoring structural kinetic energy loss $> 5\%$. |
| **T1 (Experiment)** | Flooring benchmark results (`max(actual, floor)`). Reporting a grid_n smaller than specified by H23. |
| **T2** | Modifying invariants H1–H50 without an audit trail entry in the Lessons Learned Register (`LL.md`). |

---

## Autonomous Low-Tier Execution Guardrails

> [!IMPORTANT]
> **Guardrail 1: Constrained JSON Decoding & Forbidden Status Sentinels**
> All T0 and T1 agents executing autonomously (especially local SLMs) MUST be wrapped in a constrained decoding environment. If any forbidden status (e.g., `HALLUCINATED`, `SIMULATED`, `HARDCODED`) or unparsable prose is detected, the runtime must immediately reject and retry to prevent drift.

