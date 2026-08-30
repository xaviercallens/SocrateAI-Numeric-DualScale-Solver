# AGENTS.md — Model-Tier Routing Table

## Tier Definitions

| Tier | Capability Level | Scope / Responsibilities |
|---|---|---|
| **T0** | Operational / Scaffolding | Running CI, formatting code, managing tasks, checking JSON schema, chasing pipeline errors. |
| **T1** | Exact & Numerical Implementation | Writing exact rational invariant checkers, implementing pseudo-spectral operators, RK4 integrators, writing tests with negative controls. |
| **T2** | Mathematical Physics Judgment | Modifying PDE formulations, analyzing singularity bounds, proving new algebraic recurrence locks. |

## Escalation Triggers

An agent working on this repo must immediately stop and escalate when:
1. An exact rational invariant fails verification over $\mathbb{Q}$.
2. A negative control fails to reject a falsified state.
3. Divergence in pseudo-spectral simulation under CFL condition $\le 0.5$.
