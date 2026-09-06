#!/usr/bin/env python3
"""
scripts/run_usecase_benchmarks.py

LeanFlow Enterprise — Reference Benchmark Orchestrator
=======================================================

Runs all 5 reference use cases (UC7–UC11), compares against published
reference data, and emits a certified JSON report.

Usage:
    python scripts/run_usecase_benchmarks.py [--fast] [--output results/usecase_benchmarks.json]
"""

import sys
import json
import argparse
import hashlib
import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))

from dualscale_solver.benchmarks.usecase_runners import run_all_usecases
from dualscale_solver.benchmarks.usecase_database import (
    build_usecase_registry,
    export_registry_json,
)


def main():
    parser = argparse.ArgumentParser(
        description="LeanFlow Enterprise — Reference Benchmark Suite"
    )
    parser.add_argument(
        "--fast", action="store_true",
        help="Fast mode: reduced grids for CI (default: True)"
    )
    parser.add_argument(
        "--full", action="store_true",
        help="Full resolution mode (128²–256² grids, longer integration)"
    )
    parser.add_argument(
        "--output", type=str, default="results/usecase_benchmarks_uc7_uc16.json",
        help="Output JSON path"
    )
    parser.add_argument(
        "--export-registry", action="store_true",
        help="Also export the use case registry as JSON"
    )
    args = parser.parse_args()

    fast_mode = not args.full

    print("=" * 70)
    print("LeanFlow Enterprise — Reference Benchmark Suite (UC7–UC16)")
    print(f"Mode: {'FAST (CI)' if fast_mode else 'FULL RESOLUTION'}")
    print("=" * 70)

    # Optionally export registry
    if args.export_registry:
        reg_path = REPO / "data" / "output" / "usecase_registry.json"
        export_registry_json(reg_path)
        print(f"✓ Registry exported: {reg_path}")

    # Run all benchmarks
    results = run_all_usecases(fast_mode=fast_mode)

    # Add metadata
    results["certificate_id"] = f"CERT-UC7-UC16-BENCH-{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d%H%M%S')}"
    results["timestamp"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    results["schema_version"] = "UC-BENCH-v1"

    # SHA-256 seal
    payload = json.dumps(results, sort_keys=True, default=str)
    results["sha256_hash"] = hashlib.sha256(payload.encode()).hexdigest()[:16]

    # Write output
    output_path = REPO / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2, default=str)

    # Summary
    print("\n" + "=" * 70)
    print(f"Overall: {results['overall_status']}")
    print(f"Passed: {results['passed']}/{results['total_use_cases']}")
    print(f"Wall time: {results['total_wall_time_s']}s")
    print(f"Certificate: {results['certificate_id']}")
    print(f"Output: {output_path}")
    print("=" * 70)

    for uc_id, uc_result in results.get("use_cases", {}).items():
        status_icon = "✅" if uc_result["status"] == "PASSED" else "❌"
        print(f"  {status_icon} {uc_id}: {uc_result['name']} — {uc_result['status']} ({uc_result['wall_time_s']}s)")

    return 0 if results["overall_status"] == "CERTIFIED" else 1


if __name__ == "__main__":
    sys.exit(main())
