#!/bin/bash
# =============================================================================
# FREQ AI Dashboard - Deploy to Google Cloud Run
# =============================================================================

set -e

PROJECT_ID="${1:-}"
REGION="us-central1"
SERVICE_NAME="freq-ai-dashboard"

if [ -z "$PROJECT_ID" ]; then
    echo "Usage: ./deploy.sh <PROJECT_ID>"
    exit 1
fi

echo "=============================================="
echo "  Deploying FREQ AI Dashboard"
echo "  Project: $PROJECT_ID"
echo "=============================================="

# Set project
gcloud config set project "$PROJECT_ID"

# Enable APIs
gcloud services enable run.googleapis.com cloudbuild.googleapis.com --quiet

# Build and deploy
cd "$(dirname "$0")/.."

gcloud builds submit \
    --tag "gcr.io/$PROJECT_ID/$SERVICE_NAME" \
    --file dashboard/Dockerfile \
    .

# Deploy to Cloud Run
gcloud run deploy "$SERVICE_NAME" \
    --image "gcr.io/$PROJECT_ID/$SERVICE_NAME" \
    --region "$REGION" \
    --platform managed \
    --allow-unauthenticated \
    --set-env-vars "ANTHROPIC_API_KEY=$(gcloud secrets versions access latest --secret=anthropic-api-key 2>/dev/null || echo '')" \
    --set-env-vars "GOOGLE_AI_API_KEY=$(gcloud secrets versions access latest --secret=google-ai-api-key 2>/dev/null || echo '')" \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300 \
    --quiet

# Get URL
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
    --region "$REGION" \
    --format "value(status.url)")

echo ""
echo "=============================================="
echo "  DASHBOARD DEPLOYED!"
echo "=============================================="
echo ""
echo "  URL: $SERVICE_URL"
echo ""
echo "  Open in browser to access the visual interface."
echo "=============================================="
