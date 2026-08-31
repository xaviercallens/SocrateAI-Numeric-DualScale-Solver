#!/usr/bin/env bash
# =============================================================================
# PHASE 9: AUTONOMIC RESILIENCE & RECURSIVE OPTIMIZATION RUNNER
# =============================================================================
set -eo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.."; pwd)"
cd "$REPO_DIR"

export PYTHONPATH="src:${PYTHONPATH:-}"

echo "================================================================================"
echo " INITIATING PHASE 9: AUTONOMIC RESILIENCE & RECURSIVE OPTIMIZATION"
echo "================================================================================"

# Execute the workflow orchestrator
python3 -c "
import json
from pathlib import Path
from dualscale_solver.agents.phase9_workflow_orchestrator import run_phase9_pipeline

print('Executing Phase 9 Autonomic Agents (H51-H55)...')
cert = run_phase9_pipeline()

output_dir = Path('data/output')
output_dir.mkdir(parents=True, exist_ok=True)
cert_path = output_dir / 'phase9_autonomic_cert.json'

with open(cert_path, 'w') as f:
    json.dump(cert, f, indent=2)

print(f'\nPhase 9 Execution Complete. Status: {cert[\"overall_status\"]}')
print(f'Certificate ID: {cert[\"certificate_id\"]}')
print(f'Saved to: {cert_path}')

if cert['overall_status'] != 'CERTIFIED':
    import sys
    sys.exit(1)
"
