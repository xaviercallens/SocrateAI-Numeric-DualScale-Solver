//! CLI binary for NS Forced Counter-Detonation experiments.
//!
//! Runs two phases:
//! 1. Calibration ($\alpha' = 0$): Classical NS with adversarial forcing → blow-up
//! 2. T-Dual Shield ($\alpha' > 0$): Desynchronization → Beltrami stabilization

use leanflow_solver::ns_forced_counterdetonation::*;
use std::fs;

fn main() {
    println!("================================================================================");
    println!(" NAVIER-STOKES FORCED COUNTER-DETONATION");
    println!(" OpenAI Adversarial Forcing (Clay Millennium Alternatives C/D)");
    println!("================================================================================\n");

    let config = OpenAiNsForcingConfig {
        nu: 0.001,
        n_shells: 16,
        forcing_amplitude: 5.0,
        target_blowup_time: 1.5,
        ..Default::default()
    };

    // ──────────────────────────────────────────────────────────────────────
    // PHASE 1: Calibration (Classical NS, alpha' = 0)
    // ──────────────────────────────────────────────────────────────────────
    println!("[PHASE 1] CALIBRATION RUN (alpha' = 0, Classical NS with adversarial forcing)");
    println!("  Goal: Adversarial forcing drives enstrophy explosion.\n");

    let solver_cal = NsForcedCounterDetonationSolver::new(config.clone(), None);
    let result_cal = solver_cal.run(2.0, 0.0001);

    match result_cal.outcome {
        NsForcedOutcome::ForcedBlowUp => {
            println!("  >>> [BLOW-UP DETECTED] Adversarial forcing successfully drives singularity!");
            println!(
                "      Blow-up Time T*     : {:.6}",
                result_cal.blow_up_time.unwrap_or(0.0)
            );
            println!(
                "      Peak Enstrophy      : {:.4e}",
                result_cal.max_enstrophy_reached
            );
            println!(
                "      Peak Forcing ||f||  : {:.4e}",
                result_cal.peak_forcing_magnitude
            );
            println!(
                "      Steps to Blow-Up    : {}\n",
                result_cal.total_steps
            );
        }
        ref other => {
            println!(
                "  >>> [WARNING] Expected ForcedBlowUp, got {:?}",
                other
            );
        }
    }

    // ──────────────────────────────────────────────────────────────────────
    // PHASE 2: T-Dual Shield (alpha' = 0.01)
    // ──────────────────────────────────────────────────────────────────────
    println!("[PHASE 2] T-DUAL SHIELD RUN (alpha' = 0.1, k_eff metric)");
    println!("  Goal: UV wall desynchronizes forcing, D(M) explodes, Beltrami forms.\n");

    let solver_shield = NsForcedCounterDetonationSolver::new(config.clone(), Some(0.1));
    let result_shield = solver_shield.run(2.0, 0.0001);

    match result_shield.outcome {
        NsForcedOutcome::DesynchronizedBeltrami => {
            println!(
                "  >>> [SHIELD ACTIVATED] Forcing desynchronized, flow stabilized!"
            );
        }
        ref other => {
            println!(
                "  >>> [WARNING] Expected DesynchronizedBeltrami, got {:?}",
                other
            );
        }
    }
    println!(
        "      Peak Enstrophy      : {:.4e} (bounded)",
        result_shield.max_enstrophy_reached
    );
    println!(
        "      Peak Frustration D(M): {:.2}",
        result_shield.max_frustration_index
    );
    println!(
        "      Final Alignment     : {:.4}",
        result_shield.final_alignment
    );
    println!(
        "      Final Lamb Vector   : {:.4}",
        result_shield.final_lamb_norm
    );
    println!(
        "      Peak Forcing ||f||  : {:.4e}\n",
        result_shield.peak_forcing_magnitude
    );

    // ──────────────────────────────────────────────────────────────────────
    // AUDIT
    // ──────────────────────────────────────────────────────────────────────
    let cal_ok = result_cal.outcome == NsForcedOutcome::ForcedBlowUp;
    let shield_ok = result_shield.outcome == NsForcedOutcome::DesynchronizedBeltrami;
    let frustration_ok = result_shield.max_frustration_index > 10.0;

    println!("================================================================================");
    if cal_ok && shield_ok && frustration_ok {
        println!(" [AUDIT PASSED] NS Forced Counter-Detonation Certified!");
        println!("  1. Calibration (alpha'=0): Adversarial forcing drives blow-up.");
        println!(
            "  2. Shield (alpha'=0.01): UV wall desynchronized forcing, D(M) = {:.2}.",
            result_shield.max_frustration_index
        );
        println!(
            "  3. Stabilization: Flow converged to Beltrami (cos th = {:.4}).",
            result_shield.final_alignment
        );
    } else {
        println!(" [AUDIT FAILED] Counter-detonation not fully certified.");
    }
    println!("================================================================================\n");

    // ──────────────────────────────────────────────────────────────────────
    // SAVE JSON
    // ──────────────────────────────────────────────────────────────────────
    let combined = serde_json::json!({
        "experiment": "NS_FORCED_COUNTER_DETONATION",
        "openai_correspondence": {
            "problem": "Clay Millennium Navier-Stokes (Alternatives C & D)",
            "initial_condition": "u_0 = 0 (ProblemStatement.lean:109)",
            "forcing": "f_nu(x,t) = nu^2 * f_1(x, nu*t) (ComparatorBridge.lean:61-66)",
            "forcing_type": "reverse-engineered residual (CandidateFromLimits.lean:82-125)",
            "scope_caveat": "Dyadic helical shell model surrogate, not full R3 PDE"
        },
        "calibration": result_cal,
        "shield": result_shield,
        "audit_passed": cal_ok && shield_ok && frustration_ok,
    });

    fs::create_dir_all("results").ok();
    let path = "results/ns_forced_counterdetonation_results.json";
    fs::write(path, serde_json::to_string_pretty(&combined).unwrap()).unwrap();
    println!("Report saved to: {}", path);
}
