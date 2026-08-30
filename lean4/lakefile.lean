import Lake
open Lake DSL

package «dualscale_solver» where
  -- Package configuration options

require mathlib from git
  "https://github.com/leanprover-community/mathlib4.git"

@[default_target]
lean_lib «DualScale» where
  -- Library configuration options
