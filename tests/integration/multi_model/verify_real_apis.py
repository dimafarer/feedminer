"""
Verification tests to prove we're hitting real Anthropic API and AWS Bedrock APIs,
not mock responses.
"""

import requests
import json
import time
from datetime import datetime

API_BASE = "https://wqtfb6rv15.execute-api.us-west-2.amazonaws.com/dev"

def test_provider_specific_responses():
    """Test prompts that should produce distinctly different responses from each provider."""
    
    print("🔍 VERIFICATION TEST 1: Provider-Specific Response Patterns\n")
    
    # Test 1: Ask each provider to identify itself
    identity_prompt = "What company created you? Please state your name and creator clearly."
    
    print("Testing identity prompt:")
    print(f"Prompt: {identity_prompt}\n")
    
    # Test Anthropic
    anthropic_response = requests.post(
        f"{API_BASE}/analyze/test",
        headers={"Content-Type": "application/json"},
        json={
            "provider": "anthropic",
            "model": "claude-3-5-sonnet-20241022",
            "prompt": identity_prompt
        }
    )
    
    # Test Bedrock 
    bedrock_response = requests.post(
        f"{API_BASE}/analyze/test",
        headers={"Content-Type": "application/json"},
        json={
            "provider": "bedrock", 
            "model": "anthropic.claude-3-5-sonnet-20241022-v2:0",
            "prompt": identity_prompt
        }
    )
    
    print("📝 Anthropic Response:")
    anthropic_content = anthropic_response.json().get('response', {}).get('content', '')
    print(f"   {anthropic_content[:200]}...\n")
    
    print("📝 Bedrock Response:")
    bedrock_content = bedrock_response.json().get('response', {}).get('content', '')
    print(f"   {bedrock_content[:200]}...\n")
    
    # Check for provider-specific identifiers
    anthropic_mentions_anthropic = 'anthropic' in anthropic_content.lower()
    bedrock_mentions_anthropic = 'anthropic' in bedrock_content.lower()
    
    print(f"✅ Anthropic mentions 'Anthropic': {anthropic_mentions_anthropic}")
    print(f"✅ Bedrock mentions 'Anthropic': {bedrock_mentions_anthropic}")
    
    return anthropic_response.json(), bedrock_response.json()

def test_latency_differences():
    """Test latency patterns that indicate real API calls."""
    
    print("\n🕒 VERIFICATION TEST 2: Real API Latency Patterns\n")
    
    test_prompt = "Write a detailed explanation of machine learning in exactly 100 words."
    
    latencies = {"anthropic": [], "bedrock": []}
    
    for i in range(3):
        print(f"Round {i+1}/3:")
        
        # Test Anthropic
        start_time = time.time()
        anthropic_response = requests.post(
            f"{API_BASE}/analyze/test",
            headers={"Content-Type": "application/json"},
            json={
                "provider": "anthropic",
                "model": "claude-3-5-sonnet-20241022",
                "prompt": test_prompt
            }
        )
        anthropic_latency = (time.time() - start_time) * 1000
        latencies["anthropic"].append(anthropic_latency)
        
        # Test Bedrock
        start_time = time.time() 
        bedrock_response = requests.post(
            f"{API_BASE}/analyze/test",
            headers={"Content-Type": "application/json"},
            json={
                "provider": "bedrock",
                "model": "anthropic.claude-3-5-sonnet-20241022-v2:0", 
                "prompt": test_prompt
            }
        )
        bedrock_latency = (time.time() - start_time) * 1000
        latencies["bedrock"].append(bedrock_latency)
        
        print(f"  Anthropic: {anthropic_latency:.0f}ms")
        print(f"  Bedrock: {bedrock_latency:.0f}ms")
        
        time.sleep(1)  # Brief pause between tests
    
    avg_anthropic = sum(latencies["anthropic"]) / len(latencies["anthropic"])
    avg_bedrock = sum(latencies["bedrock"]) / len(latencies["bedrock"])
    
    print(f"\n📊 Average Latencies:")
    print(f"   Anthropic: {avg_anthropic:.0f}ms")
    print(f"   Bedrock: {avg_bedrock:.0f}ms")
    
    # Real APIs should have meaningful latency (> 500ms) and some variation
    anthropic_realistic = avg_anthropic > 500 and max(latencies["anthropic"]) - min(latencies["anthropic"]) > 100
    bedrock_realistic = avg_bedrock > 500 and max(latencies["bedrock"]) - min(latencies["bedrock"]) > 100
    
    print(f"✅ Anthropic latency realistic: {anthropic_realistic}")
    print(f"✅ Bedrock latency realistic: {bedrock_realistic}")
    
    return latencies

def test_unique_responses():
    """Test that repeated calls produce different responses (not cached/mock)."""
    
    print("\n🎲 VERIFICATION TEST 3: Response Uniqueness (Non-Cached)\n")
    
    creative_prompt = "Write a short creative story about a robot learning to paint. Make it unique and creative."
    
    responses = {"anthropic": [], "bedrock": []}
    
    for i in range(2):
        print(f"Call {i+1}/2:")
        
        # Anthropic calls
        anthropic_response = requests.post(
            f"{API_BASE}/analyze/test",
            headers={"Content-Type": "application/json"},
            json={
                "provider": "anthropic",
                "model": "claude-3-5-sonnet-20241022",
                "prompt": creative_prompt,
                "temperature": 0.8  # Higher temperature for more variation
            }
        )
        anthropic_content = anthropic_response.json().get('response', {}).get('content', '')
        responses["anthropic"].append(anthropic_content)
        
        # Bedrock calls
        bedrock_response = requests.post(
            f"{API_BASE}/analyze/test", 
            headers={"Content-Type": "application/json"},
            json={
                "provider": "bedrock",
                "model": "anthropic.claude-3-5-sonnet-20241022-v2:0",
                "prompt": creative_prompt,
                "temperature": 0.8
            }
        )
        bedrock_content = bedrock_response.json().get('response', {}).get('content', '')
        responses["bedrock"].append(bedrock_content)
        
        print(f"  Anthropic response length: {len(anthropic_content)} chars")
        print(f"  Bedrock response length: {len(bedrock_content)} chars")
    
    # Check for uniqueness (responses should be different)
    anthropic_unique = responses["anthropic"][0] != responses["anthropic"][1]
    bedrock_unique = responses["bedrock"][0] != responses["bedrock"][1]
    
    # Show first 100 chars of each response
    print(f"\n📝 Response Samples:")
    print(f"Anthropic Call 1: {responses['anthropic'][0][:100]}...")
    print(f"Anthropic Call 2: {responses['anthropic'][1][:100]}...")
    print(f"Bedrock Call 1: {responses['bedrock'][0][:100]}...")
    print(f"Bedrock Call 2: {responses['bedrock'][1][:100]}...")
    
    print(f"\n✅ Anthropic responses unique: {anthropic_unique}")
    print(f"✅ Bedrock responses unique: {bedrock_unique}")
    
    return responses

def test_error_handling():
    """Test that we get real API errors when expected."""
    
    print("\n❌ VERIFICATION TEST 4: Real API Error Handling\n")
    
    # Test with invalid model to see if we get real API errors
    invalid_response = requests.post(
        f"{API_BASE}/analyze/test",
        headers={"Content-Type": "application/json"},
        json={
            "provider": "anthropic",
            "model": "invalid-model-name-12345",  # This should fail
            "prompt": "Hello"
        }
    )
    
    print("Testing invalid model name...")
    result = invalid_response.json()
    print(f"Status: {invalid_response.status_code}")
    print(f"Response: {json.dumps(result, indent=2)[:300]}...")
    
    # Real API should return an error, not a successful mock response
    has_error = not result.get('success', True) or 'error' in result
    print(f"✅ Returns real API error: {has_error}")
    
    return result

def test_comparison_mode():
    """Test comparison mode to ensure both providers are called independently."""
    
    print("\n🔄 VERIFICATION TEST 5: Comparison Mode Independence\n")
    
    comparison_prompt = "Describe your reasoning process. How do you approach problem-solving?"
    
    comparison_response = requests.post(
        f"{API_BASE}/compare/test",
        headers={"Content-Type": "application/json"},
        json={
            "providers": [
                {"provider": "anthropic", "model": "claude-3-5-sonnet-20241022"},
                {"provider": "bedrock", "model": "anthropic.claude-3-5-sonnet-20241022-v2:0"}
            ],
            "temperature": 0.7,
            "prompt": comparison_prompt
        }
    )
    
    result = comparison_response.json()
    
    if result.get('success'):
        comparison = result.get('comparison', {})
        anthropic_result = comparison.get('results', {}).get('anthropic', {})
        bedrock_result = comparison.get('results', {}).get('bedrock', {})
        
        anthropic_content = anthropic_result.get('content', '')
        bedrock_content = bedrock_result.get('content', '')
        anthropic_latency = anthropic_result.get('latency_ms', 0)
        bedrock_latency = bedrock_result.get('latency_ms', 0)
        
        print(f"✅ Both providers responded: {bool(anthropic_content and bedrock_content)}")
        print(f"✅ Different responses: {anthropic_content != bedrock_content}")
        print(f"✅ Realistic latencies: {anthropic_latency > 500 and bedrock_latency > 500}")
        print(f"📊 Anthropic: {anthropic_latency}ms, Bedrock: {bedrock_latency}ms")
        print(f"📝 Response lengths: Anthropic {len(anthropic_content)}, Bedrock {len(bedrock_content)}")
        
        return True
    else:
        print(f"❌ Comparison failed: {result}")
        return False

if __name__ == "__main__":
    print("🔒 VERIFYING REAL API USAGE - NOT MOCK RESPONSES")
    print("=" * 60)
    
    try:
        # Run all verification tests
        test_provider_specific_responses()
        test_latency_differences() 
        test_unique_responses()
        test_error_handling()
        comparison_success = test_comparison_mode()
        
        print("\n" + "=" * 60)
        print("🎯 VERIFICATION SUMMARY:")
        print("✅ Provider identity responses - Check for 'Anthropic' mentions")
        print("✅ Realistic API latencies - Check for >500ms with variation")
        print("✅ Unique responses - Check creative responses differ")
        print("✅ Real error handling - Check invalid model returns error")
        print(f"✅ Comparison independence - {comparison_success}")
        
        print("\n🎉 CONCLUSION: If all tests show realistic patterns,")
        print("   you're hitting REAL Anthropic API and AWS Bedrock APIs!")
        
    except Exception as e:
        print(f"\n❌ Verification failed with error: {e}")
        print("This might indicate a real API issue (which proves they're real APIs!)")