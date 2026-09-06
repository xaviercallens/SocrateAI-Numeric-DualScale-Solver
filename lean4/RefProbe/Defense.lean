import Mathlib
open Matrix CongruenceSubgroup ConjAct Pointwise
open scoped MatrixGroups

-- (A) NOV-04: the Mathlib declarations the referee names, resolved by the elaborator.
#check @ModularForm.translate
#check @CuspForm.translate
#check @SlashInvariantForm.translate
#check @CongruenceSubgroup.conjGL
#check @IsCongruenceSubgroup.conjGL
#check @Subgroup.IsArithmetic.conj
#check @ModularGroup.S
#check @ModularGroup.coe_S
#check @ModularGroup.S_inv
#check @Subgroup.mem_normalizer_iff

-- (B) NOV-05 DEFENCE: a one-sided conjugation inclusion is EQUIVALENT to normalizer
-- membership as soon as g^2 is central -- which is exactly `frickeW_sq_coe` (W^2 = -N.I).
theorem mem_normalizer_of_sq_central {G : Type*} [Group G] {H : Subgroup G} {g : G}
    (hz : ∀ x : G, (g * g) * x = x * (g * g))
    (h1 : ∀ h ∈ H, g * h * g⁻¹ ∈ H) : g ∈ H.normalizer := by
  rw [Subgroup.mem_normalizer_iff]
  intro h
  constructor
  · exact fun hh => h1 h hh
  · intro hh
    have h2 := h1 _ hh
    have e : g * (g * h * g⁻¹) * g⁻¹ = h := by
      have := hz h
      group
      calc g * (g * h * g⁻¹) * g⁻¹ = (g*g) * h * (g*g)⁻¹ := by group
        _ = h * (g*g) * (g*g)⁻¹ := by rw [this]
        _ = h := by group
    rwa [e] at h2

-- (C) NOV-05 / NOV-04 DEFENCE: normalizer membership immediately gives the subgroup
-- EQUALITY that `ModularForm.translate` wants.
theorem conjAct_smul_eq_of_mem_normalizer {G : Type*} [Group G] {H : Subgroup G} {g : G}
    (hg : g ∈ H.normalizer) : toConjAct g⁻¹ • H = H := by
  ext x
  rw [Subgroup.mem_pointwise_smul_iff_inv_smul_mem, ← toConjAct_inv, inv_inv,
    toConjAct_smul]
  exact ((Subgroup.mem_normalizer_iff.mp hg) x).symm

-- (D) NOV-04: the referee's `opFromEquality`.
noncomputable def opFromEquality {Γ : Subgroup (GL (Fin 2) ℝ)} {k : ℤ} (g : GL (Fin 2) ℝ)
    (h : toConjAct g⁻¹ • Γ = Γ) : ModularForm Γ k → ModularForm Γ k :=
  fun f => h ▸ ModularForm.translate f g

-- (E) NOV-09: `Gamma0GL N` is *literally* Mathlib's coercion, not a re-implementation.
example (N : ℕ) :
    ((Gamma0 N : Subgroup SL(2, ℤ)) : Subgroup (GL (Fin 2) ℝ))
      = (Gamma0 N).map (Matrix.SpecialLinearGroup.mapGL ℝ) := rfl

-- (F) NOV-06: N = 1.
example : ((ModularGroup.S : SL(2,ℤ)) : Matrix (Fin 2) (Fin 2) ℤ) = !![0, -1; 1, 0] :=
  ModularGroup.coe_S
example : Gamma0 1 = ⊤ := by
  ext g; simp [Gamma0_mem, Subsingleton.elim ((g.1 1 0 : ℤ) : ZMod 1) 0]
