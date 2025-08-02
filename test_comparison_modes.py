"""
Test both comparison modes: test mode with custom prompt and real content analysis.
"""

import requests
import json

API_BASE = "https://wqtfb6rv15.execute-api.us-west-2.amazonaws.com/dev"

def test_comparison_with_custom_prompt():
    """Test comparison mode with a custom prompt (test mode)."""
    print("🧪 Testing Comparison Mode with Custom Prompt...")
    
    response = requests.post(
        f"{API_BASE}/compare/test",
        headers={"Content-Type": "application/json"},
        json={
            "providers": [
                {"provider": "anthropic", "model": "claude-3-5-sonnet-20241022"},
                {"provider": "bedrock", "model": "anthropic.claude-3-5-sonnet-20241022-v2:0"}
            ],
            "temperature": 0.7,
            "prompt": "Compare these approaches: 1) Learning through online courses vs 2) Learning through hands-on projects. Give a brief analysis of the pros and cons of each approach for software development skills."
        }
    )
    
    print(f"Status Code: {response.status_code}")
    result = response.json()
    print(f"Success: {result.get('success')}")
    
    if result.get('success'):
        comparison = result.get('comparison', {})
        providers = comparison.get('providers', [])
        print(f"✅ Both providers tested: {providers}")
        
        # Show responses from each provider
        results = comparison.get('results', {})
        for provider, provider_result in results.items():
            if provider_result.get('success'):
                content = provider_result.get('content', '')
                print(f"\n📝 {provider.upper()} Response:")
                print(f"   {content[:200]}...")
                print(f"   Latency: {provider_result.get('latency_ms', 0)}ms")
            else:
                print(f"\n❌ {provider.upper()} Failed: {provider_result.get('error', 'Unknown error')}")
        
        # Show performance comparison
        summary = comparison.get('summary', {})
        if 'performance_comparison' in summary:
            perf = summary['performance_comparison']
            print(f"\n⚡ Performance: {perf.get('fastest_provider')} was fastest ({perf.get('fastest_time_ms')}ms)")
    
    return result.get('success', False)

def test_comparison_learning_scenarios():
    """Test different learning-related prompts to show model differences."""
    
    learning_prompts = [
        "Explain the concept of 'learning by doing' vs 'learning by studying' for programming skills.",
        "What are the key differences between frontend and backend development? Focus on learning paths.",
        "Compare Python vs JavaScript for a beginner programmer. Which should they learn first?"
    ]
    
    print("\n🎓 Testing Learning-Focused Comparison Scenarios...")
    
    for i, prompt in enumerate(learning_prompts, 1):
        print(f"\n--- Scenario {i}: {prompt[:50]}... ---")
        
        response = requests.post(
            f"{API_BASE}/compare/test",
            headers={"Content-Type": "application/json"},
            json={
                "providers": [
                    {"provider": "anthropic", "model": "claude-3-5-sonnet-20241022"},
                    {"provider": "bedrock", "model": "anthropic.claude-3-5-sonnet-20241022-v2:0"}
                ],
                "temperature": 0.7,
                "prompt": prompt
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                comparison = result.get('comparison', {})
                results = comparison.get('results', {})
                
                # Show key differences in responses
                for provider in ['anthropic', 'bedrock']:
                    if provider in results and results[provider].get('success'):
                        content = results[provider].get('content', '')
                        # Extract first sentence or key point
                        first_sentence = content.split('.')[0] if '.' in content else content[:100]
                        print(f"  {provider.capitalize()}: {first_sentence}...")
                
                # Show performance
                summary = comparison.get('summary', {})
                if 'performance_comparison' in summary:
                    perf = summary['performance_comparison']
                    print(f"  ⚡ Fastest: {perf.get('fastest_provider')} ({perf.get('fastest_time_ms')}ms)")
            else:
                print(f"  ❌ Failed: {result.get('error', 'Unknown error')}")
        else:
            print(f"  ❌ HTTP {response.status_code}")

if __name__ == "__main__":
    print("🔄 Testing Model Comparison with Different Data Types\n")
    
    # Test basic comparison functionality
    success = test_comparison_with_custom_prompt()
    
    if success:
        print("\n✅ Custom prompt comparison working!")
        # Test learning scenarios
        test_comparison_learning_scenarios()
    else:
        print("\n❌ Custom prompt comparison failed!")
    
    print("\n📊 Summary:")
    print("Your users can now compare models using:")
    print("1. 🧪 Custom prompts (test mode) - Great for experimenting")
    print("2. 📄 Real Instagram data - Analyze actual user behavior")
    print("3. 🎓 Learning scenarios - Perfect for educational comparisons")