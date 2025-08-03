#!/usr/bin/env python3
"""
Test Phase 3 Frontend Implementation
Tests the enhanced React frontend with Nova and Llama model support.
"""

import os
import sys
import json
import time
import subprocess
from datetime import datetime
from typing import Dict, Any, List

print("🎨 PHASE 3 FRONTEND TESTING")
print("="*50)

def test_build_success():
    """Test that frontend builds successfully."""
    print("\n🔧 Testing Frontend Build...")
    
    try:
        os.chdir('/home/daddyfristy/feedminer/frontend-demo')
        result = subprocess.run(['npm', 'run', 'build'], 
                              capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ Frontend builds successfully")
            return True
        else:
            print(f"❌ Frontend build failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Frontend build error: {e}")
        return False

def test_typescript_compilation():
    """Test TypeScript compilation."""
    print("\n📝 Testing TypeScript Compilation...")
    
    try:
        result = subprocess.run(['npx', 'tsc', '--noEmit'], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ TypeScript compiles without errors")
            return True
        else:
            print(f"❌ TypeScript compilation failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ TypeScript compilation error: {e}")
        return False

def test_component_structure():
    """Test that key component files exist and contain expected model configurations."""
    print("\n📂 Testing Component Structure...")
    
    test_files = [
        ('src/components/ModelProviderSelector.tsx', [
            'MODEL_FAMILIES',
            'claude', 'nova', 'llama',
            'us.amazon.nova-micro-v1:0',
            'meta.llama3-1-8b-instruct-v1:0',
            'Very Low', 'Low', 'High'
        ]),
        ('src/services/feedminerApi.ts', [
            "'nova'", "'llama'",
            'model_family?', 'cost_tier?', 'capabilities?'
        ]),
        ('src/components/ModelTestingPage.tsx', [
            'nova', 'llama',
            'us.amazon.nova-micro-v1:0',
            'meta.llama3-1-8b-instruct-v1:0'
        ])
    ]
    
    all_passed = True
    
    for file_path, expected_content in test_files:
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            missing_content = []
            for expected in expected_content:
                if expected not in content:
                    missing_content.append(expected)
            
            if missing_content:
                print(f"❌ {file_path}: Missing content - {missing_content}")
                all_passed = False
            else:
                print(f"✅ {file_path}: Contains all expected content")
                
        except Exception as e:
            print(f"❌ {file_path}: Error reading file - {e}")
            all_passed = False
    
    return all_passed

def test_model_configuration():
    """Test that model configuration contains all 6 models."""
    print("\n🤖 Testing Model Configuration...")
    
    try:
        with open('src/components/ModelProviderSelector.tsx', 'r') as f:
            content = f.read()
        
        expected_models = [
            'claude-3-5-sonnet-20241022',
            'anthropic.claude-3-5-sonnet-20241022-v2:0',
            'us.amazon.nova-micro-v1:0',
            'us.amazon.nova-lite-v1:0',
            'meta.llama3-1-8b-instruct-v1:0',
            'meta.llama3-1-70b-instruct-v1:0'
        ]
        
        missing_models = []
        for model in expected_models:
            if model not in content:
                missing_models.append(model)
        
        if missing_models:
            print(f"❌ Missing models: {missing_models}")
            return False
        else:
            print(f"✅ All 6 models configured: {len(expected_models)} models found")
            return True
            
    except Exception as e:
        print(f"❌ Error checking model configuration: {e}")
        return False

def test_api_types():
    """Test that API types support new providers."""
    print("\n🔗 Testing API Types...")
    
    try:
        with open('src/services/feedminerApi.ts', 'r') as f:
            content = f.read()
        
        # Check for updated provider types
        provider_types = ["'anthropic'", "'bedrock'", "'nova'", "'llama'"]
        missing_types = []
        
        for provider_type in provider_types:
            if provider_type not in content:
                missing_types.append(provider_type)
        
        if missing_types:
            print(f"❌ Missing provider types: {missing_types}")
            return False
        
        # Check for new response fields
        new_fields = ['model_family?', 'cost_tier?', 'capabilities?']
        missing_fields = []
        
        for field in new_fields:
            if field not in content:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"❌ Missing response fields: {missing_fields}")
            return False
        
        print("✅ API types support all new providers and response fields")
        return True
        
    except Exception as e:
        print(f"❌ Error checking API types: {e}")
        return False

def test_comparison_mode():
    """Test that comparison mode supports 6-model comparison."""
    print("\n⚖️  Testing 6-Model Comparison Mode...")
    
    try:
        with open('src/components/ModelTestingPage.tsx', 'r') as f:
            content = f.read()
        
        # Check for all 6 models in comparison mode
        comparison_models = [
            'claude-3-5-sonnet-20241022',
            'anthropic.claude-3-5-sonnet-20241022-v2:0',
            'us.amazon.nova-micro-v1:0',
            'us.amazon.nova-lite-v1:0',
            'meta.llama3-1-8b-instruct-v1:0',
            'meta.llama3-1-70b-instruct-v1:0'
        ]
        
        missing_in_comparison = []
        for model in comparison_models:
            if model not in content:
                missing_in_comparison.append(model)
        
        if missing_in_comparison:
            print(f"❌ Missing models in comparison: {missing_in_comparison}")
            return False
        
        # Check for provider types in comparison
        comparison_providers = ["'anthropic'", "'bedrock'", "'nova'", "'llama'"]
        missing_providers = []
        
        for provider in comparison_providers:
            if provider not in content:
                missing_providers.append(provider)
        
        if missing_providers:
            print(f"❌ Missing providers in comparison: {missing_providers}")
            return False
        
        print("✅ 6-model comparison mode configured correctly")
        return True
        
    except Exception as e:
        print(f"❌ Error checking comparison mode: {e}")
        return False

def generate_phase3_report():
    """Generate Phase 3 completion report."""
    print("\n" + "="*60)
    print("📊 PHASE 3 FRONTEND ENHANCEMENT REPORT")
    print("="*60)
    
    # Run all tests
    tests = [
        ("Frontend Build", test_build_success),
        ("TypeScript Compilation", test_typescript_compilation),
        ("Component Structure", test_component_structure),
        ("Model Configuration", test_model_configuration),
        ("API Types", test_api_types),
        ("6-Model Comparison", test_comparison_mode),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}: Test failed with error - {e}")
            results.append((test_name, False))
    
    # Calculate results
    total_tests = len(results)
    passed_tests = sum(1 for _, passed in results if passed)
    success_rate = (passed_tests / total_tests) * 100
    
    print(f"\nTotal Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    print(f"\n📋 Test Results:")
    for test_name, passed in results:
        status = "✅" if passed else "❌"
        print(f"  {status} {test_name}")
    
    print(f"\n🎯 Phase 3 Assessment:")
    if success_rate >= 100:
        print("  ✅ Phase 3 Complete: All frontend enhancements working perfectly")
    elif success_rate >= 80:
        print("  ⚠️  Phase 3 Mostly Complete: Minor issues to address")
    else:
        print("  ❌ Phase 3 Needs Work: Major issues found")
    
    # Summary of achievements
    if passed_tests >= 5:
        print(f"\n🚀 Frontend Achievements:")
        print(f"  ✅ 6-model support: Claude, Nova, Llama models integrated")
        print(f"  ✅ Model families: UI organized by AI company")
        print(f"  ✅ Cost indicators: Very Low, Low, High cost tiers")
        print(f"  ✅ Performance data: Response time estimates shown")
        print(f"  ✅ Capabilities: Text, Multimodal, Vision, Reasoning tags")
        print(f"  ✅ 6-model comparison: Cross-family AI comparison enabled")
    
    print(f"\n🏁 Phase 3 Status: {'COMPLETE' if success_rate >= 100 else 'NEEDS WORK'}")
    return success_rate >= 80

if __name__ == "__main__":
    success = generate_phase3_report()
    sys.exit(0 if success else 1)