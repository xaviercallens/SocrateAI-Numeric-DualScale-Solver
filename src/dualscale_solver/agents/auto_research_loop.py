import time
import asyncio
import inspect
from typing import Dict, Any, Callable, Optional
import logging

logger = logging.getLogger(__name__)


class KarpathyAutoResearchLoop:
    """
    Karpathy Ratchet Auto-Research Loop
    ====================================
    5-step cycle: PROPOSE → EVALUATE → RATCHET → VERIFY → REFLECT

    The ratchet mechanism guarantees monotonic progress:
    - If fitness improves: new parameters become the baseline ("Git Commit")
    - If fitness regresses: changes are instantly discarded ("Git Revert")

    Dynamic Temperature Breaker:
    - If the last `stagnation_window` iterations all failed to improve fitness,
      a `stuck_in_local_minimum` flag is injected into history so the hypothesis
      generator can make a radical mutation instead of micro-adjustments.
    """

    def __init__(
        self,
        problem_name: str,
        hypothesis_generator: Callable,
        execution_engine: Callable,
        verification_engine: Callable,
        max_iterations: int = 15,
        stagnation_window: int = 3,
    ):
        self.problem_name = problem_name
        self.hypothesis_generator = hypothesis_generator
        self.execution_engine = execution_engine
        self.verification_engine = verification_engine
        self.max_iterations = max_iterations
        self.stagnation_window = stagnation_window
        self.history: list = []
        self.best_fitness: float = -float("inf")
        self.best_params: Any = None
        self.best_sim_result: Optional[Dict[str, Any]] = None
        self.stagnation_count: int = 0

    async def run(self) -> Dict[str, Any]:
        logger.info(f"🚀 Starting Karpathy Ratchet Loop: {self.problem_name}")

        certified_result = None

        for iteration in range(1, self.max_iterations + 1):
            logger.info(f"[{self.problem_name}] ─── Iteration {iteration}/{self.max_iterations} ───")

            # ── 1. PROPOSE ──────────────────────────────────────────
            # Inject stagnation flag so generators can detect local minima
            is_stuck = self.stagnation_count >= self.stagnation_window
            if is_stuck:
                logger.warning(
                    f"[{self.problem_name}] 🌡️ TEMPERATURE BREAKER: "
                    f"{self.stagnation_count} stagnant iterations. Requesting radical mutation."
                )

            # Pass enriched history to hypothesis generator
            enriched_history = self._build_enriched_history(is_stuck)
            hypothesis = self.hypothesis_generator(enriched_history)
            if inspect.isawaitable(hypothesis):
                hypothesis = await hypothesis

            reasoning = ""
            if isinstance(hypothesis, dict) and "reasoning" in hypothesis:
                reasoning = hypothesis.pop("reasoning", "")
                logger.info(f"[{self.problem_name}] 🧠 Reasoning: {reasoning}")
            logger.info(f"[{self.problem_name}] ⚙️  Proposed: {hypothesis}")

            # ── 2. EVALUATE (must complete ≤ 100ms for ROM) ─────────
            t0 = time.perf_counter()
            sim_result = self.execution_engine(hypothesis)
            if inspect.isawaitable(sim_result):
                sim_result = await sim_result
            eval_time_ms = round((time.perf_counter() - t0) * 1000, 2)

            fitness = sim_result.get("fitness_score", 0.0)
            diagnostic = sim_result.get("diagnostic", "")
            logger.info(
                f"[{self.problem_name}] 📊 Fitness={fitness:.4f} | "
                f"⏱️ {eval_time_ms}ms | 🔬 {diagnostic[:120]}"
            )

            # ── 3. RATCHET (Keep or Revert) ─────────────────────────
            if fitness > self.best_fitness:
                self.best_fitness = fitness
                self.best_params = hypothesis
                self.best_sim_result = sim_result
                self.stagnation_count = 0
                ratchet_decision = "KEEP"
                logger.info(f"[{self.problem_name}] ✅ NEW BASELINE (fitness={fitness:.4f})")
            else:
                self.stagnation_count += 1
                ratchet_decision = "REVERT"
                logger.info(
                    f"[{self.problem_name}] ❌ REGRESSION (fitness={fitness:.4f} "
                    f"< best={self.best_fitness:.4f}). Discarding."
                )

            # ── 4. VERIFY (hard constraints) ────────────────────────
            # Always verify against the BEST sim_result (the ratchet baseline)
            verify_target = self.best_sim_result if self.best_sim_result else sim_result
            verification = self.verification_engine(verify_target)
            if inspect.isawaitable(verification):
                verification = await verification
            logger.info(f"[{self.problem_name}] 🔒 Verification: {verification.get('status', 'UNKNOWN')}")

            # ── 5. REFLECT ──────────────────────────────────────────
            self.history.append({
                "iteration": iteration,
                "hypothesis": hypothesis,
                "reasoning": reasoning,
                "sim_result": sim_result,
                "fitness_score": fitness,
                "diagnostic": diagnostic,
                "ratchet_decision": ratchet_decision,
                "eval_time_ms": eval_time_ms,
                "best_fitness": self.best_fitness,
                "verification": verification,
                "stuck_in_local_minimum": is_stuck,
            })

            # ── HALTING CONDITION ───────────────────────────────────
            if verification["status"] == "CERTIFIED":
                logger.info(
                    f"[{self.problem_name}] 🏆 CERTIFIED at iteration {iteration}! "
                    f"Fitness={self.best_fitness:.4f}"
                )
                certified_result = verification
                break

        # Final report
        if not certified_result:
            logger.warning(
                f"[{self.problem_name}] ⚠️ Failed to converge within "
                f"{self.max_iterations} iterations (best_fitness={self.best_fitness:.4f})."
            )
            certified_result = (
                self.history[-1]["verification"] if self.history else {"status": "FAILED"}
            )

        return {
            "problem_name": self.problem_name,
            "iterations_run": len(self.history),
            "final_status": certified_result["status"],
            "best_result": certified_result,
            "best_fitness": self.best_fitness,
            "best_params": self.best_params,
            "history": self.history,
        }

    def _build_enriched_history(self, is_stuck: bool) -> list:
        """Build history view for hypothesis generator with stagnation flag."""
        if not self.history:
            return []
        # Return the raw history entries — generators read sim_result, hypothesis, etc.
        # The last entry carries the stuck flag for the generator to detect
        enriched = list(self.history)
        if enriched:
            # Inject the live stagnation signal into the last history entry
            enriched[-1] = {**enriched[-1], "stuck_in_local_minimum": is_stuck}
        return enriched
