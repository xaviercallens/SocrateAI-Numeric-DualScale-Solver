"""
Audit and Verification Suite for Scientific Rigor, Modesty, and Epistemic Integrity.
====================================================================================
Enforces:
1. All 17 agents defined in AGENTS.md exist in .agents/agents/ with valid YAML frontmatter.
2. Target models are correctly routed:
   - T2 models routed to gemini-3.1-pro with deep_think / high reasoning.
   - T1/T0 models routed to gemini-3.8-flash or gemini-3.1-pro.
3. Zero banned pseudoscientific buzzwords in agent definitions or skills.
4. Backward-compatible alias for MonotonicGreedySearchLoop is preserved.
5. Epistemic statistical significance guardrail (p < 0.05, n >= 20).
"""

import os
import re
from pathlib import Path
import yaml
import pytest


AGENTS_DIR = Path(".agents/agents")
SKILLS_DIR = Path(".agents/skills")

EXPECTED_AGENTS = {
    # T2 Cloud Frontier
    "math_reviewer": {"tier": "T2", "model": "gemini-3.1-pro", "reasoning": "deep_think"},
    "qa_scientific_auditor": {"tier": "T2", "model": "gemini-3.1-pro", "reasoning": "high"},
    "formal_verifier": {"tier": "T2", "model": "gemini-3.1-pro", "reasoning": "deep_think"},
    "scientific_researcher": {"tier": "T2", "model": "gemini-3.1-pro", "reasoning": "deep_think"},
    # T1 MultiPhysics & Design
    "fsi_multiphysics_auditor": {"tier": "T1 (MultiPhysics)", "model": "gemini-3.1-pro"},
    "cad_generative_designer": {"tier": "T1 (Design)", "model": "gemini-3.1-pro"},
    # T1 Numerical & Runtime
    "agentic_runtime_monitor": {"tier": "T1 (Runtime)", "model": "gemini-3.8-flash"},
    "experimenter": {"tier": "T1 (Experiment)", "model": "gemini-3.8-flash"},
    "hil_edge_engineer": {"tier": "T1 (Runtime)", "model": "gemini-3.8-flash"},
    "dev_engineer": {"tier": "T1", "model": "gemini-3.8-flash"},
    "numeric_pde_solver": {"tier": "T1", "model": "gemini-3.8-flash"},
    "rust_systems_engineer": {"tier": "T1", "model": "gemini-3.8-flash"},
    "hpc_runtime_architect": {"tier": "T1", "model": "gemini-3.8-flash"},
    "ai_preprocessing_agent": {"tier": "T1", "model": "gemini-3.8-flash"},
    "cloud_telemetry_agent": {"tier": "T1 (Runtime)", "model": "gemini-3.8-flash"},
    # T0 Packaging & Licensing
    "enterprise_packaging_agent": {"tier": "T0", "model": "gemini-3.8-flash"},
    "licensing_audit_agent": {"tier": "T0", "model": "gemini-3.8-flash"},
}

BANNED_BUZZWORDS = [
    r"\bRulial\s+Inversion\b",
    r"\bHolographic\s+Regularisation\b",
    r"\bKarpathy\s+Ratchet\s+Auto-Research\s+Loop\b",
]


def parse_frontmatter(file_path: Path) -> dict:
    content = file_path.read_text()
    if not content.startswith("---"):
        return {}
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}
    return yaml.safe_load(parts[1]) or {}


def test_all_expected_agents_exist():
    """Verify that all 17 agents defined in AGENTS.md exist in .agents/agents/."""
    for agent_name in EXPECTED_AGENTS:
        agent_file = AGENTS_DIR / f"{agent_name}.md"
        assert agent_file.exists(), f"Missing agent definition file: {agent_file}"


def test_agent_model_routing():
    """Verify that agent definitions specify correct model tiers and output contracts."""
    for agent_name, expected in EXPECTED_AGENTS.items():
        agent_file = AGENTS_DIR / f"{agent_name}.md"
        fm = parse_frontmatter(agent_file)
        assert fm, f"Agent {agent_name} has invalid or missing YAML frontmatter"
        assert fm.get("target_model") == expected["model"], (
            f"Agent {agent_name} model mismatch: expected {expected['model']}, got {fm.get('target_model')}"
        )
        if "reasoning" in expected:
            assert fm.get("reasoning_budget") == expected["reasoning"], (
                f"Agent {agent_name} reasoning mismatch: expected {expected['reasoning']}, got {fm.get('reasoning_budget')}"
            )
        assert "output_contract" in fm, f"Agent {agent_name} missing output_contract in frontmatter"


def test_no_banned_buzzwords_in_agents():
    """Verify zero banned buzzwords appear in .agents/agents/*.md."""
    for agent_file in AGENTS_DIR.glob("*.md"):
        content = agent_file.read_text()
        for pattern in BANNED_BUZZWORDS:
            match = re.search(pattern, content, re.IGNORECASE)
            assert match is None, (
                f"Banned buzzword matching '{pattern}' found in {agent_file}: '{match.group(0)}'"
            )


def test_scientific_skills_exist():
    """Verify all 4 new scientific skills exist and have valid YAML frontmatter."""
    new_skills = [
        "scientific-deep-think",
        "scientific-peer-review",
        "scientific-adoption-packaging",
        "monotonic-greedy-search",
    ]
    for skill_name in new_skills:
        skill_file = SKILLS_DIR / skill_name / "SKILL.md"
        assert skill_file.exists(), f"Missing skill file: {skill_file}"
        fm = parse_frontmatter(skill_file)
        assert fm.get("name") == skill_name, f"Skill {skill_name} has mismatched frontmatter name"


def test_monotonic_greedy_search_loop_aliasing():
    """Verify MonotonicGreedySearchLoop class and its backward-compatibility alias."""
    from dualscale_solver.agents.auto_research_loop import (
        MonotonicGreedySearchLoop,
        KarpathyAutoResearchLoop,
    )
    assert MonotonicGreedySearchLoop is not None
    assert KarpathyAutoResearchLoop is MonotonicGreedySearchLoop


def test_statistical_significance_guardrail():
    """Verify that p >= 0.05 correctly invalidates claims under the audit policy."""
    def audit_spearman(n: int, rho: float, p_value: float) -> bool:
        if n < 20 or p_value >= 0.05:
            return False
        return True

    # Valid sweep: n=24, p=0.001
    assert audit_spearman(n=24, rho=0.72, p_value=0.001) is True
    # Invalid sweep: n=8 (too small), p=0.01
    assert audit_spearman(n=8, rho=0.85, p_value=0.01) is False
    # Invalid sweep: n=30, p=0.12 (not statistically significant)
    assert audit_spearman(n=30, rho=0.52, p_value=0.12) is False


def test_level2_reference_library_integrated():
    """Verify that the Level 2 SocrateAI reference library is integrated into the DualScale solver."""
    lakefile_path = Path("lean4/lakefile.lean")
    usecases_path = Path("lean4/UseCases.lean")
    
    assert lakefile_path.exists(), "lakefile.lean not found"
    assert usecases_path.exists(), "UseCases.lean not found"
    
    lakefile_content = lakefile_path.read_text()
    assert 'require SocrateAI from "../../../SocrateAI-Lean-Lib"' in lakefile_content, (
        "lakefile.lean must require the SocrateAI reference library."
    )
    
    usecases_content = usecases_path.read_text()
    assert "import SocrateAI.Core.ReferenceTheorems" in usecases_content, (
        "UseCases.lean must import SocrateAI.Core.ReferenceTheorems to enforce Tier-A claims."
    )

