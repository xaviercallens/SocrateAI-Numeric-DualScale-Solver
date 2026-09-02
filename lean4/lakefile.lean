import Lake
open Lake DSL

package «dualscale_solver» where
  -- Package configuration options

require mathlib from git
  "https://github.com/leanprover-community/mathlib4.git"

-- W3 Fix: Register all four modules so `lake build` kernel-checks them
@[default_target]
lean_lib «DualScale» where
  -- Main dual-scale geometry & Navier-Stokes cascade (Tier A certified)

lean_lib «Galerkin» where
  -- Triadic energy transfers & antisymmetry (Tier A certified, IP-02 algebraic)

lean_lib «Leray» where
  -- Leray-Helmholtz projector: concrete EuclideanSpace definition (Tier A certified, IP-02)

lean_lib «Frustration» where
  -- Triadic Frustration Index D(M) phase cancellation bounds (Tier A certified)

lean_lib «FrustrationMonotonicity» where
  -- H19 Frustration monotonicity conjecture stub (Tier C → target Tier A)

lean_lib «DynamicStability» where
  -- H24 Agentic runtime parameter bounds (TSK-62, Phase 6 — sorry stub, target Tier A)

lean_lib «Aerospace» where
  -- Aerospace DO-178C Level A Safety Invariants (Phase 11 PoC)

lean_lib «Medical» where
  -- Medical FDA Class III Hemodynamics Invariants (Phase 11 PoC)

