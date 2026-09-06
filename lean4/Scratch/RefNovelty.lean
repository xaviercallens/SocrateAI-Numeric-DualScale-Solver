import Mathlib.NumberTheory.ModularForms.Basic
import Mathlib.NumberTheory.ModularForms.SlashActions
import Mathlib.NumberTheory.ModularForms.CongruenceSubgroups

open Matrix CongruenceSubgroup ConjAct
open scoped MatrixGroups Pointwise

-- P1: analytic transport along an arbitrary GL(2,R) element already in Mathlib
#check @ModularForm.translate
#check @SlashInvariantForm.translate
#check @CuspForm.translate

-- P2: general conjugation theory for congruence subgroups already in Mathlib
#check @CongruenceSubgroup.conjGL
#check @CongruenceSubgroup.IsCongruenceSubgroup.conjGL
#check @Subgroup.IsArithmetic.conj

-- P3: N = 1 Fricke matrix already in Mathlib
#check @ModularGroup.S
#check @ModularGroup.coe_S
#check @ModularGroup.S_inv
example : ((ModularGroup.S : SL(2,ℤ)) : Matrix (Fin 2) (Fin 2) ℤ) = !![0, -1; 1, 0] :=
  ModularGroup.coe_S
