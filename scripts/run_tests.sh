#!/bin/bash
# Run FeedMiner test suite.
# Usage: ./scripts/run_tests.sh [test_type]

set -e

# Use virtual environment Python if available, otherwise system Python
if [[ -f "feedminer-env/bin/python" ]]; then
    PYTHON="./feedminer-env/bin/python"
    echo "🔄 Using virtual environment Python..."
else
    PYTHON="python3"
    echo "🔄 Using system Python..."
fi

# Default to all tests if no argument provided
TEST_TYPE=${1:-"all"}

echo "🧪 Running FeedMiner Test Suite"
echo "================================"

case $TEST_TYPE in
    "api"|"rest")
        echo "🔄 Running REST API tests..."
        $PYTHON tests/test_api.py
        ;;
    "websocket"|"ws")
        echo "🔄 Running WebSocket tests..."
        $PYTHON tests/test_websocket.py
        ;;
    "all")
        echo "🔄 Running all tests..."
        echo ""
        echo "📡 REST API Tests:"
        echo "-------------------"
        $PYTHON tests/test_api.py
        echo ""
        echo "🔌 WebSocket Tests:"
        echo "-------------------"
        $PYTHON tests/test_websocket.py
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