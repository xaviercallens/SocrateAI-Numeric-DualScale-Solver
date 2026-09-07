#!/bin/bash
set -e

PROJECT_ID=$(gcloud config get-value project)
REGION="us-central1"
SERVICE_NAME="antigravity-solver"
IMAGE="gcr.io/${PROJECT_ID}/${SERVICE_NAME}:latest"

echo "Building the Antigravity Engine Container..."
# gcloud builds submit --tag ${IMAGE} ..
# For local Docker:
docker build -t ${IMAGE} -f infrastructure/Dockerfile .

echo "Pushing to Artifact Registry..."
docker push ${IMAGE}

echo "Deploying to Google Cloud Run (g2-standard-16)..."
gcloud run deploy ${SERVICE_NAME} \
  --image ${IMAGE} \
  --region ${REGION} \
  --allow-unauthenticated \
  --memory 32Gi \
  --cpu 8 \
  --command uvicorn \
  --args main:app,--host,0.0.0.0,--port,8080 \
  --execution-environment gen2 \
  --set-env-vars=NVIDIA_VISIBLE_DEVICES=all \
  --set-env-vars=NVIDIA_DRIVER_CAPABILITIES=compute,utility \
  --platform managed

echo "Deployment complete! Cost metric should be < $0.02 per execution."
