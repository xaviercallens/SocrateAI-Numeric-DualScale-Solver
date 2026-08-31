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

    #[test]
    fn test_parse_boundary_condition() {
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
}
