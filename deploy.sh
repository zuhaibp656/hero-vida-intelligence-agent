#!/usr/bin/env bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "=========================================================="
echo " Deploy / Update Hero VIDA Agent on Agent Platform"
echo "=========================================================="

# Default Project & Region
CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null | grep -v "unset" || echo "zuhaibp-ai")
DEFAULT_ENGINE_ID="8827320801704280064"

read -p "Enter your Argolis GCP Project ID [${CURRENT_PROJECT}]: " PROJECT_ID
PROJECT_ID=${PROJECT_ID:-$CURRENT_PROJECT}

read -p "Enter GCP Region (default: us-central1): " REGION
REGION=${REGION:-us-central1}

read -p "Update existing Agent Engine ID? [${DEFAULT_ENGINE_ID} / press Enter to update, or 'new' to create a fresh instance]: " ENGINE_CHOICE
ENGINE_CHOICE=${ENGINE_CHOICE:-$DEFAULT_ENGINE_ID}

echo ""
echo "Deploying Agent to Vertex AI Agent Engine..."
echo "Project: $PROJECT_ID | Region: $REGION"

# Disable telemetry prompt
./venv/bin/adk telemetry disable 2>/dev/null || true
export PYTHONPATH="$DIR"

if [ "$ENGINE_CHOICE" = "new" ] || [ -z "$ENGINE_CHOICE" ]; then
  echo "Action: Creating a NEW Agent Engine instance..."
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
echo " Deployment Complete!"
echo " Changes are live immediately on the Agent Platform runtime."
echo "=========================================================="
