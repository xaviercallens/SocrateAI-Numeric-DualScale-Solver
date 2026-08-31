#!/usr/bin/env bash
# scripts/run_phase8_autonomous.sh
# Phase 8: Autonomous Industrial Productization & Workflow 8 Master Runner

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "========================================================================"
echo "  SOCRATEAI PHASE 8 — INDUSTRIAL PRODUCTIZATION & WORKFLOW 8"
echo "========================================================================"

# 1. Full autonomous protocol
echo ""
echo ">>> Phase 8 Autonomous 8-Agent Industrial Pipeline..."
python3 scripts/run_phase8_production_protocol.py

echo ""
echo ">>> Running Phase 8 pytest suite with 7 negative controls..."
pytest tests/test_phase8_enterprise_production.py -v

echo ""
echo "========================================================================"
echo "  PHASE 8 COMPLETE — MATHESIS 5-TIER CERTIFIED"
echo "========================================================================"
