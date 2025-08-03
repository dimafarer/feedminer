#!/usr/bin/env python3
"""
Test Optimized 3-Model Comparison
Tests the reduced comparison to avoid API Gateway timeouts.
"""

import requests
import json
import time

API_BASE_URL = 'https://wqtfb6rv15.execute-api.us-west-2.amazonaws.com/dev'

def test_optimized_comparison():
    """Test the optimized 3-model comparison."""
    print("🧪 Testing Optimized 3-Model Comparison...")
    
    payload = {
        "providers": [
            # Claude family (best representative)
            {"provider": "anthropic", "model": "claude-3-5-sonnet-20241022", "temperature": 0.7},
            # Nova family (fastest, most cost-effective)
            {"provider": "nova", "model": "us.amazon.nova-micro-v1:0", "temperature": 0.7},
            # Llama family (fastest open-source)
            {"provider": "llama", "model": "meta.llama3-1-8b-instruct-v1:0", "temperature": 0.7},
        ],
        "prompt": "Explain artificial intelligence in one sentence, emphasizing your model family's strengths."
    }
    
    try:
        print(f"  📤 Sending request to /compare/test...")
        start_time = time.time()
        
        response = requests.post(
            f"{API_BASE_URL}/compare/test",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=45  # Give it a bit more time than API Gateway limit
        )
        
        end_time = time.time()
        total_latency_ms = int((end_time - start_time) * 1000)
        
        print(f"  ⏱️  Total request time: {total_latency_ms}ms")
        
        if response.status_code == 200:
            result = response.json()
            comparison_results = result.get('comparison', {}).get('results', {})
            
            print(f"  ✅ Comparison succeeded!")
            print(f"  📊 Results for {len(comparison_results)} providers:")
            
            successful_models = 0
            for provider, provider_result in comparison_results.items():
                if provider_result.get('success'):
                    successful_models += 1
                    latency = provider_result.get('latency_ms', 0)
                    model_family = provider_result.get('model_family', 'unknown')
                    cost_tier = provider_result.get('cost_tier', 'unknown')
                    content = provider_result.get('content', '')[:80]
                    print(f"     ✅ {provider}: {latency}ms, {model_family}, {cost_tier}")
                    print(f"        Response: {content}...")
                else:
                    error = provider_result.get('error', 'unknown error')
                    print(f"     ❌ {provider}: {error}")
            
            print(f"\n  📈 Performance Summary:")
            print(f"     Total time: {total_latency_ms}ms")
            print(f"     Successful models: {successful_models}/3")
            print(f"     Success rate: {(successful_models/3)*100:.1f}%")
            
            # Check if we're under the timeout limit
            if total_latency_ms < 25000:  # 25 seconds gives us buffer
                print(f"  ✅ Under timeout limit (25s buffer)")
                return True
            else:
                print(f"  ⚠️  Close to timeout limit")
                return successful_models >= 2
            
        else:
            print(f"  ❌ HTTP {response.status_code}")
            print(f"     Error: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"  ❌ Request timed out after 45 seconds")
        return False
    except Exception as e:
        print(f"  ❌ Exception: {str(e)}")
        return False

def test_individual_models():
    """Test each model individually to ensure they still work."""
    print("\n🔍 Testing Individual Models...")
    
    models = [
        ("anthropic", "claude-3-5-sonnet-20241022", "Claude Sonnet"),
        ("nova", "us.amazon.nova-micro-v1:0", "Nova Micro"),
        ("llama", "meta.llama3-1-8b-instruct-v1:0", "Llama 8B"),
    ]
    
    results = []
    for provider, model_id, name in models:
        payload = {
            "provider": provider,
            "model": model_id,
            "temperature": 0.7,
            "prompt": f"Hello from {name}! Please confirm you're working."
        }
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{API_BASE_URL}/analyze/test",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            end_time = time.time()
            
            latency_ms = int((end_time - start_time) * 1000)
            
            if response.status_code == 200:
                result = response.json()
                content = result.get('response', {}).get('content', '')[:60]
                model_family = result.get('response', {}).get('model_family', 'unknown')
                cost_tier = result.get('response', {}).get('cost_tier', 'unknown')
                
                print(f"  ✅ {name}: {latency_ms}ms, {model_family}, {cost_tier}")
                print(f"     {content}...")
                results.append(True)
            else:
                print(f"  ❌ {name}: HTTP {response.status_code}")
                results.append(False)
                
        except Exception as e:
            print(f"  ❌ {name}: {str(e)}")
            results.append(False)
    
    successful = sum(results)
    print(f"\n  📊 Individual Tests: {successful}/3 successful")
    return successful == 3

def main():
    """Run optimized comparison testing."""
    print("🚀 OPTIMIZED COMPARISON TESTING")
    print("="*50)
    
    # Test individual models first
    individual_success = test_individual_models()
    
    # Test optimized comparison
    comparison_success = test_optimized_comparison()
    
    print(f"\n" + "="*50)
    print("📊 OPTIMIZATION RESULTS")
    print("="*50)
    
    print(f"Individual Models: {'✅' if individual_success else '❌'}")
    print(f"3-Model Comparison: {'✅' if comparison_success else '❌'}")
    
    if individual_success and comparison_success:
        print(f"\n🎉 Optimization Successful!")
        print(f"✅ All models working individually")
        print(f"✅ 3-model comparison under timeout limit")
        print(f"✅ Ready for user testing")
        return True
    elif individual_success:
        print(f"\n⚠️  Partial Success")
        print(f"✅ Individual models working")
        print(f"❌ Comparison needs further optimization")
        return False
    else:
        print(f"\n❌ Issues Found")
        print(f"❌ Individual models having problems")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)