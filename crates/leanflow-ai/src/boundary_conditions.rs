//! # Boundary Conditions Inference & Verification Module
//!
//! Neuro-symbolic boundary condition parsing and solenoidal constraint verification.

use serde::{Deserialize, Serialize};

/// Recognized boundary condition topology.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum BoundaryType {
    PeriodicTorus,
    NoSlipWall,
    InflowOutflow,
}

/// Boundary condition verification result.
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct BoundaryVerification {
    pub boundary_type: BoundaryType,
    pub is_solenoidal: bool,
    pub max_divergence: f64,
}

impl BoundaryVerification {
    pub fn new_periodic(max_divergence: f64) -> Self {
        Self {
            boundary_type: BoundaryType::PeriodicTorus,
            is_solenoidal: max_divergence < 1e-12,
            max_divergence,
        }
    }
}

/// Parse natural language or specification string into BoundaryType.
pub fn parse_boundary_condition(spec: &str) -> BoundaryType {
    let lower = spec.to_lowercase();
    if lower.contains("periodic") || lower.contains("torus") {
        BoundaryType::PeriodicTorus
    } else if lower.contains("no-slip") || lower.contains("wall") || lower.contains("dirichlet") {
        BoundaryType::NoSlipWall
    } else if lower.contains("inflow") || lower.contains("outflow") {
        BoundaryType::InflowOutflow
    } else {
        BoundaryType::PeriodicTorus
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    /// Positive test: natural language parsing covers all three topology types.
    #[test]
    fn test_parse_boundary_condition_all_types() {
        assert_eq!(
            parse_boundary_condition("3D Periodic Torus Domain"),
            BoundaryType::PeriodicTorus
        );
        assert_eq!(
            parse_boundary_condition("No-slip wall at bottom boundary"),
            BoundaryType::NoSlipWall
        );
        assert_eq!(
            parse_boundary_condition("Inflow at inlet, outflow at outlet"),
            BoundaryType::InflowOutflow
        );
    }

    /// Positive test: Leray-projected periodic field is solenoidal.
    #[test]
    fn test_bc_verification_solenoidal_accepted() {
        // Simulated post-projection max divergence (machine precision)
        let result = BoundaryVerification::new_periodic(1e-14);
        assert!(result.is_solenoidal, "Machine-precision divergence must be accepted as solenoidal");
        assert_eq!(result.boundary_type, BoundaryType::PeriodicTorus);
    }

    /// Negative control NC-RUST-BC-01:
    /// Unrecognized boundary spec must fall back to PeriodicTorus gracefully (no panic).
    #[test]
    fn test_nc_unknown_spec_defaults_to_periodic() {
        let result = parse_boundary_condition("some completely unknown boundary type XYZ123");
        assert_eq!(
            result,
            BoundaryType::PeriodicTorus,
            "NC: Unknown spec must default to PeriodicTorus, not panic"
        );
    }

    /// Negative control NC-RUST-BC-02:
    /// A field with divergence above 1e-12 must be rejected as non-solenoidal.
    #[test]
    fn test_nc_high_divergence_rejected() {
        // Simulate un-projected velocity field: div(u) = 4.1e-7 (OpenFOAM-level)
        let result = BoundaryVerification::new_periodic(4.1e-7);
        assert!(
            !result.is_solenoidal,
            "NC: Divergence 4.1e-7 must NOT be accepted as solenoidal (threshold 1e-12)"
        );
    }
}
