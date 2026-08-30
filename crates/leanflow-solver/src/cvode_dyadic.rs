//! # CVODE Dyadic Shell Solver
//!
//! Variable-order, variable-step BDF (stiff) and Adams-Moulton (non-stiff)
//! solver for the DualScale dyadic shell cascade using rusty-SUNDIALS.

use cvode::{Cvode, Method, Task};
use leanflow_core::dualscale_dissipation_rate;
use nvector::SerialVector;
use serde::{Deserialize, Serialize};

/// High-order CVODE-backed solver for dyadic cascade with dual-scale dissipation.
pub struct CvodeDyadicCascade {
    pub n_shells: usize,
    pub nu: f64,
    pub alpha_prime: Option<f64>,
    pub k: Vec<f64>,
    pub method: Method,
    pub rtol: f64,
    pub atol: f64,
}

impl CvodeDyadicCascade {
    pub fn new(
        n_shells: usize,
        nu: f64,
        alpha_prime: Option<f64>,
        use_bdf: bool,
        rtol: f64,
        atol: f64,
    ) -> Self {
        let k0: f64 = 1.0;
        let lambda: f64 = 2.0;
        let k: Vec<f64> = (0..n_shells).map(|n| k0 * lambda.powi(n as i32)).collect();
        let method = if use_bdf { Method::Bdf } else { Method::Adams };
        Self {
            n_shells,
            nu,
            alpha_prime,
            k,
            method,
            rtol,
            atol,
        }
    }

    /// Simulate the trajectory from t=0 to t_final in n_steps using CVODE.
    pub fn integrate(
        &self,
        u0: &[f64],
        t_final: f64,
        n_steps: usize,
    ) -> Result<CvodeCascadeResult, String> {
        let n = self.n_shells;
        let k_vec = self.k.clone();
        let nu = self.nu;
        let alpha = self.alpha_prime;
        let lambda: f64 = 2.0;

        // Right-hand side closure for CVODE: du_n/dt = NonLinear_n - Dissipation_n * u_n
        let rhs = move |_t: f64, y: &[f64], ydot: &mut [f64]| -> Result<(), String> {
            for i in 0..n {
                let u_prev = if i > 0 { y[i - 1] } else { 0.0 };
                let u_curr = y[i];
                let u_next = if i < n - 1 { y[i + 1] } else { 0.0 };

                let nl = k_vec[i] * (u_prev * u_prev - lambda * u_curr * u_next);
                let diss = dualscale_dissipation_rate(nu, k_vec[i] * k_vec[i], alpha);
                ydot[i] = nl - diss * u_curr;
            }
            Ok(())
        };

        let y0_vec = SerialVector::from_slice(u0);
        let mut cvode_solver = Cvode::builder(self.method)
            .rtol(self.rtol)
            .atol(self.atol)
            .max_order(if self.method == Method::Bdf { 5 } else { 12 })
            .max_steps(1_000_000)
            .build(rhs, 0.0, y0_vec)
            .map_err(|e| format!("Failed to build CVODE solver: {:?}", e))?;

        let dt = t_final / (n_steps as f64);
        let mut time_series = Vec::with_capacity(n_steps + 1);
        let mut energy_series = Vec::with_capacity(n_steps + 1);
        let mut enstrophy_series = Vec::with_capacity(n_steps + 1);
        let mut final_state = u0.to_vec();

        // Record initial state
        time_series.push(0.0);
        energy_series.push(0.5 * u0.iter().map(|&x| x * x).sum::<f64>());
        enstrophy_series.push(0.5 * u0.iter().zip(&self.k).map(|(&x, &k)| k * k * x * x).sum::<f64>());

        for step in 1..=n_steps {
            let tout = step as f64 * dt;
            let (t_curr, y_curr) = cvode_solver
                .solve(tout, Task::Normal)
                .map_err(|e| format!("CVODE solve step failed at t={}: {:?}", tout, e))?;

            for i in 0..n {
                final_state[i] = y_curr[i];
            }

            let e = 0.5 * final_state.iter().map(|&x| x * x).sum::<f64>();
            let ens = 0.5 * final_state.iter().zip(&self.k).map(|(&x, &k)| k * k * x * x).sum::<f64>();

            time_series.push(t_curr);
            energy_series.push(e);
            enstrophy_series.push(ens);
        }

        Ok(CvodeCascadeResult {
            num_steps: cvode_solver.num_steps(),
            num_rhs_evals: cvode_solver.num_rhs_evals(),
            time: time_series,
            energy: energy_series,
            enstrophy: enstrophy_series,
            final_state,
        })
    }
}

/// Results from a CVODE dyadic integration rollout.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CvodeCascadeResult {
    pub num_steps: usize,
    pub num_rhs_evals: usize,
    pub time: Vec<f64>,
    pub energy: Vec<f64>,
    pub enstrophy: Vec<f64>,
    pub final_state: Vec<f64>,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_cvode_dyadic_bdf_solve() {
        let cascade = CvodeDyadicCascade::new(10, 1e-3, Some(0.01), true, 1e-4, 1e-6);
        let mut u0 = vec![0.0; 10];
        u0[0] = 1.0;
        u0[1] = 0.5;

        let result = cascade.integrate(&u0, 0.05, 5).expect("CVODE solve failed");
        assert!(result.num_steps > 0);
        assert_eq!(result.time.len(), 6);
        // Energy remains bounded and decreases via dual-scale dissipation
        assert!(result.energy.last().unwrap() <= &result.energy[0]);
    }
}
