#!/usr/bin/env python3
"""
push_to_hub.py — LeanFlow Phase 12 HuggingFace Publisher
Enterprise Edition v1.0

Uploads to:
  - Dataset: callensxavier/leanflow-phase12-benchmark
  - Model:   callensxavier/leanflow-dual-scale-solver
"""

import os
import sys
import json
import shutil
import tempfile
import logging
from pathlib import Path

from huggingface_hub import HfApi, upload_file, upload_folder, create_repo

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

# --- Configuration ----------------------------------------------------------------
REPO_ROOT = Path(__file__).parent.parent.resolve()
HF_USERNAME = "callensxavier"
DATASET_REPO_ID = f"{HF_USERNAME}/leanflow-phase12-benchmark"
MODEL_REPO_ID = f"{HF_USERNAME}/leanflow-dual-scale-solver"

CERT_JSON = REPO_ROOT / "data" / "output" / "cert_phase12_workflow.json"
REPORT_PDF = REPO_ROOT / "reports" / "leanflow_phase12_report.pdf"
REPORT_TEX = REPO_ROOT / "reports" / "leanflow_phase12_report.tex"
LOOP_PY = REPO_ROOT / "loop.py"
README_DATASET = REPO_ROOT / "hf_publish" / "README_dataset.md"
README_MODEL = REPO_ROOT / "hf_publish" / "README_model.md"


# --- Helpers ----------------------------------------------------------------------

def load_cert() -> dict:
    with open(CERT_JSON) as f:
        return json.load(f)


def create_repo_safe(api: HfApi, repo_id: str, repo_type: str) -> str:
    try:
        url = api.create_repo(repo_id=repo_id, repo_type=repo_type, exist_ok=True)
        log.info(f"Repository ready: {repo_id} ({repo_type})")
        return url
    except Exception as e:
        log.warning(f"Repo creation warning (may already exist): {e}")
        return f"https://huggingface.co/{repo_type}s/{repo_id}"


# --- Dataset Publication ----------------------------------------------------------

def publish_dataset(api: HfApi, cert: dict) -> str:
    log.info("=" * 60)
    log.info("Publishing DATASET: %s", DATASET_REPO_ID)
    log.info("=" * 60)

    create_repo_safe(api, DATASET_REPO_ID, "dataset")

    files_to_upload = {
        "cert_phase12_workflow.json": CERT_JSON,
        "leanflow_phase12_report.pdf": REPORT_PDF,
        "leanflow_phase12_report.tex": REPORT_TEX,
        "loop.py": LOOP_PY,
        "README.md": README_DATASET,
        "hf_benchmark.json": REPO_ROOT / "data" / "output" / "hf_benchmark.json",
        "formal_manifest.json": Path("/home/xavkal/xdev/SocrateAIShared/foundationpaper2/outputs/formal_manifest.json"),
    }

    for remote_path, local_path in files_to_upload.items():
        if not Path(local_path).exists():
            log.warning("Skipping missing file: %s", local_path)
            continue
        log.info("  Uploading: %s -> %s", local_path.name if hasattr(local_path, 'name') else local_path, remote_path)
        api.upload_file(
            path_or_fileobj=str(local_path),
            path_in_repo=remote_path,
            repo_id=DATASET_REPO_ID,
            repo_type="dataset",
            commit_message=f"feat: LeanFlow Phase 12 Enterprise v1.0 — {remote_path}",
        )

    # Source snapshot deliberately omitted to protect intellectual property
    # as per enterprise and scientific licensing models.

    dataset_url = f"https://huggingface.co/datasets/{DATASET_REPO_ID}"
    log.info("Dataset published: %s", dataset_url)
    return dataset_url


# --- Model Publication -----------------------------------------------------------

def publish_model(api: HfApi, cert: dict) -> str:
    log.info("=" * 60)
    log.info("Publishing MODEL: %s", MODEL_REPO_ID)
    log.info("=" * 60)

    create_repo_safe(api, MODEL_REPO_ID, "model")

    api.upload_file(
        path_or_fileobj=str(README_MODEL),
        path_in_repo="README.md",
        repo_id=MODEL_REPO_ID,
        repo_type="model",
        commit_message="feat: LeanFlow Dual-Scale Solver model card — Enterprise v1.0",
    )

    api.upload_file(
        path_or_fileobj=str(CERT_JSON),
        path_in_repo="cert_phase12_workflow.json",
        repo_id=MODEL_REPO_ID,
        repo_type="model",
        commit_message="feat: Phase 12 certification JSON",
    )

    api.upload_file(
        path_or_fileobj=str(REPORT_PDF),
        path_in_repo="leanflow_phase12_report.pdf",
        repo_id=MODEL_REPO_ID,
        repo_type="model",
        commit_message="feat: Phase 12 technical report PDF",
    )

    model_url = f"https://huggingface.co/{MODEL_REPO_ID}"
    log.info("Model published: %s", model_url)
    return model_url


# --- Main ------------------------------------------------------------------------

def main():
    log.info("LeanFlow Phase 12 — HuggingFace Publisher")
    log.info("Enterprise Edition v1.0")

    # Validate prerequisites
    missing = [p for p in [CERT_JSON, REPORT_PDF, README_DATASET, README_MODEL] if not p.exists()]
    if missing:
        log.error("Missing required files: %s", [str(m) for m in missing])
        sys.exit(1)

    cert = load_cert()
    cert_id = cert["certificate"]["certificate_id"]
    status = cert["certificate"]["overall_status"]
    log.info("Certificate: %s | Status: %s", cert_id, status)

    if status != "CERTIFIED":
        log.error("Certificate is not CERTIFIED. Run loop.py first.")
        sys.exit(2)

    api = HfApi()

    # Verify authentication
    user = api.whoami()
    log.info("Authenticated as: %s", user["name"])

    # Publish
    dataset_url = publish_dataset(api, cert)
    model_url = publish_model(api, cert)

    print("\n" + "=" * 60)
    print("PUBLICATION COMPLETE")
    print("=" * 60)
    print(f"  Dataset: {dataset_url}")
    print(f"  Model:   {model_url}")
    print(f"  Cert:    {cert_id}")
    print("=" * 60)

    return {
        "status": "SUCCESS",
        "dataset_url": dataset_url,
        "model_url": model_url,
        "certificate_id": cert_id,
        "_measured": True,
    }


if __name__ == "__main__":
    result = main()
    print(json.dumps(result, indent=2))
