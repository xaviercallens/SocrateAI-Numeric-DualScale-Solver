# TODO.md — LeanFlow DualScale Solver Action Items

## 🚀 Active Sprint: Phase 0 Completion & Phase 1 Kickoff

### Phase 0: Foundations & Architecture Scaffolding
- [x] Create project repository structure and documentation (`SPEC.md`, `HARDNESS.md`, `LEDGER.md`, `NAMING_POLICY.md`).
- [x] Implement Tier B exact rational T-duality invariants (`dualscale_solver/exact/t_duality.py`).
- [x] Implement dyadic shell energy-enstrophy telescoping bounds (`dualscale_solver/exact/cascade_invariants.py`).
- [x] Implement 2D/3D pseudo-spectral Navier–Stokes solver with Orszag 2/3 dealiasing and Leray divergence-free projection.
- [x] Implement integrating factor RK4 (ETD-RK4) for stiff dual-scale ultraviolet dissipation.
- [x] Implement automated certificate generator and schema validator.
- [x] Implement Mathesis Stream 0 transitive soundness ledger checker (`ledger_checker.py` and `ledger.jsonl`).
- [x] Implement Runux AI Runtime & Rust Linux Mini-Kernel detection bridge (`runux_bridge.py`).
- [x] Establish 3-Gate verification protocol in `scripts/verify.sh` (21/21 tests passing).
- [x] Create Antigravity specialized agent personas and science skills in `.agents/`.

---

## 📅 Phase 1: Lean 4 Mathematical Formalization (Months 3–12)
- [ ] Scaffold `lean4/` Lake project with Mathlib pinning.
- [ ] Implement `galerkin.lean`:
  - [ ] Finite Galerkin truncation ball $\mathcal{B}(M)$ definition.
  - [ ] Non-linear triadic transfer antisymmetry $\sum T(p,q,k) = 0$.
  - [ ] Energy conservation identity in inviscid limit.
- [ ] Implement `leray.lean`:
  - [ ] Leray projector definition $\mathcal{P}_{ij}(k) = \delta_{ij} - \frac{k_i k_j}{|k|^2}$.
  - [ ] Idempotence theorem: $\mathcal{P}^2 = \mathcal{P}$.
  - [ ] Transversality / divergence-free condition: $k \cdot \mathcal{P}(k) v = 0$.
- [ ] Implement `frustration.lean`:
  - [ ] Formal definition of Triadic Frustration Index $\mathcal{D}(M, u)$.
  - [ ] High-frustration truncation theorem: $\mathcal{D}(M) > 10 \implies$ phase cancellation dominance.
- [ ] Implement `prodi_serrin.lean` & `hypothesis_U.lean`:
  - [ ] Sobolev embedding $H^1 \hookrightarrow L^6$.
  - [ ] Hypothesis U uniform enstrophy bound implying Prodi-Serrin regularity.
- [ ] Draft and submit arXiv preprint on the Dual-Scale LeanFlow mathematical foundations.

---

## ⚙️ Phase 2: High-Performance Rust Solver Core (Months 12–18)
- [ ] Initialize Cargo workspace with crates: `leanflow-core`, `leanflow-solver`, `leanflow-linear`, `leanflow-ai`.
- [ ] Implement `leanflow-core`:
  - [ ] Contiguous 2D/3D grid mesh structures with 64-byte cache alignment.
  - [ ] Complex tensor representations with SIMD vectorization.
- [ ] Implement `leanflow-solver`:
  - [ ] Bind `rusty-SUNDIALS` (`cvode`, `nvector`, `sundials-core`) BDF (1–5) and Adams-Moulton (1–12).
  - [ ] Integrate Triadic Frustration Index calculation $\mathcal{D}(M)$ in native Rust.
  - [ ] Dynamic mesh adaptation based on $\mathcal{D}(M)$.
- [ ] Implement `leanflow-linear`:
  - [ ] Preconditioned Krylov methods: GMRES, FGMRES, BiCGSTAB.
- [ ] Publish LeanFlow Community Edition (BSD-3-Clause) on Crates.io and GitHub.

---

## 🧠 Phase 3: Neuro-Symbolic AI Preconditioners (Months 18–24)
- [ ] Implement Preconditioner P1 (Spectral Fourier Gate) with $41.8\times$ target speedup.
- [ ] Implement Preconditioner P2 (Mixed-Precision FGMRES) with $61.1\times$ target speedup on CPU.
- [ ] Implement Preconditioner P3 (FP8 TensorCore AMG) with $130.8\times$ target speedup on GPU/TPU via `runux-ai-runtime`.
- [ ] Integrate SymBrain v4 adaptive mesh and timestep router.
- [ ] Benchmark against OpenFOAM and ANSYS Fluent baselines.
- [ ] Launch LeanFlow Pro (Cloud SaaS tier).

---

## 🛰️ Phase 4: Real-Time & Embedded Deployment (Months 24–30)
- [ ] Port `leanflow-solver` to `no_std` for `rust-linux-mini-kernel`.
- [ ] Build SpacemiT K1 RISC-V RVV SIMD backend.
- [ ] Build STM32 ARM Cortex-M embedded binary.
- [ ] Build Raspberry Pi ARM Linux deployment package.
- [ ] Launch LeanFlow Enterprise (Dual-licensing).

---

## 🏭 Phase 5: Industrial Validation & Research Publication (Months 30–36)
- [ ] Conduct industrial bioreactor fluidic control experiments ($k_L a = 115.89/\text{s}$, $3.14\times$ yield).
- [ ] Conduct aerodynamic wing simulation drag reduction benchmarks (5–10% drag reduction).
- [ ] Finalize mathematical proof of Asymptotic Frustration Conjecture and submit to top-tier mathematics journal.
