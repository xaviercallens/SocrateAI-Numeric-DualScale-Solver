#!/bin/bash
set -e

echo "================================================================================"
echo " PHASE 10 ENTERPRISE AI: AUTONOMOUS WORKFLOW EXECUTION"
echo "================================================================================"

# Get the script directory and project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$ROOT_DIR"

export PYTHONPATH="$ROOT_DIR/src:$PYTHONPATH"

# Run the Phase 10 execution via the CLI
python -m dualscale_solver.cli workflow10
