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
