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
- [x] Publish certified HuggingFace JHTDB Benchmark comparing LeanFlow vs OpenFOAM (7 OOM better divergence, 2.10x faster).

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

## 🏭 Phase 5: AI Preprocessing & Industrial Validation (Months 30–36)
- [x] Implement AI-driven dynamic mesh resolution based on initial enstrophy estimates.
  - [x] `NeuroSymbolicMesher` (Python `src/dualscale_solver/ai/preprocessing.py`)
  - [x] `NeuroSymbolicMesher` Rust crate (`crates/leanflow-ai/src/mesh_preprocessing.rs`)
  - [x] H20 gate: $k_{\max}\eta \ge 1.5$ invariant enforced and tested
- [x] Implement LLM-based boundary condition parser mapping natural language to exact mathematical constraints.
  - [x] `BoundaryConditionInference` (Python) + `parse_boundary_condition` (Rust)
  - [x] Leray projection solenoidality constraint enforced
- [x] Integrate `runux-ai-runtime` for zero-shot fluidic parameter tuning and hyperparameter optimization.
  - [x] `ParameterTuner` Rust + Python wrappers
  - [x] CFL-compliant dt selection + stiffness-based BDF/Adams/ETD-RK4 routing
- [x] Implement 6-agent autonomous Phase 5 workflow orchestrator.
  - [x] CERT-P5-WF-B0C43C9E issued (SHA-256 certified)
  - [x] 78/78 Python tests, 13/13 leanflow-ai Rust tests
- [x] Publish LeanFlow model to HuggingFace Hub `callensxavier/leanflow-dualscale-pde`
- [x] Phase 5 `verify.sh` Gate 5 with H17–H20 certification
- [ ] Conduct industrial bioreactor fluidic control experiments ($k_L a = 115.89/\text{s}$, $3.14\times$ yield).
- [ ] Conduct aerodynamic wing simulation validation against real empirical datasets.
- [ ] Finalize mathematical proof of Asymptotic Frustration Conjecture.

## 🔧 Sprint 1 Audit Remediation (2026-08-31)
- [x] **IP-01**: Git commit 69 files of Phase 2–5 work
- [x] **IP-03**: Wire Rust unit tests for `leanflow-ai` (13 tests: 4 NCs + 9 positives)
- [x] **IP-04**: Fix H18 SLA Gate 5 grid from N=64 → N=128 + explicit SLA probe
- [x] **IP-02**: Substantiate Lean 4 proofs:
  - [x] `Galerkin.lean`: concrete TriadicTransfer + algebraic double-sum energy conservation
  - [x] `Leray.lean`: concrete EuclideanSpace projector + field_simp/ring idempotence proof
  - [x] `FrustrationMonotonicity.lean`: H19 stub + D(M)≥1 bound proved
- [x] **IP-11**: LL-19 (Lean 4 vacuous proof pattern) added to LL.md and HARDNESS.md
- [x] **H21/H22/H23**: New hardness invariants added to HARDNESS.md
- [ ] **IP-05**: Sync TODO.md — IN PROGRESS (this file)
- [x] **IP-06**: Native rusty-SUNDIALS Rust FFI (Sprint 2)
- [x] **IP-07**: arXiv preprint draft `report/leanflow_preprint_v1.tex` (Sprint 2)
- [x] **IP-08**: HuggingFace model versioning: tag `v1.0.0-phase5-cert-B0C43C9E` (Sprint 2)
- [ ] **IP-09**: `lean4/prodi_serrin.lean` Sobolev embedding proof (Sprint 3)
- [ ] **IP-10**: N=128 throughput profiling with py-spy + Numba JIT (Sprint 3)

