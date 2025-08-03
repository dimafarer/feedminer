"""
Test the new Strands-based model switching implementation locally.
"""

import json
import os
import sys
sys.path.append('src/api')

# Set environment variables for testing
os.environ['ANTHROPIC_API_KEY'] = open('../creds/anthropic-apikey').readlines()[1].strip()
os.environ['AWS_REGION'] = 'us-west-2'

from strands_model_switching import handle_test_strands_integration, create_strands_agent, extract_strands_response

def test_basic_strands_functionality():
    """Test basic Strands agent creation and response extraction."""
    
    print("Testing Strands agent creation and response extraction...")
    
    # Test Anthropic
    print("\n1. Testing Anthropic agent creation...")
    try:
        agent = create_strands_agent("anthropic", "claude-3-5-sonnet-20241022", 0.7)
        result = agent("Hello! This is a test message.")
        extracted = extract_strands_response(result)
        print(f"✅ Anthropic agent works. Response: {extracted['content'][:100]}...")
    except Exception as e:
        print(f"❌ Anthropic agent failed: {e}")
    
    # Test Bedrock
    print("\n2. Testing Bedrock agent creation...")
    try:
        agent = create_strands_agent("bedrock", "anthropic.claude-3-5-sonnet-20241022-v2:0", 0.7)
        result = agent("Hello! This is a test message.")
        extracted = extract_strands_response(result)
        print(f"✅ Bedrock agent works. Response: {extracted['content'][:100]}...")
    except Exception as e:
        print(f"❌ Bedrock agent failed: {e}")

def test_lambda_handler_simulation():
    """Test the Lambda handler with simulated events."""
    
    print("\n\nTesting Lambda handler simulation...")
    
    headers = {'Content-Type': 'application/json'}
    
    # Test Anthropic
    print("\n3. Testing Anthropic test endpoint...")
    anthropic_body = {
        "provider": "anthropic",
        "model": "claude-3-5-sonnet-20241022",
        "prompt": "Hello! Please respond with 'Anthropic via Strands working!'"
    }
    
    try:
        result = handle_test_strands_integration(anthropic_body, headers)
        response_data = json.loads(result['body'])
        print(f"✅ Anthropic test endpoint works.")
        print(f"   Status: {result['statusCode']}")
        print(f"   Success: {response_data.get('success')}")
        print(f"   Response: {response_data.get('response', {}).get('content', '')[:100]}...")
    except Exception as e:
        print(f"❌ Anthropic test endpoint failed: {e}")
    
    # Test Bedrock
    print("\n4. Testing Bedrock test endpoint...")
    bedrock_body = {
        "provider": "bedrock",
        "model": "anthropic.claude-3-5-sonnet-20241022-v2:0",
        "prompt": "Hello! Please respond with 'Bedrock via Strands working!'"
    }
    
    try:
        result = handle_test_strands_integration(bedrock_body, headers)
        response_data = json.loads(result['body'])
        print(f"✅ Bedrock test endpoint works.")
        print(f"   Status: {result['statusCode']}")
        print(f"   Success: {response_data.get('success')}")
        print(f"   Response: {response_data.get('response', {}).get('content', '')[:100]}...")
    except Exception as e:
        print(f"❌ Bedrock test endpoint failed: {e}")

if __name__ == "__main__":
    print("🧪 Testing Strands-based Model Switching Implementation\n")
    
    test_basic_strands_functionality()
    test_lambda_handler_simulation()
    
    print("\n✅ Testing complete!")