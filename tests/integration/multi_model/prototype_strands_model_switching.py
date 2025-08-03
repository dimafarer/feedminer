"""
Prototype: Strands-based Model Switching for FeedMiner

This is a prototype implementation showing how to properly use Strands Agent patterns
for model switching between Anthropic API and AWS Bedrock.
"""

import json
import os
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
from strands import Agent
from strands.models.anthropic import AnthropicModel
from strands.models.bedrock import BedrockModel
from pydantic import BaseModel, Field


class ModelSwitchingRequest(BaseModel):
    """Request model for model switching API."""
    provider: str = Field(description="AI provider: 'anthropic' or 'bedrock'")
    model: str = Field(description="Specific model ID")
    temperature: float = Field(default=0.7, description="Temperature setting 0-1")
    prompt: Optional[str] = Field(default=None, description="Custom prompt for test mode")


class ModelSwitchingResponse(BaseModel):
    """Response model for model switching API."""
    success: bool
    contentId: str
    provider: str
    model: str
    response: Dict[str, Any]
    timestamp: str
    test_mode: bool = False


class StrandsModelSwitcher:
    """Strands-based model switching implementation."""
    
    def __init__(self):
        """Initialize the model switcher."""
        self.system_prompt = """You are an expert at analyzing Instagram saved content. 
        You understand social media trends, content categories, and user behavior patterns.
        Extract meaningful insights from content and provide structured analysis."""
    
    def create_agent_with_model(self, provider: str, model_id: str, temperature: float = 0.7) -> Agent:
        """Create a Strands agent with the specified model configuration."""
        
        if provider == "anthropic":
            api_key = os.environ.get('ANTHROPIC_API_KEY')
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY environment variable is required")
            model = AnthropicModel(
                model_id=model_id,
                api_key=api_key,
                temperature=temperature,
                max_tokens=4096
            )
        elif provider == "bedrock":
            model = BedrockModel(
                model_id=model_id,
                temperature=temperature,
                region=os.environ.get('AWS_REGION', 'us-west-2')
            )
        else:
            raise ValueError(f"Unsupported provider: {provider}")
        
        return Agent(
            name="FeedMiner Content Analysis Agent",
            model=model,
            system_prompt=self.system_prompt
        )
    
    async def analyze_with_provider(self, request: ModelSwitchingRequest, content_id: str = "test") -> ModelSwitchingResponse:
        """Analyze content with specified provider using Strands Agent."""
        
        try:
            # Create agent with specified model
            agent = self.create_agent_with_model(
                provider=request.provider,
                model_id=request.model,
                temperature=request.temperature
            )
            
            # Determine prompt based on test mode vs content analysis
            if content_id == "test" and request.prompt:
                # Test mode with custom prompt
                prompt = request.prompt
                test_mode = True
            else:
                # Content analysis mode
                # In real implementation, we would load content from DynamoDB/S3
                prompt = "Analyze this Instagram content for behavioral patterns and goal-setting opportunities."
                test_mode = False
            
            # Run analysis using Strands agent
            start_time = datetime.now()
            
            # Use the agent to generate response (Strands agents return results synchronously)
            result = agent(prompt)
            
            end_time = datetime.now()
            latency_ms = int((end_time - start_time).total_seconds() * 1000)
            
            # Format response in expected structure
            response_data = {
                "content": result,
                "provider": request.provider,
                "model": request.model,
                "latency_ms": latency_ms,
                "usage": {
                    "input_tokens": len(prompt.split()) * 1.3,  # Rough estimate
                    "output_tokens": len(str(result).split()) * 1.3,  # Rough estimate
                    "total_tokens": (len(prompt.split()) + len(str(result).split())) * 1.3
                },
                "success": True
            }
            
            return ModelSwitchingResponse(
                success=True,
                contentId=content_id,
                provider=request.provider,
                model=request.model,
                response=response_data,
                timestamp=datetime.now().isoformat(),
                test_mode=test_mode
            )
            
        except Exception as e:
            # Error handling
            return ModelSwitchingResponse(
                success=False,
                contentId=content_id,
                provider=request.provider,
                model=request.model,
                response={
                    "error": str(e),
                    "success": False
                },
                timestamp=datetime.now().isoformat(),
                test_mode=content_id == "test"
            )
    
    async def compare_providers(self, request: ModelSwitchingRequest, content_id: str) -> Dict[str, Any]:
        """Compare multiple providers using Strands agents."""
        
        providers_to_test = [
            ("anthropic", "claude-3-5-sonnet-20241022"),
            ("bedrock", "anthropic.claude-3-5-sonnet-20241022-v2:0")
        ]
        
        results = {}
        
        for provider, model in providers_to_test:
            test_request = ModelSwitchingRequest(
                provider=provider,
                model=model,
                temperature=request.temperature,
                prompt=request.prompt
            )
            
            result = await self.analyze_with_provider(test_request, content_id)
            results[provider] = result.model_dump()
        
        # Calculate comparison metrics
        comparison_summary = self.calculate_comparison_metrics(results)
        
        return {
            "success": True,
            "contentId": content_id,
            "comparison": {
                "providers": list(results.keys()),
                "results": results,
                "summary": comparison_summary
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def calculate_comparison_metrics(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comparison metrics between providers."""
        
        latencies = {}
        success_rates = {}
        
        for provider, result in results.items():
            if result["success"]:
                response_data = result["response"]
                latencies[provider] = response_data.get("latency_ms", 0)
                success_rates[provider] = 1.0
            else:
                success_rates[provider] = 0.0
        
        if latencies:
            fastest_provider = min(latencies.keys(), key=lambda p: latencies[p])
            summary = {
                "fastest_provider": fastest_provider,
                "fastest_time_ms": latencies[fastest_provider],
                "latency_by_provider": latencies,
                "average_latency_ms": sum(latencies.values()) / len(latencies) if latencies else 0,
                "all_successful": all(success_rates.values())
            }
        else:
            summary = {
                "all_successful": False,
                "error": "No successful provider responses"
            }
        
        return summary


# Example usage and testing
async def test_strands_model_switching():
    """Test the Strands-based model switching."""
    
    switcher = StrandsModelSwitcher()
    
    # Test Anthropic
    print("Testing Anthropic API...")
    anthropic_request = ModelSwitchingRequest(
        provider="anthropic",
        model="claude-3-5-sonnet-20241022",
        temperature=0.7,
        prompt="Hello! This is a test of Strands with Anthropic."
    )
    
    anthropic_result = await switcher.analyze_with_provider(anthropic_request)
    print(f"Anthropic Result: {anthropic_result.model_dump()}")
    
    # Test Bedrock
    print("\nTesting Bedrock...")
    bedrock_request = ModelSwitchingRequest(
        provider="bedrock",
        model="anthropic.claude-3-5-sonnet-20241022-v2:0",
        temperature=0.7,
        prompt="Hello! This is a test of Strands with Bedrock."
    )
    
    bedrock_result = await switcher.analyze_with_provider(bedrock_request)
    print(f"Bedrock Result: {bedrock_result.model_dump()}")
    
    # Test comparison
    print("\nTesting comparison...")
    comparison_result = await switcher.compare_providers(anthropic_request, "test")
    print(f"Comparison Result: {json.dumps(comparison_result, indent=2)}")


if __name__ == "__main__":
    # Run the test
    asyncio.run(test_strands_model_switching())