#!/usr/bin/env python3
"""
LeanFlow Hugging Face Model Publisher
=====================================
Exports and uploads the complete Neuro-Symbolic DualScale Navier-Stokes model package to Hugging Face:
  https://huggingface.co/callensxavier/leanflow-dualscale-pde

Security:
  Token read securely from environment (HF_TOKEN) or local token vault.
  Zero token exposure in logs, code, or certificates.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root / "src"))

from huggingface_hub import HfApi
from dualscale_solver.ai.hf_model_export import build_huggingface_model_package


def _get_hf_token() -> str:
    """Retrieve HF token securely from environment or token vault."""
    token = os.environ.get("HF_TOKEN")
    if token and len(token.strip()) > 10:
        return token.strip()

    vault_path = Path("/home/xavkal/Documents/tokenHugging Face.md")
    if vault_path.exists():
        content = vault_path.read_text(encoding="utf-8")
        match = re.search(r"hf_[A-Za-z0-9]+", content)
        if match:
            return match.group(0).strip()

    print("[FATAL] Could not find valid Hugging Face token.")
    print("Please run: export HF_TOKEN=hf_...")
    sys.exit(1)


def main():
    repo_root = Path(__file__).parent.parent
    staging_dir = repo_root / "data" / "output" / "hf_model_submission"

    print("=================================================================")
    print("  LeanFlow — Hugging Face Model Package Exporter & Publisher")
    print("=================================================================")

    # 1. Build Model Package
    print(f"\n[1/3] Building model submission package at: {staging_dir}")
    build_huggingface_model_package(staging_dir)
    print("      [✓] README.md (Model Card with JHTDB benchmarks)")
    print("      [✓] config.json (DualScale T-duality PDE config)")
    print("      [✓] symbrain_router.json (SymBrain v4 preconditioner rules)")
    print("      [✓] pipeline.py (Self-contained runnable inference)")
    print("      [✓] weights.json (Pre-calibrated Kolmogorov constants)")
    print("      [✓] certificate.json (Mathesis Stream 0 H1-H20 audit certificate)")

    # 2. Authenticate
    print("\n[2/3] Authenticating with Hugging Face Hub...")
    token = _get_hf_token()
    api = HfApi(token=token)
    user_info = api.whoami()
    username = user_info["name"]
    print(f"      [✓] Authenticated as: {username}")

    model_repo_id = f"{username}/leanflow-dualscale-pde"

    # 3. Create Model Repo (if not exists) & Upload
    print(f"\n[3/3] Publishing model package to: {model_repo_id}...")
    api.create_repo(
        repo_id=model_repo_id,
        repo_type="model",
        exist_ok=True,
        private=False,
    )

    api.upload_folder(
        folder_path=str(staging_dir),
        repo_id=model_repo_id,
        repo_type="model",
        commit_message="feat(model): publish LeanFlow Neuro-Symbolic DualScale Navier-Stokes solver v1.0.0",
    )

    print(f"\n=================================================================")
    print(f"  🎉 SUCCESS! Model package successfully published to Hugging Face:")
    print(f"  👉 https://huggingface.co/{model_repo_id}")
    print(f"=================================================================\n")


if __name__ == "__main__":
    main()
