import os
import sys
import pytest
from unittest import mock

# Ensure leanflow_antigravity can be imported
WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ANTIGRAVITY_DIR = os.path.join(WORKSPACE_ROOT, "leanflow_antigravity")
if ANTIGRAVITY_DIR not in sys.path:
    sys.path.insert(0, ANTIGRAVITY_DIR)

import workflow

def test_anisotropy_wall(monkeypatch):
    """
    Test Step 1: The Anisotropy Wall (ITER Tearing Modes)
    Runs 50 cycles with highly anisotropic thermal conductivity ratio (10^8).
    Asserts that the maximum FGMRES iterations required per step remains <= 10.
    """
    anisotropy_ratio = 1e8
    n_cycles = 50

    # Ensure the test doesn't crash if the dataset isn't downloaded yet. We use the existing JHTDB file if so.
    dataset_path = os.path.join(WORKSPACE_ROOT, "leanflow_antigravity", "data", "iter_m2n1_grid.safetensors")
    if not os.path.exists(dataset_path):
        dataset_path = os.path.join(WORKSPACE_ROOT, "leanflow_antigravity", "data", "jhtdb_grid.safetensors")

    # Spy on the execute_cycle_step to extract fgmres_iterations across the cycles
    iterations_list = []
    original_step = workflow.execute_cycle_step
    
    def tracked_step(*args, **kwargs):
        record = original_step(*args, **kwargs)
        iterations_list.append(record["fgmres_iterations"])
        return record
        
    monkeypatch.setattr(workflow, "execute_cycle_step", tracked_step)

    # Execute workflow with the requested anisotropy_ratio
    summary = workflow.run_multi_cycle_workflow(
        n_cycles=n_cycles,
        filepath=dataset_path,
        exit_on_fail=False,
        subset_dof=1000,
        anisotropy_ratio=anisotropy_ratio
    )
    
    max_iterations = max(iterations_list) if iterations_list else 0
    print(f"Max FGMRES Iterations: {max_iterations}")
    assert max_iterations <= 10, f"FGMRES iterations {max_iterations} exceeded the threshold of 10."
