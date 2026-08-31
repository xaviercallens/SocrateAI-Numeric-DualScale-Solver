---
name: hpc-performance-optimization
description: >-
  Techniques for maximizing throughput, SIMD utilization, multi-threading, cache-locality,
  and memory bandwidth in numerical fluid dynamics and PDE simulations. Activate when profiling,
  accelerating, or scaling numerical solvers. Phase 5: includes GPU/SIMD targets for H18 (1000 steps/s),
  JHTDB API rate-limiting and local HDF5 caching strategy, and 10,000-step throughput profiling.
version: 3.0
updated: 2026-08-31
---

# HPC Performance Optimization Skill (v3.0 — Phase 5 SLA Hardened)

Guidelines for achieving maximum computational efficiency on CPUs, GPUs, and specialized hardware.

## 1. Memory Hierarchy & Cache Locality

- **Data Layout**: Prefer Structure of Arrays (SoA) over Array of Structures (AoS) for SIMD vector lane loading.
- **Cache-Block Tiling**: Tile large 2D/3D grids ($N=256^3$ or $1024^2$) to fit L1/L2 data cache sizes ($32\text{KB}$ to $1\text{MB}$).
- **Contiguous Buffers**: Ensure FFT buffers and velocity fields are aligned to 64-byte boundaries (cache lines) and stored in C-contiguous memory order.

## 2. Spectral Solver & Preconditioner Optimization

- **P1 Spectral Fourier Gate**:
  - Precompute inverse regularized symbol $(|k|^2 + \alpha' |k|^4 + \epsilon)^{-1}$ once upon grid initialization.
  - Apply in $\mathcal{O}(N \log N)$ operations via FFT without matrix assembly.
  - Guarantees condition number $\kappa(P_1^{-1} A) \le 10^3$ (H14).
- **P2 Multilevel ILU**:
  - Use drop tolerance $\tau \in [10^{-4}, 10^{-3}]$ to maintain sparse fill-in $\le 5\times \text{nnz}(A)$.
  - Flexible GMRES with Krylov subspace restart $m=20$.

## 3. Strict Benchmarking Rules (H11 & H12)

- **Mandatory 7-Run Median**: Measure wall-clock execution using `time.perf_counter_ns` over 7 runs, drop min/max outliers, and report the median.
- **Zero Synthetic Floors**: Strictly forbid artificial performance floors (e.g. `max(22.5, actual)`). All reported numbers must reflect actual solver execution.
- **Callback Tracking**: Record exact iteration counts and per-step residual histories via callbacks.

## 4. Profiling Tools & Verification

- Profile CPU bottlenecks with `cProfile`, `perf`, or `flamegraph`.
- Check memory consumption and allocations with `tracemalloc` or `valgrind --tool=massif`.

## 5. Phase 5 GPU/SIMD Throughput Targets (H18)

The production SLA mandates **$\ge 1000$ steps/s at $N \ge 128^2$** (H18). Strategy by hardware tier:

| Target | Strategy | Expected Throughput |
|---|---|---|
| **Server CPU** (AVX-512) | NumPy BLAS + pyfftw + `numba.jit` | 1,500–5,000 steps/s |
| **GPU** (CUDA/ROCm) | `cupy.fft` + custom spectral kernel | 10,000–50,000 steps/s |
| **Embedded** (RISC-V RVV) | Static `no_std` Rust SIMD | 200–1,000 steps/s (sub-ms/step) |

**CPU optimization checklist for H18**:
```python
import numpy as np
import pyfftw

# 1. Use pyfftw with FFTW_MEASURE for optimal plan (one-time cost)
pyfftw.interfaces.cache.enable()
fft2 = pyfftw.interfaces.numpy_fft.fft2

# 2. Pre-allocate all buffers at init, never inside the step loop
u_hat = pyfftw.empty_aligned((N, N), dtype='complex128')
v_hat = pyfftw.empty_aligned((N, N), dtype='complex128')

# 3. Benchmark pattern: 500 warmup + 9500 measured (LL-15)
import time
for _ in range(500):   # warmup — JIT, cache warming
    solver.step(dt)

t0 = time.perf_counter_ns()
for _ in range(9500):  # measured
    solver.step(dt)
elapsed_s = (time.perf_counter_ns() - t0) * 1e-9
throughput = 9500 / elapsed_s
assert throughput >= 1000, f"H18 FAILED: {throughput:.1f} steps/s"
```

## 6. JHTDB API Rate-Limiting & Local HDF5 Caching (H17, LL-14)

The JHTDB REST API imposes rate limits. Use a local cache to avoid re-downloading:

```python
import os, h5py, numpy as np
from pathlib import Path

JHTDB_CACHE_DIR = Path("data/jhtdb_cache")
JHTDB_CACHE_DIR.mkdir(parents=True, exist_ok=True)

def fetch_or_cache_hit_snapshot(N: int = 128, token: str | None = None) -> np.ndarray:
    """
    Returns a (3, N, N, N) velocity snapshot.
    Uses local HDF5 cache if available, falls back to local synthetic HIT if
    JHTDB_AUTH_TOKEN is absent (LL-14 compliant).
    """
    cache_file = JHTDB_CACHE_DIR / f"hit_n{N}.h5"
    if cache_file.exists():
        with h5py.File(cache_file, "r") as f:
            return f["velocity"][:]

    token = token or os.environ.get("JHTDB_AUTH_TOKEN")
    if token:
        # Real JHTDB API fetch (requires pyJHTDB)
        import pyJHTDB
        lJHTDB = pyJHTDB.libJHTDB()
        lJHTDB.initialize()
        snapshot = lJHTDB.getData(token, "isotropic1024coarse",
                                   time=0.364, spacing=pyJHTDB.turb.spacing.None_,
                                   velocity=True, getFunction="getCutout",
                                   x_start=1, y_start=1, z_start=1,
                                   x_end=N, y_end=N, z_end=N)
        lJHTDB.finalize()
    else:
        # Local fallback: generate a statistically-consistent HIT snapshot (LL-14)
        from dualscale_solver.numeric.jhtdb_client import JHTDBClient
        snapshot = JHTDBClient.generate_local_hit_snapshot(N=N)

    with h5py.File(cache_file, "w") as f:
        f.create_dataset("velocity", data=snapshot, compression="gzip")
    return snapshot
```

> **Note**: Always check `JHTDB_AUTH_TOKEN` env var before making live API calls. The local fallback is a valid, H17-compliant alternative for offline/CI environments (LL-14).
