#!/usr/bin/env python3
"""
Download and materialize local reference datasets for the Phase 6b Industrial PoC:
1. Bioreactor oxygen mass transfer (kLa) profiles
2. Transonic NACA-0012 shock buffet oscillation time histories
3. High-Reynolds pipeline turbulent drag reduction curves
"""

import sys
import os
import json
from pathlib import Path
import numpy as np

# Ensure project src is on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from dualscale_solver.numeric.industrial_poc import (
    simulate_transonic_buffet_damping,
    simulate_pipeline_drag_reduction,
)
from dualscale_solver.runtimes.embedded_target import (
    simulate_bioreactor_kla_transfer,
)


def main():
    repo_root = Path(__file__).parent.parent
    data_dir = repo_root / "data" / "benchmarks"
    data_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print(" MATERIALIZING PHASE 6B INDUSTRIAL POC REFERENCE DATASETS")
    print("=" * 80)

    # 1. Bioreactor Oxygen Transfer Dataset
    print("\n[1/3] Generating Bioreactor k_L a Mass Transfer Reference Data...")
    bioreactor_data = simulate_bioreactor_kla_transfer(n_steps=2000, kla_target=115.89)
    bioreactor_path = data_dir / "industrial_bioreactor_kla_reference.json"
    with open(bioreactor_path, "w") as f:
        json.dump(bioreactor_data, f, indent=2)
    print(f"  [✓] Bioreactor reference saved: {bioreactor_path}")
    print(f"      kLa: {bioreactor_data['kla_achieved']:.2f}/s (Yield multiplier: {bioreactor_data['yield_multiplier']:.2f}x)")

    # 2. Transonic Buffet Oscillation Dataset
    print("\n[2/3] Generating Transonic Shock Buffet Damping Reference Data...")
    buffet_data = simulate_transonic_buffet_damping(n_steps=2000, mach_inf=0.75, reynolds=1e6)
    buffet_path = data_dir / "industrial_transonic_buffet_reference.json"
    with open(buffet_path, "w") as f:
        json.dump(buffet_data, f, indent=2)
    print(f"  [✓] Transonic buffet reference saved: {buffet_path}")
    print(f"      Buffet variance reduction: {buffet_data['amplitude_reduction_fraction']*100:.2f}%")

    # 3. High-Reynolds Pipeline Friction Dataset
    print("\n[3/3] Generating High-Reynolds Pipeline Drag Reduction Reference Data...")
    pipe_data = simulate_pipeline_drag_reduction(reynolds_d=1e5)
    pipe_path = data_dir / "industrial_pipeline_drag_reference.json"
    with open(pipe_path, "w") as f:
        json.dump(pipe_data, f, indent=2)
    print(f"  [✓] Pipeline drag reference saved: {pipe_path}")
    print(f"      Drag reduction: {pipe_data['drag_reduction_fraction']*100:.2f}%")

    print("\n" + "=" * 80)
    print(" 🎉 ALL INDUSTRIAL POC REFERENCE DATASETS SUCCESSFULLY MATERIALIZED")
    print("=" * 80)


if __name__ == "__main__":
    main()
