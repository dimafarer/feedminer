#!/bin/bash
"""
Run FeedMiner test suite.
Usage: ./scripts/run_tests.sh [test_type]
"""

set -e

# Activate virtual environment if not already active
if [[ -z "$VIRTUAL_ENV" ]]; then
    source feedminer-env/bin/activate
fi

# Default to all tests if no argument provided
TEST_TYPE=${1:-"all"}

echo "🧪 Running FeedMiner Test Suite"
echo "================================"

case $TEST_TYPE in
    "api"|"rest")
        echo "🔄 Running REST API tests..."
        python tests/test_api.py
        ;;
    "websocket"|"ws")
        echo "🔄 Running WebSocket tests..."
        python tests/test_websocket.py
        ;;
    "all")
        echo "🔄 Running all tests..."
        echo ""
        echo "📡 REST API Tests:"
        echo "-------------------"
        python tests/test_api.py
        echo ""
        echo "🔌 WebSocket Tests:"
        echo "-------------------"
        python tests/test_websocket.py
        ;;
    "pytest")
        echo "🔄 Running pytest suite..."
        pytest tests/ -v
        ;;
    *)
        echo "❌ Unknown test type: $TEST_TYPE"
        echo "Valid options: api, websocket, all, pytest"
        exit 1
        ;;
esac

echo ""
echo "✅ Test run completed!"