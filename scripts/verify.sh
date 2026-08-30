#!/usr/bin/env bash
set -eo pipefail

echo "================================================================================"
echo " SOCRATEAI DUAL-SCALE SOLVER: TWO-GATE VERIFICATION PROTOCOL"
echo "================================================================================"

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_DIR"

export PYTHONPATH="src:${PYTHONPATH:-}"

echo ""
echo "--- GATE 1: UNIT & EXACT RATIONAL INVARIANT SUITE ---"
echo "Executing pytest across all exact and numerical test modules..."
pytest -v tests/

echo ""
echo "--- GATE 2: AUDIT CERTIFICATE GENERATION & SCHEMA AUDIT ---"
mkdir -p data
python3 -m dualscale_solver.cli verify --output data/verification_cert.json

echo ""
echo "Validating generated certificate structure..."
python3 -c "
import json
from pathlib import Path
from dualscale_solver.cert.certificate_generator import load_certificate_schema
import jsonschema

cert_path = Path('data/verification_cert.json')
with open(cert_path, 'r') as f:
    cert = json.load(f)

schema = load_certificate_schema()
jsonschema.validate(instance=cert, schema=schema)

assert cert['status'] == 'PASSED', f'Expected PASSED, got {cert[\"status\"]}'
assert all(cert['negative_controls'].values()), 'Negative control failure detected'
print('Gate 2 Schema & Negative Controls: 100% VERIFIED')
"

echo ""
echo "================================================================================"
echo " ✅ ALL VERIFICATION GATES PASSED (TIER B / TIER C CERTIFIED)"
echo "================================================================================"
