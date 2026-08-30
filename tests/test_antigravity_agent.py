"""
Unit tests for Google Antigravity Agent tools, configuration, and server.
"""

import json
from dualscale_solver.agents import (
    LEANFLOW_AGENT_TOOLS,
    create_agent_config,
    run_dyadic_simulation_tool,
    run_spectral_simulation_tool,
    verify_rational_invariants_tool,
    audit_mathesis_ledger_tool,
    probe_runtime_engines_tool,
)


def test_agent_tools_count():
    assert len(LEANFLOW_AGENT_TOOLS) == 5


def test_dyadic_simulation_tool():
    res_str = run_dyadic_simulation_tool(n_shells=8, nu=1e-3, alpha_prime=0.01, dt=1e-3, n_steps=20)
    data = json.loads(res_str)
    assert data["status"] == "SUCCESS"
    assert data["bound_satisfied"] is True
    assert data["max_enstrophy"] <= data["enstrophy_bound"]


def test_spectral_simulation_tool():
    res_str = run_spectral_simulation_tool(n_grid=16, nu=1e-3, alpha_prime=0.01, dt=1e-3, n_steps=10)
    data = json.loads(res_str)
    assert data["status"] == "SUCCESS"
    assert data["solenoidal_condition_verified"] is True
    assert data["max_divergence_residual"] < 1e-12


def test_verify_rational_invariants_tool():
    res_str = verify_rational_invariants_tool(1, 4)
    data = json.loads(res_str)
    assert data["status"] == "PASSED"
    assert data["t_duality_symmetry"] is True
    assert data["singularity_lower_bound"] is True


def test_audit_mathesis_ledger_tool():
    res_str = audit_mathesis_ledger_tool()
    data = json.loads(res_str)
    assert data["status"] == "PASSED"
    assert data["soundness"]["is_sound"] is True


def test_probe_runtime_engines_tool():
    res_str = probe_runtime_engines_tool()
    data = json.loads(res_str)
    assert "rusty_sundials" in data
    assert "runux_ai_runtime" in data


def test_create_agent_config_local_and_gcp():
    local_cfg = create_agent_config(use_vertex=False, model="gemini-2.5-pro")
    assert local_cfg["vertex"] is False
    assert len(local_cfg["tools"]) == 5

    gcp_cfg = create_agent_config(use_vertex=True, project="my-gcp-project", location="europe-west1")
    assert gcp_cfg["vertex"] is True
    assert gcp_cfg["project"] == "my-gcp-project"
    assert gcp_cfg["location"] == "europe-west1"
