#!/bin/bash
set -e

# Arguments
ENVIRONMENT=${1:-staging} # Default to staging
SERVICE_NAME="reverb-backend"
REGION="us-central1"
ENV_FILE=".env.${ENVIRONMENT}"

echo "Deploying $SERVICE_NAME to Google Cloud Run (Environment: $ENVIRONMENT)..."

if [ ! -f "$ENV_FILE" ]; then
    echo "Error: Configuration file $ENV_FILE not found."
    exit 1
fi

echo "Loading environment variables from $ENV_FILE..."

# Read CLOUDSQL_INSTANCE
CLOUDSQL_INSTANCE=$(grep "^CLOUDSQL_INSTANCE=" "$ENV_FILE" | cut -d '=' -f2)

# Prepare environment variables
# Read file, ignore comments/empty lines, replace newlines with commas
# We use a temporary variable to hold the content to avoid pipe subshell issues
ENV_CONTENT=$(grep -v '^#' "$ENV_FILE" | grep -v '^$')
ENV_VARS=$(echo "$ENV_CONTENT" | tr '\n' ',' | sed 's/,$//')

# Construct the command using an array to handle spaces/args correctly
CMD=(gcloud run deploy "$SERVICE_NAME")
CMD+=(--source .)
CMD+=(--platform managed)
CMD+=(--region "$REGION")
CMD+=(--allow-unauthenticated)
CMD+=(--memory 512Mi)
CMD+=(--cpu 1)
CMD+=(--min-instances 1)
CMD+=(--max-instances 1)
CMD+=(--set-env-vars "ENV=$ENVIRONMENT,$ENV_VARS")

if [ -n "$CLOUDSQL_INSTANCE" ]; then
    echo "Detected Cloud SQL Instance: $CLOUDSQL_INSTANCE"
    CMD+=(--add-cloudsql-instances "$CLOUDSQL_INSTANCE")
fi

# Execute
"${CMD[@]}"

echo "Deployment command finished."
