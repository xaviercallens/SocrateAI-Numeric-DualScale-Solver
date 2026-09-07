#!/usr/bin/env bash
set -euo pipefail

# Enterprise Edition Autonomous Execution Script
echo "================================================================================"
echo " Starting Enterprise Edition Multi-Agent Autonomous Pipeline (Phases E1–E4)"
echo "================================================================================"

WORKSPACE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$WORKSPACE_ROOT"

# 1. Verify Rust Enterprise Crates
echo "[1/3] Running Rust Enterprise Crate Tests..."
cargo test --manifest-path crates/leanflow-enterprise/Cargo.toml

# 2. Verify Lean 4 Formal Proofs
echo "[2/3] Auditing Lean 4 Enterprise Formal Proofs..."
(cd lean4 && lake build EnterpriseSpec EnterprisePhase2Spec)

# 3. Execute Autonomous 8-Agent Enterprise Workflow
echo "[3/3] Executing 8-Agent Enterprise Workflow Orchestrator..."
PYTHONPATH=src python3 scripts/run_enterprise_workflow.py

echo "================================================================================"
echo " Enterprise Edition Autonomous Pipeline Complete: All Gates Passed!"
echo " Certificate sealed at certs/CERT-ENTERPRISE-V3.3.0.json"
echo "================================================================================"
