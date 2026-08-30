"""
Unit Tests for Audit Certificate Generation and Schema Validation.
"""

from fractions import Fraction
import jsonschema
import pytest

from dualscale_solver.cert.certificate_generator import (
    generate_verification_certificate,
    load_certificate_schema,
)


def test_schema_validates_positive_certificate():
    cert = generate_verification_certificate()
    schema = load_certificate_schema()
    # If invalid, this raises jsonschema.ValidationError
    jsonschema.validate(instance=cert, schema=schema)
    
    assert cert["status"] == "PASSED"
    assert cert["epistemic_tier"] == "TIER_B_EXACT_RATIONAL"
    assert cert["negative_controls"]["nc_ds_01_singularity"] is True
    assert cert["negative_controls"]["nc_ds_02_asymmetry"] is True
    assert cert["negative_controls"]["nc_ds_04_energy_leak"] is True


def test_schema_rejects_malformed_certificate():
    schema = load_certificate_schema()
    
    # Missing required field 'negative_controls'
    malformed = {
        "certificate_id": "CERT-DS-12345678",
        "timestamp": "2026-08-30T12:00:00Z",
        "solver_version": "0.1.0",
        "epistemic_tier": "TIER_B_EXACT_RATIONAL",
        "status": "PASSED",
        "claims_verified": ["CLM-DS-01"],
        "audit_metrics": {"samples_tested": 10},
    }
    
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=malformed, schema=schema)
