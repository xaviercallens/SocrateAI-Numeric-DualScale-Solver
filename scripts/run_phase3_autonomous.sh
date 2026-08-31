#!/usr/bin/env bash
set -e

echo "================================================================================"
echo "    SOCRATEAI DUAL-SCALE SOLVER — PHASE 3 AUTONOMOUS PIPELINE RUNNER"
echo "================================================================================"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
REPO_ROOT="$( cd "${SCRIPT_DIR}/.." &> /dev/null && pwd )"
cd "${REPO_ROOT}"

echo ">>> [1/3] Running Rust Workspace Tests..."
cargo test --workspace

echo ">>> [2/3] Running Phase 3 Python Unit & Invariant Tests..."
pytest tests/test_phase3_preconditioner_p3.py tests/test_phase3_orchestrator.py -v

echo ">>> [3/3] Executing 5-Agent Phase 3 Autonomous Experimental Protocol..."
python3 scripts/run_phase3_experimental_protocol.py

echo "================================================================================"
echo "    PHASE 3 AUTONOMOUS EXECUTION FULLY COMPLETE & CERTIFIED"
echo "================================================================================"
