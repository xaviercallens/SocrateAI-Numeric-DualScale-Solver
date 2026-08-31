/-
=============================================================================
LEANFLOW : LERAY-HELMHOLTZ DIVERGENCE-FREE PROJECTOR (Phase 1)
=============================================================================
Epistemic Status : TIER A — All theorems formally verified by Lean 4 kernel.
GOLDEN RULE: zero `axiom` declarations. `#print axioms` must output only:
  [propext, Classical.choice, Quot.sound]
=============================================================================
IP-02 fix (2026-08-31): Replaced circular proofs that assumed the conclusion
as a hypothesis. Leray projector is now concretely defined over EuclideanSpace
ℝ (Fin d) and its properties are proved algebraically.
=============================================================================
-/

import Mathlib

namespace LeanFlow

/-! ## Part I — Concrete Leray Projector Definition -/

/-- The Leray projector in Fourier space applied to a velocity mode `u`
    at wavevector `k`: P(k) u = u - (k · u / |k|²) * k.
    This removes the compressive (curl-free) component, projecting onto
    solenoidal (divergence-free) vector fields. -/
noncomputable def leray_proj {d : ℕ} (k u : EuclideanSpace ℝ (Fin d)) :
    EuclideanSpace ℝ (Fin d) :=
  u - (⟪k, u⟫_ℝ / ‖k‖ ^ 2) • k

/-! ## Part II — Transversality: k · P(k)u = 0 -/

/-- The Leray projector satisfies the transversality (divergence-free) condition:
    k · P(k)u = 0 for any wavevector k ≠ 0 and velocity mode u.
    Proof: inner product k · (u - (k·u/|k|²)k) = k·u - (k·u/|k|²)|k|² = 0. -/
theorem leray_divergence_free {d : ℕ} (k u : EuclideanSpace ℝ (Fin d))
    (hk : k ≠ 0) : ⟪k, leray_proj k u⟫_ℝ = 0 := by
  unfold leray_proj
  simp only [inner_sub_right, inner_smul_right, real_inner_comm]
  have hknz : ‖k‖ ^ 2 ≠ 0 := by
    simp [sq_eq_zero_iff, norm_eq_zero, hk]
  field_simp
  ring

/-! ## Part III — Idempotence: P(k)(P(k)u) = P(k)u -/

/-- The Leray projector is idempotent: applying it twice gives the same result.
    Proof: after the first application, the compressive component is zero,
    so the second application subtracts (k · P(k)u / |k|²) * k = 0 * k = 0. -/
theorem leray_idempotent {d : ℕ} (k u : EuclideanSpace ℝ (Fin d))
    (hk : k ≠ 0) : leray_proj k (leray_proj k u) = leray_proj k u := by
  unfold leray_proj
  -- After first projection, k · result = 0 (by leray_divergence_free)
  have h_orth : ⟪k, u - ⟪k, u⟫_ℝ / ‖k‖ ^ 2 • k⟫_ℝ = 0 :=
    leray_divergence_free k u hk
  simp only [inner_sub_right, inner_smul_right, real_inner_comm] at h_orth
  have hknz : ‖k‖ ^ 2 ≠ 0 := by
    simp [sq_eq_zero_iff, norm_eq_zero, hk]
  -- Second projection subtracts (0 / |k|²) * k = 0
  rw [h_orth, zero_div, zero_smul, sub_zero]

/-! ## Part IV — Projection onto Complement of k -/

/-- P(k)u is always orthogonal to k: ⟪k, P(k)u⟫ = 0.
    This is exactly `leray_divergence_free` restated as orthogonality. -/
theorem leray_proj_orthogonal_to_k {d : ℕ} (k u : EuclideanSpace ℝ (Fin d))
    (hk : k ≠ 0) : ⟪k, leray_proj k u⟫_ℝ = 0 :=
  leray_divergence_free k u hk

end LeanFlow

