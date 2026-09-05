---
name: monotonic-greedy-search
description: >-
  Workflows and algorithmic guidelines for Monotonic Greedy Line Search with Backtracking
  (replacing legacy buzzwords like 'Karpathy Ratchet'). Enforces 5-step optimization cycles,
  strict monotonic progress, temperature breakers for local minimum escape, and SHA-256 audit sealing.
version: 1.0
tier: T1
target_model: gemini-3.8-flash
reasoning_budget: high
---

# Monotonic Greedy Line Search with Backtracking

This skill provides operational and algorithmic guidelines for autonomous parameter optimization in scientific simulations using **Monotonic Greedy Line Search with Backtracking**.

> [!NOTE]
> Per `AGENTS.md` and `LL.md`, this replaces all legacy references to `"Karpathy Ratchet Auto-Research Loop"` with rigorous, standard mathematical optimization nomenclature.

---

## The 5-Step Optimization Cycle

```
┌────────────────────────────────────────────────────────┐
│  1. PROPOSE                                            │
│  - Hypothesis generator proposes parameter mutation    │
└──────────────────────────┬─────────────────────────────┘
                           │
┌──────────────────────────▼─────────────────────────────┐
│  2. EVALUATE                                           │
│  - Run PDE solver simulation & compute fitness metric  │
└──────────────────────────┬─────────────────────────────┘
                           │
┌──────────────────────────▼─────────────────────────────┐
│  3. RATCHET                                            │
│  - If fitness improves: accept & commit as baseline    │
│  - If fitness regresses: reject & revert immediately   │
└──────────────────────────┬─────────────────────────────┘
                           │
┌──────────────────────────▼─────────────────────────────┐
│  4. VERIFY                                             │
│  - Audit negative controls & compute SHA-256 seal      │
└──────────────────────────┬─────────────────────────────┘
                           │
┌──────────────────────────▼─────────────────────────────┐
│  5. REFLECT                                            │
│  - Update history; trigger temperature breaker if stuck│
└────────────────────────────────────────────────────────┘
```

---

## Dynamic Temperature Breaker

When an optimization sweep encounters a local minimum:
1. **Stagnation Counter**: Track consecutive non-improving iterations (`stagnation_count`).
2. **Breaker Threshold**: When `stagnation_count >= stagnation_window` (default: 3 iterations), set `is_stuck = True`.
3. **Radical Mutation**: Instruct the hypothesis generator (or LLM steering prompt) to perturb parameters by a larger exploration factor ($> 30\%$) or switch parameter subspace, breaking out of shallow local extrema.

---

## Epistemic Guardrails for Line Search

1. **Deterministic Monotonicity**:
   The baseline fitness $f(x_{\text{best}})$ must be strictly non-decreasing across accepted iterations:
   $$f(x_{k+1}) \ge f(x_k)$$
   Any rollback must guarantee that $x_{\text{best}}$ remains unaltered.
2. **Surrogate Scope Caveat**:
   Optimizations performed over a reduced-order model (e.g. $N=32$ Fourier modes) must explicitly log that the obtained optimum is a **surrogate optimum**, not necessarily the global optimum of the full Navier-Stokes equations.
3. **Audit Hash Sealing**:
   Compute a deterministic SHA-256 hash linking the optimization history, best parameters, and solver certificate:
   $$\text{hash} = \text{SHA-256}(\text{JSON}(\{ \text{problem}, \text{best\_params}, \text{fitness}, \text{steps} \}))$$
