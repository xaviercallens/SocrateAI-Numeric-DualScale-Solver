#!/usr/bin/env python3
"""
scripts/download_usecase_datasets.py

LeanFlow Enterprise — Dataset Downloader for UC7–UC11
======================================================

Downloads reference datasets from Hugging Face, Zenodo, and GitHub
for the 5 canonical benchmark use cases.

Usage:
    python scripts/download_usecase_datasets.py [--use-case UC7] [--cache-dir data/datasets/]

Sources:
    UC7:  HuggingFace pdearena/NavierStokes-2D (PDEBench, ~2 GB)
    UC8:  Zenodo 7813803 (CFDBench, ~0.5 GB) + embedded Ghia tables
    UC9:  Zenodo 5520633 (Dedalus RB, ~1.5 GB)
    UC10: GitHub PrincetonUniversity/athena (KH reference)
    UC11: HuggingFace callensxavier/leanflow-phase12-benchmark (~0.3 GB)

Note: Large downloads require network access and disk space.
      Ghia (UC8) reference data is embedded directly in usecase_database.py
      and does not require external download.
"""

import sys
import json
import argparse
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))

from dualscale_solver.benchmarks.usecase_database import (
    DATASET_DOWNLOAD_REGISTRY,
    GHIA_REFERENCE,
    build_usecase_registry,
)

import numpy as np


def download_huggingface(entry: dict, cache_dir: Path) -> Path:
    """Download a dataset from Hugging Face Hub."""
    try:
        from huggingface_hub import hf_hub_download
    except ImportError:
        print("  ⚠ huggingface_hub not installed. Run: pip install huggingface_hub")
        return Path()

    repo_id = entry["repo_id"]
    filename = entry.get("filename", "")
    repo_type = entry.get("repo_type", "dataset")

    print(f"  Downloading from HF: {repo_id} / {filename}")
    path = hf_hub_download(
        repo_id=repo_id,
        filename=filename,
        repo_type=repo_type,
        cache_dir=str(cache_dir),
    )
    print(f"  ✓ Downloaded: {path}")
    return Path(path)


def download_zenodo(entry: dict, cache_dir: Path) -> Path:
    """Download a dataset from Zenodo."""
    import urllib.request

    url = entry.get("url", "")
    zenodo_id = entry.get("zenodo_id", "")

    if not url:
        url = f"https://zenodo.org/api/records/{zenodo_id}"

    print(f"  Checking Zenodo record: {url}")
    # For Zenodo, we just verify the record exists and print download instructions
    # (actual file listing requires the Zenodo API)
    try:
        api_url = f"https://zenodo.org/api/records/{zenodo_id}"
        with urllib.request.urlopen(api_url, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            files = data.get("files", [])
            print(f"  ✓ Zenodo record {zenodo_id} found: {len(files)} file(s)")
            for f in files[:5]:
                print(f"    → {f.get('key', 'unknown')} ({f.get('size', 0) / 1e6:.1f} MB)")
            return cache_dir / f"zenodo_{zenodo_id}"
    except Exception as e:
        print(f"  ⚠ Could not access Zenodo API: {e}")
        print(f"  → Manual download: {url}")
        return Path()


def materialize_ghia_tables(cache_dir: Path) -> Path:
    """Save Ghia reference data as .npz for offline use."""
    output = cache_dir / "ghia_reference_tables.npz"
    output.parent.mkdir(parents=True, exist_ok=True)

    data = {}
    for re_val, table in GHIA_REFERENCE.items():
        data[f"re{re_val}_y"] = np.array(table["y"])
        data[f"re{re_val}_u"] = np.array(table["u"])

    np.savez_compressed(str(output), **data)
    print(f"  ✓ Ghia tables materialized: {output} ({output.stat().st_size / 1024:.1f} KB)")
    return output


def main():
    parser = argparse.ArgumentParser(
        description="Download reference datasets for UC7–UC11 benchmarks"
    )
    parser.add_argument(
        "--use-case", type=str, default="all",
        help="Specific use case to download (UC7, UC8, ..., UC11, or 'all')"
    )
    parser.add_argument(
        "--cache-dir", type=str, default="data/datasets",
        help="Local cache directory for downloaded data"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="List datasets without downloading"
    )
    parser.add_argument(
        "--ghia-only", action="store_true",
        help="Only materialize embedded Ghia reference tables (no network)"
    )
    args = parser.parse_args()

    cache_dir = REPO / args.cache_dir
    cache_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("LeanFlow Enterprise — Dataset Downloader (UC7–UC11)")
    print(f"Cache: {cache_dir}")
    print("=" * 60)

    if args.ghia_only:
        materialize_ghia_tables(cache_dir)
        return 0

    # Filter registry
    if args.use_case.lower() == "all":
        entries = DATASET_DOWNLOAD_REGISTRY.items()
    else:
        uc = args.use_case.upper()
        entries = [(k, v) for k, v in DATASET_DOWNLOAD_REGISTRY.items()
                   if k.startswith(uc)]

    for name, entry in entries:
        print(f"\n{'─' * 40}")
        print(f"Dataset: {name}")
        print(f"  Source: {entry['source']}")
        print(f"  Format: {entry.get('format', 'unknown')}")
        print(f"  Size: ~{entry.get('size_gb', '?')} GB")
        print(f"  DOI: {entry.get('doi', 'N/A')}")

        if args.dry_run:
            print("  [DRY RUN — skipping download]")
            continue

        src = entry["source"]
        if src == "huggingface":
            download_huggingface(entry, cache_dir)
        elif src == "zenodo":
            download_zenodo(entry, cache_dir)
        elif src == "github":
            print(f"  → GitHub repo: {entry.get('url', entry.get('repo', ''))}")
            print(f"    Clone manually: git clone {entry.get('url', '')}")
        else:
            print(f"  ⚠ Unknown source type: {src}")

    # Always materialize Ghia tables
    print(f"\n{'─' * 40}")
    print("Ghia reference tables (embedded — no download needed):")
    materialize_ghia_tables(cache_dir)

    print(f"\n{'=' * 60}")
    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
