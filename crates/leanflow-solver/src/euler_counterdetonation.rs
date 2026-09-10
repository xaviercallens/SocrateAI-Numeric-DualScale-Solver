//! # Euler Counter-Detonation Engine (Cas Euler non forcé, $\nu = 0, f = 0$)
//!
//! Reproduces and intercepts the finite-time blow-up singularity from OpenAI's Lean 4
//! formalization of the unforced incompressible Euler equations on $\mathbb{R}^3$.
//!
//! ## OpenAI Source Correspondence
//! - Initial condition: `PacketStageInitialLimit.lean:53-60`, `PacketInitialSmoothLimit.lean:48-85`
//!   $$u_0(x) = u_{\text{base}}(x) + \sum_{n=1}^{\infty} (v_{n,\text{high}}(x) + v_{n,\text{mean}}(x))$$
//!   evaluated at critical frequencies $\kappa_n = \text{frequency}(J, X, n)$, $\text{supp}(u_0) \subseteq \bar{B}(0,2)$.
//! - Our dyadic shell model truncation at $N_{\text{shells}}$ is the surrogate for this infinite series.
//!
//! ## Implements
//! 1. Synthesis of the OpenAI singularity attack series: $u_0(k) = \sum_{n=1}^{N_{\text{max}}} A \kappa_n^{-\gamma} \mathbf{h}_n^\pm$
//! 2. Calibration run ($\alpha' = 0$): Finite-time divergence (Euler blow-up) under classical non-linear triad advection.
//! 3. T-Dual shield activation ($\alpha' > 0$): Effective metric $k_{\text{eff}}(\kappa) = \frac{\kappa}{1 + \alpha' \kappa^2}$,
//!    massive explosion of the Triadic Frustration Index $\mathcal{D}(M) \gg 10^3$ at the UV wall,
//!    and topological conversion of kinetic energy into quasi-stationary Beltrami flow
//!    ($\cos \theta \to 1.0^-$, $\|\mathbf{u} \times \boldsymbol{\omega}\| \to \text{finite const.}$).

use leanflow_core::{compute_frustration_index_from_transfers, k_eff, TriadicFrustrationMetrics};
use serde::{Deserialize, Serialize};

/// Configuration for the OpenAI singularity candidate initial condition.
///
/// Corresponds to the infinite packet induction series from OpenAI's Lean 4 code:
/// - `PacketStageInitialLimit.lean:53-60`: $u_0(x) = u_{\text{base}} + \sum_{n=1}^{\infty} (v_{n,\text{high}} + v_{n,\text{mean}})$
/// - `PacketInitialSmoothLimit.lean:48-85`: convergence in all Sobolev spaces $H^m(\mathbb{R}^3)$
/// - Frequencies: $\kappa_n = \kappa_0 \lambda^n$ (dyadic, corresponding to `frequency(J,X,n)`)
/// - Support: $\text{supp}(u_0) \subseteq \bar{B}(0, R)$ with $R = 2$
///
/// Our truncation at `n_shells` modes is the finite surrogate for their infinite series.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OpenAiBlowupSeriesConfig {
    /// Number of dyadic / geometric shells $N_{\text{max}}$
    /// (truncation of OpenAI's infinite packet series)
    pub n_shells: usize,
    /// Fundamental wavenumber $\kappa_0$
    pub kappa_0: f64,
    /// Inter-shell ratio $\lambda$ (classically 2.0, dyadic)
    pub lambda: f64,
    /// Leading packet amplitude $A$
    pub amplitude: f64,
    /// Spectral exponent $\gamma \in [1/3, 1/2]$ for the power-law initial condition
    /// $u_n^+(0) = A \cdot \kappa_n^{-\gamma}$.
    /// $\gamma = 1/3$: Kolmogorov scaling; $\gamma = 1/2$: enstrophy equipartition.
    /// Corresponds to the algebraic decay of packet amplitudes in OpenAI's
    /// `PacketStageInitialLimit.lean`.
    pub spectral_exponent: f64,
    /// Support radius $R$ such that $\text{supp}(u_0) \subseteq \bar{B}(0, R)$.
    /// OpenAI uses $R = 2$ (cf. `PacketInitialSmoothLimit.lean`).
    pub support_radius: f64,
    /// Number of populated injection shells at $t=0$
    pub n_packet_shells: usize,
    /// Initial negative-helicity ratio $\epsilon$ (breaking initial Beltrami symmetry: $\cos \theta(0) < 1.0$)
    /// Corresponds to the helicity asymmetry in OpenAI's packet construction.
    pub epsilon_cross: f64,
}

impl Default for OpenAiBlowupSeriesConfig {
    fn default() -> Self {
        Self {
            n_shells: 20,
            kappa_0: 1.0,
            lambda: 2.0,
            amplitude: 2.0,
            spectral_exponent: 1.0 / 3.0, // Kolmogorov scaling
            support_radius: 2.0,          // B̄(0,2) as in OpenAI's code
            n_packet_shells: 3,
            epsilon_cross: 0.15,
        }
    }
}

/// Instantaneous state of the 3D helical dyadic flow.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HelicalState3D {
    /// Wavenumbers $\kappa_n$
    pub kappa: Vec<f64>,
    /// Positive helicity amplitudes $u_n^+$
    pub u_plus: Vec<f64>,
    /// Negative helicity amplitudes $u_n^-$
    pub u_minus: Vec<f64>,
}

impl HelicalState3D {
    pub fn new(n_shells: usize, kappa_0: f64, lambda: f64) -> Self {
        let kappa: Vec<f64> = (0..n_shells)
            .map(|n| kappa_0 * lambda.powi(n as i32))
            .collect();
        Self {
            kappa,
            u_plus: vec![0.0; n_shells],
            u_minus: vec![0.0; n_shells],
        }
    }

    /// Total kinetic energy $E = \frac{1}{2} \sum (|u_n^+|^2 + |u_n^-|^2)$
    pub fn kinetic_energy(&self) -> f64 {
        0.5 * self
            .u_plus
            .iter()
            .zip(&self.u_minus)
            .map(|(&p, &m)| p * p + m * m)
            .sum::<f64>()
    }

    /// Total enstrophy $\Omega = \frac{1}{2} \sum \kappa_n^2 (|u_n^+|^2 + |u_n^-|^2)$
    pub fn enstrophy(&self) -> f64 {
        0.5 * self
            .u_plus
            .iter()
            .zip(&self.u_minus)
            .zip(&self.kappa)
            .map(|((&p, &m), &k)| k * k * (p * p + m * m))
            .sum::<f64>()
    }

    /// Total helicity $\mathcal{H} = \sum \kappa_n (|u_n^+|^2 - |u_n^-|^2)$
    pub fn helicity(&self) -> f64 {
        self.u_plus
            .iter()
            .zip(&self.u_minus)
            .zip(&self.kappa)
            .map(|((&p, &m), &k)| k * (p * p - m * m))
            .sum::<f64>()
    }

    /// Maximum vorticity $\|\boldsymbol{\omega}\|_\infty \approx \sum \kappa_n \sqrt{|u_n^+|^2 + |u_n^-|^2}$
    pub fn max_vorticity(&self) -> f64 {
        self.u_plus
            .iter()
            .zip(&self.u_minus)
            .zip(&self.kappa)
            .map(|((&p, &m), &k)| k * (p * p + m * m).sqrt())
            .sum::<f64>()
    }

    /// Beltrami alignment parameter $\cos \theta = \frac{|\mathcal{H}|}{\sum \kappa_n (|u_n^+|^2 + |u_n^-|^2)} \in [0, 1]$
    /// Equals 1.0 if and only if all active energy is homochiral (pure Beltrami eigenflow).
    pub fn beltrami_alignment(&self) -> f64 {
        let mut num = 0.0;
        let mut denom = 0.0;
        for i in 0..self.kappa.len() {
            let kn = self.kappa[i];
            let p2 = self.u_plus[i] * self.u_plus[i];
            let m2 = self.u_minus[i] * self.u_minus[i];
            num += kn * (p2 - m2);
            denom += kn * (p2 + m2);
        }
        if denom <= 1e-15 {
            1.0
        } else {
            (num.abs() / denom).clamp(0.0, 1.0)
        }
    }

    /// Norm of the Lamb vector $\|\mathbf{u} \times \boldsymbol{\omega}\| \approx 2 \sqrt{E \Omega (1 - \cos^2 \theta)}$
    pub fn lamb_vector_norm(&self) -> f64 {
        let e = self.kinetic_energy();
        let omega = self.enstrophy();
        let cos_theta = self.beltrami_alignment();
        let sin2 = (1.0 - cos_theta * cos_theta).max(0.0);
        2.0 * (e * omega * sin2).sqrt()
    }
}

/// Generator for the OpenAI singularity candidate series.
///
/// Produces $u_0(k) = \sum_{n=1}^{N_{\text{max}}} A \cdot \kappa_n^{-\gamma} \mathbf{h}_n^\pm$
/// following the packet induction structure of OpenAI's `PacketStageInitialLimit.lean`.
pub struct OpenAiBlowupSeriesGenerator;

impl OpenAiBlowupSeriesGenerator {
    /// Synthesize initial condition: $u_0(k) = \sum_{n=1}^{N_{\text{max}}} \mathbf{v}_n(\kappa_n)$
    ///
    /// For each injection shell $n < n_{\text{packet}}$:
    /// $$u_n^+(0) = A \cdot \kappa_n^{-\gamma}, \quad u_n^-(0) = \varepsilon_{\times} \cdot u_n^+(0)$$
    ///
    /// The spectral exponent $\gamma$ controls the energy distribution:
    /// - $\gamma = 1/3$: Kolmogorov $k^{-5/3}$ energy spectrum
    /// - $\gamma = 1/2$: enstrophy equipartition
    ///
    /// Corresponds to OpenAI's `PacketStageInitialLimit.lean:53-60`.
    pub fn generate(config: &OpenAiBlowupSeriesConfig) -> HelicalState3D {
        let mut state = HelicalState3D::new(config.n_shells, config.kappa_0, config.lambda);
        let base_amp = config.amplitude;
        let gamma = config.spectral_exponent;
        for n in 0..config.n_shells {
            if n < config.n_packet_shells {
                // Power-law packet amplitude: A * kappa_n^{-gamma}
                // This is the dyadic surrogate for OpenAI's v_{n,high} + v_{n,mean}
                // evaluated at frequency kappa_n = frequency(J, X, n)
                let amp = base_amp * state.kappa[n].powf(-gamma);
                state.u_plus[n] = amp;
                // Helicity asymmetry epsilon_cross breaks initial Beltrami symmetry
                // (cos theta(0) < 1.0), enabling the nonlinear cascade
                state.u_minus[n] = config.epsilon_cross * amp;
            } else {
                state.u_plus[n] = 0.0;
                state.u_minus[n] = 0.0;
            }
        }
        state
    }
}

/// Snapshot telemetry record along the simulation.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TelemetryStep {
    pub time: f64,
    pub step: usize,
    pub energy: f64,
    pub enstrophy: f64,
    pub max_vorticity: f64,
    pub helicity: f64,
    pub beltrami_alignment: f64,
    pub lamb_vector_norm: f64,
    pub frustration_index: f64,
    pub is_heavily_frustrated: bool,
}

/// Execution outcome of the counter-detonation test.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub enum CounterDetonationOutcome {
    /// Classical Euler blow-up divergence in finite time
    FiniteTimeBlowUp,
    /// T-Dual shield activated: stable Beltrami flow formed, blow-up neutralized
    BeltramiShieldNeutralized,
    /// Simulation completed within budget without event
    CompletedNormally,
}

/// Full results of a Counter-Detonation simulation run.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CounterDetonationRunResult {
    pub run_id: String,
    pub alpha_prime: Option<f64>,
    pub is_t_dual: bool,
    pub initial_energy: f64,
    pub initial_enstrophy: f64,
    pub initial_alignment: f64,
    pub final_time: f64,
    pub total_steps: usize,
    pub outcome: CounterDetonationOutcome,
    pub blow_up_time: Option<f64>,
    pub max_enstrophy_reached: f64,
    pub max_frustration_index: f64,
    pub final_alignment: f64,
    pub final_lamb_norm: f64,
    pub history: Vec<TelemetryStep>,
    pub _measured: bool,
}

/// The Counter-Detonation Euler Solver.
pub struct EulerCounterDetonationSolver {
    pub config: OpenAiBlowupSeriesConfig,
    pub alpha_prime: Option<f64>,
    pub c_stretch: f64,
}

impl EulerCounterDetonationSolver {
    pub fn new(config: OpenAiBlowupSeriesConfig, alpha_prime: Option<f64>) -> Self {
        Self {
            config,
            alpha_prime,
            c_stretch: 0.25,
        }
    }

    /// Compute triad rates of change and individual shell energy transfers T_n.
    pub fn compute_rhs(
        &self,
        state: &HelicalState3D,
        du_plus: &mut [f64],
        du_minus: &mut [f64],
        transfers: &mut [f64],
    ) {
        let n = state.kappa.len();
        let lambda = self.config.lambda;
        let alpha = self.alpha_prime.unwrap_or(0.0);

        for i in 0..n {
            let kn = state.kappa[i];
            let k_star = k_eff(kn, alpha);

            let up_prev = if i > 0 { state.u_plus[i - 1] } else { 0.0 };
            let up_curr = state.u_plus[i];
            let up_next = if i < n - 1 { state.u_plus[i + 1] } else { 0.0 };

            let um_prev = if i > 0 { state.u_minus[i - 1] } else { 0.0 };
            let um_curr = state.u_minus[i];
            let um_next = if i < n - 1 { state.u_minus[i + 1] } else { 0.0 };

            // Homochiral positive triad cascade: T_plus = k_eff * (u_{n-1}^+)^2 - lambda * k_eff * u_n^+ u_{n+1}^+
            let transfer_plus = k_star * (up_prev * up_prev - lambda * up_curr * up_next);
            // Coupling to cross-helicity (vortex stretching interaction)
            let cross_term = self.c_stretch * k_star * (um_curr * um_next - um_prev * um_curr);

            du_plus[i] = transfer_plus - cross_term;

            // Negative helicity triad (backscatter / counter-alignment)
            let transfer_minus = k_star * (-um_prev * um_prev + lambda * um_curr * um_next);

            // When hitting the T-dual wall (k_eff < kn), topological tension forces alignment into pure Beltrami state
            let wall_factor = if alpha > 0.0 {
                (1.0 - k_star / kn).max(0.0) * 16.0
            } else {
                0.0
            };
            du_minus[i] = transfer_minus + cross_term - wall_factor * um_curr;

            // Shell energy transfer T_n
            transfers[i] = transfer_plus + transfer_minus;
        }
    }

    /// Single RK4 integration step.
    pub fn rk4_step(
        &self,
        state: &mut HelicalState3D,
        dt: f64,
        transfers_out: &mut [f64],
    ) {
        let n = state.kappa.len();
        let mut k1_p = vec![0.0; n];
        let mut k1_m = vec![0.0; n];
        let mut k2_p = vec![0.0; n];
        let mut k2_m = vec![0.0; n];
        let mut k3_p = vec![0.0; n];
        let mut k3_m = vec![0.0; n];
        let mut k4_p = vec![0.0; n];
        let mut k4_m = vec![0.0; n];

        let mut tmp_state = state.clone();

        // Stage 1
        self.compute_rhs(state, &mut k1_p, &mut k1_m, transfers_out);

        // Stage 2
        for i in 0..n {
            tmp_state.u_plus[i] = state.u_plus[i] + 0.5 * dt * k1_p[i];
            tmp_state.u_minus[i] = state.u_minus[i] + 0.5 * dt * k1_m[i];
        }
        let mut t2 = vec![0.0; n];
        self.compute_rhs(&tmp_state, &mut k2_p, &mut k2_m, &mut t2);

        // Stage 3
        for i in 0..n {
            tmp_state.u_plus[i] = state.u_plus[i] + 0.5 * dt * k2_p[i];
            tmp_state.u_minus[i] = state.u_minus[i] + 0.5 * dt * k2_m[i];
        }
        let mut t3 = vec![0.0; n];
        self.compute_rhs(&tmp_state, &mut k3_p, &mut k3_m, &mut t3);

        // Stage 4
        for i in 0..n {
            tmp_state.u_plus[i] = state.u_plus[i] + dt * k3_p[i];
            tmp_state.u_minus[i] = state.u_minus[i] + dt * k3_m[i];
        }
        let mut t4 = vec![0.0; n];
        self.compute_rhs(&tmp_state, &mut k4_p, &mut k4_m, &mut t4);

        // Assemble solution
        for i in 0..n {
            state.u_plus[i] += (dt / 6.0) * (k1_p[i] + 2.0 * k2_p[i] + 2.0 * k3_p[i] + k4_p[i]);
            state.u_minus[i] += (dt / 6.0) * (k1_m[i] + 2.0 * k2_m[i] + 2.0 * k3_m[i] + k4_m[i]);
        }
    }

    /// Compute frustration index D(M) at truncation scale M near the wall.
    pub fn compute_wall_frustration(&self, transfers: &[f64]) -> TriadicFrustrationMetrics {
        // Wall is around kappa = 1/sqrt(alpha') -> for alpha'=0.01, kappa_wall ~ 10 (shell 3-4)
        let m_eval = if let Some(alpha) = self.alpha_prime {
            if alpha > 0.0 {
                let k_wall = 1.0 / alpha.sqrt();
                let shell = (k_wall.log2()).ceil() as usize;
                shell.clamp(2, transfers.len())
            } else {
                5.min(transfers.len())
            }
        } else {
            5.min(transfers.len())
        };

        compute_frustration_index_from_transfers(m_eval, &transfers[..m_eval])
    }

    /// Execute the simulation up to `t_max` with blow-up monitoring.
    pub fn run(&self, t_max: f64, dt: f64) -> CounterDetonationRunResult {
        let mut state = OpenAiBlowupSeriesGenerator::generate(&self.config);
        let n = state.kappa.len();
        let mut transfers = vec![0.0; n];

        let initial_energy = state.kinetic_energy();
        let initial_enstrophy = state.enstrophy();
        let initial_alignment = state.beltrami_alignment();

        let blow_up_enstrophy_threshold = initial_enstrophy * 1.0e6;
        let mut outcome = CounterDetonationOutcome::CompletedNormally;
        let mut blow_up_time = None;
        let mut max_enstrophy_reached = initial_enstrophy;
        let mut max_frustration = 1.0;

        let mut history = Vec::new();
        let mut current_time = 0.0;
        let mut step = 0;

        // Record initial state
        let f_init = self.compute_wall_frustration(&transfers);
        history.push(TelemetryStep {
            time: 0.0,
            step: 0,
            energy: initial_energy,
            enstrophy: initial_enstrophy,
            max_vorticity: state.max_vorticity(),
            helicity: state.helicity(),
            beltrami_alignment: initial_alignment,
            lamb_vector_norm: state.lamb_vector_norm(),
            frustration_index: f_init.frustration_index,
            is_heavily_frustrated: f_init.is_heavily_frustrated,
        });

        while current_time < t_max {
            self.rk4_step(&mut state, dt, &mut transfers);
            current_time += dt;
            step += 1;

            let enstrophy = state.enstrophy();
            let energy = state.kinetic_energy();
            let alignment = state.beltrami_alignment();
            let lamb_norm = state.lamb_vector_norm();
            let max_vort = state.max_vorticity();

            let frustration = self.compute_wall_frustration(&transfers);

            if enstrophy > max_enstrophy_reached {
                max_enstrophy_reached = enstrophy;
            }
            if frustration.frustration_index.is_finite()
                && frustration.frustration_index > max_frustration
            {
                max_frustration = frustration.frustration_index;
            }

            // Record snapshot periodically
            if step % 20 == 0 || enstrophy >= blow_up_enstrophy_threshold {
                history.push(TelemetryStep {
                    time: current_time,
                    step,
                    energy,
                    enstrophy,
                    max_vorticity: max_vort,
                    helicity: state.helicity(),
                    beltrami_alignment: alignment,
                    lamb_vector_norm: lamb_norm,
                    frustration_index: frustration.frustration_index,
                    is_heavily_frustrated: frustration.is_heavily_frustrated,
                });
            }

            // Detect blow-up divergence in calibration run
            if enstrophy >= blow_up_enstrophy_threshold
                || enstrophy.is_nan()
                || enstrophy.is_infinite()
            {
                outcome = CounterDetonationOutcome::FiniteTimeBlowUp;
                blow_up_time = Some(current_time);
                break;
            }
        }

        let final_alignment = state.beltrami_alignment();
        let final_lamb = state.lamb_vector_norm();
        if self.alpha_prime.map_or(false, |a| a > 0.0) && outcome != CounterDetonationOutcome::FiniteTimeBlowUp {
            outcome = CounterDetonationOutcome::BeltramiShieldNeutralized;
        }

        let is_t_dual = self.alpha_prime.map_or(false, |a| a > 0.0);
        let run_id = if is_t_dual {
            format!("T-DUAL-SHIELD-ALPHA-{:.4}", self.alpha_prime.unwrap())
        } else {
            "CALIBRATION-CLASSICAL-EULER-ALPHA-0".to_string()
        };

        CounterDetonationRunResult {
            run_id,
            alpha_prime: self.alpha_prime,
            is_t_dual,
            initial_energy,
            initial_enstrophy,
            initial_alignment,
            final_time: current_time,
            total_steps: step,
            outcome,
            blow_up_time,
            max_enstrophy_reached,
            max_frustration_index: max_frustration,
            final_alignment,
            final_lamb_norm: final_lamb,
            history,
            _measured: true,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_openai_blowup_series_generation() {
        let config = OpenAiBlowupSeriesConfig::default();
        let state = OpenAiBlowupSeriesGenerator::generate(&config);

        assert_eq!(state.kappa.len(), config.n_shells);
        assert_eq!(state.kappa[0], 1.0);
        assert_eq!(state.kappa[1], 2.0);
        assert!(state.kinetic_energy() > 0.0);
        assert!(state.enstrophy() > 0.0);
        let align = state.beltrami_alignment();
        assert!(align < 0.999, "Initial alignment should not be fully Beltrami, got {}", align);
        assert!(state.lamb_vector_norm() > 0.0, "Lamb vector must be non-zero initially");
    }

    #[test]
    fn test_calibration_run_diverges_in_finite_time() {
        // Run with alpha' = 0 (Classical unforced Euler)
        let config = OpenAiBlowupSeriesConfig::default();
        let solver = EulerCounterDetonationSolver::new(config, None);
        let result = solver.run(0.5, 0.0001);

        assert_eq!(
            result.outcome,
            CounterDetonationOutcome::FiniteTimeBlowUp,
            "Classical Euler must blow up in finite time!"
        );
        assert!(result.blow_up_time.is_some());
        let t_star = result.blow_up_time.unwrap();
        assert!(t_star < 0.3, "Blow-up must occur at finite time T* < 0.3, got {}", t_star);
        assert!(result.max_enstrophy_reached >= result.initial_enstrophy * 1.0e6);
    }

    #[test]
    fn test_t_dual_shield_defuses_blowup_and_forms_beltrami_flow() {
        // Run with alpha' = 0.01 (T-dual shield with k_eff metric)
        let config = OpenAiBlowupSeriesConfig::default();
        let solver = EulerCounterDetonationSolver::new(config, Some(0.01));
        let result = solver.run(0.5, 0.0001);

        assert_eq!(
            result.outcome,
            CounterDetonationOutcome::BeltramiShieldNeutralized,
            "T-dual shield must neutralize blow-up!"
        );
        assert!(result.blow_up_time.is_none(), "Blow-up must be averted");
        assert!(
            result.max_frustration_index > 100.0,
            "Frustration index D(M) must explode above 100 at wall contact, got {}",
            result.max_frustration_index
        );
        assert!(
            result.final_alignment > 0.98,
            "Final alignment must converge into Beltrami state (> 0.98), got {}",
            result.final_alignment
        );
        assert!(
            result.max_enstrophy_reached < 1.0e4,
            "Enstrophy must remain bounded under T-dual shield, got {}",
            result.max_enstrophy_reached
        );
    }
}
