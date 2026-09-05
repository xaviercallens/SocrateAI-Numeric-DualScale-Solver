#!/usr/bin/env bash
set -eo pipefail

echo "================================================================================"
echo " SocrateAI LeanFlow: Phase 12 Monotonic Greedy Search Loop & Industrial Workflows"
echo "================================================================================"

export PYTHONPATH="src:${PYTHONPATH:-}"

# Ensure output directory exists
mkdir -p data/output

echo "[1/3] Running Phase 12 Auto-Research Pytest Suite (Negative Controls & Convergence Tests)..."
pytest tests/test_phase12_autoresearch.py -v
echo "[1/3] Phase 12 Auto-Research Tests Passed."
echo ""

echo "[2/3] Executing Phase 12 Workflow via CLI (Instantiating the 5 Industrial Loops)..."
python3 -m dualscale_solver.cli workflow12 --output data/output/cert_phase12_workflow.json
echo "[2/3] Workflow 12 execution completed."
echo ""

echo "[3/3] Inspecting Auto-Research Output Certificate..."
cat data/output/cert_phase12_workflow.json | grep -E '"overall_status"|"certificate_id"'
echo ""
echo "Phase 12 Autonomous Execution Pipeline Finished Successfully."
echo "================================================================================"
