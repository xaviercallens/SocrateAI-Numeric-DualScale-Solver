import Mathlib
open Matrix
open scoped MatrixGroups

-- The hypothesis of `mem_normalizer_of_sq_central`, discharged from exactly the artifact's
-- `frickeW_sq_coe : ((W * W : GL (Fin 2) ℝ) : Matrix _ _ ℝ) = (-(N:ℝ)) • 1`.
theorem sq_central_of_coe_smul_one {n : Type*} [Fintype n] [DecidableEq n] {u : GL n ℝ} {c : ℝ}
    (h : ((u * u : GL n ℝ) : Matrix n n ℝ) = c • (1 : Matrix n n ℝ)) :
    ∀ x : GL n ℝ, (u * u) * x = x * (u * u) := by
  intro x
  apply Units.ext
  show ((u * u : GL n ℝ) : Matrix n n ℝ) * (x : Matrix n n ℝ)
      = (x : Matrix n n ℝ) * ((u * u : GL n ℝ) : Matrix n n ℝ)
  rw [h, Matrix.smul_mul, Matrix.mul_smul, Matrix.one_mul, Matrix.mul_one]
