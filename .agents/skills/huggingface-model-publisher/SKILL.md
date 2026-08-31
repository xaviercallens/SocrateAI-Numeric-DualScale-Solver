---
name: huggingface-model-publisher
description: >-
  Guidelines and automated workflows for packaging, validating, and publishing LeanFlow PDE models and benchmark datasets
  to the Hugging Face Hub (huggingface_hub API). Enforces zero-credential leakage in git/logs, generates standard Model Cards
  with verified empirical metrics, and stages runnable inference pipelines. Activate when preparing or publishing Hugging Face models.
version: 1.0
updated: 2026-08-31
---

# Hugging Face Model Publisher Skill

## 1. Security & Token Isolation Mandates

1. **Zero Token in Source Code**: Never hardcode, print, log, or commit Hugging Face tokens (`hf_*`).
2. **Environment Variable Injection**: Rely strictly on `HF_TOKEN` from the shell environment.
3. **Repository Verification**: Verify organization / username ownership (`api.whoami()`) before push.

## 2. Package Architecture

A valid LeanFlow model submission package must contain:
1. `README.md`: Model card with standard YAML metadata (`license`, `tags`, `datasets`, `metrics`).
2. `config.json`: Core numerical and mathematical solver parameters.
3. `symbrain_router.json`: Adaptive AI routing rules and preconditioner thresholds.
4. `pipeline.py`: Pure, runnable Python inference class (`LeanFlowPipeline.from_pretrained()`).
5. `weights.json`: Calibrated empirical cascade and Kolmogorov constants.
6. `certificate.json`: Mathesis Stream 0 SHA-256 certificate chain.

## 3. Publication Workflow

```bash
# Set write token securely
export HF_TOKEN=<token>

# Execute validated model export and upload
python3 scripts/hf_model_upload.py
```
