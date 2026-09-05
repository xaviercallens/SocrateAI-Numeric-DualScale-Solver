# HARDNESS.md — Program-Wide Scientific Hardness & Epistemic Charter
**Version:** 5.0 — Phase 8/9 Productization & Fleet Autonomy (2026-08-31)
**Program:** SocrateAI Dual-Scale & LeanFlow Multiscale Navier–Stokes Program  
**Status:** MANDATORY & NON-NEGOTIABLE INVARIANTS  
**Scope:** All mathematical proofs, exact verifiers, numerical solvers, AI preconditioners, embedded kernels, **agent workflow outputs**, Phase 5 production / JHTDB validation pipelines, Phase 6 agentic runtime orchestration, **Phase 7 industrial multi-physics**, **Phase 8 enterprise productization & bare-metal HIL**, and **Phase 9 global fleet autonomy & sovereign airworthiness**.  
**Changelog v5.0:** Added H51 (Byzantine Fault-Tolerant Fleet Consensus Gate), H52 (Autonomous Piezo-Morphing Wing Closed-Loop Gate), H53 (Direct CNC CAM G-Code Synthesis Gate), H54 (Sovereign FAA/EASA DO-178C Level A Airworthiness Gate), H55 (Hyperscale Multi-Cloud Kubernetes Auto-Scaling SLO Gate). Extended Phase 9 Agent Hardness Contracts. Added LL-33–LL-36.  
**Changelog v4.0:** Added H26 (Agent Persona Integrity Gate), H27 (SDK Availability Hard Prerequisite). Tightened H24 with `negative_control_nc_ds11()` mandatory implementation. Added LL-19–LL-20.  
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

### `H5` : Wavenumber-Dependent Scale Thresholding / Dual-Scale Regularization (No Artificial Cutoffs)
Singularity prevention and scale regularization must never rely on ad-hoc empirical cutoffs or artificial smoothing, but strictly on exact **dual-scale wavenumber thresholding / T-duality mapping**:

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
| **Gate 8** | Agentic Runtime Intercept (H24) | Monitor intercepts `NC-DS-11` stiffness spike; stabilizes enstrophy within 50 steps | v4.0 |
| **Gate 9** | Continuous HF CI (H25) | CI automation strictly conditioned on Gates 0-8 passing; isolated `HF_TOKEN` | v4.0 |

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
| LL-19 | P6 Audit | Phase 6 orchestrator issued `CERTIFIED` when SDK absent and all agents `SIMULATED` | H10, H11, H26, H27 | Add `FORBIDDEN_STATUSES` check; introduce `SCAFFOLDING_ONLY` status; block `CERTIFIED` |
| LL-20 | P6 Audit | SHA-256 hash computed over `b"phase6"` constant — identical across all runs | H10, H13 | Hash over real pipeline results dict (`json.dumps(payload, sort_keys=True)`) |


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

---

## Phase 6 Agentic Invariant Additions v4.0

### `H24` : Phase 6 Agentic Runtime Intercept Gate (Tier B)
The Phase 6 `agentic_runtime_monitor` must autonomously steer failing numerical states to stability:
1. **Dynamic Parameter Intervention**: If the solver's local stiffness $\sigma > 100$ or enstrophy rate of change exceeds threshold, the agent must issue a parameter update (e.g., scheme $\rightarrow$ BDF, $\Delta t \rightarrow \Delta t/2$) within 1 timestep.
2. **Negative Control**: `NC-DS-11` — deliberate injection of a stiffness spike via abrupt physical viscosity drop (100× drop in ν). The `negative_control_nc_ds11()` function in `production_sla_monitor.py` must pass (σ detected > 100; stabilized within 50 steps; no NaN triggered). The gate is **wired to real measured code**, not prose assertion.
3. **Stiffness Formula**: σ = (u_max · Δx) / ν — the diffusive Péclet-like indicator. When ν drops by 100×, σ rises by 100×.

### `H25` : Phase 6 Continuous HuggingFace CI Gate (Tier T0)
1. **Automated Publishing**: The HF model card and benchmark update must trigger autonomously on `main` branch pushes.
2. **Strict Conditioning**: The HF API call is only permitted if Gates 0 through 8 successfully pass in the CI environment.
3. **Zero Token Leakage**: The push must use the `HF_TOKEN` environment variable and explicitly reject any configuration storing the token in source tracking.

### `H26` : Agent Persona Integrity Gate (Phase 6 — NEW)
All agent tool outputs for Phase 6 must be **structured JSON** matching the workflow schema defined in `antigravity-agent-personas/SKILL.md`.
1. **No Prose Commands**: An agent response that is pure text without a `status`, `_measured`, and relevant structured fields must be **rejected** by the orchestrator before reaching the hardness auditor.
2. **Forbidden Status Values**: The orchestrator must treat `{"SIMULATED", "MOCKED_NO_SDK", "SCAFFOLDING_ONLY", "SDK_ERROR"}` as gate failures, not as valid measurements.
3. **Enforcement**: The hardness auditor's H13 inspection block must programmatically check all four agent status fields before issuing any certificate.

### `H27` : SDK Availability is a Hard Prerequisite (Phase 6 — NEW)
The Phase 6 hardness certificate (`CERT-P6-WF-*`) **must not carry `overall_status: CERTIFIED`** if any agent's status is `SCAFFOLDING_ONLY`, `SIMULATED`, or `SDK_ERROR`.
1. **Fallback Behavior**: A pipeline running without `google-antigravity` installed must yield `overall_status: SCAFFOLDING_ONLY`. This is a valid scaffolding artifact, not a scientific certificate.
2. **SHA-256 Integrity**: The certificate hash must be computed over the actual pipeline results JSON dict (serialized deterministically), never over a constant byte string like `b"phase6"`.
3. **Installation Requirement**: `google-antigravity` must appear in `requirements.txt` (TSK-66) so that CI environments can achieve `CERTIFIED` status.

---

## Phase 6b & 6c Industrial PoC Invariants (H28–H34)

### `H28` : Backend Liveness Pre-flight Gate
Automated detection of live LLM backends (Gemini API, Mistral API, Ollama) before initiating multi-turn chat interactions.

### `H29` : Bioreactor Mass Transfer Gate
Measured volumetric mass transfer coefficient $k_L a \ge 100.0\,\text{s}^{-1}$ and dissolved oxygen yield multiplier $\ge 2.5\times$ (target $> 3.0\times$). Negative control: `NC-IND-01`.

### `H30` : Transonic Buffet Suppression Gate
Dynamic enstrophy damping over supercritical airfoils achieving shock oscillation variance reduction $\ge 35\%$ (target $> 40\%$). Negative control: `NC-IND-02`.

### `H31` : Embedded Edge Budget Gate
Static memory footprint $\le 64\,\text{KB}$ RAM and deterministic per-step latency $\le 1.0\,\text{ms}$. Negative control: `NC-IND-03`.

### `H32` : Industrial Multi-Backend Parity
Multi-agent workflow parity across verified LLM backends. Negative control: `NC-IND-04`.

### `H33` : Secure Vault & Telemetry Parity
Strict credential isolation and remote telemetry streaming. Negative control: `NC-IND-05`.

### `H34` : Distributed JHTDB Scaling Gate
Pipeline turbulent drag reduction $\ge 10\%$ scaling across distributed multi-node arrays ($nodes \ge 2$). Negative control: `NC-IND-06`.

---

## Phase 7 Federated Autonomous Industrial Invariants (H35–H40)

### `H35` : Multi-Physics FSI Aeroelastic Flutter Suppression Gate (Tier B)
Coupled 2-DOF aeroelastic pitch-plunge wing section with transonic shock-boundary layer interaction. LeanFlow dual-scale enstrophy damping must achieve:
- **Measured Variance Reduction**: $\ge 45\%$ reduction in flutter energy variance $(h^2 + \alpha^2)$.
- **Epistemic Negative Control**: `NC-P7-01` — falsified divergent flutter or variance reduction $< 45\%$ is deterministically rejected.

### `H36` : Biopharmaceutical Coupled Metabolic Kinetics Gate (Tier B)
Coupled non-linear reaction-diffusion system integrating oxygen transfer, substrate consumption, and biomass growth:
- **Oxygen Transfer Rate**: $k_L a \ge 115.0\,\text{s}^{-1}$.
- **Biomass Yield Multiplier**: $\ge 3.0\times$ vs standard laminar sparging.
- **Epistemic Negative Control**: `NC-P7-02` — sub-threshold $k_L a < 115.0\,\text{s}^{-1}$ or yield $< 3.0\times$ is deterministically rejected.

### `H37` : Generative Inverse Design Frustration Reduction Gate (Tier B)
AI-driven inverse geometry optimization loop over aerodynamic/impeller camber topologies:
- **Frustration Reduction**: $\ge 20\%$ reduction in Triadic Frustration Index $\mathcal{D}(M)$.
- **Drag Coefficient Reduction**: $\ge 8.0\%$ reduction in $C_d$ in $\le 10$ optimization iterations.
- **Epistemic Negative Control**: `NC-P7-03` — stagnant or increasing $\mathcal{D}(M)$ is deterministically rejected.

### `H38` : Hierarchical Edge-to-Cloud Swarm Synchronization Gate (Tier B)
Split-scale execution across cloud macroscopic continuous solvers ($N=256^2$) and edge microcontroller swarms (16 ARM Cortex-M4 nodes):
- **Deterministic Edge Latency**: Single-step execution time $\le 1.0\,\text{ms}$ on ARM Cortex-M4.
- **Swarm Scaling Efficiency**: $\ge 85\%$ parallel aggregation scaling efficiency.
- **Epistemic Negative Control**: `NC-P7-04` — edge latency $> 1.0\,\text{ms}$ or scaling $< 85\%$ is deterministically rejected.

### `H39` : Holographic Scale Regularization & Attractor Boundedness Gate (Tier A / B)
The Holographic dual-scale operator $R_{\text{eff}}(R) = R + \alpha'/R$ and enstrophy attractor $Z^*$:
- **Universal Lower Bound**: $R_{\text{eff}}(R) \ge 2\sqrt{\alpha'}$ verified for all $R > 0$.
- **Enstrophy Boundedness**: Peak enstrophy bounded by $Z^* = (1 - \nu\alpha') / (\nu \alpha'^2)$.
- **Epistemic Negative Control**: `NC-P7-05` — $R_{\text{eff}} < 2\sqrt{\alpha'}$ or enstrophy blowup is deterministically rejected.

### `H40` : Automated Regulatory Compliance Audit Trail Gate (Tier T0 / B)
Automated generation of FDA 21 CFR Part 11 and EASA/FAA DO-178C Level A verification packages:
- **Cryptographic Traceability**: 64-character SHA-256 hash linking Lean 4 zero-sorry modules (`Galerkin.lean`, `Leray.lean`, `Frustration.lean`), test results, and timestamped certificates.
- **Epistemic Negative Control**: `NC-P7-06` — incomplete proof matrices (`sorry > 0`) or broken hashes are deterministically rejected.


## Phase 7 Production Roadmap Invariants (H41–H44)

### `H41` : ARM Cortex-M4 HIL Cycle-Budget Gate (Tier B)
Static cycle-accurate timing analysis of the LeanFlow N=4×4 Leray projection micro-kernel on ARM Cortex-M4 @ 168 MHz:
- **Latency Bound**: Single-step execution time $\le 1.0\,\text{ms}$ (Cortex-M4 instruction-cycle table, DDIO r0p1).
- **Cycle Scope**: Includes FPU VMUL/VADD, LDR/STR, branch overhead for a 4×4 grid micro-kernel.
- **Epistemic Negative Control**: `NC-P7-07` — falsified over-budget cycle count (latency $> 1.0\,\text{ms}$ at 168 MHz) is deterministically rejected.

### `H42` : CAD / STEP AP203 Topology Export Gate (Tier B)
After generative inverse design (H37), the frustration-minimized airfoil/blade camber profile must be exportable to a valid STEP AP203 (ISO 10303-21) file:
- **Valid STEP Structure**: `ISO-10303-21` header, `END-ISO-10303-21;` footer, $\ge 5$ entities.
- **B-Spline Encoding**: Camber-line encoded as `B_SPLINE_CURVE_WITH_KNOTS` with `CARTESIAN_POINT` control points.
- **SHA-256 Traceability**: 64-character hash linking the STEP file to the generating optimization run.
- **Epistemic Negative Control**: `NC-P7-08` — malformed STEP file (missing footer or B-spline entity) is deterministically rejected.

### `H43` : Live Multi-Cloud Telemetry Stream Integrity Gate (Tier B)
The `EdgeCloudSwarmAgent` telemetry stream must satisfy:
- **Schema Completeness**: All events carry `event_id`, `timestamp_ns`, `source_node`, `metric_name`, `metric_value`, `unit`, `sequence_number`.
- **Monotonic Ordering**: `timestamp_ns` strictly monotonically increasing across the stream.
- **Zero Event Loss**: `events_emitted == events_attempted` (no dropped events).
- **Rolling SHA-256 Integrity Hash**: End-to-end stream hash computed and verified.
- **Epistemic Negative Control**: `NC-P7-09` — out-of-order timestamps or missing schema fields are deterministically rejected.

### `H44` : 3D Volume Mesh FSI Co-Simulation Coupling Gate (Tier B)
Structured hexahedral $16^3$ mesh fluid-structure interaction co-simulation:
- **Interface Velocity Continuity**: No-slip boundary condition enforced at fluid-solid interface.
- **H44b Sub-Invariant**: `pre_enforcement_velocity_mismatch > 1e-8` (coupling is physically non-trivial).
- **Enstrophy Transfer**: Dimensionless coupling coefficient $|\eta| = |\Delta\Omega / M_b| \ge 1e-6$ (active coupling verified, sign-agnostic).
- **FSI Coupling Loss**: $< 5\%$ structural kinetic energy loss per step cycle.
- **Epistemic Negative Control**: `NC-P7-10` — interface velocity discontinuity $> 0.1$ without no-slip enforcement is deterministically rejected.

---

## Phase 8 Productization & Industrialization Invariants (H45–H50)

### `H45` : Real Silicon QEMU / Physical HIL Benchmark Gate (Tier B / Physical)
Automated bare-metal execution of `leanflow-embedded` on QEMU ARM Cortex-M4 and SpacemiT K1 RISC-V targets:
- **Latency Bound**: Single-step execution time $\le 1.0\,\text{ms}$ at target frequency.
- **Memory Footprint**: Static stack/BSS RAM $\le 64\,\text{KB}$; zero dynamic heap allocations (`malloc_calls == 0`).
- **Epistemic Negative Control**: `NC-P8-01` — execution latency $> 1.0\,\text{ms}$ or heap allocation detected is deterministically rejected.

### `H46` : Multi-CAD OpenCASCADE B-Rep Solid Topology Gate (Tier B)
Conversion of frustration-minimized 2D camber geometries into watertight 3D B-Rep solids (STEP AP214 / IGES 5.3 / STL):
- **Watertight Solid**: Valid Euler-Poincaré topological characteristic $V - E + F = 2(1 - g)$.
- **Manufacturing Readiness**: Zero self-intersecting faces; continuous surface curvature for 5-axis CNC milling toolpath export.
- **SHA-256 Integrity**: 64-character hash linking CAD artifact directly to the generative optimization ledger.
- **Epistemic Negative Control**: `NC-P8-02` — non-manifold edge or negative volume is deterministically rejected.

### `H47` : Production Cloud-Native gRPC & BigQuery Stream Ingestion Gate (Tier B / Infrastructure)
High-throughput asynchronous streaming of simulation metrics to Google Cloud BigQuery and Grafana Cloud:
- **Throughput & Latency**: Ingestion throughput $\ge 10,000\,\text{events/s}$ with end-to-end delivery latency $< 50\,\text{ms}$.
- **Zero Loss & Monotonicity**: Zero dropped events (`loss_rate == 0.0`); strictly monotonic `timestamp_ns` and contiguous `sequence_number`.
- **Rolling SHA-256 Digest**: Block-level stream integrity digest verified against BigQuery audit table.
- **Epistemic Negative Control**: `NC-P8-03` — dropped events $> 0$ or schema mismatch is deterministically rejected.

### `H48` : High-Order 3D FSI Bi-Directional Stress-Strain Tensor Coupling Gate (Tier B / MultiPhysics)
Fully coupled 3D Navier-Stokes and non-linear Saint-Venant Kirchhoff elasticity tensor on $32^3$ hexahedral mesh:
- **Interface Traction Balance**: Fluid normal stress matches structural boundary stress $\|\sigma_f \cdot n - \sigma_s \cdot n\|_2 / \|\sigma_f \cdot n\|_2 < 10^{-4}$.
- **Kinematic Continuity**: $\|u_f - \dot{d}_s\|_\infty < 10^{-6}$ post-projection.
- **Coupling Loss**: Energy conservation error $< 2.0\%$ over 100 complete aeroelastic cycles.
- **Epistemic Negative Control**: `NC-P8-04` — uncoupled stress jump $> 10^{-3}$ or energy divergence is deterministically rejected.

### `H49` : Commercial Enterprise Packaging & Zero-Dependency C-ABI Gate (Tier T0 / B)
Universal distribution packages for frictionless industrial deployment:
- **Universal Python Wheel**: `pip install leanflow` binary wheel with pre-compiled SIMD AVX-512 / NEON extensions for Linux (x86_64, aarch64) and macOS (Apple Silicon).
- **C-ABI Shared Library**: `libleanflow.so` / `libleanflow.dylib` / `leanflow.dll` with ANSI C99 / C++17 header `leanflow.h`.
- **Docker Appliance**: Production OCI container image (`leanflow:latest`) with compressed footprint $< 150\,\text{MB}$.
- **Epistemic Negative Control**: `NC-P8-05` — missing C-ABI symbol or container image size $> 250\,\text{MB}$ is deterministically rejected.

### `H50` : Cryptographic License Protection & Tamper-Proof Audit Lock (Tier T0 / Security)
Dual-licensing enforcement with tamper-proof epistemic audit locking:
- **Ed25519 License Verification**: Cryptographically signed license token unlocking Enterprise features (HPC acceleration, custom FSI hooks).
- **Immutable Ledger Seal**: Audit certificates (Tier A/B/L/C/X) sealed with Ed25519 signature and SHA-256 merkle roots preventing downgrade or tampering.
- **Epistemic Negative Control**: `NC-P8-06` — expired, unsigned, or tampered license token is deterministically rejected.

---

## Phase 9 Global Fleet Autonomy & Sovereign Airworthiness Invariants (H51–H55)

### `H51` : Byzantine Fault-Tolerant Fleet Consensus Gate (Tier B / Distributed)
Global synchronization of ≥1,000 physical edge nodes (aircraft flight computers, turbomachinery PLCs) using a Byzantine Fault-Tolerant (BFT) consensus protocol:
- **Consensus Latency**: End-to-end global consensus latency $\le 50\,\text{ms}$ across geographically distributed nodes.
- **Fault Tolerance**: System remains operational with up to $f = \lfloor (N-1)/3 \rfloor$ Byzantine (arbitrarily failing) nodes at any time.
- **Enstrophy-Coherent State**: All live nodes must converge on the same enstrophy attractor $Z^*$ reading within $\pm 1\%$ relative tolerance.
- **Cryptographic Ordering**: Every consensus round sealed with Ed25519-signed vector clock preventing replay attacks.
- **Epistemic Negative Control**: `NC-P9-01` — consensus with $> f$ faulty nodes, latency $> 50\,\text{ms}$, or unsigned round is deterministically rejected.

### `H52` : Autonomous Piezo-Morphing Wing Closed-Loop Control Gate (Tier B / Physical)
Real-time closed-loop active aeroelastic control of piezo-morphing camber surfaces mitigating buffet oscillations at Mach 0.88:
- **Flutter Suppression**: Measured peak wing-root bending moment variance reduced $\ge 60\%$ within 3 oscillation cycles under real atmospheric gust turbulence.
- **Actuation Latency**: End-to-end sensor → solver → actuator latency $\le 2\,\text{ms}$ at 168 MHz.
- **Stability Margin**: Minimum flutter speed margin $V_F \ge 1.2 \times V_{\text{design}}$ under all certified gust load cases.
- **Epistemic Negative Control**: `NC-P9-02` — open-loop baseline (no actuation) or actuation latency $> 5\,\text{ms}$ fails to suppress flutter by $\ge 60\%$ and is deterministically rejected.

### `H53` : Direct 5-Axis CNC CAM G-Code Synthesis Gate (Tier T1 / Manufacturing)
One-click conversion of dual-scale frustration-minimized flow solutions directly into certified 5-axis CNC machining G-code:
- **Surface Finish**: Computed Ra roughness $\le 0.8\,\mu\text{m}$ (ISO 1302 N6) guaranteed by toolpath cusp height analysis.
- **Machining Time**: G-code estimated cycle time within $\pm 5\%$ of operator-targeted cycle time for the given spindle speed and feed rate.
- **CAM Traceability**: G-code SHA-256 hash linked to the generating STEP AP214 entity and dual-scale optimization run in the audit ledger.
- **ISO-Compliance**: G-code conforms to RS-274D (ISO 6983-1) and passes a dry-run syntax validation against a reference CNC post-processor.
- **Epistemic Negative Control**: `NC-P9-03` — G-code with Ra $> 1.6\,\mu\text{m}$, cycle time deviation $> 10\%$, or broken SHA-256 link is deterministically rejected.

### `H54` : Sovereign FAA/EASA DO-178C Level A Airworthiness Certification Gate (Tier A / Regulatory)
End-to-end formal mathematical certification of flight-control software under FAA AC 20-115D / EASA AMC 20-115D:
- **Zero-Sorry Lean 4 Proof Coverage**: 100% of safety-critical control laws machine-checked in Lean 4 with zero `sorry` and output only `[propext, Classical.choice, Quot.sound]`.
- **MC/DC Coverage**: Modified Condition/Decision Coverage (MC/DC) ≥ 100% over all structural and boundary-condition branches.
- **Traceability Matrix**: Every requirement in the PSAC (Plan for Software Aspects of Certification) linked to at least one Lean 4 theorem and one test case.
- **DER Review**: Formal DER (Designated Engineering Representative) review record sealing the certification artifact with a timestamped Ed25519 signature.
- **Epistemic Negative Control**: `NC-P9-04` — any `sorry` in a safety-critical module, MC/DC gap, or broken traceability link is deterministically rejected and blocks certification.

### `H55` : Hyperscale Multi-Cloud Kubernetes SaaS Auto-Scaling SLO Gate (Tier T0 / Infrastructure)
Cloud-native auto-scaling of the LeanFlow SaaS tier serving global fleet digital twin workloads:
- **Scale-Out SLO**: Kubernetes HPA scales from 1 to 100 replica pods within $\le 90\,\text{s}$ under a step 100× load increase.
- **P99 Request Latency**: API gateway P99 latency $\le 200\,\text{ms}$ at steady-state with $\ge 10,000$ concurrent simulation RPC streams.
- **Cost Efficiency**: Spot/preemptible node fraction $\ge 60\%$ of total fleet, keeping cost-per-simulation-hour below the contracted SLA unit price.
- **Zero-Downtime Rollout**: Rolling updates with `maxUnavailable=0` and `maxSurge=1` must complete with zero failed health-check probes recorded.
- **Epistemic Negative Control**: `NC-P9-05` — scale-out exceeding 90 s, P99 latency $> 500\,\text{ms}$, or any failed rolling-update health probe is deterministically rejected.

### `H56` : Autonomous Low-Tier Edge Execution (Tier T0/T1 / Execution)
Autonomous execution of the workflow must be capable of running 100% offline via local Low-Tier SLMs (e.g. Ollama, Gemma 2, Mistral, Qwen Coder) without any reliance on frontier cloud models.
- **Zero Cloud API Cost / Telemetry**: No payload containing simulation metrics, CAD geometries, or confidential intellectual property leaves the edge node.
- **Constrained Decoding**: Output generated by local SLMs must strictly conform to JSON schemas with guaranteed rejection of `HALLUCINATED`, `SIMULATED`, or prose-only output.
- **Deterministic Check**: The orchestrator pipeline detects a valid local edge model configuration and completes the gating cycle autonomously without HTTP calls outside `localhost`.
- **Epistemic Negative Control**: `NC-P8-07` — any attempt to route an execution step to a missing cloud model or unverified backend API results in an immediate `SCAFFOLDING_ONLY` downgrade.

---

## Phase 9 Agent Hardness Contracts (Extended)

The following output contracts extend the AGENTS.md v3.0 table for Phase 9 agents:

| Agent | Must Return (key fields) | Forbidden Outputs |
|-------|--------------------------|-------------------|
| `fleet_consensus_agent` | `{"status": "CONVERGED\|REJECTED", "node_count": N, "consensus_latency_ms": N, "faulty_nodes_tolerated": N, "enstrophy_coherence_pct": N, "_measured": true}` | Simulated consensus without real network calls; missing `faulty_nodes_tolerated` |
| `morphing_wing_controller` | `{"status": "STABILIZED\|FAILED", "flutter_variance_reduction_pct": N, "actuation_latency_ms": N, "stability_margin_ratio": N, "_measured": true}` | Open-loop baseline reported as closed-loop; missing `actuation_latency_ms` |
| `cam_synthesis_agent` | `{"status": "EXPORTED\|REJECTED", "gcode_path": "...", "ra_roughness_um": N, "cycle_time_s": N, "sha256_hash": "...", "_measured": true}` | G-code without toolpath cusp height analysis; missing `sha256_hash` |
| `airworthiness_certifier` | `{"status": "CERTIFIED\|REJECTED", "sorry_count": 0, "mcdc_coverage_pct": 100.0, "traceability_gaps": 0, "der_signature": "...", "_measured": true}` | Any `sorry_count > 0`; missing `traceability_gaps` field |
| `saas_autoscale_agent` | `{"status": "SLO_MET\|VIOLATED", "scale_out_s": N, "p99_latency_ms": N, "spot_fraction_pct": N, "rollout_failures": 0, "_measured": true}` | Synthetically estimated latency; missing `rollout_failures` field |

### Phase 9 Escalation Triggers (additions to AGENTS.md §Escalation Triggers)

1. Fleet consensus fails with $\le f$ faulty nodes (Byzantine tolerance violated).
2. Closed-loop flutter suppression fails to reach 60% variance reduction within 3 cycles.
3. G-code SHA-256 traceability link is broken at any point in the CAM synthesis chain.
4. A `sorry` is detected in any safety-critical Lean 4 module under DO-178C Level A review.
5. SaaS auto-scaling P99 latency exceeds 500 ms during a certified load test.

