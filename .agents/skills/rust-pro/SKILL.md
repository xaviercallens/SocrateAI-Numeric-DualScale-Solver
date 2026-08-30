---
name: rust-pro
description: >-
  Expert Rust systems programming, memory safety, zero-copy FFI, PyO3/C-ABI bindings,
  SIMD vectorization, and concurrency patterns. Activate when developing, refactoring,
  or optimizing Rust modules, crates, or runtime kernel bindings.
---

# Rust Pro Systems Engineering Skill

Expert methodologies for high-performance, memory-safe, and zero-cost abstraction systems programming in Rust.

## 1. Core Directives

1. **Zero-Copy & Memory Architecture**:
   - Prefer borrowing (`&T`, `&mut T`) and slicing (`&[T]`) over heap cloning (`Clone`, `to_vec()`).
   - Use custom arena allocators (e.g. `bumpalo` or `arena_mem` from `runux-ai-runtime`) for batch PDE grid allocations to avoid global allocator contention.

2. **SIMD & High-Throughput Compute**:
   - Exploit target-specific auto-vectorization (`target-cpu=native`, AVX-512, NEON, RVV).
   - Utilize `std::simd` or explicit vector intrinsics for inner spectral grid transforms and dyadic shell loops.

3. **FFI & Python Integration (PyO3 / C-ABI)**:
   - Expose safe C-ABI `extern "C"` functions with `#[no_mangle]` or PyO3 extension modules.
   - Guard against panics crossing FFI boundaries using `std::panic::catch_unwind`.
   - Pass contiguous memory slices via raw pointer and length (`*const f64`, `usize`) with strict safety invariants.

## 2. Verification & Safety

- Run strict Clippy linter: `cargo clippy --all-targets -- -D warnings`.
- Verify memory leak freedom using Valgrind or Miri: `cargo miri test`.
- Eliminate unsafe blocks unless strictly required for FFI, with comprehensive `// SAFETY:` rationale.
