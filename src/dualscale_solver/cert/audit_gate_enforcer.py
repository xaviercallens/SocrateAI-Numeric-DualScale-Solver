"""
Audit Gate Enforcer: Centralized Gate Invariant Validation Engine
================================================================

Provides authoritative, rigorous validation functions for all certification
and hardness gates (H45–H50, etc.).

Ensures negative controls test genuine gate rejection of falsified or corrupted
payloads, rather than evaluating local tautologies.
"""

from __future__ import annotations

from typing import Any, Dict


def validate_h45_hil_gate(payload: Dict[str, Any]) -> bool:
    """
    Validates H45 Bare-Metal QEMU Silicon HIL Gate invariants:
      - Payload is a valid dictionary
      - `_measured` is strictly True
      - `malloc_calls` == 0 (zero dynamic heap allocation on embedded targets)
      - `latency_ms` <= 1.0 ms (real-time embedded execution budget)
      - `ram_usage_bytes` <= 65536 (64 KB static RAM budget)
      - `status` == 'PASSED'
    """
    if not isinstance(payload, dict):
        return False
    if not payload.get("_measured", False):
        return False
    if payload.get("status") != "PASSED":
        return False
    if payload.get("malloc_calls", -1) != 0:
        return False
    try:
        latency = float(payload.get("latency_ms", float("inf")))
        if latency > 1.0 or latency < 0.0:
            return False
    except (ValueError, TypeError):
        return False
    try:
        ram = int(payload.get("ram_usage_bytes", 1000000))
        if ram > 65536 or ram < 0:
            return False
    except (ValueError, TypeError):
        return False
    return True


def validate_h46_cad_gate(payload: Dict[str, Any]) -> bool:
    """
    Validates H46 OpenCASCADE 3D Watertight B-Rep Solid Gate invariants:
      - Payload is a valid dictionary
      - `_measured` is strictly True
      - `is_watertight_manifold` is True
      - `euler_poincare_characteristic` == 2 (genus 0 topological sphere, V - E + F = 2)
      - `enclosed_volume_m3` > 0.0 (strictly positive volume)
      - `step_content_bytes` > 0
      - `status` == 'PASSED'
    """
    if not isinstance(payload, dict):
        return False
    if not payload.get("_measured", False):
        return False
    if payload.get("status") != "PASSED":
        return False
    if not payload.get("is_watertight_manifold", False):
        return False
    if payload.get("euler_poincare_characteristic") != 2:
        return False
    try:
        vol = float(payload.get("enclosed_volume_m3", -1.0))
        if vol <= 0.0:
            return False
    except (ValueError, TypeError):
        return False
    try:
        step_bytes = int(payload.get("step_content_bytes", 0))
        if step_bytes <= 0:
            return False
    except (ValueError, TypeError):
        return False
    return True


def validate_h47_telemetry_gate(payload: Dict[str, Any]) -> bool:
    """
    Validates H47 Cloud-Native gRPC & BigQuery Telemetry Streaming Gate invariants:
      - Payload is a valid dictionary
      - `_measured` is strictly True
      - `loss_rate` == 0.0 (zero packet/event loss)
      - `is_timestamp_monotonic` is True
      - `is_sequence_contiguous` is True (zero sequence gaps)
      - `events_ingested` > 0
      - `status` == 'PASSED'
    """
    if not isinstance(payload, dict):
        return False
    if not payload.get("_measured", False):
        return False
    if payload.get("status") != "PASSED":
        return False
    try:
        loss = float(payload.get("loss_rate", 1.0))
        if loss != 0.0:
            return False
    except (ValueError, TypeError):
        return False
    if not payload.get("is_timestamp_monotonic", False):
        return False
    if not payload.get("is_sequence_contiguous", False):
        return False
    try:
        events = int(payload.get("events_ingested", payload.get("events_attempted", 0)))
        if events <= 0:
            return False
    except (ValueError, TypeError):
        return False
    return True


def validate_h48_fsi_gate(payload: Dict[str, Any]) -> bool:
    """
    Validates H48 High-Order 3D Volume Mesh Tensor FSI Gate invariants:
      - Payload is a valid dictionary
      - `_measured` is strictly True
      - `mean_traction_relative_error` <= 1e-4
      - `max_kinematic_residual` <= 1e-6
      - `fsi_coupling_loss_pct` <= 2.0%
      - `status` == 'PASSED'
    """
    if not isinstance(payload, dict):
        return False
    if not payload.get("_measured", False):
        return False
    if payload.get("status") != "PASSED":
        return False
    try:
        traction_err = float(payload.get("mean_traction_relative_error", 1.0))
        if traction_err > 1e-4 or traction_err < 0.0:
            return False
    except (ValueError, TypeError):
        return False
    try:
        kinematic_res = float(payload.get("max_kinematic_residual", 1.0))
        if kinematic_res > 1e-6 or kinematic_res < 0.0:
            return False
    except (ValueError, TypeError):
        return False
    try:
        coupling_loss = float(payload.get("fsi_coupling_loss_pct", 100.0))
        if coupling_loss > 2.0 or coupling_loss < 0.0:
            return False
    except (ValueError, TypeError):
        return False
    return True


def validate_h49_packaging_gate(payload: Dict[str, Any]) -> bool:
    """
    Validates H49 Commercial Distribution & Packaging Gate invariants:
      - Payload is a valid dictionary
      - `_measured` is strictly True
      - `missing_symbols_count` == 0 (all C-ABI symbols present)
      - `docker_compressed_size_mb` <= 150.0 MB (lightweight container appliance)
      - `c_header_lines` > 0
      - `status` == 'PASSED'
    """
    if not isinstance(payload, dict):
        return False
    if not payload.get("_measured", False):
        return False
    if payload.get("status") != "PASSED":
        return False
    if payload.get("missing_symbols_count", -1) != 0:
        return False
    try:
        docker_size = float(payload.get("docker_compressed_size_mb", 1000.0))
        if docker_size > 150.0 or docker_size <= 0.0:
            return False
    except (ValueError, TypeError):
        return False
    try:
        header_lines = int(payload.get("c_header_lines", 0))
        if header_lines <= 0:
            return False
    except (ValueError, TypeError):
        return False
    return True


def validate_h50_licensing_gate(payload: Dict[str, Any]) -> bool:
    """
    Validates H50 Cryptographic Licensing & Audit Lock Gate invariants:
      - Payload is a valid dictionary
      - `_measured` is strictly True
      - `token_verified` is True
      - `merkle_root` is a valid 64-character hexadecimal SHA-256 string
      - `status` == 'PASSED'
    """
    if not isinstance(payload, dict):
        return False
    if not payload.get("_measured", False):
        return False
    if payload.get("status") != "PASSED":
        return False
    if not payload.get("token_verified", False):
        return False
    merkle_root = payload.get("merkle_root", "")
    if not isinstance(merkle_root, str) or len(merkle_root) != 64:
        return False
    try:
        int(merkle_root, 16)
    except ValueError:
        return False
    return True


GATE_VALIDATORS = {
    "H45": validate_h45_hil_gate,
    "H46": validate_h46_cad_gate,
    "H47": validate_h47_telemetry_gate,
    "H48": validate_h48_fsi_gate,
    "H49": validate_h49_packaging_gate,
    "H50": validate_h50_licensing_gate,
}


def validate_audit_gate(gate_id: str, payload: Dict[str, Any]) -> bool:
    """Dispatches payload validation to the corresponding authoritative gate validator."""
    validator = GATE_VALIDATORS.get(gate_id.upper())
    if not validator:
        raise ValueError(f"Unknown gate identifier: {gate_id}")
    return validator(payload)
