#!/usr/bin/env bash
set -e

echo "================================================================================"
 echo "    SOCRATEAI DUAL-SCALE & LEANFLOW NAVIER-STOKES PROGRAM — MASTER RUNNER"
echo "    AUTONOMOUS PHASES 1, 2, 3, 4, 5 FULL PIPELINE & CERTIFICATION SUITE"
echo "================================================================================"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
REPO_ROOT="$( cd "${SCRIPT_DIR}/.." &> /dev/null && pwd )"
cd "${REPO_ROOT}"

echo ""
echo ">>> [GATE 0 & RUST] Building & Testing Rust Workspace..."
cargo test --workspace

echo ""
echo ">>> [GATE 1 & PYTHON] Running Full Pytest Invariant & Unit Test Suite..."
pytest tests/ -v

echo ""
echo ">>> [PHASE 1] Executing Phase 1 Experimental Protocol..."
python3 scripts/run_phase1_experimental_protocol.py

echo ""
echo ">>> [PHASE 2] Executing Phase 2 Preconditioner Protocol..."
python3 scripts/run_phase2_experimental_protocol.py

echo ""
echo ">>> [PHASE 3] Executing Phase 3 Neuro-Symbolic TensorCore AMG Protocol..."
python3 scripts/run_phase3_experimental_protocol.py

echo ""
echo ">>> [PHASE 4] Executing Phase 4 Real-Time & Embedded Protocol..."
python3 scripts/run_phase4_experimental_protocol.py

echo ""
echo ">>> [PHASE 5] Executing Phase 5 JHTDB Spectral + SLA + Frustration Protocol..."
python3 scripts/run_phase5_experimental_protocol.py

echo ""
echo ">>> [VERIFICATION GATES] Running Formal 6-Gate Verification Suite..."
./scripts/verify.sh

echo ""
echo "================================================================================"
echo "    🎉 ALL PHASES (1, 2, 3, 4, 5) AND GATES (0-6) ARE FULLY CERTIFIED!"
echo "================================================================================"
