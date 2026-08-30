"""
Unit Tests for Runux AI Runtime & Rust Mini-Kernel Bridge.
"""

from pathlib import Path
import numpy as np
from dualscale_solver.runtimes.runux_bridge import RunuxRuntimeBridge


def test_runux_runtime_bridge_detection():
    bridge = RunuxRuntimeBridge()
    caps = bridge.inspect_capabilities()
    
    assert "runux_ai_runtime" in caps
    assert "rust_linux_mini_kernel" in caps
    assert isinstance(caps["runux_ai_runtime"]["available"], bool)
    assert isinstance(caps["rust_linux_mini_kernel"]["available"], bool)

    # Check that when cloned, capabilities list crates
    if caps["runux_ai_runtime"]["available"]:
        assert len(caps["runux_ai_runtime"]["crates"]) > 0


def test_runux_runtime_buffer_allocation():
    bridge = RunuxRuntimeBridge()
    buf = bridge.allocate_spectral_buffer((2, 64, 64), dtype=np.complex128)
    assert buf.shape == (2, 64, 64)
    assert buf.dtype == np.complex128
    assert buf.flags["C_CONTIGUOUS"] is True
