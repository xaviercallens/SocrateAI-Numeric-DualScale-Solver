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

# FFI structs for C-ABI
import ctypes
import numpy as np

class FfiCvodeResult(ctypes.Structure):
    _fields_ = [
        ("time_ptr", ctypes.POINTER(ctypes.c_double)),
        ("time_len", ctypes.c_size_t),
        ("energy_ptr", ctypes.POINTER(ctypes.c_double)),
        ("energy_len", ctypes.c_size_t),
        ("enstrophy_ptr", ctypes.POINTER(ctypes.c_double)),
        ("enstrophy_len", ctypes.c_size_t),
        ("final_state_ptr", ctypes.POINTER(ctypes.c_double)),
        ("final_state_len", ctypes.c_size_t),
        ("num_steps", ctypes.c_size_t),
        ("num_rhs_evals", ctypes.c_size_t),
        ("handle", ctypes.c_void_p),
    ]

def native_cvode_integrate(
    n_shells: int,
    nu: float,
    alpha_prime: Optional[float],
    use_bdf: bool,
    rtol: float,
    atol: float,
    u0: np.ndarray,
    t_final: float,
    n_steps: int
) -> Dict[str, Any]:
    """Native FFI bridge to rusty-SUNDIALS CVODE integration."""
    repo_root = Path(__file__).parent.parent.parent.parent
    lib_path = repo_root / "target" / "release" / "libleanflow_solver.so"
    
    if not lib_path.exists():
        raise RuntimeError(f"Native solver lib not found at {lib_path}. Run `cargo build --release`.")
        
    lib = ctypes.CDLL(str(lib_path))
    
    lib.solve_cvode_dyadic.argtypes = [
        ctypes.c_size_t, ctypes.c_double, ctypes.c_double,
        ctypes.c_bool, ctypes.c_double, ctypes.c_double,
        ctypes.POINTER(ctypes.c_double), ctypes.c_size_t,
        ctypes.c_double, ctypes.c_size_t,
        ctypes.POINTER(FfiCvodeResult)
    ]
    lib.solve_cvode_dyadic.restype = ctypes.c_int
    
    lib.free_cvode_result.argtypes = [ctypes.c_void_p]
    lib.free_cvode_result.restype = None
    
    out_result = FfiCvodeResult()
    u0_data = np.ascontiguousarray(u0, dtype=np.float64)
    u0_ptr = u0_data.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
    
    alpha_val = alpha_prime if alpha_prime is not None else -1.0
    
    res_code = lib.solve_cvode_dyadic(
        n_shells, nu, alpha_val, use_bdf, rtol, atol,
        u0_ptr, u0_data.size, t_final, n_steps,
        ctypes.byref(out_result)
    )
    
    if res_code != 0:
        raise RuntimeError(f"rusty-SUNDIALS CVODE integration failed with code {res_code}")
        
    # Copy data out
    time_arr = np.ctypeslib.as_array(out_result.time_ptr, shape=(out_result.time_len,)).copy()
    energy_arr = np.ctypeslib.as_array(out_result.energy_ptr, shape=(out_result.energy_len,)).copy()
    enstrophy_arr = np.ctypeslib.as_array(out_result.enstrophy_ptr, shape=(out_result.enstrophy_len,)).copy()
    final_state_arr = np.ctypeslib.as_array(out_result.final_state_ptr, shape=(out_result.final_state_len,)).copy()
    
    num_steps_out = out_result.num_steps
    num_rhs_evals = out_result.num_rhs_evals
    
    # Free Rust memory
    lib.free_cvode_result(out_result.handle)
    
    return {
        "times": time_arr,
        "energy": energy_arr,
        "enstrophy": enstrophy_arr,
        "final_state": final_state_arr,
        "num_steps": num_steps_out,
        "num_rhs_evals": num_rhs_evals,
    }


# =========================================================================
# Phase E2: PyO3 Native Extension Zero-Copy Bridge
# =========================================================================
import sys
_REPO_ROOT = Path(__file__).parent.parent.parent.parent
_RELEASE_DIR = _REPO_ROOT / "target" / "release"
if _RELEASE_DIR.exists() and str(_RELEASE_DIR) not in sys.path:
    sys.path.insert(0, str(_RELEASE_DIR))

try:
    import leanflow_enterprise as _lfe
    PYO3_ENTERPRISE_AVAILABLE = True
except ImportError:
    _lfe = None
    PYO3_ENTERPRISE_AVAILABLE = False


def native_cvode_integrate_zerocopy(
    n_shells: int,
    nu: float,
    alpha_prime: Optional[float],
    use_bdf: bool,
    rtol: float,
    atol: float,
    u0: np.ndarray,
    t_final: float,
    n_steps: int
) -> Dict[str, Any]:
    """Execute CVODE dyadic integration with zero-copy NumPy array views via PyO3."""
    if PYO3_ENTERPRISE_AVAILABLE and _lfe is not None:
        u0_c = np.ascontiguousarray(u0, dtype=np.float64)
        res = _lfe.solve_cvode_dyadic_zerocopy(
            n_shells, nu, alpha_prime, use_bdf, rtol, atol, u0_c, t_final, n_steps
        )
        return {
            "times": res.time_history,
            "energy": res.energy_history,
            "enstrophy": res.enstrophy_history,
            "final_state": res.final_state,
            "num_steps": res.num_steps,
            "num_rhs_evals": res.num_rhs_evals,
            "is_zerocopy": True,
        }
    # Fallback to ctypes
    res_ctypes = native_cvode_integrate(
        n_shells, nu, alpha_prime, use_bdf, rtol, atol, u0, t_final, n_steps
    )
    res_ctypes["is_zerocopy"] = False
    return res_ctypes


def native_ida_solenoidal_integrate_zerocopy(
    n_modes: int,
    nu: float,
    alpha_prime: Optional[float],
    rtol: float,
    atol: float,
    u0: np.ndarray,
    p0: float,
    t_final: float,
    h: float
) -> Dict[str, Any]:
    """Execute IDA Incompressible Navier-Stokes DAE solenoidal solve via PyO3."""
    if not PYO3_ENTERPRISE_AVAILABLE or _lfe is None:
        raise RuntimeError("leanflow_enterprise PyO3 extension is required for IDA DAE solve.")
    u0_c = np.ascontiguousarray(u0, dtype=np.float64)
    res = _lfe.solve_ida_solenoidal_zerocopy(
        n_modes, nu, alpha_prime, rtol, atol, u0_c, p0, t_final, h
    )
    return {
        "t_final": res.t_final,
        "velocity": res.velocity,
        "pressure": res.pressure,
        "div_residual": res.div_residual,
        "energy": res.energy,
        "enstrophy": res.enstrophy,
        "is_solenoidal": res.is_solenoidal,
        "is_zerocopy": True,
    }


def native_polarquant_compress_zerocopy(
    state: np.ndarray,
    target_bits: int = 4,
    step_index: int = 0,
    time: float = 0.0,
    seed: int = 42
) -> Any:
    """Compress high-frequency telemetry state using PolarQuant orthogonal rotation."""
    if not PYO3_ENTERPRISE_AVAILABLE or _lfe is None:
        raise RuntimeError("leanflow_enterprise PyO3 extension is required for PolarQuant compression.")
    state_c = np.ascontiguousarray(state, dtype=np.float64)
    return _lfe.polarquant_compress_zerocopy(state_c, target_bits, step_index, time, seed)


def native_polarquant_decompress_zerocopy(
    packet: Any,
    seed: int = 42
) -> np.ndarray:
    """Decompress PolarQuant telemetry packet back into physical f64 state vector."""
    if not PYO3_ENTERPRISE_AVAILABLE or _lfe is None:
        raise RuntimeError("leanflow_enterprise PyO3 extension is required for PolarQuant decompression.")
    return _lfe.polarquant_decompress_zerocopy(packet, seed)


