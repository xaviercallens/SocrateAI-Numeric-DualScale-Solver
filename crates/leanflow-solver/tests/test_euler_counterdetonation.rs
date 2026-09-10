//! Integration tests for Euler Counter-Detonation Testbench.

use leanflow_solver::euler_counterdetonation::{
    CounterDetonationOutcome, EulerCounterDetonationSolver, OpenAiBlowupSeriesConfig,
    OpenAiBlowupSeriesGenerator,
};

#[test]
fn test_integration_openai_blowup_virus_synthesis() {
    let config = OpenAiBlowupSeriesConfig::default();
    let state = OpenAiBlowupSeriesGenerator::generate(&config);

    assert_eq!(state.kappa.len(), config.n_shells);
    assert_eq!(state.kappa[0], 1.0);
    assert!(state.kinetic_energy() > 0.0);
    assert!(state.enstrophy() > 0.0);
    // Non-Beltrami initial state
    assert!(state.beltrami_alignment() < 0.99);
    assert!(state.lamb_vector_norm() > 0.0);
}

#[test]
fn test_integration_calibration_classical_euler_divergence() {
    let config = OpenAiBlowupSeriesConfig::default();
    let solver = EulerCounterDetonationSolver::new(config, None);
    let result = solver.run(0.5, 0.0001);

    assert_eq!(result.outcome, CounterDetonationOutcome::FiniteTimeBlowUp);
    assert!(result.blow_up_time.is_some());
    let t_star = result.blow_up_time.unwrap();
    assert!(t_star > 0.05 && t_star < 0.3);
    assert!(result.max_enstrophy_reached > result.initial_enstrophy * 1.0e6);
}

#[test]
fn test_integration_t_dual_shield_frustration_and_beltrami_flow() {
    let config = OpenAiBlowupSeriesConfig::default();
    let solver = EulerCounterDetonationSolver::new(config, Some(0.01));
    let result = solver.run(0.5, 0.0001);

    assert_eq!(result.outcome, CounterDetonationOutcome::BeltramiShieldNeutralized);
    assert!(result.blow_up_time.is_none());
    assert!(result.max_frustration_index > 1000.0, "D(M) must explode above 1000 at wall contact, got {}", result.max_frustration_index);
    assert!(result.final_alignment > 0.98, "Flow must converge to Beltrami state, got {}", result.final_alignment);
    assert!(result.max_enstrophy_reached < 1.0e4);
}
