import asyncio
import json
import time
from pathlib import Path
import logging

from dualscale_solver.agents.auto_research_loop import KarpathyAutoResearchLoop
from dualscale_solver.numeric.phase12_autoresearch_problems import (
    AerospaceScramjetMitigation,
    MedicalVADRotorDynamics,
    HyperscaleWindFarmSteering,
    AutomotiveBTMSMicroChannels,
    NuclearTokamakDisruption,
    generate_phase12_certificate,
    solve_scramjet_sbli_mitigation,
    solve_medical_vad_dynamics,
    solve_wind_farm_steering,
    solve_btms_microchannels,
    solve_tokamak_disruption,
    evaluate_4_performance_gains,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Bisection-guided hypothesis generators (FIX-05)
# Each generator reads the last sim_result to steer the search direction.
# ---------------------------------------------------------------------------

def _aero_hypothesis(hist: list) -> dict:
    """Bisection on spectral_filter_coef with Chain-of-Thought reasoning."""
    if not hist:
        return {"spectral_filter_coef": 2.0,
                "reasoning": "Initial probe: moderate spectral filter strength for SBLI control."}

    is_stuck = hist[-1].get("stuck_in_local_minimum", False)
    last_sim = hist[-1]["sim_result"]
    prev_coef = hist[-1]["hypothesis"].get("spectral_filter_coef", 2.0)

    if is_stuck:
        delta = 2.0
        reasoning = (f"STUCK IN LOCAL MINIMUM. Last {len(hist)} iterations failed to improve. "
                     f"Applying radical +2.0 spectral filter jump from {prev_coef:.1f}.")
    elif last_sim.get("sbli_horizon", 0) < 5.0:
        delta = 0.6
        reasoning = (f"Horizon {last_sim.get('sbli_horizon', 0):.1f}ms < 5.0ms target. "
                     f"Enstrophy={last_sim.get('enstrophy', 0):.1f} too high. "
                     f"Increasing filter coef by 0.6 to strengthen biharmonic dissipation.")
    elif not last_sim.get("unstart", False):
        delta = 0.4
        reasoning = (f"Horizon OK but unstart not prevented. "
                     f"Increasing filter coef by 0.4 for stronger shock stabilisation.")
    else:
        delta = 0.1
        reasoning = (f"Nearly converged (horizon={last_sim.get('sbli_horizon', 0):.1f}ms, unstart prevented). "
                     f"Fine-tuning with +0.1.")

    return {"spectral_filter_coef": prev_coef + delta, "reasoning": reasoning}


def _med_hypothesis(hist: list) -> dict:
    """Bisection on tensor_stiffness with Chain-of-Thought reasoning."""
    if not hist:
        return {"tensor_stiffness": 2.5,
                "reasoning": "Initial probe: moderate tensor stiffness for VAD shear control."}

    is_stuck = hist[-1].get("stuck_in_local_minimum", False)
    last_sim = hist[-1]["sim_result"]
    prev_stiff = hist[-1]["hypothesis"].get("tensor_stiffness", 2.5)
    shear = last_sim.get("shear", 200.0)

    if is_stuck:
        delta = 3.0
        reasoning = (f"STUCK IN LOCAL MINIMUM. Shear={shear:.1f} Pa not improving. "
                     f"Radical jump: +3.0 tensor stiffness.")
    elif shear >= 150.0:
        delta = max(0.5, (shear - 150.0) / 50.0)
        reasoning = (f"Shear {shear:.1f} Pa ≥ 150 Pa limit. Enstrophy={last_sim.get('enstrophy', 0):.1f}. "
                     f"Increasing stiffness by {delta:.1f} to strengthen regularisation.")
    else:
        delta = 0.1
        reasoning = (f"Shear {shear:.1f} Pa below limit. Fine-tuning stiffness for "
                     f"marginal hemolysis reduction improvement.")

    return {"tensor_stiffness": prev_stiff + delta, "reasoning": reasoning}


def _wind_hypothesis(hist: list) -> list:
    """Bisection on yaw angle with Chain-of-Thought reasoning.
    Note: returns list (yaw_matrix format). Reasoning is logged by the loop via sim_result."""
    if not hist:
        return [4.5]

    is_stuck = hist[-1].get("stuck_in_local_minimum", False)
    last_sim = hist[-1]["sim_result"]
    prev_yaw = hist[-1]["hypothesis"][0] if hist[-1]["hypothesis"] else 4.5

    if is_stuck:
        delta = 4.0
    elif last_sim.get("yield", 0) < 15.0:
        delta = 1.2
    elif last_sim.get("turbines", 0) < 1000:
        delta = 1.0
    else:
        delta = 0.1

    return [prev_yaw + delta]


def _auto_hypothesis(hist: list) -> float:
    """Bisection on fractal_dim with temperature breaker."""
    if not hist:
        return 2.5

    is_stuck = hist[-1].get("stuck_in_local_minimum", False)
    last_sim = hist[-1]["sim_result"]
    prev_dim = hist[-1]["hypothesis"] if isinstance(hist[-1]["hypothesis"], float) else 2.5
    heat = last_sim.get("heat", 0.0)

    if is_stuck:
        delta = 3.0
    elif heat < 30.0:
        delta = max(0.5, (30.0 - heat) / 15.0)
    else:
        delta = 0.1

    return prev_dim + delta


def _nuke_hypothesis(hist: list) -> dict:
    """Bisection on holographic_threshold with Chain-of-Thought reasoning."""
    if not hist:
        return {"holographic_threshold": 1.0,
                "reasoning": "Initial probe: holographic threshold 1.0 for MHD confinement."}

    is_stuck = hist[-1].get("stuck_in_local_minimum", False)
    last_sim = hist[-1]["sim_result"]
    prev_thresh = hist[-1]["hypothesis"].get("holographic_threshold", 1.0)

    if is_stuck:
        delta = 3.0
        reasoning = (f"STUCK IN LOCAL MINIMUM. Applying radical +3.0 threshold jump. "
                     f"Current R_eff={last_sim.get('r_eff', 0):.3f} insufficient.")
    elif not last_sim.get("holo", False):
        delta = 0.8
        reasoning = (f"Holographic bound violated. Enstrophy={last_sim.get('enstrophy', 0):.1f} "
                     f"exceeds R_eff² bound. Increasing threshold by 0.8.")
    elif last_sim.get("horizon", 0) < 10.0:
        delta = 0.4
        reasoning = (f"Holographic bound holds but horizon={last_sim.get('horizon', 0):.1f}ms < 10ms. "
                     f"Increasing threshold by 0.4 to extend prediction window.")
    else:
        delta = 0.1
        reasoning = (f"Nearly converged. Horizon={last_sim.get('horizon', 0):.1f}ms, β stable. "
                     f"Fine-tuning with +0.1.")

    return {"holographic_threshold": prev_thresh + delta, "reasoning": reasoning}


# ---------------------------------------------------------------------------
# Verification factories (FIX-06: delegate to verify_hXX())
# ---------------------------------------------------------------------------

def _aero_verify(r: dict) -> dict:
    model = AerospaceScramjetMitigation(
        status="CERTIFIED" if r["sbli_horizon"] >= 5.0 and r["unstart"] and r["latency"] <= 1.0 else "FAILED",
        sbli_prediction_horizon_ms=r["sbli_horizon"],
        unstart_prevented=r["unstart"],
        actuation_latency_ms=r["latency"],
    )
    # Single source of truth: status derived from verify_h66()
    if model.status == "CERTIFIED" and not model.verify_h66():
        model = model.model_copy(update={"status": "FAILED"})
    return model.model_dump(by_alias=True)


def _med_verify(r: dict) -> dict:
    model = MedicalVADRotorDynamics(
        status="CERTIFIED" if r["shear"] < 150.0 and r["zones"] == 0 and r["reduction"] > 45.0 else "FAILED",
        max_shear_stress_pa=r["shear"],
        thrombosis_stagnation_zones=r["zones"],
        hemolysis_index_reduction_pct=r["reduction"],
    )
    if model.status == "CERTIFIED" and not model.verify_h67():
        model = model.model_copy(update={"status": "FAILED"})
    return model.model_dump(by_alias=True)


def _wind_verify(r: dict) -> dict:
    model = HyperscaleWindFarmSteering(
        status="CERTIFIED" if r["turbines"] >= 1000 and r["yaw"] > 5.0 and r["yield"] >= 15.0 else "FAILED",
        turbines_simulated=r["turbines"],
        wake_deflection_angle_deg=r["yaw"],
        power_yield_increase_pct=r["yield"],
    )
    if model.status == "CERTIFIED" and not model.verify_h68():
        model = model.model_copy(update={"status": "FAILED"})
    return model.model_dump(by_alias=True)


def _auto_verify(r: dict) -> dict:
    model = AutomotiveBTMSMicroChannels(
        status="CERTIFIED" if r["gens"] >= 3 and r["drop"] >= 20.0 and r["heat"] >= 30.0 else "FAILED",
        fractal_generations=r["gens"],
        pressure_drop_reduction_pct=r["drop"],
        heat_transfer_increase_pct=r["heat"],
    )
    if model.status == "CERTIFIED" and not model.verify_h69():
        model = model.model_copy(update={"status": "FAILED"})
    return model.model_dump(by_alias=True)


def _nuke_verify(r: dict) -> dict:
    model = NuclearTokamakDisruption(
        status="CERTIFIED" if r["beta"] > 0.05 and r["holo"] and r["horizon"] >= 10.0 else "FAILED",
        plasma_beta=r["beta"],
        holographic_bound_satisfied=r["holo"],
        disruption_prediction_horizon_ms=r["horizon"],
    )
    if model.status == "CERTIFIED" and not model.verify_h70():
        model = model.model_copy(update={"status": "FAILED"})
    return model.model_dump(by_alias=True)


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

class Phase12AutoResearchOrchestrator:
    """Orchestrates the 5 industrial Auto-Research loops in parallel."""

    def __init__(self):
        logger.info("Initializing Phase 12 Auto-Research Workflow Orchestrator")

    async def execute_workflow(self) -> dict:
        t_start = time.perf_counter()

        # Build loops
        aero_loop = KarpathyAutoResearchLoop(
            "Aerospace Scramjet Mitigation",
            hypothesis_generator=_aero_hypothesis,
            execution_engine=solve_scramjet_sbli_mitigation,
            verification_engine=_aero_verify,
        )
        med_loop = KarpathyAutoResearchLoop(
            "Medical VAD Rotor Dynamics",
            hypothesis_generator=_med_hypothesis,
            execution_engine=solve_medical_vad_dynamics,
            verification_engine=_med_verify,
        )
        wind_loop = KarpathyAutoResearchLoop(
            "Hyperscale Wind Farm Steering",
            hypothesis_generator=_wind_hypothesis,
            execution_engine=solve_wind_farm_steering,
            verification_engine=_wind_verify,
        )
        auto_loop = KarpathyAutoResearchLoop(
            "Automotive BTMS Micro-Channels",
            hypothesis_generator=_auto_hypothesis,
            execution_engine=solve_btms_microchannels,
            verification_engine=_auto_verify,
        )
        nuke_loop = KarpathyAutoResearchLoop(
            "Nuclear Tokamak Disruption",
            hypothesis_generator=_nuke_hypothesis,
            execution_engine=solve_tokamak_disruption,
            verification_engine=_nuke_verify,
        )

        # FIX-04: Parallelize all loops with asyncio.gather()
        aero_res, med_res, wind_res, auto_res, nuke_res = await asyncio.gather(
            aero_loop.run(), med_loop.run(), wind_loop.run(),
            auto_loop.run(), nuke_loop.run()
        )

        results = {
            "aerospace":  aero_res,
            "medical":    med_res,
            "wind":       wind_res,
            "automotive": auto_res,
            "nuclear":    nuke_res,
        }

        wall_time_s = round(time.perf_counter() - t_start, 3)
        logger.info(f"All 5 loops completed in {wall_time_s}s (parallel gather)")

        # Collect measured metrics for traceable certificate (FIX-03)
        measured_metrics = {
            name: loop_res.get("best_result", {})
            for name, loop_res in results.items()
        }
        measured_metrics["wall_time_s"] = wall_time_s

        gains_summary = evaluate_4_performance_gains(results)

        h66 = results["aerospace"]["final_status"] == "CERTIFIED"
        h67 = results["medical"]["final_status"] == "CERTIFIED"
        h68 = results["wind"]["final_status"] == "CERTIFIED"
        h69 = results["automotive"]["final_status"] == "CERTIFIED"
        h70 = results["nuclear"]["final_status"] == "CERTIFIED"

        cert = generate_phase12_certificate(h66, h67, h68, h69, h70, measured_metrics)

        report = {
            "certificate":       cert.model_dump(by_alias=True),
            "performance_gains": gains_summary,
            "loops":             results,
            "wall_time_s":       wall_time_s,
        }

        out_path = Path("data/output/cert_phase12_workflow.json")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w") as f:
            json.dump(report, f, indent=2)

        return report


def run_phase12_pipeline() -> dict:
    orchestrator = Phase12AutoResearchOrchestrator()
    return asyncio.run(orchestrator.execute_workflow())
