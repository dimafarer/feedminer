"""
End-to-end test of the Strands-based model switching with frontend API.
"""

import requests
import json

# Test the deployed API endpoints directly (same as frontend would use)
API_BASE = "https://wqtfb6rv15.execute-api.us-west-2.amazonaws.com/dev"

def test_anthropic_endpoint():
    """Test Anthropic provider via deployed API."""
    print("🧪 Testing Anthropic endpoint...")
    
    response = requests.post(
        f"{API_BASE}/analyze/test",
        headers={"Content-Type": "application/json"},
        json={
            "provider": "anthropic",
            "model": "claude-3-5-sonnet-20241022",  
            "temperature": 0.7,
            "prompt": "This is an end-to-end test. Please respond with: E2E Anthropic Success!"
        }
    )
    
    print(f"Status Code: {response.status_code}")
    result = response.json()
    print(f"Success: {result.get('success')}")
    print(f"Provider: {result.get('provider')}")
    print(f"Response: {result.get('response', {}).get('content', '')[:100]}...")
    return result.get('success', False)

def test_bedrock_endpoint():
    """Test Bedrock provider via deployed API."""
    print("\n🧪 Testing Bedrock endpoint...")
    
    response = requests.post(
        f"{API_BASE}/analyze/test",
        headers={"Content-Type": "application/json"},
        json={
            "provider": "bedrock",
            "model": "anthropic.claude-3-5-sonnet-20241022-v2:0",
            "temperature": 0.7,
            "prompt": "This is an end-to-end test. Please respond with: E2E Bedrock Success!"
        }
    )
    
    print(f"Status Code: {response.status_code}")
    result = response.json()
    print(f"Success: {result.get('success')}")
    print(f"Provider: {result.get('provider')}")
    print(f"Response: {result.get('response', {}).get('content', '')[:100]}...")
    return result.get('success', False)

def test_comparison_endpoint():
    """Test provider comparison via deployed API."""
    print("\n🧪 Testing comparison endpoint...")
    
    response = requests.post(
        f"{API_BASE}/compare/test",
        headers={"Content-Type": "application/json"},
        json={
            "providers": [
                {"provider": "anthropic", "model": "claude-3-5-sonnet-20241022"},
                {"provider": "bedrock", "model": "anthropic.claude-3-5-sonnet-20241022-v2:0"}
            ],
            "temperature": 0.7,
            "prompt": "Compare test: please respond with your provider name."
        }
    )
    
    print(f"Status Code: {response.status_code}")
    result = response.json()
    print(f"Success: {result.get('success')}")
    
    if result.get('success'):
        comparison = result.get('comparison', {})
        providers = comparison.get('providers', [])
        print(f"Providers tested: {providers}")
        
        summary = comparison.get('summary', {})
        if 'performance_comparison' in summary:
            perf = summary['performance_comparison']
            print(f"Fastest provider: {perf.get('fastest_provider')} ({perf.get('fastest_time_ms')}ms)")
    
    return result.get('success', False) and len(result.get('comparison', {}).get('providers', [])) == 2

if __name__ == "__main__":
    print("🚀 End-to-End Strands Model Switching Test\n")
    
    tests_passed = 0
    total_tests = 3
    
    # Test individual providers
    if test_anthropic_endpoint():
        tests_passed += 1
        print("✅ Anthropic test passed")
    else:
        print("❌ Anthropic test failed")
    
    if test_bedrock_endpoint():
        tests_passed += 1
        print("✅ Bedrock test passed")
    else:
        print("❌ Bedrock test failed")
    
    # Test comparison
    if test_comparison_endpoint():
        tests_passed += 1
        print("✅ Comparison test passed")
    else:
        print("❌ Comparison test failed")
    
    print(f"\n📊 Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Strands model switching is working end-to-end.")
    else:
        print("⚠️  Some tests failed. Check the implementation.")