//! # LeanFlow Solver
//!
//! High-performance numerical solvers, integrating factor RK4 (ETD-RK4),
//! and adaptive time-stepping for multiscale PDEs.

pub mod cvode_dyadic;
pub mod embedded;

pub use cvode_dyadic::{CvodeCascadeResult, CvodeDyadicCascade};
pub use embedded::EmbeddedDyadicState;
use leanflow_core::dualscale_dissipation_rate;
use serde::{Deserialize, Serialize};

/// High-performance Dyadic Shell Model Solver (Katz-Pavlović).
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RustDyadicSolver {
    pub n_shells: usize,
    pub k0: f64,
    pub lambda: f64,
    pub nu: f64,
    pub alpha_prime: Option<f64>,
    pub k: Vec<f64>,
}

impl RustDyadicSolver {
    pub fn new(n_shells: usize, nu: f64, alpha_prime: Option<f64>) -> Self {
        let k0: f64 = 1.0;
        let lambda: f64 = 2.0;
        let k: Vec<f64> = (0..n_shells).map(|n| k0 * lambda.powi(n as i32)).collect();
        Self {
            n_shells,
            k0,
            lambda,
            nu,
            alpha_prime,
            k,
        }
    }

    /// Compute non-linear triad rate du/dt for all shells.
    pub fn non_linear_rhs(&self, u: &[f64], du: &mut [f64]) {
        for n in 0..self.n_shells {
            let u_prev = if n > 0 { u[n - 1] } else { 0.0 };
            let u_curr = u[n];
            let u_next = if n < self.n_shells - 1 { u[n + 1] } else { 0.0 };
            du[n] = self.k[n] * (u_prev * u_prev - self.lambda * u_curr * u_next);
        }
    }

    /// Total kinetic energy E = 0.5 * sum u_n^2
    pub fn kinetic_energy(&self, u: &[f64]) -> f64 {
        0.5 * u.iter().map(|&x| x * x).sum::<f64>()
    }

    /// Total enstrophy Omega = 0.5 * sum k_n^2 * u_n^2
    pub fn enstrophy(&self, u: &[f64]) -> f64 {
        0.5 * u.iter().zip(&self.k).map(|(&x, &k)| k * k * x * x).sum::<f64>()
    }

    /// Step simulation using exact Integrating Factor RK4 (ETD-RK4).
    ///
    /// Correct Cox-Matthews / Kassam-Trefethen integrating factor coefficients:
    /// Stage 1: k1 = N(u_n)
    /// Stage 2: u_tmp2 = e^{L dt/2} u_n + 0.5 * dt * e^{L dt/2} k1
    /// Stage 3: u_tmp3 = e^{L dt/2} u_n + 0.5 * dt * k2  (since k2 = N(u_tmp2))
    /// Stage 4: u_tmp4 = e^{L dt} u_n + dt * e^{L dt/2} k3 (since k3 = N(u_tmp3))
    /// Final:   u_{n+1} = e^{L dt} u_n + (dt/6) * (e^{L dt} k1 + 2 e^{L dt/2} k2 + 2 e^{L dt/2} k3 + k4)
    pub fn step_etd_rk4(&self, u: &[f64], dt: f64, out: &mut [f64]) {
        let n = self.n_shells;
        let mut k1 = vec![0.0; n];
        let mut k2 = vec![0.0; n];
        let mut k3 = vec![0.0; n];
        let mut k4 = vec![0.0; n];

        let mut u_tmp = vec![0.0; n];

        // Linear dissipation decay factors: e^{-0.5 d dt} and e^{-d dt}
        let e_half: Vec<f64> = (0..n)
            .map(|i| {
                let d = dualscale_dissipation_rate(self.nu, self.k[i] * self.k[i], self.alpha_prime);
                (-0.5 * d * dt).exp()
            })
            .collect();

        let e_full: Vec<f64> = (0..n)
            .map(|i| {
                let d = dualscale_dissipation_rate(self.nu, self.k[i] * self.k[i], self.alpha_prime);
                (-d * dt).exp()
            })
            .collect();

        // Stage 1: compute N(u)
        self.non_linear_rhs(u, &mut k1);

        // Stage 2: u_tmp = e_half * u + 0.5 * dt * e_half * k1
        for i in 0..n {
            u_tmp[i] = e_half[i] * (u[i] + 0.5 * dt * k1[i]);
        }
        self.non_linear_rhs(&u_tmp, &mut k2);

        // Stage 3: u_tmp = e_half * u + 0.5 * dt * k2
        for i in 0..n {
            u_tmp[i] = e_half[i] * u[i] + 0.5 * dt * k2[i];
        }
        self.non_linear_rhs(&u_tmp, &mut k3);

        // Stage 4: u_tmp = e_full * u + dt * e_half * k3
        for i in 0..n {
            u_tmp[i] = e_full[i] * u[i] + dt * e_half[i] * k3[i];
        }
        self.non_linear_rhs(&u_tmp, &mut k4);

        // Assemble solution
        for i in 0..n {
            out[i] = e_full[i] * u[i]
                + (dt / 6.0)
                    * (e_full[i] * k1[i] + 2.0 * e_half[i] * k2[i] + 2.0 * e_half[i] * k3[i] + k4[i]);
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_dyadic_solver_etd_step() {
        let solver = RustDyadicSolver::new(12, 1e-3, Some(0.01));
        let mut u0 = vec![0.0; 12];
        u0[0] = 1.0;
        u0[1] = 0.5;

        let mut u1 = vec![0.0; 12];
        solver.step_etd_rk4(&u0, 0.001, &mut u1);

        let e0 = solver.kinetic_energy(&u0);
        let e1 = solver.kinetic_energy(&u1);

        // Energy decays or transfers stably
        assert!(e1 <= e0);
        assert!(e1 > 0.0);
    }
}
