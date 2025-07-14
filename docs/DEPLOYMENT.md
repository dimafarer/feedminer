# FeedMiner Deployment Guide

**Version**: 0.1.0 (MVP)  
**Status**: Infrastructure Complete - Bedrock Integration This Week (July 16)

## Prerequisites

1. **AWS CLI** configured with appropriate permissions
2. **SAM CLI** installed
3. **Python 3.12+** with virtual environment
4. **Anthropic API key** OR **AWS Bedrock access**

## Quick Deployment

### 1. Setup Environment
```bash
./scripts/setup.sh
source feedminer-env/bin/activate
```

### 2. Deploy to AWS
```bash
# Current: With Anthropic API key (for rapid prototyping)
./scripts/deploy.sh dev sk-ant-your-key-here

# Coming July 16: With Bedrock (for model comparison)
./scripts/deploy.sh dev
```

### 3. Test Deployment
```bash
./scripts/run_tests.sh
```

## Manual Deployment

### 1. Build Application
```bash
sam validate --lint
sam build
```

### 2. Deploy
```bash
# Anthropic API option
sam deploy --parameter-overrides \
  EnableWebSocket=true \
  AnthropicApiKey=sk-ant-your-key-here

# Bedrock option  
sam deploy --parameter-overrides \
  EnableWebSocket=true \
  AnthropicApiKey=BEDROCK_WILL_OVERRIDE
```

## Environment Configuration

### Parameters
- `Environment`: Deployment stage (dev/staging/prod)
- `AnthropicApiKey`: API key for Claude access
- `AllowedOrigins`: CORS origins for WebSocket connections
- `EnableWebSocket`: Enable/disable WebSocket API

### Environment Variables (Auto-configured)
- `ANTHROPIC_API_KEY`: Claude API access
- `CONTENT_BUCKET`: S3 bucket name
- `WEBSOCKET_API_ENDPOINT`: WebSocket URL
- `CONTENT_TABLE`: DynamoDB content table
- `JOBS_TABLE`: DynamoDB jobs table
- `CONNECTIONS_TABLE`: DynamoDB connections table

## Local Development

### SAM Local
```bash
# Start API locally (WebSocket disabled for compatibility)
sam local start-api --parameter-overrides EnableWebSocket=false

# Invoke specific function
sam local invoke ContentUploadFunction --event tests/data/sample_instagram_enhanced_format.json
```

### Testing
```bash
# All tests
./scripts/run_tests.sh

# Specific test types
./scripts/run_tests.sh api
./scripts/run_tests.sh websocket
./scripts/run_tests.sh pytest
```

## Troubleshooting

### Common Issues

**Deployment Failures**
- Check AWS credentials: `aws sts get-caller-identity`
- Validate template: `sam validate --lint`
- Check build output: `sam build --debug`

**Runtime Errors**
- Check CloudWatch logs: `aws logs tail /aws/lambda/feedminer-content-upload-dev --follow`
- Test individual functions: `sam local invoke FunctionName`

**WebSocket Issues**
- SAM local doesn't support WebSocket - deploy to AWS for testing
- Check connection table: `aws dynamodb scan --table-name feedminer-connections-dev`

## Multi-Environment Setup

### Development
```bash
sam deploy --parameter-overrides Environment=dev EnableWebSocket=true
```

### Staging
```bash
sam deploy --parameter-overrides Environment=staging EnableWebSocket=true
```

### Production
```bash
sam deploy --parameter-overrides Environment=prod EnableWebSocket=true
```

Each environment creates separate AWS resources with environment-specific naming.