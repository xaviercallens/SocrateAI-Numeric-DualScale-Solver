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

## 2. Stiffness Ratio Formula (IP-09, corrected)

The stiffness indicator used by this agent is the **diffusive Péclet-like ratio**:

$$\sigma = \frac{u_{\max} \cdot \Delta x}{\nu}$$

where $u_{\max}$ is the maximum velocity magnitude, $\Delta x = 2\pi/N$ is the grid spacing, and $\nu$ is the kinematic viscosity.

**Physical meaning:** When $\nu$ drops by a factor of 100 (NC-DS-11 spike), $\sigma$ increases by 100×. A baseline $\sigma \approx 3$ becomes $\sigma \approx 314$ post-spike. The detection threshold is $\sigma > 100$.

> [!IMPORTANT]
> **Do NOT** use the old ratio $\sigma = \Delta t_{\text{adv}} / \Delta t_{\text{diff}}$. The implementation in
> `production_sla_monitor.py:negative_control_nc_ds11()` uses the formula above.

## 3. Telemetry Schema
The solver writes JSON telemetry to the RunuX shared memory buffer. The agent must parse:
```json
{
  "step": 5000,
  "dt": 0.001,
  "enstrophy": 45.2,
  "stiffness_ratio": 8.4,
  "max_divergence": 1.2e-14,
  "u_max": 1.23,
  "nu": 0.001,
  "dx": 0.245
}
```

## 4. Intervention Policies
If $\sigma > 100$ or `max_divergence` jumps by more than a factor of $10^2$ in 5 steps:
1. Issue a steering command (H26: must be structured JSON, not prose):
```json
{
  "command": "steer",
  "scheme": "BDF",
  "target_dt": 0.0005,
  "steps_to_stabilize": 47,
  "_measured": true
}
```
2. Monitor the next 50 steps. If stabilization fails, issue `"command": "escalate"`.

## 5. Output Contract (H26 Mandatory)
Every response from `agentic_runtime_monitor` must be structured JSON:
```json
{
  "command": "steer|hold|escalate",
  "scheme": "BDF|Adams",
  "steps_to_stabilize": 47,
  "_measured": true
}
```
A prose response (free-form text) is a **hard H26 violation** — the orchestrator will reject it.

## 6. Phase 6 Negative Control (H24)
To verify this skill, the agent must pass Gate 8 (H24): Intercept `NC-DS-11` (stiffness spike injection via
100× viscosity drop → σ rises from ~3 to ~314) and successfully return the solver to a stable state within
50 time steps. **The gate is wired to `negative_control_nc_ds11()` in `production_sla_monitor.py`** — not prose assertion.
