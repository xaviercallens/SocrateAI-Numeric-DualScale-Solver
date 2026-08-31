---
name: agentic-runtime-monitoring
description: Phase 6 guidelines for Agentic Runtime Monitoring (RunuX) and steering of numerical simulations.
---

# Agentic Runtime Monitoring (RunuX)

This skill dictates the behavior for the `agentic_runtime_monitor` (Tier 1 Runtime agent) during live simulation runs.

## 1. Responsibilities
The `agentic_runtime_monitor` agent operates concurrently with the `rusty-SUNDIALS` solver via the `runux-ai-runtime` memory arena. Its primary goals are:
- **Anomaly Detection**: Monitor the streaming telemetry (stiffness $\sigma$, enstrophy, divergence) for signs of numerical instability (e.g., stiffness spiking, divergence growing $>10^{-13}$).
- **Parameter Steering**: Issue dynamic adjustments to the solver parameters (e.g., scheme order, $\Delta t$, $\alpha'$) without stopping the simulation.

## 2. Telemetry Schema
The solver writes JSON telemetry to the RunuX shared memory buffer. The agent must parse:
```json
{
  "step": 5000,
  "dt": 0.001,
  "enstrophy": 45.2,
  "stiffness_ratio": 8.4,
  "max_divergence": 1.2e-14
}
```

## 3. Intervention Policies
If $\sigma > 100$ or `max_divergence` jumps by more than a factor of $10^2$ in 5 steps:
1. Issue a steering command:
```json
{
  "command": "steer",
  "target_dt": 0.0005,
  "scheme": "BDF"
}
```
2. Monitor the next 50 steps. If stabilization fails, throw a hard escalation.

## 4. Phase 6 Negative Control (H24)
To verify this skill, the agent must pass Gate 8 (H24): Intercept `NC-DS-11` (stiffness spike injection) and successfully return the solver to a stable state within 50 time steps.
