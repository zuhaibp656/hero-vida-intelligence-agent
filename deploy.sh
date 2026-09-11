#!/usr/bin/env bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "=========================================================="
echo " Deploy Hero VIDA Intelligence Agent to Google Cloud"
echo " Vertex AI Agent Engine (Reasoning Engine)"
echo "=========================================================="

# 1. Non-interactive or custom parameters via flags/environment
# Flags: --auto, --update, --new, --id=<ENGINE_ID>, --project=<PROJECT_ID>, --region=<REGION>
AUTO_MODE=${AUTO_DEPLOY:-0}
INPUT_ENGINE_ID=""
INPUT_PROJECT_OVERRIDE=""
INPUT_REGION_OVERRIDE=""

for arg in "$@"; do
  case $arg in
    --auto|-y)
      AUTO_MODE=1
      shift
      ;;
    --update)
      AUTO_MODE=1
      ENGINE_CHOICE="3838207625833480192"
      shift
      ;;
    --new)
      AUTO_MODE=1
      ENGINE_CHOICE="new"
      shift
      ;;
    --id=*)
      INPUT_ENGINE_ID="${arg#*=}"
      ENGINE_CHOICE="$INPUT_ENGINE_ID"
      AUTO_MODE=1
      shift
      ;;
    --project=*)
      INPUT_PROJECT_OVERRIDE="${arg#*=}"
      shift
      ;;
    --region=*)
      INPUT_REGION_OVERRIDE="${arg#*=}"
      shift
      ;;
  esac
done

# Detect Current Project
DETECTED_PROJECT=$(gcloud config get-value project 2>/dev/null | grep -v "unset" || echo "")

if [ "$AUTO_MODE" = "1" ]; then
  PROJECT_ID=${INPUT_PROJECT_OVERRIDE:-${GOOGLE_CLOUD_PROJECT:-${DETECTED_PROJECT:-"zuhaibp-ai"}}}
  REGION=${INPUT_REGION_OVERRIDE:-${GOOGLE_CLOUD_LOCATION:-"us-central1"}}
  if [ -z "$ENGINE_CHOICE" ]; then
    if [ "$PROJECT_ID" = "zuhaibp-ai" ] || [ "$PROJECT_ID" = "632239123109" ]; then
      ENGINE_CHOICE="3838207625833480192"
    else
      ENGINE_CHOICE="new"
    fi
  fi
  echo "🤖 Automated Mode Active:"
  echo "   Project ID: $PROJECT_ID"
  echo "   Region:     $REGION"
  echo "   Target ID:  $ENGINE_CHOICE"
else
  # Interactive mode
  ACTIVE_ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>/dev/null || echo "")
  if [ -n "$ACTIVE_ACCOUNT" ]; then
    echo "Authenticated GCP Account: $ACTIVE_ACCOUNT"
  fi

  if [ -n "$DETECTED_PROJECT" ]; then
    read -p "Enter Target Google Cloud Project ID [$DETECTED_PROJECT]: " INPUT_PROJECT
    PROJECT_ID=${INPUT_PROJECT:-$DETECTED_PROJECT}
  else
    read -p "Enter Target Google Cloud Project ID: " PROJECT_ID
    while [ -z "$PROJECT_ID" ]; do
      read -p "Project ID cannot be empty. Enter Target Google Cloud Project ID: " PROJECT_ID
    done
  fi

  read -p "Enter GCP Region [default: us-central1]: " INPUT_REGION
  REGION=${INPUT_REGION:-us-central1}

  DEFAULT_ENGINE="new"
  if [ "$PROJECT_ID" = "zuhaibp-ai" ] || [ "$PROJECT_ID" = "632239123109" ]; then
    DEFAULT_ENGINE="3838207625833480192"
  fi

  read -p "Deploy new instance or update existing? Type 'new' or enter existing Agent Engine ID [default: $DEFAULT_ENGINE]: " INPUT_CHOICE
  ENGINE_CHOICE=${INPUT_CHOICE:-"$DEFAULT_ENGINE"}
fi

echo ""
echo "Preparing deployment environment..."

# 1. Ensure Python virtual environment and dependencies
if [ ! -f "./venv/bin/adk" ]; then
  echo "Setting up Python virtual environment and installing dependencies..."
  python3 -m venv venv
  ./venv/bin/pip install --upgrade pip --quiet
  ./venv/bin/pip install -r requirements.txt --quiet
fi

# 2. Enable Required Google Cloud APIs
echo "Verifying Vertex AI and Cloud Storage APIs in project $PROJECT_ID..."
gcloud services enable aiplatform.googleapis.com storage.googleapis.com --project="$PROJECT_ID" 2>/dev/null || true

# 3. Create or Verify Reports Cloud Storage Bucket
BUCKET_NAME="${PROJECT_ID}-hero-vida-reports"
echo "Verifying Cloud Storage bucket: gs://$BUCKET_NAME ..."
if ! gcloud storage buckets describe "gs://$BUCKET_NAME" --project="$PROJECT_ID" >/dev/null 2>&1; then
  echo "Provisioning bucket gs://$BUCKET_NAME in region $REGION..."
  gcloud storage buckets create "gs://$BUCKET_NAME" --project="$PROJECT_ID" --location="$REGION" --uniform-bucket-level-access 2>/dev/null || true
  echo "✅ Bucket gs://$BUCKET_NAME provisioned successfully."
else
  echo "✅ Bucket gs://$BUCKET_NAME is verified and ready."
fi

# 4. Set up environment variables
export GOOGLE_CLOUD_PROJECT="$PROJECT_ID"
export GOOGLE_CLOUD_LOCATION="$REGION"
export GCS_BUCKET_NAME="$BUCKET_NAME"
export GOOGLE_GENAI_USE_ENTERPRISE=1
export PYTHONPATH="$DIR"

# Disable telemetry prompt
./venv/bin/adk telemetry disable 2>/dev/null || true

echo "Configured for Google Cloud Agent Platform & Gemini Enterprise (GOOGLE_GENAI_USE_ENTERPRISE=1)..."
echo "Deploying Agent to Vertex AI Agent Engine..."
echo "Project: $PROJECT_ID | Region: $REGION | Bucket: $BUCKET_NAME"

if [ "$ENGINE_CHOICE" = "new" ]; then
  echo "Action: Provisioning a fresh Agent Engine instance in $REGION..."
  ./venv/bin/adk deploy agent_engine \
    --project="$PROJECT_ID" \
    --region="$REGION" \
    --display_name="Hero VIDA Competitor Intelligence Agent" \
    --description="Autonomous competitive pricing and 15-city benchmark agent for Hero MotoCorp VIDA" \
    agent
else
  echo "Action: In-place updating active instance ID: $ENGINE_CHOICE..."
  ./venv/bin/adk deploy agent_engine \
    --project="$PROJECT_ID" \
    --region="$REGION" \
    --agent_engine_id="$ENGINE_CHOICE" \
    --display_name="Hero VIDA Competitor Intelligence Agent" \
    --description="Autonomous competitive pricing and 15-city benchmark agent for Hero MotoCorp VIDA" \
    agent
fi

echo ""
echo "=========================================================="
echo " 🚀 Deployment to Google Cloud Agent Platform Complete!"
echo "=========================================================="
echo ""
echo "1. Vertex AI Agent Playground:"
echo "   👉 https://console.cloud.google.com/vertex-ai/agents/agent-engines/locations/$REGION/agent-engines/${ENGINE_CHOICE:-3838207625833480192}/playground?project=$PROJECT_ID"
echo ""
echo "2. Reports Storage Bucket:"
echo "   👉 https://console.cloud.google.com/storage/browser/${BUCKET_NAME}/reports?project=$PROJECT_ID"
echo "=========================================================="
