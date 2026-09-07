use pyo3::prelude::*;
use numpy::ndarray::{ArrayViewMut1, Array1};
use numpy::{PyArray1, PyReadwriteArray1};
use antigravity_core::run_simulation;

/// simulate_disruption(dof, dataset, state)
/// Zero-copy memory binding from Python numpy to Rust ndarray.
#[pyfunction]
fn simulate_disruption(
    dof: usize,
    _dataset: String,
    mut state: PyReadwriteArray1<f64>
) -> PyResult<String> {
    // Obtain a mutable view into the Python numpy array without copying memory
    let mut state_view = state.as_array_mut();

    // Convert to a slice and pass directly to the high-performance core
    let state_slice = state_view.as_slice_mut().expect("Failed to get contiguous slice");
    run_simulation(dof, state_slice);

    Ok(format!("Simulation complete. Integrated {} DOF.", dof))
}

/// The Antigravity python module
#[pymodule]
fn antigravity(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(simulate_disruption, m)?)?;
    Ok(())
}
