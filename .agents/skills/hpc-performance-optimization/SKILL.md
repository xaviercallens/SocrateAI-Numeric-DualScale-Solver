---
name: hpc-performance-optimization
description: >-
  Techniques for maximizing throughput, SIMD utilization, multi-threading, cache-locality,
  and memory bandwidth in numerical fluid dynamics and PDE simulations. Activate when profiling,
  accelerating, or scaling numerical solvers.
---

# HPC Performance Optimization Skill

Guidelines for achieving maximum computational efficiency on CPUs, GPUs, and specialized hardware.

## 1. Memory Hierarchy & Cache Locality

- **Data Layout**: Prefer Structure of Arrays (SoA) over Array of Structures (AoS) for SIMD vector lane loading.
- **Cache-Block Tiling**: Tile large 2D/3D grids (e.g. $N=256^3$ or $1024^2$) to fit L1/L2 data cache sizes ($32\text{KB}$ to $1\text{MB}$).
- **Contiguous Buffers**: Ensure FFT buffers and velocity fields are aligned to 64-byte boundaries (cache lines) and stored in C-contiguous memory order.

## 2. Spectral Solver Optimization

- **Fast Fourier Transforms**:
  - Precompute wavenumber grids ($k_x, k_y, |k|^2, \mathcal{P}_{ij}(k)$) and reuse plans across RK4 sub-steps.
  - Apply in-place FFT operations (`fftn(..., out=...)` or `fftw` planning) to eliminate memory reallocation overhead.
- **Exponential Time Differencing (ETD)**:
  - Precompute exponential integrating factors $E = e^{-D(k) \Delta t}$ once per timestep.
  - Decouple stiff linear decay from advective non-linear products.

## 3. Profiling Tools & Verification

- Profile CPU bottlenecks with `cProfile`, `perf`, or `flamegraph`.
- Check memory consumption and allocations with `tracemalloc` or `valgrind --tool=massif`.
