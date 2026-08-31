//! # FFI Telemetry Hook for rusty-SUNDIALS and RunuX
//!
//! Provides zero-copy telemetry streaming and steering FFI callbacks for
//! real-time simulation monitoring (TSK-61 / H24).

use std::ffi::{c_char, c_void, CString};
use std::sync::atomic::{AtomicPtr, Ordering};
use serde::{Deserialize, Serialize};

/// Telemetry metric payload emitted during integration steps.
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct TelemetryRecord {
    pub step: usize,
    pub t: f64,
    pub dt: f64,
    pub energy: f64,
    pub enstrophy: f64,
    pub stiffness_ratio: f64,
    pub max_divergence: f64,
    pub u_max: f64,
    pub nu: f64,
    pub dx: f64,
}

impl TelemetryRecord {
    /// Compute stiffness ratio following IP-09:
    /// $\sigma = \frac{u_{\max} \cdot \Delta x}{\nu}$
    #[inline]
    pub fn compute_stiffness_ratio(u_max: f64, dx: f64, nu: f64) -> f64 {
        if nu.abs() < 1e-15 {
            f64::INFINITY
        } else {
            (u_max * dx) / nu
        }
    }

    /// Serialize this record to a JSON string for RunuX shared memory buffer.
    pub fn to_json(&self) -> Result<String, serde_json::Error> {
        serde_json::to_string(self)
    }

    /// Parse telemetry record from JSON string.
    pub fn from_json(json_str: &str) -> Result<Self, serde_json::Error> {
        serde_json::from_str(json_str)
    }
}

/// C-ABI compatible layout for zero-copy streaming of simulation telemetry.
#[repr(C)]
#[derive(Debug, Copy, Clone)]
pub struct FfiTelemetryData {
    pub step: usize,
    pub t: f64,
    pub dt: f64,
    pub energy: f64,
    pub enstrophy: f64,
    pub stiffness_ratio: f64,
    pub max_divergence: f64,
    pub u_max: f64,
    pub nu: f64,
    pub dx: f64,
}

impl From<&TelemetryRecord> for FfiTelemetryData {
    fn from(r: &TelemetryRecord) -> Self {
        Self {
            step: r.step,
            t: r.t,
            dt: r.dt,
            energy: r.energy,
            enstrophy: r.enstrophy,
            stiffness_ratio: r.stiffness_ratio,
            max_divergence: r.max_divergence,
            u_max: r.u_max,
            nu: r.nu,
            dx: r.dx,
        }
    }
}

impl From<&FfiTelemetryData> for TelemetryRecord {
    fn from(d: &FfiTelemetryData) -> Self {
        Self {
            step: d.step,
            t: d.t,
            dt: d.dt,
            energy: d.energy,
            enstrophy: d.enstrophy,
            stiffness_ratio: d.stiffness_ratio,
            max_divergence: d.max_divergence,
            u_max: d.u_max,
            nu: d.nu,
            dx: d.dx,
        }
    }
}

/// Steering command emitted by runtime agents (e.g., `agentic_runtime_monitor`).
#[repr(C)]
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct SteeringCommand {
    pub command: String,
    pub scheme: String,
    pub target_dt: f64,
    pub steps_to_stabilize: usize,
    pub _measured: bool,
}

/// C-compatible callback function pointer.
///
/// Returns 0 for continue, 1 for steering intervention, negative for error/abort.
pub type FfiTelemetryCallback = extern "C" fn(
    data: *const FfiTelemetryData,
    json_payload: *const c_char,
    user_data: *mut c_void,
) -> i32;

/// Global callback registry for rusty-SUNDIALS FFI hooks.
static GLOBAL_TELEMETRY_CALLBACK: AtomicPtr<c_void> = AtomicPtr::new(std::ptr::null_mut());
static GLOBAL_USER_DATA: AtomicPtr<c_void> = AtomicPtr::new(std::ptr::null_mut());

/// Register a global telemetry callback for rusty-SUNDIALS time integration.
#[no_mangle]
pub extern "C" fn register_sundials_telemetry_hook(
    cb: Option<FfiTelemetryCallback>,
    user_data: *mut c_void,
) -> i32 {
    let fn_ptr = match cb {
        Some(f) => f as *mut c_void,
        None => std::ptr::null_mut(),
    };
    GLOBAL_TELEMETRY_CALLBACK.store(fn_ptr, Ordering::SeqCst);
    GLOBAL_USER_DATA.store(user_data, Ordering::SeqCst);
    0
}

/// Dispatch a telemetry record to the registered FFI hook.
#[no_mangle]
pub extern "C" fn emit_sundials_telemetry(data: *const FfiTelemetryData) -> i32 {
    if data.is_null() {
        return -1;
    }

    let cb_ptr = GLOBAL_TELEMETRY_CALLBACK.load(Ordering::SeqCst);
    if cb_ptr.is_null() {
        return 0; // No hook registered, no-op
    }

    let cb: FfiTelemetryCallback = unsafe { std::mem::transmute(cb_ptr) };
    let user_data = GLOBAL_USER_DATA.load(Ordering::SeqCst);

    let record = unsafe { TelemetryRecord::from(&*data) };
    let json_string = match record.to_json() {
        Ok(s) => s,
        Err(_) => return -2,
    };

    let c_str = match CString::new(json_string) {
        Ok(s) => s,
        Err(_) => return -3,
    };

    cb(data, c_str.as_ptr(), user_data)
}

/// Free a C-string allocated on the Rust heap (for FFI consumers).
#[no_mangle]
pub extern "C" fn free_telemetry_string(ptr: *mut c_char) {
    if !ptr.is_null() {
        unsafe {
            let _ = CString::from_raw(ptr);
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::ffi::CStr;

    extern "C" fn test_callback(
        data: *const FfiTelemetryData,
        json_payload: *const c_char,
        user_data: *mut c_void,
    ) -> i32 {
        assert!(!data.is_null());
        assert!(!json_payload.is_null());
        assert_eq!(user_data as usize, 0x1337);

        let d = unsafe { &*data };
        assert_eq!(d.step, 5000);
        assert!((d.stiffness_ratio - 314.0).abs() < 1e-3);

        let c_str = unsafe { CStr::from_ptr(json_payload) };
        let json_str = c_str.to_str().unwrap();
        let parsed: TelemetryRecord = serde_json::from_str(json_str).unwrap();
        assert_eq!(parsed.step, 5000);
        1 // Return 1 indicating intervention requested
    }

    #[test]
    fn test_telemetry_stiffness_calculation() {
        let u_max = 1.0;
        let dx = 2.0 * std::f64::consts::PI / 64.0;
        let nu = 0.001;
        let sigma = TelemetryRecord::compute_stiffness_ratio(u_max, dx, nu);
        assert!((sigma - 98.17477).abs() < 1e-3);

        let nu_spike = nu * 0.01;
        let sigma_spike = TelemetryRecord::compute_stiffness_ratio(u_max, dx, nu_spike);
        assert!(sigma_spike > 100.0);
    }

    #[test]
    fn test_telemetry_ffi_roundtrip() {
        let record = TelemetryRecord {
            step: 5000,
            t: 1.25,
            dt: 0.001,
            energy: 0.45,
            enstrophy: 45.2,
            stiffness_ratio: 314.0,
            max_divergence: 1.2e-14,
            u_max: 1.23,
            nu: 0.00001,
            dx: 0.245,
        };

        let ffi_data = FfiTelemetryData::from(&record);
        let user_ptr = 0x1337 as *mut c_void;

        register_sundials_telemetry_hook(Some(test_callback), user_ptr);
        let code = emit_sundials_telemetry(&ffi_data);
        assert_eq!(code, 1);

        // Clear hook
        register_sundials_telemetry_hook(None, std::ptr::null_mut());
    }
}
