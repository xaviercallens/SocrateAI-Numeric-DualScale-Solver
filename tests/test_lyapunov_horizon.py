import os
import sys
import pytest
import numpy as np

# Ensure leanflow_antigravity can be imported
WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ANTIGRAVITY_DIR = os.path.join(WORKSPACE_ROOT, "leanflow_antigravity")
if ANTIGRAVITY_DIR not in sys.path:
    sys.path.insert(0, ANTIGRAVITY_DIR)

import workflow

def test_lyapunov_horizon(monkeypatch):
    """
    Test Step 2: The Long-Horizon Lyapunov Test
    Runs 5000 continuous cycles to check for numerical instability.
    Asserts the test fails if any gradient norm evaluates to NaN or Infinity, 
    or if energy monotonically increases (blows up).
    """
    n_cycles = 5000

    dataset_path = os.path.join(WORKSPACE_ROOT, "leanflow_antigravity", "data", "iter_m2n1_grid.safetensors")
    if not os.path.exists(dataset_path):
        dataset_path = os.path.join(WORKSPACE_ROOT, "leanflow_antigravity", "data", "jhtdb_grid.safetensors")

    kinetic_energies = []
    lss_gradients = []
    
    original_step = workflow.execute_cycle_step
    
    def tracked_step(*args, **kwargs):
        record = original_step(*args, **kwargs)
        kinetic_energies.append(record["kinetic_energy"])
        lss_gradients.append(record["lss_gradient_norm"])
        
        # Check for NaN or Inf in real time
        assert not np.isnan(record["lss_gradient_norm"]), f"LSS gradient norm became NaN at cycle {record['cycle']}"
        assert not np.isinf(record["lss_gradient_norm"]), f"LSS gradient norm became Infinity at cycle {record['cycle']}"
        
        return record
        
    monkeypatch.setattr(workflow, "execute_cycle_step", tracked_step)

    # We use a very small subset to make 5000 cycles fast enough for the test runner.
    workflow.run_multi_cycle_workflow(
        n_cycles=n_cycles,
        filepath=dataset_path,
        exit_on_fail=False,
        subset_dof=100
    )

    # Check for energy blowup (monotonic increase over the last N steps)
    if len(kinetic_energies) > 10:
        recent_energies = kinetic_energies[-10:]
        is_monotonic_increase = all(recent_energies[i] < recent_energies[i+1] for i in range(len(recent_energies)-1))
        assert not is_monotonic_increase, "Kinetic energy is monotonically increasing (blowup detected)."

