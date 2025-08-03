#!/usr/bin/env python3
"""
Test Production Nova and Llama Models
Tests the deployed backend API with Nova and Llama models.
"""

import requests
import json
import time
from typing import Dict, Any

API_BASE_URL = 'https://wqtfb6rv15.execute-api.us-west-2.amazonaws.com/dev'

def test_model(provider: str, model_id: str, name: str) -> Dict[str, Any]:
    """Test a specific model via the production API."""
    print(f"\n🧪 Testing {name}...")
    
    payload = {
        "provider": provider,
        "model": model_id,
        "temperature": 0.7,
        "prompt": f"Hello! Please respond with 'Working: {name}' to confirm this model is operational."
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{API_BASE_URL}/analyze/test",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        end_time = time.time()
        
        latency_ms = int((end_time - start_time) * 1000)
        
        if response.status_code == 200:
            result = response.json()
            content = result.get('response', {}).get('content', '')[:100]
            model_family = result.get('response', {}).get('model_family', 'unknown')
            cost_tier = result.get('response', {}).get('cost_tier', 'unknown')
            
            print(f"  ✅ {name}: {latency_ms}ms")
            print(f"     Response: {content}...")
            print(f"     Family: {model_family}, Cost: {cost_tier}")
            
            return {
                "success": True,
                "latency_ms": latency_ms,
                "model_family": model_family,
                "cost_tier": cost_tier,
                "content": content
            }
        else:
            print(f"  ❌ {name}: HTTP {response.status_code}")
            print(f"     Error: {response.text}")
            return {
                "success": False,
                "error": f"HTTP {response.status_code}: {response.text}",
                "latency_ms": latency_ms
            }
            
    except Exception as e:
        print(f"  ❌ {name}: Exception - {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "latency_ms": 0
        }

def test_6_model_comparison():
    """Test 6-model comparison via the production API."""
    print(f"\n⚖️  Testing 6-Model Comparison...")
    
    payload = {
        "providers": [
            {"provider": "anthropic", "model": "claude-3-5-sonnet-20241022", "temperature": 0.7},
            {"provider": "bedrock", "model": "anthropic.claude-3-5-sonnet-20241022-v2:0", "temperature": 0.7},
            {"provider": "nova", "model": "us.amazon.nova-micro-v1:0", "temperature": 0.7},
            {"provider": "nova", "model": "us.amazon.nova-lite-v1:0", "temperature": 0.7},
            {"provider": "llama", "model": "meta.llama3-1-8b-instruct-v1:0", "temperature": 0.7},
            {"provider": "llama", "model": "meta.llama3-1-70b-instruct-v1:0", "temperature": 0.7},
        ],
        "prompt": "Explain AI in one sentence."
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{API_BASE_URL}/compare/test",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=120  # Longer timeout for 6 models
        )
        end_time = time.time()
        
        total_latency_ms = int((end_time - start_time) * 1000)
        
        if response.status_code == 200:
            result = response.json()
            comparison_results = result.get('comparison', {}).get('results', {})
            
            print(f"  ✅ Comparison completed in {total_latency_ms}ms")
            print(f"  📊 Results for {len(comparison_results)} providers:")
            
            for provider, provider_result in comparison_results.items():
                if provider_result.get('success'):
                    latency = provider_result.get('latency_ms', 0)
                    model_family = provider_result.get('model_family', 'unknown')
                    cost_tier = provider_result.get('cost_tier', 'unknown')
                    print(f"     ✅ {provider}: {latency}ms, {model_family}, {cost_tier}")
                else:
                    error = provider_result.get('error', 'unknown error')
                    print(f"     ❌ {provider}: {error}")
            
            return {
                "success": True,
                "total_latency_ms": total_latency_ms,
                "results": comparison_results,
                "successful_models": len([r for r in comparison_results.values() if r.get('success')])
            }
        else:
            print(f"  ❌ Comparison failed: HTTP {response.status_code}")
            print(f"     Error: {response.text}")
            return {
                "success": False,
                "error": f"HTTP {response.status_code}: {response.text}",
                "total_latency_ms": total_latency_ms
            }
            
    except Exception as e:
        print(f"  ❌ Comparison exception: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "total_latency_ms": 0
        }

def main():
    """Run comprehensive production testing."""
    print("🚀 PRODUCTION NOVA & LLAMA TESTING")
    print("="*50)
    
    # Test individual models
    models_to_test = [
        # Claude models (baseline)
        ("anthropic", "claude-3-5-sonnet-20241022", "Claude 3.5 Sonnet (API)"),
        ("bedrock", "anthropic.claude-3-5-sonnet-20241022-v2:0", "Claude 3.5 Sonnet (Bedrock)"),
        
        # Nova models (NEW)
        ("nova", "us.amazon.nova-micro-v1:0", "Nova Micro"),
        ("nova", "us.amazon.nova-lite-v1:0", "Nova Lite"),
        
        # Llama models (NEW)
        ("llama", "meta.llama3-1-8b-instruct-v1:0", "Llama 3.1 8B"),
        ("llama", "meta.llama3-1-70b-instruct-v1:0", "Llama 3.1 70B"),
    ]
    
    individual_results = []
    for provider, model_id, name in models_to_test:
        result = test_model(provider, model_id, name)
        individual_results.append((name, result))
    
    # Test 6-model comparison
    comparison_result = test_6_model_comparison()
    
    # Generate report
    print(f"\n" + "="*60)
    print("📊 PRODUCTION TESTING REPORT")
    print("="*60)
    
    successful_individual = len([r for _, r in individual_results if r.get('success')])
    total_individual = len(individual_results)
    
    print(f"Individual Model Tests: {successful_individual}/{total_individual}")
    for name, result in individual_results:
        status = "✅" if result.get('success') else "❌"
        latency = result.get('latency_ms', 0)
        print(f"  {status} {name}: {latency}ms")
    
    print(f"\n6-Model Comparison:")
    if comparison_result.get('success'):
        successful_in_comparison = comparison_result.get('successful_models', 0)
        total_latency = comparison_result.get('total_latency_ms', 0)
        print(f"  ✅ {successful_in_comparison}/6 models successful in {total_latency}ms")
    else:
        print(f"  ❌ Comparison failed: {comparison_result.get('error', 'unknown')}")
    
    print(f"\n🎯 Production Assessment:")
    if successful_individual == total_individual and comparison_result.get('success'):
        print("  ✅ All models working perfectly in production!")
        print("  ✅ 6-model comparison functional!")
        print("  🚀 Phase 2 & 3 deployment: COMPLETE")
    elif successful_individual >= 4:
        print(f"  ⚠️  Most models working ({successful_individual}/{total_individual})")
        print("  🔧 Minor issues to resolve")
    else:
        print(f"  ❌ Major issues found ({successful_individual}/{total_individual} working)")
        print("  🛠️  Requires investigation")
    
    print(f"\n📈 Performance Summary:")
    working_models = [r for _, r in individual_results if r.get('success')]
    if working_models:
        latencies = [r['latency_ms'] for r in working_models]
        avg_latency = sum(latencies) / len(latencies)
        min_latency = min(latencies)
        max_latency = max(latencies)
        print(f"  Average latency: {avg_latency:.0f}ms")
        print(f"  Range: {min_latency}ms - {max_latency}ms")
        
        # Group by model family
        families = {}
        for name, result in individual_results:
            if result.get('success'):
                family = result.get('model_family', 'unknown')
                if family not in families:
                    families[family] = []
                families[family].append(result['latency_ms'])
        
        for family, latencies in families.items():
            avg = sum(latencies) / len(latencies)
            print(f"  {family.title()} family average: {avg:.0f}ms")

if __name__ == "__main__":
    main()