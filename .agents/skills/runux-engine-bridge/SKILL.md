---
name: runux-engine-bridge
description: >-
  Workflows for bridging the Dual-Scale PDE numerical solver with Xavier Callens' runux-ai-runtime
  (GPU compute, HAL, Arena memory, SIMD) and rust-linux-mini-kernel (bare-metal compute & Lean 4 verification).
  Activate when interfacing Python numerical solvers with Runux AI runtime crates or native mini-kernel engines.
---

# Runux AI Runtime & Rust Mini-Kernel Bridge Skill (v2.0 — Phase 2 Hardened)

This skill governs integration between the **Dual-Scale Numerical Solver** and the **Runux AI Runtime** / **Rust Linux Mini-Kernel** ecosystem.

## 1. System Architecture & Repositories

```
/home/xavkal/xdev/
├── SocrateAI-Numeric-DualScale-Solver/   # High-level multiscale PDE solvers & verification
├── runux-ai-runtime/                    # High-throughput AI runtime, GPU compute, SIMD & arena memory
└── rust-linux-mini-kernel/              # Bare-metal Rust kernel, no-std harnesses & Lean 4 specs
```

## 2. Phase 2 Integration Points

| Integration Area | Runux Crates | DualScale Solver Capability | Hardness Target |
|---|---|---|---|
| **Memory Allocation** | `crates/arena_mem` | Zero-allocation buffer reuse for spectral grid iterations | Zero heap allocation in inner loop |
| **P1 Fourier Gate** | `crates/gpu_compute`, `crates/rvv_simd` | Hardware-accelerated FFT & Rulial scale regularized gate | $\kappa(P_1^{-1} A) \le 10^3$ (H14) |
| **P2 Multilevel ILU** | `crates/ai_bridge`, `crates/hal` | Unified C-ABI / FFI execution loop with FGMRES | Residual reduction $\ge 10^8$ |
| **Formal Specs** | `specs/` (Lean 4) | Cross-validation of kernel mathematical invariants | Zero sorry (H1) |

## 3. Python FFI Bridge & Preconditioner Dispatch

The module [`src/dualscale_solver/runtimes/runux_bridge.py`](file:///home/xavkal/xdev/SocrateAI-Numeric-DualScale-Solver/SocrateAI-Numeric-DualScale-Solver/src/dualscale_solver/runtimes/runux_bridge.py) provides a direct abstraction to detect, link, and dispatch high-throughput simulation payloads:

```python
from dualscale_solver.runtimes.runux_bridge import RunuxEngineBridge
bridge = RunuxEngineBridge()
# Dispatches to native Runux Arena + SIMD kernel if available, with graceful Python fallback
```

## 4. Epistemic Hardness Invariants
- **No Mock Defaults**: All bridge bindings must set `_measured: true` and record real runtime benchmarks.
- **Negative Control**: Bridge must fail gracefully and reject unaligned memory buffers.
