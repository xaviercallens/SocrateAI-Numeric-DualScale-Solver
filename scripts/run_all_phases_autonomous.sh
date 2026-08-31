#!/usr/bin/env bash
set -e

echo "================================================================================"
echo "    SOCRATEAI DUAL-SCALE & LEANFLOW NAVIER-STOKES PROGRAM — MASTER RUNNER"
echo "    AUTONOMOUS PHASES 1 THROUGH 9 FULL PIPELINE & CERTIFICATION SUITE"
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
echo ">>> [PHASE 6] Executing Phase 6 Agentic Runtime Monitoring Protocol..."
python3 scripts/run_phase6_experimental_protocol.py

echo ""
echo ">>> [PHASE 6B] Executing Phase 6b Cross-Sector PoC Protocol..."
python3 scripts/run_phase6b_experimental_protocol.py

echo ""
echo ">>> [PHASE 6C] Executing Phase 6c Cloud-Production PoC Protocol..."
python3 scripts/run_phase6c_production_protocol.py

echo ""
echo ">>> [PHASE 7] Executing Phase 7 Industrialization Protocol..."
python3 scripts/run_phase7_production_protocol.py

echo ""
echo ">>> [PHASE 8] Executing Phase 8 Productization & Workflow 8 Protocol..."
python3 scripts/run_phase8_autonomous.sh

echo ""
echo ">>> [PHASE 9] Executing Phase 9 Autonomic Resilience & Recursive Optimization..."
./scripts/run_phase9_autonomous.sh

echo ""
echo ">>> [PHASE 10] Executing Phase 10 Enterprise AI, Real-Time Edge & OpenFOAM Supremacy..."
./scripts/run_phase10_autonomous.sh

echo ""
echo ">>> [VERIFICATION GATES] Running Formal 17-Gate Verification Suite (Gates 0-16)..."
./scripts/verify.sh

echo ""
echo "================================================================================"
echo "    🎉 ALL PHASES (1 THROUGH 10) AND GATES (0-16) ARE FULLY CERTIFIED!"
echo "================================================================================"

