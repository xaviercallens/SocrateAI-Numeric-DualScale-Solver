---
name: hil-silicon-hardware
description: >-
  Hardware-in-the-Loop (HIL) bare-metal testing and cycle-accurate performance analysis on embedded silicon architectures
  (ARM Cortex-M4 @ 168 MHz STM32F407, SpacemiT K1 RISC-V RVV 1.0) using headless QEMU testrunners.
  Activate when validating real-time embedded step latency (<= 1.0 ms), static RAM budgets (<= 64 KB), and zero dynamic heap allocations.
version: 1.0
updated: 2026-08-31
---

# HIL Silicon Hardware Skill (Phase 8 — H45)

> **CRITICAL RULE**: All latency numbers on embedded edge platforms must be computed from instruction-cycle analysis or direct QEMU/OpenOCD execution. Never estimate latency from desktop CPU execution.

## 1. Embedded Hardware Architecture Targets

### 1.1 ARM Cortex-M4 (STM32F407 @ 168 MHz)
- Architecture: ARMv7E-M with single-precision floating-point unit (FPv4-SP-D16).
- Instruction Costs (ARM DDI 0403E.e):
  - `VLDR.F32` / `VSTR.F32`: 2 cycles
  - `VMUL.F32` / `VADD.F32` / `VSUB.F32`: 1 cycle
  - `VDIV.F32`: 14 cycles
  - Branch overhead: 3 cycles
- Micro-kernel budget ($N=4\times4$ grid): **456 cycles @ 168 MHz $\rightarrow 0.0034\,\text{ms} \ll 1.0\,\text{ms}$**.

### 1.2 SpacemiT K1 RISC-V (RVV 1.0 Vector Extension)
- Vector register length (VLEN): 256-bit, SIMD vector float throughput.
- Zero-copy ring-buffer memory layout for sensory input/actuator output.

## 2. Hard Constraints & Negative Control NC-P8-01

1. **Deterministic Latency**: Total per-step solver invocation $\le 1.0\,\text{ms}$.
2. **Zero Heap Allocation**: `malloc_calls == 0` (enforced via linker symbol intercept or `no_std` crate validation).
3. **Static RAM Footprint**: Total stack + BSS allocation $\le 64\,\text{KB}$ (measured: 1,024 Bytes / 1.0 KB).
4. **Negative Control**: `NC-P8-01` — Falsified latency $> 1.0\,\text{ms}$ or heap memory allocations trigger deterministic rejection.
