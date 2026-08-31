#!/usr/bin/env bash
# scripts/run_phase5_autonomous.sh
# Phase 5: JHTDB Spectral Validation, Production SLA, Frustration Monotonicity
# Mirrors run_phase3_autonomous.sh and run_phase4_autonomous.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "========================================================================"
echo "  SOCRATEAI PHASE 5 — JHTDB SPECTRAL + PRODUCTION SLA + H19"
echo "========================================================================"

# 1. Unit tests
echo ""
echo ">>> Phase 5 Unit Tests (H17, H18, H19, NC-DS-09, NC-DS-10)..."
python3 -m pytest tests/test_phase5_spectral.py -v --tb=short

# 2. Full autonomous protocol
echo ""
echo ">>> Phase 5 Autonomous 5-Agent Pipeline..."
python3 scripts/run_phase5_experimental_protocol.py

echo ""
echo "========================================================================"
echo "  PHASE 5 COMPLETE"
echo "========================================================================"
