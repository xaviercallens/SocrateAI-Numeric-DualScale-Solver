#!/usr/bin/env python3
"""
Monotonic Greedy Search Loop Runner (`loop.py`)
==============================================
Definitive Monotonic Greedy Line Search with Backtracking architecture for LeanFlow Phase 12.

5-Step Cycle per problem:
  1. PROPOSE  — LLM-style hypothesis generator with Chain-of-Thought reasoning
  2. EVALUATE — LeanFlow spectral ROM executes physics in ≤ 100ms
  3. RATCHET  — If fitness improves: KEEP (Git Commit). If not: REVERT (Git Revert)
  4. VERIFY   — Hard constraint gate (Pydantic invariants H66–H70)
  5. REFLECT  — Append diagnostics + ratchet decision to history

5 Industrial Use Cases:
  1. Aerospace Hypersonic Scramjet Unstart Mitigation (H66)
  2. Medical Magnetically Levitated VAD Rotor Dynamics (H67)
  3. Hyperscale Offshore Wind Farm Yaw Steering (H68)
  4. Automotive BTMS Micro-Channel Cooling (H69)
  5. Nuclear Tokamak Plasma Disruption Avoidance (H70)
"""

import os
import sys
import json
import logging
from pathlib import Path

# Ensure src/ is on PYTHONPATH
repo_root = Path(__file__).resolve().parent
src_path = repo_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Configure process-level logging (entry-point only — never in library modules)
logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from dualscale_solver.agents.phase12_workflow_orchestrator import run_phase12_pipeline

console = Console()


def _print_loop_history(loop_name: str, loop_res: dict):
    """Print per-iteration ratchet trace for a single loop."""
    history = loop_res.get("history", [])
    if not history:
        return

    table = Table(
        title=f"🔄 {loop_name}",
        show_header=True,
        header_style="bold cyan",
        border_style="dim",
    )
    table.add_column("Iter", justify="center", width=4)
    table.add_column("Fitness", justify="right", width=10)
    table.add_column("Best", justify="right", width=10)
    table.add_column("Ratchet", justify="center", width=8)
    table.add_column("Time", justify="right", width=8)
    table.add_column("Diagnostic", max_width=60, no_wrap=True)

    for entry in history:
        ratchet = entry.get("ratchet_decision", "?")
        ratchet_styled = (
            f"[bold green]✅ KEEP[/]" if ratchet == "KEEP"
            else f"[bold red]❌ REVERT[/]"
        )
        diag = entry.get("diagnostic", "")
        # Truncate diagnostic for table display
        diag_short = diag[:58] + "…" if len(diag) > 60 else diag

        table.add_row(
            str(entry["iteration"]),
            f"{entry.get('fitness_score', 0):.2f}",
            f"{entry.get('best_fitness', 0):.2f}",
            ratchet_styled,
            f"{entry.get('eval_time_ms', 0):.1f}ms",
            diag_short,
        )

    console.print(table)
    console.print()


def main():
    console.print(Panel.fit(
        "[bold white]SOCRATEAI LEANFLOW — MONOTONIC GREEDY SEARCH LOOP[/]\n"
        "[dim]PROPOSE → EVALUATE → RATCHET → VERIFY → REFLECT[/]",
        border_style="bright_cyan",
    ))
    console.print()

    report = run_phase12_pipeline()
    cert = report["certificate"]
    gains = report.get("performance_gains", {}).get("gains", {})

    # ── Per-Loop Ratchet Traces ──────────────────────────────
    console.print(Panel("[bold]📊 Ratchet Iteration Traces[/]", border_style="dim"))
    for loop_name, loop_res in report["loops"].items():
        _print_loop_history(loop_name.upper(), loop_res)

    # ── Certificate Summary ──────────────────────────────────
    status_color = "green" if cert["overall_status"] == "CERTIFIED" else "red"
    console.print(Panel.fit(
        f"[bold {status_color}]{cert['overall_status']}[/]\n\n"
        f"Certificate ID : [cyan]{cert['certificate_id']}[/]\n"
        f"SHA-256 Hash   : [dim]{cert['sha256_hash']}[/]\n"
        f"Wall Time      : [yellow]{report.get('wall_time_s', '?')}s[/]",
        title="🎖️  CERTIFICATION",
        border_style=status_color,
    ))
    console.print()

    # ── 4 Key Performance Gains ──────────────────────────────
    gains_table = Table(
        title="🎯 4 KEY PERFORMANCE GAINS",
        show_header=True,
        header_style="bold magenta",
    )
    gains_table.add_column("Gain", max_width=35)
    gains_table.add_column("Measured", max_width=40)
    gains_table.add_column("Baseline", max_width=20)
    gains_table.add_column("Result", max_width=25)
    gains_table.add_column("Status", justify="center", width=8)

    for gain_id, gain_info in gains.items():
        passed = gain_info.get("passed", False)
        status_icon = "[bold green]✅[/]" if passed else "[bold red]❌[/]"
        gains_table.add_row(
            gain_info.get("name", gain_id),
            str(gain_info.get("measured_value", "")),
            str(gain_info.get("baseline_value", "")),
            str(gain_info.get("gain_achieved", "")),
            status_icon,
        )

    console.print(gains_table)
    console.print()

    # ── Save report ──────────────────────────────────────────
    output_dir = repo_root / "data" / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    out_file = output_dir / "cert_phase12_workflow.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    console.print(f"[dim]Report saved to: {out_file.resolve()}[/]")

    if cert["overall_status"] == "CERTIFIED":
        console.print(Panel.fit(
            "[bold green]🏆 ALL 5 INDUSTRIAL USE CASES CONVERGED & 4 GAINS FULLY CERTIFIED![/]",
            border_style="green",
        ))
        sys.exit(0)
    else:
        console.print(Panel.fit(
            "[bold red]❌ AUTO-RESEARCH LOOP FAILED CERTIFICATION.[/]",
            border_style="red",
        ))
        sys.exit(1)


if __name__ == "__main__":
    main()
