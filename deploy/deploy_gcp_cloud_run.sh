#!/usr/bin/env bash
# ==============================================================================
# Deploy SocrateAI LeanFlow Antigravity Agent to Google Cloud Run (Vertex AI)
# ==============================================================================
set -euo pipefail

PROJECT_ID="${GCP_PROJECT:-$(gcloud config get-value project 2>/dev/null || echo "")}"
REGION="${GCP_LOCATION:-europe-west1}"
SERVICE_NAME="leanflow-antigravity-agent"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}:latest"

if [ -z "${PROJECT_ID}" ]; then
    echo "ERROR: GCP_PROJECT is not set and no active gcloud project found."
    echo "Please set your project ID: export GCP_PROJECT='your-project-id'"
    exit 1
fi

echo "================================================================================"
echo " DEPLOYING SOCRATEAI LEANFLOW ANTIGRAVITY AGENT TO GOOGLE CLOUD RUN"
echo " Project : ${PROJECT_ID}"
echo " Region  : ${REGION}"
echo " Service : ${SERVICE_NAME}"
echo "================================================================================"

echo ""
echo "[1/3] Building container image via Google Cloud Build..."
gcloud builds submit --project="${PROJECT_ID}" --tag="${IMAGE_NAME}" -f Dockerfile.agent .

echo ""
echo "[2/3] Deploying container to Cloud Run with Vertex AI permissions..."
gcloud run deploy "${SERVICE_NAME}" \
    --project="${PROJECT_ID}" \
    --region="${REGION}" \
    --image="${IMAGE_NAME}" \
    --platform="managed" \
    --allow-unauthenticated \
    --set-env-vars="GCP_PROJECT=${PROJECT_ID},GCP_LOCATION=${REGION},MODE=gcp-vertex" \
    --memory="2Gi" \
    --cpu="2" \
    --min-instances=0 \
    --max-instances=5

echo ""
echo "[3/3] Deployment complete! Retrieving service URL..."
SERVICE_URL=$(gcloud run services describe "${SERVICE_NAME}" --platform="managed" --region="${REGION}" --format="value(status.url)")
echo "Service live at: ${SERVICE_URL}"
echo "================================================================================"
