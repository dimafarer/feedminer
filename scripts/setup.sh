#!/bin/bash
"""
Setup FeedMiner development environment.
Usage: ./scripts/setup.sh
"""

set -e

echo "🔧 Setting up FeedMiner Development Environment"
echo "=============================================="

# Check if Python 3.12+ is available
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.12"

if [[ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]]; then
    echo "❌ Python 3.12+ required. Found: $python_version"
    exit 1
fi

echo "✅ Python version: $python_version"

# Create virtual environment if it doesn't exist
if [[ ! -d "feedminer-env" ]]; then
    echo "🐍 Creating virtual environment..."
    python3 -m venv feedminer-env
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source feedminer-env/bin/activate

# Install development dependencies
echo "📥 Installing development dependencies..."
pip install -r requirements-dev.txt

# Install additional development tools
echo "🛠 Installing development tools..."
pip install pytest pytest-asyncio black flake8 mypy

# Check AWS CLI
if command -v aws &> /dev/null; then
    echo "✅ AWS CLI found"
    aws_identity=$(aws sts get-caller-identity 2>/dev/null || echo "Not configured")
    echo "🔐 AWS Identity: $aws_identity"
else
    echo "⚠️  AWS CLI not found. Install with: pip install awscli"
fi

# Check SAM CLI
if command -v sam &> /dev/null; then
    echo "✅ SAM CLI found: $(sam --version)"
else
    echo "⚠️  SAM CLI not found. Install from: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html"
fi

echo ""
echo "✅ Development environment setup complete!"
echo ""
echo "📝 Next steps:"
echo "  1. Activate environment: source feedminer-env/bin/activate"
echo "  2. Configure AWS credentials if needed"
echo "  3. Build: sam build"
echo "  4. Deploy: ./scripts/deploy.sh"
echo "  5. Test: ./scripts/run_tests.sh"