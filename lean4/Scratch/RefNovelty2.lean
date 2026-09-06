import Mathlib.NumberTheory.ModularForms.Basic
import Mathlib.NumberTheory.ModularForms.SlashActions
import Mathlib.NumberTheory.ModularForms.CongruenceSubgroups

open Matrix CongruenceSubgroup ConjAct
open scoped MatrixGroups Pointwise

namespace RefProbe

def W (N : ℕ) : Matrix (Fin 2) (Fin 2) ℝ := !![0, -1; (N : ℝ), 0]

-- (C1) determinant: is it a one-liner from existing Mathlib simp lemmas?
example (N : ℕ) : (W N).det = (N : ℝ) := by simp [W]

-- (C2) square: one-liner?
example (N : ℕ) : W N * W N = (-(N:ℝ)) • (1 : Matrix (Fin 2) (Fin 2) ℝ) := by
  ext i j; fin_cases i <;> fin_cases j <;>
    simp [W, Matrix.mul_apply, Fin.sum_univ_two]

-- (C4) restated: does Mathlib close the normalisation statement on its own?
noncomputable def WG {N : ℕ} (hN : 0 < N) : GL (Fin 2) ℝ :=
  Matrix.GeneralLinearGroup.mkOfDetNeZero (W N)
    (by simp [W]; exact_mod_cast hN.ne')

example {N : ℕ} (hN : 0 < N) :
    ∀ g ∈ (Gamma0 N).map (Matrix.SpecialLinearGroup.mapGL ℝ),
      WG hN * g * (WG hN)⁻¹ ∈ (Gamma0 N).map (Matrix.SpecialLinearGroup.mapGL ℝ) := by
  exact?

end RefProbe
