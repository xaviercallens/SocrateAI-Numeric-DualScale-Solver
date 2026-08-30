//! # LeanFlow Core
//!
//! Core types, Dual-Scale metrics, and Triadic Frustration Index calculations.

use num_complex::Complex64;
use serde::{Deserialize, Serialize};

/// Dual-Scale effective radius: R_eff(R) = max(R, alpha / R)
#[inline]
pub fn r_eff(alpha: f64, r: f64) -> f64 {
    assert!(alpha > 0.0, "alpha must be positive");
    assert!(r > 0.0, "radius r must be positive");
    let t_dual = alpha / r;
    if r > t_dual { r } else { t_dual }
}

/// Dual-Scale ultraviolet dissipation rate: D(k) = nu * |k|^2 * max(1.0, alpha * |k|^2)
#[inline]
pub fn dualscale_dissipation_rate(nu: f64, k_sq: f64, alpha: Option<f64>) -> f64 {
    let base = nu * k_sq;
    match alpha {
        Some(a) if a > 0.0 => base * f64::max(1.0, a * k_sq),
        _ => base,
    }
}

/// 3D Wavevector index
pub type Wavevector3D = [i32; 3];

/// Compute the Triadic Frustration Index D(M) on a finite Galerkin truncation.
///
/// D(M, u) = (sum_{k in B(M)} sum_{p+q=k} |T(p, q, k, u)|) / |sum_{k in B(M)} sum_{p+q=k} T(p, q, k, u)|
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TriadicFrustrationMetrics {
    pub m: usize,
    pub sum_abs_transfers: f64,
    pub sum_signed_transfers: f64,
    pub frustration_index: f64,
    pub is_heavily_frustrated: bool,
}

/// Calculate the Triadic Frustration Index from modal transfer samples.
pub fn compute_frustration_index_from_transfers(
    m: usize,
    transfers: &[f64],
) -> TriadicFrustrationMetrics {
    let mut sum_abs = 0.0;
    let mut sum_signed = 0.0;

    for &t in transfers {
        sum_abs += t.abs();
        sum_signed += t;
    }

    let denom = sum_signed.abs();
    let d_m = if denom < 1e-12 {
        f64::INFINITY
    } else {
        sum_abs / denom
    };

    TriadicFrustrationMetrics {
        m,
        sum_abs_transfers: sum_abs,
        sum_signed_transfers: sum_signed,
        frustration_index: d_m,
        is_heavily_frustrated: d_m > 10.0,
    }
}

/// A 2D Fourier velocity state on an N x N periodic grid.
#[derive(Debug, Clone)]
pub struct FourierVelocity2D {
    pub n: usize,
    pub ux_hat: Vec<Complex64>,
    pub uy_hat: Vec<Complex64>,
}

impl FourierVelocity2D {
    pub fn new(n: usize) -> Self {
        let size = n * n;
        Self {
            n,
            ux_hat: vec![Complex64::new(0.0, 0.0); size],
            uy_hat: vec![Complex64::new(0.0, 0.0); size],
        }
    }

    /// Total kinetic energy E = 0.5 * sum (|ux|^2 + |uy|^2) / N^4
    pub fn kinetic_energy(&self) -> f64 {
        let mut sum_sq = 0.0;
        for i in 0..self.ux_hat.len() {
            sum_sq += self.ux_hat[i].norm_sqr() + self.uy_hat[i].norm_sqr();
        }
        0.5 * sum_sq / (self.n.pow(4) as f64)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_r_eff_properties() {
        let alpha = 0.25; // sqrt(alpha) = 0.5
        // Macroscopic regime
        assert_eq!(r_eff(alpha, 1.0), 1.0);
        // Bounce regime
        assert_eq!(r_eff(alpha, 0.125), 2.0);
        // Crossover
        assert_eq!(r_eff(alpha, 0.5), 0.5);
        // Lower bound
        assert!(r_eff(alpha, 0.01) >= 0.5);
    }

    #[test]
    fn test_frustration_index_calculation() {
        // High frustration sample: opposing signs cancelling
        let transfers = vec![1.0, -0.99, 1.0, -1.01, 0.5, -0.49];
        let metrics = compute_frustration_index_from_transfers(4, &transfers);
        assert!(metrics.frustration_index > 10.0);
        assert!(metrics.is_heavily_frustrated);
    }
}
