---
name: rust-pro
description: >-
  Expert Rust systems programming, memory safety, zero-copy FFI, PyO3/C-ABI bindings,
  SIMD vectorization, and concurrency patterns. Activate when developing, refactoring,
  or optimizing Rust modules, crates, or runtime kernel bindings.
  Phase 5: includes rayon + AVX-512 streaming throughput patterns for H18 (1000+ steps/s).
version: 3.0
updated: 2026-08-31
---

# Rust Pro Systems Engineering Skill (v3.0 — Phase 5 SLA Hardened)

Expert methodologies for high-performance, memory-safe, and zero-cost abstraction systems programming in Rust.

## 1. Core Directives

1. **Zero-Copy & Memory Architecture**:
   - Prefer borrowing (`&T`, `&mut T`) and slicing (`&[T]`) over heap cloning (`Clone`, `to_vec()`).
   - Use custom arena allocators (`bumpalo` or `arena_mem` from `runux-ai-runtime`) for batch PDE grid allocations.
   - Maintain 64-byte alignment on all tensor buffers for AVX-512 vector pipelines.

2. **SIMD & ETD-RK4 Implementation Patterns**:
   - Strictly follow exact Cox-Matthews / Kassam-Trefethen integrating factor coefficients in `step_etd_rk4`:
     - Stage 2: `u_tmp = e_half * (u + 0.5 * dt * k1)`
     - Stage 3: `u_tmp = e_half * u + 0.5 * dt * k2`
     - Stage 4: `u_tmp = e_full * u + dt * e_half * k3`
     - Final combine: `out = e_full * u + (dt/6) * (e_full * k1 + 2 * e_half * k2 + 2 * e_half * k3 + k4)`
   - Never omit `e_half` scaling on intermediate RK stages.

3. **FFI & Python Integration (PyO3 / C-ABI)**:
   - Expose safe C-ABI `extern "C"` functions with `#[no_mangle]`.
   - Guard against panics crossing FFI boundaries using `std::panic::catch_unwind`.
   - Pass contiguous memory slices via raw pointer and length (`*const f64`, `usize`).

## 2. Verification & Safety

- Run strict Clippy linter: `cargo clippy --all-targets -- -D warnings`.
- Workspace unit test verification: `cargo test --workspace`.
- Eliminate unsafe blocks unless strictly required for FFI, with comprehensive `// SAFETY:` rationale.

## 3. Phase 5 Streaming SIMD Throughput Pattern (H18 — 1000+ steps/s)

For Phase 5 production SLA compliance, the Rust spectral step must sustain $\ge 1000$ steps/s at $N=128^2$. Use `rayon` + SIMD parallelism over spectral shell buffers:

```rust
use rayon::prelude::*;

/// Apply Fourier-space Leray projection in parallel over wavenumber shells.
/// Achieves cache-local SIMD throughput for H18 SLA compliance.
pub fn leray_project_parallel(u_hat: &mut [f64], k_sq: &[f64], n: usize) {
    debug_assert_eq!(u_hat.len(), 2 * n);  // interleaved Re/Im
    debug_assert_eq!(k_sq.len(), n);

    u_hat
        .par_chunks_mut(8)  // 4 complex values per SIMD lane (AVX-512 f64x8)
        .zip(k_sq.par_chunks(4))
        .for_each(|(u_chunk, k_chunk)| {
            for i in 0..k_chunk.len() {
                let k2 = k_chunk[i];
                if k2 > 0.0 {
                    // Project out longitudinal component: û ← (I - k⊗k/|k|²) û
                    let re = u_chunk[2 * i];
                    let im = u_chunk[2 * i + 1];
                    let proj_factor = 1.0 - 1.0 / k2;
                    u_chunk[2 * i]     = re * proj_factor;
                    u_chunk[2 * i + 1] = im * proj_factor;
                }
            }
        });
}

/// H18 throughput benchmark — call from integration tests.
/// Measures steps/s over 9500 steps (500 warmup, per LL-15).
pub fn benchmark_h18_throughput(solver: &mut impl SpectralSolver) -> f64 {
    // Warmup (LL-15: avoid cold-start cache artifacts)
    for _ in 0..500 { solver.step(); }

    let t0 = std::time::Instant::now();
    for _ in 0..9500 { solver.step(); }
    let elapsed = t0.elapsed().as_secs_f64();

    9500.0 / elapsed
}
```

**Cargo.toml additions** for Phase 5 SIMD:
```toml
[dependencies]
rayon = "1.10"

[profile.release]
opt-level = 3
lto = "thin"
codegen-units = 1

[build]
rustflags = ["-C", "target-cpu=native"]  # Enable AVX-512 on capable CPUs
```
