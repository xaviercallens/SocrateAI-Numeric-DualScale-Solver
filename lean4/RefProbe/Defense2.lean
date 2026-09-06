import Mathlib
open Matrix CongruenceSubgroup ConjAct Pointwise
open scoped MatrixGroups

-- NOV-05 DEFENCE: one-sided conjugation inclusion + centrality of g^2 => normalizer membership.
theorem mem_normalizer_of_sq_central {G : Type*} [Group G] {H : Subgroup G} {g : G}
    (hz : ∀ x : G, (g * g) * x = x * (g * g))
    (h1 : ∀ h ∈ H, g * h * g⁻¹ ∈ H) : g ∈ Subgroup.normalizer (H : Set G) := by
  rw [Subgroup.mem_normalizer_iff]
  intro h
  refine ⟨fun hh => h1 h hh, fun hh => ?_⟩
  have h2 := h1 _ hh
  have e : g * (g * h * g⁻¹) * g⁻¹ = h := by
    have hc := hz h
    calc g * (g * h * g⁻¹) * g⁻¹ = (g * g) * h * (g * g)⁻¹ := by group
      _ = h * (g * g) * (g * g)⁻¹ := by rw [hc]
      _ = h := by group
  rwa [e] at h2

-- normalizer membership gives exactly the subgroup EQUALITY `ModularForm.translate` needs.
theorem conjAct_smul_eq_of_mem_normalizer {G : Type*} [Group G] {H : Subgroup G} {g : G}
    (hg : g ∈ Subgroup.normalizer (H : Set G)) : toConjAct g⁻¹ • H = H := by
  ext x
  rw [Subgroup.mem_pointwise_smul_iff_inv_smul_mem, ← toConjAct_inv, inv_inv, toConjAct_smul]
  exact ((Subgroup.mem_normalizer_iff.mp hg) x).symm
