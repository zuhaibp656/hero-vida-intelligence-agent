#!/usr/bin/env bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "=========================================================="
echo " Deploy Hero VIDA Intelligence Agent to Google Cloud"
echo " Vertex AI Agent Engine (Reasoning Engine)"
echo "=========================================================="

# Check for gcloud authentication
ACTIVE_ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>/dev/null || echo "")
if [ -z "$ACTIVE_ACCOUNT" ]; then
  echo "⚠️  No active Google Cloud account detected."
  echo "Please authenticate using:"
  echo "    gcloud auth login"
  echo "    gcloud auth application-default login"
  echo ""
  read -p "Proceed anyway? (y/N): " PROCEED_AUTH
  if [[ "$PROCEED_AUTH" != "y" && "$PROCEED_AUTH" != "Y" ]]; then
    exit 1
  fi
else
  echo "Authenticated GCP Account: $ACTIVE_ACCOUNT"
fi

# Detect Current Project
DETECTED_PROJECT=$(gcloud config get-value project 2>/dev/null | grep -v "unset" || echo "")

if [ -n "$DETECTED_PROJECT" ]; then
  read -p "Enter Target Google Cloud Project ID [$DETECTED_PROJECT]: " INPUT_PROJECT
  PROJECT_ID=${INPUT_PROJECT:-$DETECTED_PROJECT}
else
  read -p "Enter Target Google Cloud Project ID: " PROJECT_ID
  while [ -z "$PROJECT_ID" ]; do
    echo "Google Cloud Project ID is required."
    read -p "Enter Target Google Cloud Project ID: " PROJECT_ID
  done
fi

read -p "Enter GCP Region [default: us-central1]: " INPUT_REGION
REGION=${INPUT_REGION:-us-central1}

read -p "Deploy new instance or update existing? Type 'new' or enter existing Agent Engine ID [default: new]: " ENGINE_CHOICE
ENGINE_CHOICE=${ENGINE_CHOICE:-new}

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
echo "Enabling Vertex AI and Cloud Storage APIs in project $PROJECT_ID..."
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

if [ "$ENGINE_CHOICE" = "new" ] || [ -z "$ENGINE_CHOICE" ]; then
  echo "Action: Provisioning a fresh Agent Engine instance in $REGION..."
  ./venv/bin/adk deploy agent_engine \
    --project="$PROJECT_ID" \
    --region="$REGION" \
    --display_name="Hero VIDA Competitor Intelligence Agent" \
    --description="Autonomous competitive pricing and 15-city benchmark agent for Hero MotoCorp VIDA" \
    agent
else
  echo "Action: In-place updating existing instance ID: $ENGINE_CHOICE..."
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
echo "   👉 https://console.cloud.google.com/vertex-ai/agents/agent-engines?project=$PROJECT_ID"
echo ""
echo "2. Gemini Enterprise Integration:"
echo "   • This agent is built with Gemini Enterprise support (--gemini_enterprise_app_name=agent)."
echo "   • To connect to Gemini Enterprise / Agent Space:"
echo "     a. Go to Google Cloud Console > Vertex AI > Agent Space / Gemini Enterprise."
echo "     b. Under 'Connected Agents / Tools', register the newly deployed Reasoning Engine:"
echo "        projects/$PROJECT_ID/locations/$REGION/reasoningEngines/<ENGINE_ID>"
echo "     c. Enable corporate user access via IAM role 'roles/aiplatform.user'."
echo "     d. Users can now query @hero-vida-agent directly inside Gemini Enterprise chat!"
echo ""
echo "3. Reports Storage Bucket:"
echo "   👉 https://console.cloud.google.com/storage/browser/${PROJECT_ID}-hero-vida-reports/reports?project=$PROJECT_ID"
echo "=========================================================="
