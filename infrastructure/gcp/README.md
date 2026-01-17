# FREQ AI Lattice - Google Cloud Run Deployment

Deploy the FREQ AI Sophisticated Operational Lattice to Google Cloud Run.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Google Cloud Platform                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────┐     ┌─────────────────────────────────────┐  │
│   │   Client    │────▶│         Cloud Run Service           │  │
│   │  (Browser)  │     │      freq-ai-lattice                │  │
│   └─────────────┘     │                                     │  │
│                       │   ┌─────────────────────────────┐   │  │
│                       │   │      FastAPI App            │   │  │
│                       │   │                             │   │  │
│                       │   │   ┌─────┐  ┌─────┐  ┌─────┐ │   │  │
│                       │   │   │ SSC │→ │ CGE │→ │ TOM │ │   │  │
│                       │   │   └──┬──┘  └──┬──┘  └──┬──┘ │   │  │
│                       │   └─────────────────────────────┘   │  │
│                       └───────────┬─────────────┬───────────┘  │
│                                   │             │              │
│   ┌───────────────────────────────┼─────────────┼──────────┐   │
│   │     Secret Manager            │             │          │   │
│   │  ┌──────────────────┐  ┌──────┴─────┐  ┌────┴────┐    │   │
│   │  │ anthropic-api-key│  │google-ai-  │  │ (future)│    │   │
│   │  │                  │  │ api-key    │  │         │    │   │
│   │  └────────┬─────────┘  └────────────┘  └─────────┘    │   │
│   └───────────┼────────────────────────────────────────────┘   │
│               │                                                │
└───────────────┼────────────────────────────────────────────────┘
                │
                ▼
    ┌───────────────────────┐
    │   Anthropic API       │ ◀── Claude Opus 4.5 (SSC, CGE)
    │   (api.anthropic.com) │
    └───────────────────────┘
    ┌───────────────────────┐
    │   Google AI API       │ ◀── Gemini Flash (TOM)
    │   (generativelanguage)│
    └───────────────────────┘
```

## Prerequisites

1. **Google Cloud SDK** installed
   ```bash
   # Install: https://cloud.google.com/sdk/docs/install
   gcloud --version
   ```

2. **Google Cloud Project** with billing enabled
   ```bash
   # Create project
   gcloud projects create my-freq-ai-project

   # Set project
   gcloud config set project my-freq-ai-project
   ```

3. **API Keys**
   - Anthropic: https://console.anthropic.com/settings/keys
   - Google AI: https://aistudio.google.com/app/apikey

## Quick Start (5 Minutes)

### Step 1: Create API Key Secrets

```bash
# Store Anthropic API key
echo -n 'sk-ant-api03-YOUR-KEY' | \
  gcloud secrets create anthropic-api-key --data-file=-

# Store Google AI API key
echo -n 'AIzaSy-YOUR-KEY' | \
  gcloud secrets create google-ai-api-key --data-file=-
```

### Step 2: Deploy

```bash
cd infrastructure/gcp
chmod +x deploy.sh
./deploy.sh YOUR-PROJECT-ID
```

### Step 3: Test

```bash
# Get service URL
SERVICE_URL=$(gcloud run services describe freq-ai-lattice \
  --region us-central1 --format "value(status.url)")

# Health check
curl $SERVICE_URL/health

# Run test directive
curl -X POST $SERVICE_URL/api/v1/test

# Submit custom directive
curl -X POST $SERVICE_URL/api/v1/directive \
  -H "Content-Type: application/json" \
  -d '{"directive": "Scan barge ALPHA-1 at Mile Marker 100"}'
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API info |
| `/health` | GET | Health check |
| `/docs` | GET | Interactive API docs (Swagger UI) |
| `/api/v1/directive` | POST | Process a directive |
| `/api/v1/test` | POST | Run test directive |
| `/api/v1/mission/{id}` | GET | Get mission status |
| `/api/v1/missions` | GET | List recent missions |
| `/api/v1/maritime/scan-barge` | POST | Maritime barge scan |

## Example Requests

### Process a Directive

```bash
curl -X POST $SERVICE_URL/api/v1/directive \
  -H "Content-Type: application/json" \
  -d '{
    "directive": "Analyze weather conditions for drone deployment at Mississippi River Mile Marker 142",
    "priority": "HIGH"
  }'
```

### Maritime Barge Scan

```bash
curl -X POST $SERVICE_URL/api/v1/maritime/scan-barge \
  -H "Content-Type: application/json" \
  -d '{
    "barge_id": "DELTA-7",
    "location": "Mississippi River Mile Marker 142",
    "weather": "Clear, wind 5 knots",
    "priority": "HIGH"
  }'
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ANTHROPIC_API_KEY` | Anthropic API key (from Secret Manager) | - |
| `GOOGLE_AI_API_KEY` | Google AI API key (from Secret Manager) | - |
| `LOG_LEVEL` | Logging level | INFO |
| `FREQ_LAW_TIMEOUT_MS` | FREQ LAW timeout | 2000 |

### Scaling

Edit `service.yaml` to adjust:

```yaml
annotations:
  autoscaling.knative.dev/minScale: "0"   # Scale to zero
  autoscaling.knative.dev/maxScale: "10"  # Max instances
```

## Cost Estimate

Cloud Run charges only when handling requests:

| Component | Estimate |
|-----------|----------|
| Cloud Run | ~$0.00002400 per vCPU-second |
| Memory | ~$0.00000250 per GiB-second |
| Anthropic API | ~$15/million input tokens |
| Google AI | ~$0.35/million tokens |

**Typical mission:** ~$0.01 - $0.05 depending on complexity

## Troubleshooting

### View Logs

```bash
gcloud run services logs read freq-ai-lattice --region us-central1
```

### Check Service Status

```bash
gcloud run services describe freq-ai-lattice --region us-central1
```

### Update Secrets

```bash
echo -n 'NEW-API-KEY' | \
  gcloud secrets versions add anthropic-api-key --data-file=-
```

## Files

```
infrastructure/gcp/
├── README.md           # This file
├── app.py              # FastAPI application
├── Dockerfile          # Container definition
├── requirements.txt    # Python dependencies
├── service.yaml        # Cloud Run service config
├── cloudbuild.yaml     # Cloud Build config
└── deploy.sh           # Deployment script
```
