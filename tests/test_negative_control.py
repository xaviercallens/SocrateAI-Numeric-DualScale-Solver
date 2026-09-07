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

def test_negative_control_gauge_violation():
    """
    Test Step 3: Adversarial Negative Control Injection
    Maliciously injects a massive divergence anomaly to violate the solenoidal constraint.
    Asserts that a GaugeViolationError is immediately caught and execution is aborted.
    """
    dataset_path = os.path.join(WORKSPACE_ROOT, "leanflow_antigravity", "data", "jhtdb_grid.safetensors")
    
    # Load dataset
    state, dof = workflow.load_data(dataset_path, subset_dof=1000)
    
    # Inject massive anomaly (magnetic monopole)
    state[0] = 1e9
    
    with pytest.raises(workflow.GaugeViolationError) as exc_info:
        workflow.execute_cycle_step(state, dof, cycle_idx=0)
        
    assert "Solenoidal constraint" in str(exc_info.value) or "monopole" in str(exc_info.value)
