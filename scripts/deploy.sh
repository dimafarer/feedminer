#!/bin/bash
"""
Deploy FeedMiner to AWS.
Usage: ./scripts/deploy.sh [environment] [anthropic_key]
"""

set -e

# Default environment
ENV=${1:-"dev"}
ANTHROPIC_KEY=${2:-""}

# Activate virtual environment if not already active
if [[ -z "$VIRTUAL_ENV" ]]; then
    source feedminer-env/bin/activate
fi

echo "🚀 Deploying FeedMiner to AWS"
echo "=============================="
echo "Environment: $ENV"

# Validate SAM template
echo "🔍 Validating SAM template..."
sam validate --lint

# Build application
echo "🔨 Building application..."
sam build

# Deploy based on environment
if [[ -n "$ANTHROPIC_KEY" ]]; then
    echo "🌐 Deploying with Anthropic API key..."
    sam deploy --no-confirm-changeset \
        --parameter-overrides \
        Environment=$ENV \
        EnableWebSocket=true \
        AnthropicApiKey=$ANTHROPIC_KEY
else
    echo "🌐 Deploying with Bedrock (no API key)..."
    sam deploy --no-confirm-changeset \
        --parameter-overrides \
        Environment=$ENV \
        EnableWebSocket=true \
        AnthropicApiKey=BEDROCK_WILL_OVERRIDE
fi

# Get deployment outputs
echo ""
echo "📋 Deployment Outputs:"
echo "====================="
aws cloudformation describe-stacks \
    --stack-name feedminer \
    --query 'Stacks[0].Outputs[*].[OutputKey,OutputValue]' \
    --output table

echo ""
echo "✅ Deployment completed successfully!"
echo ""
echo "🧪 Run tests with: ./scripts/run_tests.sh"