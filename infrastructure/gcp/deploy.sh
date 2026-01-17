#!/bin/bash
# =============================================================================
# FREQ AI Lattice - Google Cloud Run Deployment Script
# =============================================================================
#
# This script deploys the FREQ AI Lattice to Google Cloud Run.
#
# Prerequisites:
#   1. Google Cloud SDK installed (gcloud)
#   2. Docker installed
#   3. A Google Cloud project with billing enabled
#   4. API keys for Anthropic and Google AI
#
# Usage:
#   ./deploy.sh <PROJECT_ID>
#
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="${1:-}"
REGION="us-central1"
SERVICE_NAME="freq-ai-lattice"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# =============================================================================
# VALIDATION
# =============================================================================

if [ -z "$PROJECT_ID" ]; then
    log_error "Usage: ./deploy.sh <PROJECT_ID>"
    echo ""
    echo "Example: ./deploy.sh my-gcp-project-123"
    exit 1
fi

log_info "Deploying FREQ AI Lattice to Google Cloud Run"
echo "=============================================="
echo "  Project:  $PROJECT_ID"
echo "  Region:   $REGION"
echo "  Service:  $SERVICE_NAME"
echo "=============================================="
echo ""

# =============================================================================
# STEP 1: SET PROJECT
# =============================================================================

log_info "Step 1/6: Setting Google Cloud project..."
gcloud config set project "$PROJECT_ID"
log_success "Project set to $PROJECT_ID"

# =============================================================================
# STEP 2: ENABLE REQUIRED APIS
# =============================================================================

log_info "Step 2/6: Enabling required APIs..."
gcloud services enable \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    containerregistry.googleapis.com \
    secretmanager.googleapis.com \
    --quiet

log_success "APIs enabled"

# =============================================================================
# STEP 3: CREATE SECRETS (if they don't exist)
# =============================================================================

log_info "Step 3/6: Setting up secrets..."

# Check if secrets exist, create if not
if ! gcloud secrets describe anthropic-api-key --quiet 2>/dev/null; then
    log_warn "Secret 'anthropic-api-key' not found."
    echo ""
    echo "Please create it with your Anthropic API key:"
    echo "  echo -n 'sk-ant-api03-...' | gcloud secrets create anthropic-api-key --data-file=-"
    echo ""
    read -p "Press Enter after creating the secret (or Ctrl+C to abort)..."
fi

if ! gcloud secrets describe google-ai-api-key --quiet 2>/dev/null; then
    log_warn "Secret 'google-ai-api-key' not found."
    echo ""
    echo "Please create it with your Google AI API key:"
    echo "  echo -n 'AIzaSy...' | gcloud secrets create google-ai-api-key --data-file=-"
    echo ""
    read -p "Press Enter after creating the secret (or Ctrl+C to abort)..."
fi

log_success "Secrets configured"

# =============================================================================
# STEP 4: BUILD DOCKER IMAGE
# =============================================================================

log_info "Step 4/6: Building Docker image..."

# Navigate to project root
cd "$(dirname "$0")/../.."

# Build using Cloud Build
gcloud builds submit \
    --tag "$IMAGE_NAME:latest" \
    --config infrastructure/gcp/cloudbuild.yaml \
    --quiet

log_success "Docker image built and pushed to $IMAGE_NAME"

# =============================================================================
# STEP 5: DEPLOY TO CLOUD RUN
# =============================================================================

log_info "Step 5/6: Deploying to Cloud Run..."

# Update service.yaml with project ID
sed "s/PROJECT_ID/$PROJECT_ID/g" infrastructure/gcp/service.yaml > /tmp/service-deploy.yaml

# Deploy
gcloud run services replace /tmp/service-deploy.yaml \
    --region "$REGION" \
    --quiet

# Allow unauthenticated access (for demo purposes)
gcloud run services add-iam-policy-binding "$SERVICE_NAME" \
    --region "$REGION" \
    --member="allUsers" \
    --role="roles/run.invoker" \
    --quiet

log_success "Deployed to Cloud Run"

# =============================================================================
# STEP 6: GET SERVICE URL
# =============================================================================

log_info "Step 6/6: Getting service URL..."

SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
    --region "$REGION" \
    --format "value(status.url)")

echo ""
echo "=============================================="
log_success "DEPLOYMENT COMPLETE!"
echo "=============================================="
echo ""
echo "  Service URL: $SERVICE_URL"
echo ""
echo "  API Endpoints:"
echo "    - Health:     $SERVICE_URL/health"
echo "    - Test:       $SERVICE_URL/api/v1/test"
echo "    - Directive:  $SERVICE_URL/api/v1/directive"
echo "    - Barge Scan: $SERVICE_URL/api/v1/maritime/scan-barge"
echo "    - API Docs:   $SERVICE_URL/docs"
echo ""
echo "  Quick Test:"
echo "    curl $SERVICE_URL/health"
echo ""
echo "=============================================="
