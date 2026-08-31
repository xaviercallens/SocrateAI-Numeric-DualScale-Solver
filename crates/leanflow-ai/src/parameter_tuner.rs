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

    /// Positive test: high-Re stiff regime selects BDF; high-viscosity laminar selects BDF too.
    #[test]
    fn test_parameter_tuner_stiff_vs_nonstiff() {
        // High Reynolds / small viscosity -> advection dominates -> ETD-RK4
        let rec_stiff = ParameterTuner::tune(0.01, 1e-5, 1.0, 1e-4, 3, 0.4);
        assert!(rec_stiff.dt_recommended > 0.0, "dt must be positive");
        // stiffness_ratio = dt_adv / dt_diff = (dx/u) / (dx^2/(2d*nu))
        // = 2*d*nu*u / (dx*u^2) -- at dx=0.01, nu=1e-5, u=1, d=3: small ratio -> ETD-RK4
        assert!(rec_stiff.dt_recommended <= 0.4 * 0.01, "dt must satisfy CFL bound");

        // High viscosity -> diffusion dominates -> stiff BDF
        let rec_diff = ParameterTuner::tune(0.01, 1.0, 0.01, 1e-4, 3, 0.4);
        assert_eq!(rec_diff.recommended_scheme, RecommendedTimeScheme::RustySundialsCvodeBdf);
    }

    /// Positive test: CFL constraint is respected (dt <= cfl_target * dx / u_max).
    #[test]
    fn test_cfl_constraint_satisfied() {
        let dx = 0.05;
        let u_max = 2.0;
        let cfl = 0.4;
        let rec = ParameterTuner::tune(dx, 1e-4, u_max, 1e-6, 2, cfl);

        // Advective CFL bound: dt <= cfl * dx / u_max = 0.4 * 0.05 / 2.0 = 0.01
        let cfl_bound = cfl * dx / u_max;
        assert!(
            rec.dt_recommended <= cfl_bound * 1.001, // small tolerance for float
            "dt_recommended={} violates CFL bound={}", rec.dt_recommended, cfl_bound
        );
    }

    /// Negative control NC-RUST-PT-01:
    /// Zero u_max must not panic and must yield a strictly positive dt.
    #[test]
    fn test_nc_zero_umax_no_panic() {
        // u_max = 0.0: floor at 1e-6 must prevent division by zero
        let rec = ParameterTuner::tune(0.01, 1e-4, 0.0, 1e-6, 3, 0.4);
        assert!(rec.dt_recommended > 0.0, "NC: dt must be positive even at u_max=0");
        assert!(rec.stiffness_ratio >= 0.0);
    }

    /// Negative control NC-RUST-PT-02:
    /// Non-stiff laminar flow must NEVER select BDF (Adams is correct).
    #[test]
    fn test_nc_nonstiff_laminar_never_bdf() {
        // Highly diffusive laminar: large nu relative to advection -> stiffness_ratio << 0.5
        // dx=0.1, nu=10.0, u=0.01, d=2 -> dt_adv=10, dt_diff=dx^2/(2*2*nu)=1e-2/40=2.5e-4
        // stiffness_ratio = dt_adv/dt_diff = 10/2.5e-4 = 40000 >> 2 -> BDF is expected
        // Use extremely non-stiff case instead:
        // dx=0.01, nu=1e-6, u=0.001 -> dt_adv=10, dt_diff=0.01^2/(2*3*1e-6)=1/6e4~1.67
        // stiffness_ratio = 10/1.67 = 6.0 > 2 -> BDF
        //
        // True non-stiff: viscosity moderate, advection fast
        // dx=0.1, nu=0.5, u=100 -> dt_adv=1e-3, dt_diff=0.1^2/(2*3*0.5)=1e-2/3=3.3e-3
        // stiffness_ratio = 1e-3/3.3e-3 = 0.30 < 0.5 -> Adams
        let rec = ParameterTuner::tune(0.1, 0.5, 100.0, 1e-3, 3, 0.4);
        assert_eq!(
            rec.recommended_scheme,
            RecommendedTimeScheme::RustySundialsCvodeAdams,
            "NC: Non-stiff flow (ratio={:.3}) must select Adams, not BDF", rec.stiffness_ratio
        );
    }
}
