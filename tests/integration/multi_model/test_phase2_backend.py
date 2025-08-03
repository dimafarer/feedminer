#!/usr/bin/env python3
"""
Test Phase 2 Backend Implementation
Tests the enhanced strands_model_switching.py with Nova and Llama support.
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, Any, List

# Set environment variables
os.environ['ANTHROPIC_API_KEY'] = open('../creds/anthropic-apikey').readlines()[1].strip()
os.environ['AWS_REGION'] = 'us-west-2'

# Add source paths
sys.path.append('src/api')

try:
    from strands_model_switching import (
        create_strands_agent, 
        extract_strands_response,
        detect_model_family,
        get_default_model,
        create_bedrock_model_for_family
    )
    BACKEND_AVAILABLE = True
    print("✅ Backend imports successful")
except ImportError as e:
    print(f"❌ Backend import error: {e}")
    BACKEND_AVAILABLE = False

class Phase2BackendTester:
    """Test Phase 2 backend enhancements."""
    
    def __init__(self):
        self.test_results = []
        self.test_configurations = [
            # Claude models (baseline)
            {"provider": "anthropic", "model": "claude-3-5-sonnet-20241022", "name": "Claude 3.5 Sonnet (API)"},
            {"provider": "bedrock", "model": "anthropic.claude-3-5-sonnet-20241022-v2:0", "name": "Claude 3.5 Sonnet (Bedrock)"},
            
            # Nova models (NEW)
            {"provider": "nova", "model": "us.amazon.nova-micro-v1:0", "name": "Nova Micro"},
            {"provider": "nova", "model": "us.amazon.nova-lite-v1:0", "name": "Nova Lite"},
            
            # Llama models (NEW)
            {"provider": "llama", "model": "meta.llama3-1-8b-instruct-v1:0", "name": "Llama 3.1 8B"},
            {"provider": "llama", "model": "meta.llama3-1-70b-instruct-v1:0", "name": "Llama 3.1 70B"},
        ]
    
    def log_result(self, test_name: str, success: bool, details: str, config: Dict = None):
        """Log test results for analysis."""
        result = {
            "test_name": test_name,
            "config": config or {},
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅" if success else "❌"
        model_info = f"({config.get('name', 'Unknown')})" if config else ""
        print(f"{status} {test_name} {model_info}: {details}")
    
    def test_model_family_detection(self):
        """Test model family detection logic."""
        print("\n🔍 Testing Model Family Detection...")
        
        test_cases = [
            ("us.amazon.nova-micro-v1:0", "nova"),
            ("us.amazon.nova-lite-v1:0", "nova"),
            ("meta.llama3-1-8b-instruct-v1:0", "llama"),
            ("meta.llama3-1-70b-instruct-v1:0", "llama"),
            ("anthropic.claude-3-5-sonnet-20241022-v2:0", "claude"),
            ("claude-3-5-sonnet-20241022", "claude"),
        ]
        
        for model_id, expected_family in test_cases:
            try:
                detected_family = detect_model_family(model_id)
                success = detected_family == expected_family
                details = f"Detected: {detected_family}, Expected: {expected_family}"
                self.log_result(f"Family Detection", success, details, {"model": model_id})
            except Exception as e:
                self.log_result(f"Family Detection", False, f"Error: {str(e)}", {"model": model_id})
    
    def test_default_models(self):
        """Test default model selection for each provider."""
        print("\n📋 Testing Default Model Selection...")
        
        providers = ["anthropic", "bedrock", "nova", "llama"]
        
        for provider in providers:
            try:
                default_model = get_default_model(provider)
                success = bool(default_model)
                details = f"Default model: {default_model}"
                self.log_result(f"Default Model", success, details, {"provider": provider})
            except Exception as e:
                self.log_result(f"Default Model", False, f"Error: {str(e)}", {"provider": provider})
    
    def test_bedrock_model_creation(self):
        """Test Bedrock model creation for all families."""
        print("\n🔧 Testing Bedrock Model Creation...")
        
        test_models = [
            "anthropic.claude-3-5-sonnet-20241022-v2:0",
            "us.amazon.nova-micro-v1:0",
            "meta.llama3-1-8b-instruct-v1:0"
        ]
        
        for model_id in test_models:
            try:
                bedrock_model = create_bedrock_model_for_family(model_id, 0.7)
                success = bedrock_model is not None
                family = detect_model_family(model_id)
                details = f"Created BedrockModel for {family} family"
                self.log_result(f"Bedrock Model Creation", success, details, {"model": model_id})
            except Exception as e:
                self.log_result(f"Bedrock Model Creation", False, f"Error: {str(e)}", {"model": model_id})
    
    def test_agent_creation(self):
        """Test Strands agent creation for all model families."""
        print("\n🤖 Testing Strands Agent Creation...")
        
        for config in self.test_configurations:
            try:
                agent = create_strands_agent(
                    config["provider"], 
                    config["model"], 
                    0.7
                )
                success = agent is not None
                details = f"Successfully created agent"
                self.log_result(f"Agent Creation", success, details, config)
            except Exception as e:
                self.log_result(f"Agent Creation", False, f"Error: {str(e)}", config)
    
    def test_inference_with_all_models(self):
        """Test actual inference with all model families."""
        print("\n🧠 Testing Model Inference...")
        
        test_prompt = "Hello! Please respond with 'Working: [Your Model Family]' where you identify whether you are Claude, Nova, or Llama."
        
        for config in self.test_configurations:
            try:
                # Create agent
                agent = create_strands_agent(
                    config["provider"], 
                    config["model"], 
                    0.7
                )
                
                # Run inference
                start_time = datetime.now()
                strands_result = agent(test_prompt)
                end_time = datetime.now()
                
                # Extract response
                model_family = detect_model_family(config["model"])
                response_data = extract_strands_response(strands_result, model_family)
                
                latency_ms = int((end_time - start_time).total_seconds() * 1000)
                
                success = response_data.get("success", False)
                content = response_data.get("content", "")[:100]  # First 100 chars
                
                details = f"Response in {latency_ms}ms: {content}..."
                self.log_result(f"Model Inference", success, details, config)
                
                # Log additional metadata
                if success:
                    metadata = {
                        "model_family": response_data.get("model_family"),
                        "cost_tier": response_data.get("cost_tier"),
                        "capabilities": response_data.get("capabilities")
                    }
                    print(f"    📊 Metadata: {json.dumps(metadata, indent=4)}")
                
            except Exception as e:
                self.log_result(f"Model Inference", False, f"Error: {str(e)}", config)
    
    def test_comparison_scenario(self):
        """Test model comparison across families."""
        print("\n⚖️  Testing Cross-Family Model Comparison...")
        
        # Test comparing one model from each family
        comparison_models = [
            {"provider": "bedrock", "model": "anthropic.claude-3-5-sonnet-20241022-v2:0", "name": "Claude"},
            {"provider": "nova", "model": "us.amazon.nova-micro-v1:0", "name": "Nova"},
            {"provider": "llama", "model": "meta.llama3-1-8b-instruct-v1:0", "name": "Llama"},
        ]
        
        test_prompt = "Explain artificial intelligence in one sentence."
        comparison_results = {}
        
        for config in comparison_models:
            try:
                # Create agent and run inference
                agent = create_strands_agent(config["provider"], config["model"], 0.7)
                start_time = datetime.now()
                strands_result = agent(test_prompt)
                end_time = datetime.now()
                
                # Extract response
                model_family = detect_model_family(config["model"])
                response_data = extract_strands_response(strands_result, model_family)
                
                latency_ms = int((end_time - start_time).total_seconds() * 1000)
                
                comparison_results[config["name"]] = {
                    "success": response_data.get("success", False),
                    "latency_ms": latency_ms,
                    "model_family": response_data.get("model_family"),
                    "cost_tier": response_data.get("cost_tier"),
                    "content_length": len(response_data.get("content", ""))
                }
                
            except Exception as e:
                comparison_results[config["name"]] = {
                    "success": False,
                    "error": str(e)
                }
        
        # Analyze comparison results
        successful_models = [name for name, result in comparison_results.items() if result.get("success")]
        success = len(successful_models) >= 2  # At least 2 models should work
        
        details = f"Successful models: {successful_models}"
        self.log_result(f"Cross-Family Comparison", success, details)
        
        if success:
            print(f"    📊 Comparison Results:")
            for model_name, result in comparison_results.items():
                if result.get("success"):
                    print(f"      {model_name}: {result['latency_ms']}ms, {result['cost_tier']} cost, {result['content_length']} chars")
    
    def generate_report(self):
        """Generate comprehensive Phase 2 test report."""
        print("\n" + "="*70)
        print("📊 PHASE 2 BACKEND ENHANCEMENT TEST REPORT")
        print("="*70)
        
        total_tests = len(self.test_results)
        successful_tests = len([r for r in self.test_results if r["success"]])
        
        print(f"Total Tests: {total_tests}")
        print(f"Successful: {successful_tests}")
        print(f"Failed: {total_tests - successful_tests}")
        print(f"Success Rate: {(successful_tests/total_tests)*100:.1f}%")
        
        # Group results by test type
        test_types = {}
        for result in self.test_results:
            test_type = result["test_name"]
            if test_type not in test_types:
                test_types[test_type] = {"total": 0, "successful": 0}
            test_types[test_type]["total"] += 1
            if result["success"]:
                test_types[test_type]["successful"] += 1
        
        print(f"\n📋 Results by Test Type:")
        for test_type, stats in test_types.items():
            success_rate = (stats["successful"] / stats["total"]) * 100
            print(f"  {test_type}: {stats['successful']}/{stats['total']} ({success_rate:.1f}%)")
        
        # Model family analysis
        model_family_results = {}
        for result in self.test_results:
            config = result.get("config", {})
            model = config.get("model", "")
            if model:
                family = detect_model_family(model)
                if family not in model_family_results:
                    model_family_results[family] = {"total": 0, "successful": 0}
                model_family_results[family]["total"] += 1
                if result["success"]:
                    model_family_results[family]["successful"] += 1
        
        print(f"\n🏗️  Results by Model Family:")
        for family, stats in model_family_results.items():
            if stats["total"] > 0:
                success_rate = (stats["successful"] / stats["total"]) * 100
                print(f"  {family.title()}: {stats['successful']}/{stats['total']} ({success_rate:.1f}%)")
        
        print(f"\n🎯 Phase 2 Assessment:")
        
        # Check if all model families work
        working_families = [family for family, stats in model_family_results.items() 
                          if stats["successful"] > 0 and stats["total"] > 0]
        
        if len(working_families) >= 3:
            print(f"  ✅ Multi-family support achieved ({len(working_families)} families working)")
        else:
            print(f"  ⚠️  Limited family support ({len(working_families)} families working)")
        
        # Check overall success rate
        if successful_tests / total_tests >= 0.8:
            print(f"  ✅ High success rate ({(successful_tests/total_tests)*100:.1f}%)")
        else:
            print(f"  ⚠️  Low success rate ({(successful_tests/total_tests)*100:.1f}%)")
        
        print(f"\n🚀 Phase 2 Status: {'COMPLETE' if len(working_families) >= 3 else 'NEEDS WORK'}")


def main():
    """Run comprehensive Phase 2 backend tests."""
    if not BACKEND_AVAILABLE:
        print("❌ Backend not available. Please ensure strands_model_switching.py is working.")
        return
    
    print("🧪 PHASE 2 BACKEND ENHANCEMENT TESTING")
    print("="*50)
    
    tester = Phase2BackendTester()
    
    # Run all tests
    tester.test_model_family_detection()
    tester.test_default_models()
    tester.test_bedrock_model_creation()
    tester.test_agent_creation()
    tester.test_inference_with_all_models()
    tester.test_comparison_scenario()
    
    # Generate final report
    tester.generate_report()


if __name__ == "__main__":
    main()