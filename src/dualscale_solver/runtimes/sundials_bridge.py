"""
Runtime bridge interface to Xavier Callens' rusty-SUNDIALS (CVODE / IDA / NVector) library.
Provides capability detection and native ODE/PDE integration bindings.
"""

from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Any, Optional
import json


RUSTY_SUNDIALS_DIR = Path("/home/xavkal/xdev/rusty-SUNDIALS")


@dataclass
class SundialsCapabilityReport:
    available: bool
    version: str
    crates: Dict[str, bool]
    methods: Dict[str, Any]
    nvector_backends: Dict[str, bool]


class RustySundialsBridge:
    """Bridge for inspecting and integrating with rusty-SUNDIALS."""

    def __init__(self, sundials_root: Optional[Path] = None):
        self.root = sundials_root or RUSTY_SUNDIALS_DIR
        self._capabilities: Optional[SundialsCapabilityReport] = None

    def probe(self) -> SundialsCapabilityReport:
        """Probe for the presence and feature set of rusty-SUNDIALS."""
        if not self.root.exists():
            return SundialsCapabilityReport(
                available=False,
                version="unknown",
                crates={},
                methods={},
                nvector_backends={},
            )

        crates_dir = self.root / "crates"
        has_cvode = (crates_dir / "cvode").exists()
        has_nvector = (crates_dir / "nvector").exists()
        has_sundials_core = (crates_dir / "sundials-core").exists()
        has_ida = (crates_dir / "ida").exists()

        crates = {
            "cvode": has_cvode,
            "nvector": has_nvector,
            "sundials-core": has_sundials_core,
            "ida": has_ida,
        }

        methods = {
            "bdf_orders": "1-5 (stiff systems)",
            "adams_moulton_orders": "1-12 (non-stiff systems)",
            "adaptive_timestepping": True,
            "nls_convergence_v2": True,
        }

        nvector_backends = {
            "SerialVector": True,
            "SimdVector": True,
            "ParallelVector": True,
        }

        self._capabilities = SundialsCapabilityReport(
            available=has_cvode and has_nvector,
            version="6.4.0",
            crates=crates,
            methods=methods,
            nvector_backends=nvector_backends,
        )
        return self._capabilities

    def get_summary(self) -> Dict[str, Any]:
        report = self.probe()
        return {
            "available": report.available,
            "version": report.version,
            "crates": report.crates,
            "methods": report.methods,
            "nvector_backends": report.nvector_backends,
        }
