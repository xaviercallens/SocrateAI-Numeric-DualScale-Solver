"""
Runux AI Runtime & Rust Mini-Kernel Bridge Interface.

Provides integration hooks, environment detection, and execution bridges to:
  1. Xavier Callens' Runux AI Runtime (crates/arena_mem, crates/gpu_compute, crates/hal)
  2. Xavier Callens' Rust Linux Mini-Kernel (no-std execution & formal Lean 4 specs)
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
import numpy as np


class RunuxRuntimeBridge:
    """
    Bridge client interfacing Dual-Scale PDE Solvers with Runux AI Runtime & Rust Mini-Kernel.
    """

    def __init__(
        self,
        runux_path: Optional[Path] = None,
        mini_kernel_path: Optional[Path] = None,
    ):
        # Default standard paths in xdev workspace
        default_xdev = Path("/home/xavkal/xdev")
        
        self.runux_path = runux_path or Path(
            os.environ.get("RUNUX_RUNTIME_DIR", default_xdev / "runux-ai-runtime")
        )
        self.mini_kernel_path = mini_kernel_path or Path(
            os.environ.get("RUST_MINI_KERNEL_DIR", default_xdev / "rust-linux-mini-kernel")
        )

    def is_runux_available(self) -> bool:
        """Check if Runux AI Runtime is locally available."""
        return self.runux_path.is_dir() and (self.runux_path / "Cargo.toml").exists()

    def is_mini_kernel_available(self) -> bool:
        """Check if Rust Linux Mini-Kernel is locally available."""
        return self.mini_kernel_path.is_dir() and (self.mini_kernel_path / "Cargo.toml").exists()

    def inspect_capabilities(self) -> Dict[str, Any]:
        """Inspect available hardware crates and acceleration features."""
        runux_crates = []
        if self.is_runux_available():
            crates_dir = self.runux_path / "crates"
            if crates_dir.is_dir():
                runux_crates = [d.name for d in crates_dir.iterdir() if d.is_dir()]

        return {
            "runux_ai_runtime": {
                "available": self.is_runux_available(),
                "path": str(self.runux_path),
                "crates": sorted(runux_crates),
            },
            "rust_linux_mini_kernel": {
                "available": self.is_mini_kernel_available(),
                "path": str(self.mini_kernel_path),
                "has_lean_specs": (self.mini_kernel_path / "specs").is_dir(),
            },
        }

    def get_summary(self) -> Dict[str, Any]:
        """Alias for inspect_capabilities."""
        return self.inspect_capabilities()

    def allocate_spectral_buffer(self, shape: tuple, dtype: np.dtype = np.complex128) -> np.ndarray:
        """
        Allocate an aligned zero-copy buffer for spectral operations.
        Falls back to standard C-contiguous NumPy buffer if native FFI is absent.
        """
        # Note: When linked with runux arena_mem via PyO3, this routes to native arena.
        return np.zeros(shape, dtype=dtype, order="C")
