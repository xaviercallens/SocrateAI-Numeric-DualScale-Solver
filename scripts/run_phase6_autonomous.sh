#!/usr/bin/env bash
# scripts/run_phase6_autonomous.sh
# Phase 6: Agentic Runtime Monitoring, Lean 4 Bounds, Continuous HF CI
# Mirrors run_phase5_autonomous.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "========================================================================"
echo "  SOCRATEAI PHASE 6 — AGENTIC RUNTIME ORCHESTRATION"
echo "========================================================================"

# 1. Full autonomous protocol
echo ""
echo ">>> Phase 6 Autonomous 4-Agent Pipeline..."
python3 scripts/run_phase6_experimental_protocol.py

echo ""
echo "========================================================================"
echo "  PHASE 6 COMPLETE"
echo "========================================================================"
