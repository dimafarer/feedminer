"""
Phase 1 Testing: Strands Compatibility with Nova and Llama Models

This script tests whether Strands BedrockModel can handle:
1. Amazon Nova models (with direct model IDs vs inference profile IDs)
2. Meta Llama models 
3. Parameter mapping via additional_request_fields
4. Response extraction compatibility
"""

import os
import sys
import asyncio
from datetime import datetime
from typing import Dict, Any, List

# Set environment variables
os.environ['ANTHROPIC_API_KEY'] = open('../../../../creds/anthropic-apikey').readlines()[1].strip()
os.environ['AWS_REGION'] = 'us-west-2'

# Add source paths
sys.path.append('src/api')

try:
    from strands import Agent
    from strands.models.bedrock import BedrockModel
    STRANDS_AVAILABLE = True
    print("✅ Strands imports successful")
except ImportError as e:
    print(f"❌ Strands import error: {e}")
    STRANDS_AVAILABLE = False

class NovaLlamaStrandsTester:
    """Test Nova and Llama models with Strands framework."""
    
    def __init__(self):
        self.test_results = []
        self.system_prompt = "You are a helpful AI assistant. Respond concisely to test prompts."
    
    def log_result(self, test_name: str, success: bool, details: str, model_id: str = ""):
        """Log test results for analysis."""
        result = {
            "test_name": test_name,
            "model_id": model_id,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅" if success else "❌"
        print(f"{status} {test_name}: {details}")
    
    def test_basic_strands_agent_creation(self, model_id: str, additional_fields: Dict = None) -> bool:
        """Test basic Strands BedrockModel creation."""
        try:
            config = {
                "model_id": model_id,
                "temperature": 0.7,
                "region": os.environ.get('AWS_REGION', 'us-west-2')
            }
            
            if additional_fields:
                config["additional_request_fields"] = additional_fields
            
            # Test BedrockModel creation
            bedrock_model = BedrockModel(**config)
            
            # Test Agent creation
            agent = Agent(
                name="Test Agent",
                model=bedrock_model,
                system_prompt=self.system_prompt
            )
            
            self.log_result(f"Agent Creation", True, f"Successfully created agent", model_id)
            return True
            
        except Exception as e:
            self.log_result(f"Agent Creation", False, f"Failed: {str(e)}", model_id)
            return False
    
    def test_model_inference(self, model_id: str, additional_fields: Dict = None) -> Dict[str, Any]:
        """Test actual model inference with Strands."""
        try:
            config = {
                "model_id": model_id,
                "temperature": 0.7,
                "region": os.environ.get('AWS_REGION', 'us-west-2')
            }
            
            if additional_fields:
                config["additional_request_fields"] = additional_fields
            
            # Create agent
            bedrock_model = BedrockModel(**config)
            agent = Agent(
                name="Test Agent",
                model=bedrock_model,
                system_prompt=self.system_prompt
            )
            
            # Test inference
            test_prompt = f"Hello! This is a test of {model_id}. Please respond with 'Model {model_id.split('.')[-1]} working via Strands!'"
            
            start_time = datetime.now()
            result = agent(test_prompt)
            end_time = datetime.now()
            
            latency_ms = int((end_time - start_time).total_seconds() * 1000)
            
            # Extract response
            if isinstance(result, dict):
                content = str(result)
            else:
                content = str(result)
            
            response_data = {
                "content": content[:200],  # First 200 chars
                "latency_ms": latency_ms,
                "success": True,
                "full_response_type": str(type(result))
            }
            
            self.log_result(f"Inference Test", True, f"Response received in {latency_ms}ms", model_id)
            return response_data
            
        except Exception as e:
            error_msg = str(e)
            self.log_result(f"Inference Test", False, f"Failed: {error_msg}", model_id)
            
            # Check for specific error patterns
            if "not found" in error_msg.lower():
                return {"error": "model_not_found", "message": error_msg}
            elif "inference profile" in error_msg.lower():
                return {"error": "needs_inference_profile", "message": error_msg}
            elif "parameter" in error_msg.lower():
                return {"error": "parameter_issue", "message": error_msg}
            else:
                return {"error": "other", "message": error_msg}
    
    def test_nova_models(self):
        """Test Amazon Nova models with different approaches."""
        print("\n🔍 Testing Amazon Nova Models...")
        
        nova_models = [
            {
                "id": "us.amazon.nova-micro-v1:0",
                "name": "Nova Micro",
                "additional_fields": {
                    "maxTokens": 4096,
                    "topP": 0.9
                }
            },
            {
                "id": "us.amazon.nova-lite-v1:0", 
                "name": "Nova Lite",
                "additional_fields": {
                    "maxTokens": 4096,
                    "topP": 0.9
                }
            }
        ]
        
        for model in nova_models:
            print(f"\n📝 Testing {model['name']} ({model['id']})")
            
            # Test 1: Direct model ID
            print(f"  Test 1: Direct model ID...")
            creation_success = self.test_basic_strands_agent_creation(
                model['id'], 
                model['additional_fields']
            )
            
            if creation_success:
                inference_result = self.test_model_inference(
                    model['id'],
                    model['additional_fields']
                )
                
                if inference_result.get("error") == "needs_inference_profile":
                    print(f"  ⚠️  {model['name']} requires inference profile ID")
                    print(f"      Please provide inference profile ID from AWS console")
                elif inference_result.get("success"):
                    print(f"  ✅ {model['name']} works with direct model ID!")
    
    def test_llama_models(self):
        """Test Meta Llama models."""
        print("\n🦙 Testing Meta Llama Models...")
        
        llama_models = [
            {
                "id": "meta.llama3-1-8b-instruct-v1:0",
                "name": "Llama 3.1 8B",
                "additional_fields": {
                    "max_gen_len": 4096,
                    "top_p": 0.9
                }
            },
            {
                "id": "meta.llama3-1-70b-instruct-v1:0",
                "name": "Llama 3.1 70B", 
                "additional_fields": {
                    "max_gen_len": 4096,
                    "top_p": 0.9
                }
            }
        ]
        
        for model in llama_models:
            print(f"\n📝 Testing {model['name']} ({model['id']})")
            
            creation_success = self.test_basic_strands_agent_creation(
                model['id'],
                model['additional_fields']
            )
            
            if creation_success:
                inference_result = self.test_model_inference(
                    model['id'],
                    model['additional_fields']
                )
                
                if inference_result.get("success"):
                    print(f"  ✅ {model['name']} works with Strands!")
                else:
                    error_type = inference_result.get("error", "unknown")
                    print(f"  ❌ {model['name']} failed: {error_type}")
    
    def test_claude_baseline(self):
        """Test existing Claude model as baseline."""
        print("\n🤖 Testing Claude Baseline...")
        
        claude_model = "anthropic.claude-3-5-sonnet-20241022-v2:0"
        
        creation_success = self.test_basic_strands_agent_creation(claude_model)
        
        if creation_success:
            inference_result = self.test_model_inference(claude_model)
            
            if inference_result.get("success"):
                print(f"  ✅ Claude baseline working correctly")
            else:
                print(f"  ⚠️  Claude baseline issue: {inference_result.get('error')}")
    
    def test_parameter_mapping(self):
        """Test if additional_request_fields works correctly."""
        print("\n⚙️  Testing Parameter Mapping...")
        
        # Test different parameter configurations
        test_configs = [
            {
                "name": "Nova-style parameters",
                "model": "anthropic.claude-3-5-sonnet-20241022-v2:0",  # Use working model
                "fields": {"maxTokens": 100, "topP": 0.8}  # Nova-style naming
            },
            {
                "name": "Llama-style parameters", 
                "model": "anthropic.claude-3-5-sonnet-20241022-v2:0",  # Use working model
                "fields": {"max_gen_len": 100, "top_p": 0.8}  # Llama-style naming
            }
        ]
        
        for config in test_configs:
            print(f"  Testing {config['name']}...")
            try:
                bedrock_model = BedrockModel(
                    model_id=config['model'],
                    temperature=0.7,
                    region=os.environ.get('AWS_REGION', 'us-west-2'),
                    additional_request_fields=config['fields']
                )
                
                agent = Agent(
                    name="Parameter Test Agent",
                    model=bedrock_model,
                    system_prompt=self.system_prompt
                )
                
                # Quick test
                result = agent("Say 'Parameter mapping test successful'")
                print(f"    ✅ {config['name']} parameter mapping works")
                
            except Exception as e:
                print(f"    ❌ {config['name']} failed: {str(e)}")
    
    def generate_report(self):
        """Generate comprehensive test report."""
        print("\n" + "="*60)
        print("📊 NOVA & LLAMA STRANDS COMPATIBILITY REPORT")
        print("="*60)
        
        total_tests = len(self.test_results)
        successful_tests = len([r for r in self.test_results if r["success"]])
        
        print(f"Total Tests: {total_tests}")
        print(f"Successful: {successful_tests}")
        print(f"Failed: {total_tests - successful_tests}")
        print(f"Success Rate: {(successful_tests/total_tests)*100:.1f}%")
        
        print("\n📋 Detailed Results:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            model_info = f" ({result['model_id']})" if result['model_id'] else ""
            print(f"{status} {result['test_name']}{model_info}: {result['details']}")
        
        print("\n💡 Recommendations:")
        
        # Check for inference profile needs
        inference_profile_needed = any(
            "inference profile" in r["details"].lower() 
            for r in self.test_results if not r["success"]
        )
        
        if inference_profile_needed:
            print("🔸 Some models require inference profile IDs from AWS console")
        
        # Check for parameter issues
        parameter_issues = any(
            "parameter" in r["details"].lower()
            for r in self.test_results if not r["success"]
        )
        
        if parameter_issues:
            print("🔸 Parameter mapping may need adjustment")
        
        # Check overall compatibility
        model_tests = [r for r in self.test_results if "Inference Test" in r["test_name"]]
        working_models = [r for r in model_tests if r["success"]]
        
        if working_models:
            print(f"🔸 {len(working_models)} models working with Strands")
        
        print("\n🚀 Next Steps:")
        print("1. Obtain inference profile IDs for failed Nova models")
        print("2. Implement backend parameter mapping")
        print("3. Proceed with Phase 2 implementation")


def main():
    """Run comprehensive Nova and Llama compatibility tests."""
    if not STRANDS_AVAILABLE:
        print("❌ Strands not available. Please ensure strands-agents is installed.")
        return
    
    print("🧪 NOVA & LLAMA STRANDS COMPATIBILITY TESTING")
    print("="*50)
    
    tester = NovaLlamaStrandsTester()
    
    # Run all tests
    tester.test_claude_baseline()
    tester.test_parameter_mapping()
    tester.test_nova_models()
    tester.test_llama_models()
    
    # Generate final report
    tester.generate_report()


if __name__ == "__main__":
    main()