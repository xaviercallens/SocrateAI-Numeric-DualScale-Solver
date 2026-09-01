#!/usr/bin/env bash
set -e

echo "================================================================================"
echo " LAUNCHING MULTI-AGENT PHASE 11 WORKFLOW & HYPERSCALE PROTOCOL"
echo "================================================================================"

python3 -c "
import sys
sys.path.insert(0, 'src')
from dualscale_solver.agents.phase11_workflow_orchestrator import Phase11HyperscaleOrchestrator
orchestrator = Phase11HyperscaleOrchestrator()
report = orchestrator.execute_workflow()
if report['certificate']['overall_status'] != 'CERTIFIED':
    sys.exit(1)
"

echo "================================================================================"
echo " PHASE 11 WORKFLOW COMPLETE "
echo "================================================================================"
