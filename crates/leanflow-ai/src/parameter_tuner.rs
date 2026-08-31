//! # Parameter Tuner Module
//!
//! Automated parameter tuning, stiffness ratio estimation, and time-scheme selection.

use serde::{Deserialize, Serialize};

/// Recommended integration time scheme.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum RecommendedTimeScheme {
    RustySundialsCvodeBdf,
    RustySundialsCvodeAdams,
    EtdRk4IntegratingFactor,
}

/// Parameter tuning recommendation.
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct ParameterRecommendation {
    pub dt_recommended: f64,
    pub cfl_target: f64,
    pub stiffness_ratio: f64,
    pub recommended_scheme: RecommendedTimeScheme,
    pub recommended_order: usize,
}

/// Parameter Tuner.
pub struct ParameterTuner;

impl ParameterTuner {
    /// Tune timestep and integration scheme based on grid size dx, viscosity nu, and peak velocity u_max.
    pub fn tune(
        dx: f64,
        nu: f64,
        u_max: f64,
        alpha_prime: f64,
        dimension: usize,
        cfl_target: f64,
    ) -> ParameterRecommendation {
        let u_safe = u_max.max(1e-6);
        let nu_safe = nu.max(1e-12);

        // Advective timescale: dt_adv = dx / u_max
        let dt_adv = dx / u_safe;

        // Diffusive timescale: dt_diff = dx^2 / (2 * dim * nu)
        let dt_diff = (dx * dx) / (2.0 * (dimension as f64) * nu_safe);

        // Dual-scale regularized timescale: dt_dual = dx^4 / (alpha' * nu)
        let dt_dual = (dx.powi(4)) / (alpha_prime.max(1e-12) * nu_safe);

        let dt_min = dt_adv.min(dt_diff).min(dt_dual);
        let dt_recommended = cfl_target * dt_min;

        let stiffness_ratio = dt_adv / dt_diff.max(1e-15);

        let (scheme, order) = if stiffness_ratio > 2.0 {
            (RecommendedTimeScheme::RustySundialsCvodeBdf, 5)
        } else if stiffness_ratio > 0.5 {
            (RecommendedTimeScheme::EtdRk4IntegratingFactor, 4)
        } else {
            (RecommendedTimeScheme::RustySundialsCvodeAdams, 12)
        };

        ParameterRecommendation {
            dt_recommended,
            cfl_target,
            stiffness_ratio,
            recommended_scheme: scheme,
            recommended_order: order,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parameter_tuner_stiff_vs_nonstiff() {
        // High Reynolds / small viscosity -> advection dominates
        let rec_stiff = ParameterTuner::tune(0.01, 1e-5, 1.0, 1e-4, 3, 0.4);
        assert!(rec_stiff.dt_recommended > 0.0);

        // High viscosity -> diffusion dominates -> stiff BDF
        let rec_diff = ParameterTuner::tune(0.01, 1.0, 0.01, 1e-4, 3, 0.4);
        assert_eq!(rec_diff.recommended_scheme, RecommendedTimeScheme::RustySundialsCvodeBdf);
    }
}
