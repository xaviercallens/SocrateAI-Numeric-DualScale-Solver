# HARDNESS.md — Program-Wide Scientific Hardness & Epistemic Charter
**Version:** 3.0 — Phase 5 Extended (2026-08-31)
**Program:** SocrateAI Dual-Scale & LeanFlow Multiscale Navier–Stokes Program  
**Status:** MANDATORY & NON-NEGOTIABLE INVARIANTS  
**Scope:** All mathematical proofs, exact verifiers, numerical solvers, AI preconditioners, embedded kernels, **agent workflow outputs**, and **Phase 5 production / JHTDB validation pipelines**.  
**Changelog v3.0:** Added H17 (JHTDB Spectral Fidelity Gate), H18 (Production SLA Gate), H19 (Frustration Monotonicity Gate). Added LL-14–LL-16 from Phase 5 gap analysis. Added Gates 5 & 6.  
**Changelog v2.0:** Added H11 (No Synthetic Results), H12 (Real Benchmark Mandate), H13 (Agent Code Review Gate). Strengthened H6 tolerance to `1e-13`. Added Lesson Learned annotations.

---

## 1. The Nineteen Inviolable Scientific Invariants (H1–H19)

These structural invariants define the hardness of the SocrateAI scientific program. They **never bend** under schedule pressure, token limits, or algorithmic convenience.

### `H1` : Zero-Sorry Lean 4 Formal Verification (Tier A)
All foundational algebraic and geometric theorems must compile in Lean 4 without `sorry` and with zero unvetted custom `axiom` declarations. `#print axioms <theorem_name>` must strictly output:
```lean
[propext, Classical.choice, Quot.sound]
```
**Agent Gate**: The `math_reviewer` agent must run `lake build` and assert exit code 0 before any theorem is considered Tier A certified. A passing `lake build` run must be captured in the workflow JSON artifact.

**Lesson Learned (Phase 1 Audit)**: Three Lean 4 modules (`Galerkin.lean`, `Leray.lean`, `Frustration.lean`) were written but never registered in `lakefile.lean`. They were never kernel-checked. The `math_reviewer` agent reported them as "Tier A" without evidence. Fix: agents must call `lake build` programmatically, not rely on file existence.

---

### `H2` : Negative Control is the Checker (Tier B)
Every verifier, invariant checker, and test suite must ship with an explicit negative control demonstrating that falsified states, broken symmetries, or energy leaks are **deterministically caught and rejected**. A verifier without a demonstrated-to-fail negative control is invalid.

**Agent Gate**: The `qa_scientific_auditor` agent must call all `negative_control_*()` functions programmatically and assert each returns `True` (i.e., each negative control correctly rejected the falsified input).

**Lesson Learned (Phase 1 Audit)**: All 10 HARDNESS invariants were hardcoded to `True` in the QA agent. H2 was marked "passed" without any negative control function being called. This made the `CERT-P1-WF-*` certificate scientifically void.

---

### `H3` : Exact Rational Arithmetic Over $\mathbb{Q}$ (Tier B)
Floating-point approximations (`f32`, `f64`) are strictly forbidden in Tier B verification algorithms. Invariant checking, certificate emission, and symmetry validation must use exact rational arithmetic ($\mathbb{Q}$ via `fractions.Fraction` or integer lattices).

---

### `H4` : Non-Vacuity & Falsifiability
Every theorem statement, predicate, and filter must be proven non-vacuous by exhibiting:
1. At least one non-trivial instance satisfying the premise.
2. At least one explicit counter-model or perturbation violating the conclusion when premises are relaxed.

---

### `H5` : Strict Rulial Inversion (No Artificial Cutoffs)
Singularity prevention and scale regularization must never rely on ad-hoc empirical cutoffs or artificial smoothing, but strictly on exact **Rulial Inversions**:

$$R_{\text{eff}}(R) = \max\left(R, \frac{\alpha'}{R}\right), \quad R_{\text{eff}} \ge \sqrt{\alpha'}$$

The inverse scale $\alpha'/R$ guarantees bounded geometry at all scales without breaking microscopic conservation laws.

---

### `H6` : Solenoidal Transversality & Leray Idempotence (Tightened)
Incompressible velocity fields must maintain exact machine-precision transversality:

$$\mathcal{P}_{ij}(k) = \delta_{ij} - \frac{k_i k_j}{|k|^2}, \quad \mathcal{P}^2 = \mathcal{P}, \quad |k \cdot \hat{u}(k)| < 10^{-13}$$

**Per-step recording required**: The `experimenter` agent must record divergence at **every time step** and store the time-series in the workflow artifact. Reporting only the maximum scalar is insufficient.

**Lesson Learned (Phase 1 Audit)**: The divergence figure was generated using random jitter (`(0.8 + 0.4 * np.random.rand())`), not actual per-step data. This constitutes result fabrication. The orchestrator now uses a `callback` to record real per-step divergence.

---

### `H7` : Thermodynamic Energy Critic over Statistical Losses
AI modules (`leanflow-ai`, `runux-ai-runtime`) loss functions and preconditioner gating must incorporate physical energy critics that penalize unphysical energy generation, enstrophy blowups ($\Omega > 1/\alpha'$), or Triadic Frustration Index violations.

**Agent Gate**: The `dev_engineer` agent must verify energy monotonicity (`energy[-1] < energy[0]` for viscous runs) and record this boolean explicitly in the workflow JSON.

---

### `H8` : No Claim Outside the Machine-Checked Ledger
No result, bound, theorem, or speedup factor may be cited or relied upon unless entered into `ledger.jsonl` and `LEDGER.md` with:
- Formal unique identifier (`DS-<TIER>-<INDEX>`).
- Explicit epistemic tier ($A, B, L, C, X$).
- Provenance, verification command, and negative control reference.

**Lesson Learned (Phase 1 Audit)**: A "21.2× iteration gain" and "22.5% wall-time reduction" were cited in the QA certificate without ledger entries. Both were hardcoded constants, not measurements. No ledger ID was issued. Fix: all quantitative claims must have a ledger entry before the QA certificate is issued.

---

### `H9` : Transitive Tier Monotonicity
A higher-tier claim cannot depend on a lower-tier assertion:

$$\text{Sound}(L) := \forall a, b. \, b \in L(a).\text{supports} \implies \text{tier}(L(a)) \le \text{tier}(L(b))$$

Where the total order is: $\text{Tier A} > \text{Tier B} > \text{Tier L} > \text{Tier C} > \text{Tier X}$.

---

### `H10` : Agent Self-Reports are Not Evidence
An AI agent stating *"the test passed"* or *"the invariant holds"* does not constitute verification. Verification requires running the code independently, capturing exit code 0, validating the SHA-256 certificate hash, and checking the machine ledger.

**Lesson Learned (Phase 1 Audit)**: The entire 10-invariant QA checklist was a dictionary of hardcoded `True` values. No subprocess, no test runner, no live function call. The agent's text output was treated as the verification artifact. This violates H10 by definition.

---

### `H11` : No Synthetic or Fabricated Results (NEW — Phase 1 Lesson)
**All quantitative results reported in workflow artifacts, figures, and certificates must be derived from actual simulation runs, real solver calls, or real benchmark measurements.** It is explicitly forbidden to:
- Use synthetic formulas as proxies for physical quantities (e.g., `D_M = 12.5 + (m/8)*1.8`).
- Hardcode performance metrics (e.g., `avg_iterations = 85` / `avg_iterations = 4`).
- Apply artificial floors to performance ratios (e.g., `max(22.5, actual_pct)`).
- Generate figures from random noise instead of recorded trajectory data.

**Enforcement**: The `qa_scientific_auditor` agent must inspect the `_formula` or `_method` provenance field of each result. If it reads "synthetic" or "hardcoded", the certificate is automatically `REJECTED`.

**Lesson Learned (Phase 1 Audit)**: Four critical findings (C1–C4) were all violations of this rule. The Phase 1 QA certificate was marked `CERTIFIED` despite all four being present.

---

### `H12` : Real Benchmark Mandate (NEW — Phase 1 Lesson)
Any claimed performance improvement (wall-time, iteration count, memory bandwidth, throughput) must be:
1. **Measured** via a real solver invocation (not a ratio of constants).
2. **Reproducible** — anyone re-running the script must get a result within ±10% of the reported value.
3. **Bounded by physics** — the benchmark setup must use a problem size where the claimed gain mechanism (preconditioner, ETD-RK4, dual-scale) is actually active and dominant.

**Enforcement**: The `experimenter` agent must record the benchmark setup (grid size, system matrix dimensions, solver type) alongside every reported performance number.

**Lesson Learned (Phase 1 Audit)**: The comparison benchmark used two identical `DyadicShellSolver` calls (differing only in `alpha_prime`). The ETD integrating factor in the dual-scale solver added cost, making it potentially **slower** on small grids, yet the code forced a gain by flooring at 22.5%.

---

### `H13` : Agent Code Review Gate Before Certificate (NEW — Phase 1 Lesson)
Before issuing a `CERT-P*-WF-*` certificate, the `qa_scientific_auditor` agent must:
1. Verify that no result field in the workflow JSON contains the string `"synthetic"`, `"hardcoded"`, or `"estimated"` in its value or provenance field.
2. Assert that every numerical performance claim has a corresponding `_measured: true` flag set by the producing agent.
3. Run the verification script (`./scripts/verify.sh`) and capture the exit code — not just call it as a subprocess without checking the return value.

---

### `H14` : Phase 2 Preconditioner Goal Gate (NEW — Phase 2 Protocol)
For all AI and Fourier-space preconditioners ($P_1, P_2$) applied to multiscale linear and non-linear systems $A u = b$:
1. **Spectral Condition Number**: The preconditioned operator $P^{-1} A$ must satisfy:
   $$\kappa(P^{-1} A) \le 10^3 \quad \text{for all resolution levels } N \ge 64^2$$
2. **Krylov Residual Reduction**: Real Krylov solvers (CG/FGMRES) must achieve:
   $$\frac{\|r_k\|_2}{\|r_0\|_2} \le 10^{-8}$$
   within $\le 20$ iterations without synthetic convergence floors.
3. **Cross-Model Validation**: Galerkin truncation invariants in Lean 4 and ETD-RK4 trajectories in Rust must agree within relative error $< 10^{-7}$.
4. **Epistemic Negative Control**: Preconditioners must reject corrupted or non-elliptic operators deterministically.

---

### `H15` : Phase 3 TensorCore AMG & OpenFOAM Supremacy Gate (Tier B / C)
The Phase 3 Neuro-Symbolic AI Preconditioner suite (`P3: Algebraic Multigrid` with FP8 TensorCore acceleration and SymBrain routing) must satisfy:
1. **Measured OpenFOAM Supremacy**: Real measured iteration count reduction $\ge 5\times$ (target $> 10\times$ wall-clock throughput) on identical pressure-Poisson systems compared to OpenFOAM `pimpleFoam` DIC/CG.
2. **Quantization Fidelity**: FP8 quantized coarse solves must exhibit relative difference $\le 10^{-5}$ compared to full-precision FP64 solves.
3. **CFL Stability Margin**: Demonstrate $\ge 100\times$ timestep stability margin over explicit CFL limits without numerical divergence.

---

### `H16` : Phase 4 Zero-Allocation Embedded Target Gate (Tier B / Embedded)
The Phase 4 Embedded & Edge Real-Time solver (`no_std` kernel) must satisfy:
1. **Zero Heap Allocation**: Exactly zero dynamic heap allocations in the inner simulation/control loop.
2. **Static RAM Budget**: Total static memory footprint $\le 64\text{ KB}$ RAM.
3. **Deterministic Latency**: Maximum single-step execution latency $\le 1.0\text{ ms}$ (measured over 1,000 steps).
4. **Bioreactor Transfer Validation**: Achieve oxygen mass transfer $k_L a = 115.89/\text{s}$ yielding $\ge 3.0\times$ algal biomass multiplier.

---

### `H17` : Phase 5 JHTDB Spectral Fidelity Gate (Tier B / X)
The Phase 5 spectral energy auditor must compare solver $E(k)$ against the Johns Hopkins Turbulence Database (JHTDB) $1024^3$ Forced Isotropic HIT DNS reference:
1. **Spectral $L^2$ Accuracy**: Relative $L^2$ error on the inertial range $k \in [k_{\text{min}}, k_{\text{max}}]$:
   $$\frac{\|E_{\text{solver}}(k) - E_{\text{JHTDB}}(k)\|_{L^2}}{\|E_{\text{JHTDB}}(k)\|_{L^2}} < 2\%$$
2. **Kolmogorov Scaling Exponent**: Log-log linear regression of $E(k)$ vs $k$ on the inertial sub-range must yield slope $\beta \in [-1.8,\,-1.6]$ (Kolmogorov $-5/3$ law).
3. **No Synthetic Spectrum**: The reference $E_{\text{JHTDB}}(k)$ must be derived from either real JHTDB API data or a locally-generated statistically-consistent HIT snapshot — never a hardcoded array.
4. **Negative Control**: `NC-DS-09` — injecting a random-phase (white-noise) spectrum must fail the $L^2 < 2\%$ test deterministically.

---

### `H18` : Phase 5 Production SLA Gate (Tier B)
The production-grade deployment of the dual-scale solver must satisfy:
1. **Step Throughput**: End-to-end simulation throughput $\ge 1000$ time steps/s at grid resolution $N \ge 128^2$, measured over a continuous 10,000-step run with real `time.perf_counter_ns` timing.
2. **NaN/Overflow Safety**: Zero NaN or Inf values in velocity, pressure, or enstrophy fields across all 10,000 steps.
3. **Uptime Fraction**: Fraction of steps completing without exception $\ge 99.9\%$ (i.e., $\le 10$ failures in 10,000 steps).
4. **Negative Control**: `NC-DS-10` — deliberate NaN injection at step 5,000 must be detected within one step by the NaN guard and trigger a hard failure before step 5,001.

---

### `H19` : Phase 5 Cross-Scale Frustration Monotonicity Gate (Tier C → B)
For turbulent flow states with Taylor-scale Reynolds number $Re_{\lambda} > 100$, the Triadic Frustration Index $\mathcal{D}(M)$ must exhibit **non-increasing monotonicity** with Galerkin truncation order $M$:
$$\mathcal{D}(M_1) \ge \mathcal{D}(M_2) \quad \text{for all } M_1 < M_2, \quad Re_{\lambda} > 100$$
This promotes the Tier C conjecture (DS-C-0002) to a measured Tier B claim once verified across $M \in \{4, 8, 16, 24\}$.

**Physical Interpretation**: The frustration index $\mathcal{D}(M) = \sum_n |T_n| / |\sum_n T_n|$ measures triadic transfer *phase cancellation*. As $M$ grows, more shells participate in the cascade, increasing cancellation between triadic transfers, so $\mathcal{D}(M)$ decreases monotonically. This is the *convergence to the turbulent attractor* property.

**Empirical Note (Phase 5 Verification, 2026-08-31)**: Numerical measurements with $\nu=10^{-3}$, unit-normalized HIT initial conditions confirm $\mathcal{D}(4) \gg \mathcal{D}(8) > \mathcal{D}(16) \approx \mathcal{D}(24)$ for turbulent trajectories. The 10% tolerance accommodates statistical fluctuations at small shell counts.

**Lean 4 Obligation**: A proof skeleton `FrustrationMonotonicity.lean` must exist with a `sorry`-tagged stub formally stating the conjecture (tracking future Tier A promotion).

**Negative Control**: For laminar states ($Re_{\lambda} < 10$), $\mathcal{D}(M)$ is near-constant and does not necessarily satisfy H19 monotonicity — violation in this regime is acceptable and must not trigger H19 failure.

---

### `H20` : Phase 5 AI Preprocessing & Kolmogorov Resolution Gate (Tier B / X)
The AI Preprocessing module (`dualscale_solver.ai` / `crates/leanflow-ai`) must satisfy:
1. **Kolmogorov Dissipation Resolution**: Grid resolution recommended by the neuro-symbolic mesher must resolve the Kolmogorov microscale ($k_{\max} \eta \ge 1.5$, minimum threshold $\ge 1.0$) for all input velocity fields.
2. **Solenoidal Boundary Projection**: Projected velocity fields must satisfy $\max |\nabla \cdot u| < 10^{-12}$ via Fourier Leray projector $\mathcal{P}_{ij}(k) = \delta_{ij} - k_i k_j / |k|^2$.
3. **Automated Parameter Tuning**: Timestep recommendations must strictly satisfy CFL stability $\Delta t \le \text{CFL} \cdot \Delta x / u_{\max}$ with explicit stiffness ratio diagnostics $\sigma = \Delta t_{\text{adv}} / \Delta t_{\text{diff}}$.
4. **Zero-Token Exposure**: Model package exports to Hugging Face Hub must never leak API tokens into source code, artifacts, or certificates (`HF_TOKEN` isolation).

---

## 2. Epistemic Tier Calculus

```
┌──────────────────────────────────────────────────────────┐
│  Tier A: Lean 4 Kernel Verified                          │  Highest Rigor
│  (zero sorry, #print axioms [propext, choice, quot])     │
├──────────────────────────────────────────────────────────┤
│  Tier B: Exact Deterministic Rational Verifier           │
│  (Arithmetic over ℚ, negative controls mandatory)        │
├──────────────────────────────────────────────────────────┤
│  Tier L: Peer-Reviewed Literature Consensus              │
│  (Exact quoted theorem + verified citation)              │
├──────────────────────────────────────────────────────────┤
│  Tier C: Mathematical Conjecture / Physical Heuristic    │
│  (Plausible hypothesis, unproven, non-blocking)          │
├──────────────────────────────────────────────────────────┤
│  Tier X: Numerical Exploratory Simulation / AI Outputs   │  Lowest Rigor
│  (Floating point, GPU/TPU rollout, cannot gate claims)   │
└──────────────────────────────────────────────────────────┘
```

---

## 3. Mandatory Gate Verification Checklist (Enhanced — v3.0)

```bash
./scripts/verify.sh
```

| Gate | Scope | Criteria | Added |
|---|---|---|---|
| **Gate 0** | Lean 4 Kernel Build | `lake build` exits 0; zero `sorry` in all modules | v2.0 |
| **Gate 1** | Unit & Exact Invariant Tests | 100% pass rate: `pytest` + `cargo test --workspace` | v1.0 |
| **Gate 2** | Audit Certificate Generation | Deterministic `verification_cert.json`, schema-verified | v1.0 |
| **Gate 3** | Mathesis Ledger Soundness | Transitive tier monotonicity, zero inversions | v1.0 |
| **Gate 4** | Benchmark Integrity Audit | All perf fields have `_measured: true`; no `"synthetic"` provenance | v2.0 |
| **Gate 5** | JHTDB Spectral Fidelity (H17) | $L^2$ relative error $< 2\%$; Kolmogorov exponent $\in [-1.8, -1.6]$ | v3.0 |
| **Gate 6** | Production SLA & NaN Safety (H18) | $\ge 1000$ steps/s; uptime $\ge 99.9\%$; NaN guard fires on `NC-DS-10` | v3.0 |
| **Gate 7** | AI Preprocessing & Solenoidality (H20) | $k_{\max}\eta \ge 1.0$; $\max\|\nabla\cdot u\| < 10^{-12}$; CFL stable $\Delta t$ | v3.0 |

---

## 4. Lessons Learned Register

> Permanently maintained. New lessons appended after each phase audit.

| ID | Phase | Root Cause | Invariant Violated | Resolution |
|---|---|---|---|---|
| LL-01 | P1 Audit | Lean 4 modules not in `lakefile.lean`; never compiled | H1 | Register all `.lean` files; agent calls `lake build` |
| LL-02 | P1 Audit | QA checklist hardcoded to `True`; no live function calls | H2, H10 | Wire H2 to `negative_control_*()` calls; H10 enforced by subprocess |
| LL-03 | P1 Audit | Iteration counts `85` and `4` are constants, not measurements | H8, H11, H12 | Replace with `scipy.sparse.linalg.cg` callback counter |
| LL-04 | P1 Audit | Wall-time gain floored at `max(22.5, actual)` | H11, H12 | Remove floor; use median of 7 runs; report actual value |
| LL-05 | P1 Audit | Phase II used `DyadicShellSolver` for 3D TGV benchmark | H4 (non-vacuity) | Replace with `PseudoSpectralNavierStokes2D` |
| LL-06 | P1 Audit | D(M) computed as `12.5 + (m/8)*1.8`, a linear formula | H11 | Implement `sum(|T_n|) / |sum(T_n)|` from real trajectory |
| LL-07 | P1 Audit | Divergence figure used `np.random.rand()` noise | H11, H6 | Record actual per-step divergences via `callback` hook |
| LL-08 | P1 Audit | ETD-RK4 stage 3 missing `E_half` on `k2` | (numerical) | Fix to `u3 = E_half * curr_u + 0.5 * dt * E_half * k2` |
| LL-09 | P1 Audit | Leray projection at intermediate RK4 stages degrades order | H6 | Apply projection only at final combined step |
| LL-10 | P1 Audit | `sim_peak_t = 0.6` vs `ref_peak_t = 9.0` never flagged | H4, H10 | Add assertion with 25% relative tolerance in QA agent |
| LL-11 | P2 Protocol | Naive diagonal preconditioner ignores dyadic triad coupling | H14 | Implement Rulial Fourier-gate P1 operator matching shell dissipation |
| LL-12 | P3 Protocol | Un-regularized coarse AMG level causes near-zero pivot singular solve | H15 | Add diagonal epsilon floor on Galerkin coarse operator $A_c$ |
| LL-13 | P4 Protocol | Dynamic heap allocation causes non-deterministic interrupt latency | H16 | Enforce static array buffers with zero dynamic allocation |
| LL-14 | P5 Gap | JHTDB client attempted live HTTP without local fallback; fails in offline environments | H17 | Implement local HIT snapshot generator as deterministic fallback when `JHTDB_AUTH_TOKEN` absent |
| LL-15 | P5 Gap | Production SLA test skipped warmup; first 100 steps include JIT/cache-cold costs | H18 | Burn-in 500 steps before recording throughput; only measure steps 501–10,500 |
| LL-16 | P5 Gap | Frustration monotonicity failed for coarsely-initialized states with $M=4$; $\mathcal{D}(4) > \mathcal{D}(8)$ | H19 | Require minimum 50-step spinup with $\nu > 0$ before computing $\mathcal{D}(M)$ for H19 check |
| LL-17 | P5 AI Pre | Under-resolved grids in AI mesher caused aliased dissipation and blowup | H20 | Enforce strict Kolmogorov resolution inequality $k_{\max} \eta \ge 1.5$ before meshing |
| LL-18 | P5 HF Pub | Hugging Face credentials risked exposure in git tracking | H11, H13 | Isolate token loading to `HF_TOKEN` environment variable; zero credentials in git |


---

## Invariant Additions v3.1 (Audit 2026-08-31)

### H21 — Non-Vacuity of Lean 4 Proofs

Every Lean 4 theorem declared with Tier A status must be **non-trivially constructive**: its proof term must not reduce to `fun h => h` or a direct application of a hypothesis of identical type (a tautology). The `math_reviewer` agent must perform a syntactic non-vacuity check before signing off on any `.lean` file. Violation: a theorem whose proof is `exact h_same_type` or `hP v` where `hP : ∀ v, P(P v) = P v` and the conclusion is `P(P v) = P v`.

**Gate:** `lake build` succeeds AND at least one Mathlib lemma or local `have` derivation appears in every Tier A proof.

### H22 — Rust Test Coverage Gate

Every Rust crate in the workspace (`leanflow-core`, `leanflow-solver`, `leanflow-ai`) must expose ≥2 named unit tests, including at least one positive test and one negative control. `cargo test --workspace` must report zero crates with "0 tests".

**Gate:** `cargo test --workspace` output shows ≥2 test lines per crate.

### H23 — SLA Tests Must Run at Specified Grid Scale

Hardness gates referencing a minimum grid resolution (e.g., H18: N≥128²) must be exercised **at or above** that exact resolution in `verify.sh`. A gate test run at a smaller grid is a failing gate even if it passes. The grid size used must be logged in the gate output.

**Gate:** `verify.sh` Gate 5 must log `Grid: N=128 (H18 compliant)` or higher.

