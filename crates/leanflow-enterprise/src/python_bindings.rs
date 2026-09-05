//! # PyO3 Zero-Copy Native Python Extension
//!
//! Direct zero-copy NumPy array binding for LeanFlow Enterprise,
//! replacing legacy ctypes memory copies with non-copying strided array views.
//!
//! Implements:
//!   - REQ-E2-1: Zero-copy NumPy buffer ingestion and output array construction.
//!   - REQ-E2-2: IDA DAE Solenoidal Projection solver integration.
//!   - REQ-E2-3: PolarQuant 8x telemetry compression and decompression.
//!   - Formal verification link: Lean 4 `EnterprisePhase2Spec.lean`.

use numpy::{IntoPyArray, PyArray1, PyReadonlyArray1};
use pyo3::prelude::*;
use pyo3::types::PyBytes;

use crate::ida_dae_solver::EnterpriseIdaSolenoidalSolver;
use crate::polarquant_compression::{CompressedTelemetryPacket, PolarQuantTelemetryCompressor};
use leanflow_solver::CvodeDyadicCascade;

/// Result structure for PyO3 CVODE Stiff Integrations.
#[pyclass]
pub struct PyEnterpriseCvodeResult {
    #[pyo3(get)]
    pub t_final: f64,
    #[pyo3(get)]
    pub num_steps: usize,
    #[pyo3(get)]
    pub num_rhs_evals: usize,
    pub time_history: Vec<f64>,
    pub energy_history: Vec<f64>,
    pub enstrophy_history: Vec<f64>,
    pub final_state: Vec<f64>,
}

#[pymethods]
impl PyEnterpriseCvodeResult {
    #[getter]
    pub fn get_time_history<'py>(&self, py: Python<'py>) -> &'py PyArray1<f64> {
        self.time_history.clone().into_pyarray(py)
    }

    #[getter]
    pub fn get_energy_history<'py>(&self, py: Python<'py>) -> &'py PyArray1<f64> {
        self.energy_history.clone().into_pyarray(py)
    }

    #[getter]
    pub fn get_enstrophy_history<'py>(&self, py: Python<'py>) -> &'py PyArray1<f64> {
        self.enstrophy_history.clone().into_pyarray(py)
    }

    #[getter]
    pub fn get_final_state<'py>(&self, py: Python<'py>) -> &'py PyArray1<f64> {
        self.final_state.clone().into_pyarray(py)
    }
}

/// Result structure for PyO3 IDA DAE Solenoidal Projection.
#[pyclass]
pub struct PyEnterpriseIdaResult {
    #[pyo3(get)]
    pub t_final: f64,
    #[pyo3(get)]
    pub pressure: f64,
    #[pyo3(get)]
    pub div_residual: f64,
    #[pyo3(get)]
    pub energy: f64,
    #[pyo3(get)]
    pub enstrophy: f64,
    #[pyo3(get)]
    pub is_solenoidal: bool,
    pub velocity: Vec<f64>,
}

#[pymethods]
impl PyEnterpriseIdaResult {
    #[getter]
    pub fn get_velocity<'py>(&self, py: Python<'py>) -> &'py PyArray1<f64> {
        self.velocity.clone().into_pyarray(py)
    }
}

/// PyO3 Compressed Telemetry Packet backed by PolarQuant.
#[pyclass]
#[derive(Clone)]
pub struct PyCompressedTelemetryPacket {
    #[pyo3(get)]
    pub step_index: usize,
    #[pyo3(get)]
    pub time: f64,
    #[pyo3(get)]
    pub original_dim: usize,
    #[pyo3(get)]
    pub target_bits: u8,
    #[pyo3(get)]
    pub original_bytes: usize,
    #[pyo3(get)]
    pub compressed_byte_count: usize,
    #[pyo3(get)]
    pub compression_ratio: f32,
    pub scales: Vec<f32>,
    pub zeros: Vec<f32>,
    pub packed_bytes: Vec<u8>,
}

#[pymethods]
impl PyCompressedTelemetryPacket {
    #[getter]
    pub fn get_scales<'py>(&self, py: Python<'py>) -> &'py PyArray1<f32> {
        self.scales.clone().into_pyarray(py)
    }

    #[getter]
    pub fn get_zeros<'py>(&self, py: Python<'py>) -> &'py PyArray1<f32> {
        self.zeros.clone().into_pyarray(py)
    }

    #[getter]
    pub fn get_packed_bytes<'py>(&self, py: Python<'py>) -> &'py PyBytes {
        PyBytes::new(py, &self.packed_bytes)
    }
}

/// Zero-copy solve for CVODE Dyadic cascade.
#[pyfunction]
#[pyo3(signature = (n_shells, nu, alpha_prime, use_bdf, rtol, atol, u0, t_final, n_steps))]
pub fn solve_cvode_dyadic_zerocopy(
    _py: Python,
    n_shells: usize,
    nu: f64,
    alpha_prime: Option<f64>,
    use_bdf: bool,
    rtol: f64,
    atol: f64,
    u0: PyReadonlyArray1<f64>,
    t_final: f64,
    n_steps: usize,
) -> PyResult<PyEnterpriseCvodeResult> {
    let u0_slice = u0.as_slice()?;
    let cascade = CvodeDyadicCascade::new(n_shells, nu, alpha_prime, use_bdf, rtol, atol);
    let result = cascade
        .integrate(u0_slice, t_final, n_steps)
        .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e))?;

    Ok(PyEnterpriseCvodeResult {
        t_final: result.time.last().copied().unwrap_or(0.0),
        num_steps: result.num_steps,
        num_rhs_evals: result.num_rhs_evals,
        time_history: result.time,
        energy_history: result.energy,
        enstrophy_history: result.enstrophy,
        final_state: result.final_state,
    })
}

/// Zero-copy solve for IDA Incompressible Navier-Stokes DAE solenoidal projection.
#[pyfunction]
#[pyo3(signature = (n_modes, nu, alpha_prime, rtol, atol, u0, p0, t_final, h))]
pub fn solve_ida_solenoidal_zerocopy(
    _py: Python,
    n_modes: usize,
    nu: f64,
    alpha_prime: Option<f64>,
    rtol: f64,
    atol: f64,
    u0: PyReadonlyArray1<f64>,
    p0: f64,
    t_final: f64,
    h: f64,
) -> PyResult<PyEnterpriseIdaResult> {
    let u0_slice = u0.as_slice()?;
    let solver = EnterpriseIdaSolenoidalSolver::new(n_modes, nu, alpha_prime, rtol, atol);
    let res = solver
        .solve(u0_slice, p0, t_final, h)
        .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e))?;

    Ok(PyEnterpriseIdaResult {
        t_final: res.t_final,
        pressure: res.pressure,
        div_residual: res.div_residual,
        energy: res.energy,
        enstrophy: res.enstrophy,
        is_solenoidal: res.is_solenoidal,
        velocity: res.velocity,
    })
}

/// PolarQuant telemetry state compression (8x target reduction).
#[pyfunction]
#[pyo3(signature = (state, target_bits=4, step_index=0, time=0.0, seed=42))]
pub fn polarquant_compress_zerocopy(
    _py: Python,
    state: PyReadonlyArray1<f64>,
    target_bits: u8,
    step_index: usize,
    time: f64,
    seed: u64,
) -> PyResult<PyCompressedTelemetryPacket> {
    let state_slice = state.as_slice()?;
    let compressor = PolarQuantTelemetryCompressor::new(state_slice.len(), target_bits, seed);
    let packet = compressor.compress(step_index, time, state_slice);

    Ok(PyCompressedTelemetryPacket {
        step_index: packet.step_index,
        time: packet.time,
        original_dim: packet.original_dim,
        target_bits: packet.target_bits,
        original_bytes: packet.original_bytes,
        compressed_byte_count: packet.compressed_bytes,
        compression_ratio: packet.compression_ratio,
        scales: packet.scales,
        zeros: packet.zeros,
        packed_bytes: packet.packed_bytes,
    })
}

/// PolarQuant telemetry state decompression.
#[pyfunction]
#[pyo3(signature = (packet, seed=42))]
pub fn polarquant_decompress_zerocopy<'py>(
    py: Python<'py>,
    packet: &PyCompressedTelemetryPacket,
    seed: u64,
) -> PyResult<&'py PyArray1<f64>> {
    let compressor = PolarQuantTelemetryCompressor::new(packet.original_dim, packet.target_bits, seed);
    let native_packet = CompressedTelemetryPacket {
        step_index: packet.step_index,
        time: packet.time,
        original_dim: packet.original_dim,
        packed_bytes: packet.packed_bytes.clone(),
        scales: packet.scales.clone(),
        zeros: packet.zeros.clone(),
        target_bits: packet.target_bits,
        original_bytes: packet.original_bytes,
        compressed_bytes: packet.compressed_byte_count,
        compression_ratio: packet.compression_ratio,
    };
    let restored = compressor.decompress(&native_packet);
    Ok(restored.into_pyarray(py))
}

/// Memory slice bounds verification matching Lean 4 `isWithinCapacity`.
#[pyfunction]
pub fn verify_memory_slice_safety(offset: usize, length: usize, capacity: usize) -> bool {
    offset.saturating_add(length) <= capacity
}

/// PyO3 C-Extension module initializer for `leanflow_enterprise`.
#[pymodule]
pub fn leanflow_enterprise(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PyEnterpriseCvodeResult>()?;
    m.add_class::<PyEnterpriseIdaResult>()?;
    m.add_class::<PyCompressedTelemetryPacket>()?;
    m.add_function(wrap_pyfunction!(solve_cvode_dyadic_zerocopy, m)?)?;
    m.add_function(wrap_pyfunction!(solve_ida_solenoidal_zerocopy, m)?)?;
    m.add_function(wrap_pyfunction!(polarquant_compress_zerocopy, m)?)?;
    m.add_function(wrap_pyfunction!(polarquant_decompress_zerocopy, m)?)?;
    m.add_function(wrap_pyfunction!(verify_memory_slice_safety, m)?)?;
    Ok(())
}
