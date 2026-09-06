import Mathlib.NumberTheory.ModularForms.Basic
open Matrix ConjAct
open scoped MatrixGroups Pointwise

-- Claim: given ONLY the subgroup equality, Mathlib's `ModularForm.translate` already
-- delivers the bundled operator, holomorphy + cusp-boundedness included.
noncomputable def opFromEquality {Γ : Subgroup (GL (Fin 2) ℝ)} {k : ℤ} (g : GL (Fin 2) ℝ)
    (h : toConjAct g⁻¹ • Γ = Γ) : ModularForm Γ k → ModularForm Γ k :=
  fun f => h ▸ ModularForm.translate f g

-- And a one-sided inclusion `toConjAct g⁻¹ • Γ ≤ Γ` is NOT the same as normalising:
-- Mathlib's own normaliser membership is an iff on both sides.
#check @Subgroup.mem_normalizer_iff
#check @Subgroup.mem_normalizer_iff'
