# AWS Bedrock Model Switching with Strands Agents: A Complete Guide

## Overview

This guide demonstrates how to elegantly switch between multiple AI models on AWS Bedrock using the Strands Agents SDK. You'll learn to build a production-ready system that can seamlessly switch between Anthropic Claude, Amazon Nova, and Meta Llama models with a single, unified interface.

## 🎯 What You'll Learn

1. **Strands Agent Fundamentals** - How to create and configure agents for different model families
2. **Dynamic Model Switching** - Runtime provider selection without code changes
3. **Multi-Provider Comparison** - Side-by-side analysis across different AI families
4. **Production Patterns** - Error handling, performance optimization, and monitoring
5. **Cost Optimization** - Smart model selection based on use case requirements

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client App    │    │  Lambda Handler │    │  Strands Agent  │
│                 │    │                 │    │                 │
│ Model Selection ├────┤ Route Request   ├────┤ Create Agent    │
│ Temperature     │    │ Parse Config    │    │ Execute Prompt  │
│ Prompt/Content  │    │ Handle Response │    │ Extract Result  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                      │
                                ▼                      ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   AWS Bedrock   │    │ Response Parser │
                       │                 │    │                 │
                       │ • Claude Models │    │ • Extract Text  │
                       │ • Nova Models   │    │ • Parse Metrics │
                       │ • Llama Models  │    │ • Add Metadata  │
                       └─────────────────┘    └─────────────────┘
```

## 🚀 Core Implementation

### 1. Agent Creation Pattern

The foundation of elegant model switching is a clean agent creation pattern:

```python
from strands import Agent
from strands.models.anthropic import AnthropicModel
from strands.models.bedrock import BedrockModel

def create_strands_agent(provider: str, model_id: str, temperature: float = 0.7) -> Agent:
    """
    Create a Strands agent with the specified model configuration.
    
    Key Design Principles:
    1. Single interface for multiple providers
    2. Provider-specific configuration handled internally
    3. Consistent Agent interface regardless of underlying model
    """
    
    system_prompt = """You are an expert analyst. Provide clear, structured insights."""
    
    if provider == "anthropic":
        # Direct Anthropic API access
        model = AnthropicModel(
            model_id=model_id,
            api_key=os.environ.get('ANTHROPIC_API_KEY'),
            temperature=temperature,
            max_tokens=4096
        )
    elif provider in ["bedrock", "nova", "llama"]:
        # All Bedrock models use the same interface
        model = BedrockModel(
            model_id=model_id,
            temperature=temperature,
            region=os.environ.get('AWS_REGION', 'us-west-2')
        )
    else:
        raise ValueError(f"Unsupported provider: {provider}")
    
    return Agent(
        name="Multi-Model Analysis Agent",
        model=model,
        system_prompt=system_prompt
    )
```

**🔑 Key Insight**: Strands abstracts away the complexity of different model APIs. BedrockModel handles parameter mapping for Nova (maxTokens) and Llama (max_gen_len) internally.

### 2. Model Family Registry

Organize models by capabilities and use cases:

```python
MODEL_REGISTRY = {
    # Anthropic Claude - High capability, premium cost
    "claude-3-5-sonnet-20241022": {
        "family": "claude",
        "provider": "anthropic",
        "cost_tier": "high",
        "capabilities": ["text", "vision", "reasoning"],
        "use_cases": ["complex_analysis", "creative_writing", "problem_solving"]
    },
    "anthropic.claude-3-5-sonnet-20241022-v2:0": {
        "family": "claude", 
        "provider": "bedrock",
        "cost_tier": "high",
        "capabilities": ["text", "vision", "reasoning"],
        "use_cases": ["enterprise_deployment", "complex_analysis"]
    },
    
    # Amazon Nova - Ultra-low cost, fast
    "us.amazon.nova-micro-v1:0": {
        "family": "nova",
        "provider": "bedrock",
        "cost_tier": "very_low",
        "capabilities": ["text"],
        "use_cases": ["classification", "summarization", "quick_analysis"]
    },
    "us.amazon.nova-lite-v1:0": {
        "family": "nova",
        "provider": "bedrock", 
        "cost_tier": "very_low",
        "capabilities": ["text", "multimodal"],
        "use_cases": ["content_analysis", "multimodal_tasks"]
    },
    
    # Meta Llama - Open-source efficiency
    "meta.llama3-1-8b-instruct-v1:0": {
        "family": "llama",
        "provider": "bedrock",
        "cost_tier": "low", 
        "capabilities": ["text"],
        "use_cases": ["efficient_processing", "cost_optimization"]
    },
    "meta.llama3-1-70b-instruct-v1:0": {
        "family": "llama",
        "provider": "bedrock",
        "cost_tier": "medium",
        "capabilities": ["text"],
        "use_cases": ["balanced_performance", "complex_reasoning"]
    }
}

def get_optimal_model(use_case: str, cost_priority: str = "balanced") -> str:
    """Smart model selection based on requirements."""
    candidates = [
        model_id for model_id, config in MODEL_REGISTRY.items() 
        if use_case in config["use_cases"]
    ]
    
    if cost_priority == "lowest":
        return min(candidates, key=lambda m: ["very_low", "low", "medium", "high"].index(MODEL_REGISTRY[m]["cost_tier"]))
    elif cost_priority == "performance":
        return max(candidates, key=lambda m: len(MODEL_REGISTRY[m]["capabilities"]))
    
    return candidates[0]  # Default to first match
```

### 3. Unified Response Processing

Handle different response formats consistently:

```python
from typing import Dict, Any, Union
from dataclasses import dataclass

@dataclass
class StandardResponse:
    """Unified response format across all model families."""
    content: str
    model_family: str
    provider: str
    model_id: str
    latency_ms: int
    cost_tier: str
    capabilities: list[str]
    usage: Dict[str, int]
    success: bool
    error: str = None

def extract_strands_response(strands_result, model_info: Dict[str, Any]) -> StandardResponse:
    """
    Extract and normalize response from any Strands agent result.
    
    Handles multiple response formats:
    1. Dictionary with message structure
    2. Object with attributes
    3. Direct content strings
    """
    
    try:
        # Extract text content (handles multiple formats)
        content = _extract_content(strands_result)
        
        # Extract performance metrics
        metrics = _extract_metrics(strands_result)
        
        return StandardResponse(
            content=content,
            model_family=model_info["family"],
            provider=model_info["provider"],
            model_id=model_info["model_id"],
            latency_ms=metrics.get("latency_ms", 0),
            cost_tier=model_info["cost_tier"],
            capabilities=model_info["capabilities"],
            usage=metrics.get("usage", {}),
            success=True
        )
        
    except Exception as e:
        return StandardResponse(
            content=str(strands_result),
            model_family="unknown",
            provider="unknown", 
            model_id="unknown",
            latency_ms=0,
            cost_tier="unknown",
            capabilities=[],
            usage={},
            success=False,
            error=str(e)
        )

def _extract_content(strands_result) -> str:
    """Extract text content from various Strands response formats."""
    if isinstance(strands_result, dict):
        # Handle dictionary response formats
        if 'message' in strands_result:
            message = strands_result['message']
            if isinstance(message, dict) and 'content' in message:
                content_list = message['content']
                if isinstance(content_list, list) and len(content_list) > 0:
                    return content_list[0].get('text', str(strands_result))
        elif 'content' in strands_result:
            content_list = strands_result['content']
            if isinstance(content_list, list) and len(content_list) > 0:
                return content_list[0].get('text', str(content_list[0]))
    
    elif hasattr(strands_result, 'message'):
        # Handle object response format
        message = strands_result.message
        if hasattr(message, 'content') and message.content:
            return message.content[0].text if hasattr(message.content[0], 'text') else str(message.content[0])
    
    # Fallback to string representation
    return str(strands_result)

def _extract_metrics(strands_result) -> Dict[str, Any]:
    """Extract performance metrics from Strands response."""
    metrics = {}
    
    if isinstance(strands_result, dict):
        strands_metrics = strands_result.get('metrics', {})
        usage_info = strands_metrics.get('accumulated_usage', {})
        cycle_durations = strands_metrics.get('cycle_durations', [])
        
        metrics = {
            "latency_ms": int(sum(cycle_durations) * 1000) if cycle_durations else 0,
            "usage": {
                "input_tokens": usage_info.get('inputTokens', 0),
                "output_tokens": usage_info.get('outputTokens', 0),
                "total_tokens": usage_info.get('totalTokens', 0)
            }
        }
    
    return metrics
```

### 4. Multi-Provider Comparison Engine

Enable side-by-side model comparisons:

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict

async def compare_models_async(
    prompt: str, 
    model_configs: List[Dict[str, Any]], 
    temperature: float = 0.7
) -> Dict[str, StandardResponse]:
    """
    Compare multiple models asynchronously for optimal performance.
    
    Example usage:
    results = await compare_models_async(
        prompt="Analyze this content...",
        model_configs=[
            {"provider": "anthropic", "model": "claude-3-5-sonnet-20241022"},
            {"provider": "nova", "model": "us.amazon.nova-micro-v1:0"},
            {"provider": "llama", "model": "meta.llama3-1-8b-instruct-v1:0"}
        ]
    )
    """
    
    async def process_single_model(config: Dict[str, Any]) -> tuple[str, StandardResponse]:
        """Process a single model configuration."""
        provider = config["provider"]
        model_id = config["model"]
        
        try:
            # Create agent (this should be cached in production)
            agent = create_strands_agent(provider, model_id, temperature)
            
            # Execute in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                start_time = asyncio.get_event_loop().time()
                strands_result = await loop.run_in_executor(executor, agent, prompt)
                end_time = asyncio.get_event_loop().time()
            
            # Extract response with model info
            model_info = MODEL_REGISTRY[model_id]
            model_info["model_id"] = model_id
            
            response = extract_strands_response(strands_result, model_info)
            
            # Override latency if not provided by Strands
            if response.latency_ms == 0:
                response.latency_ms = int((end_time - start_time) * 1000)
            
            return provider, response
            
        except Exception as e:
            # Return error response
            return provider, StandardResponse(
                content="",
                model_family=MODEL_REGISTRY.get(model_id, {}).get("family", "unknown"),
                provider=provider,
                model_id=model_id,
                latency_ms=0,
                cost_tier="unknown",
                capabilities=[],
                usage={},
                success=False,
                error=str(e)
            )
    
    # Execute all models concurrently
    tasks = [process_single_model(config) for config in model_configs]
    results = await asyncio.gather(*tasks)
    
    # Return as dictionary
    return dict(results)

def analyze_comparison_results(results: Dict[str, StandardResponse]) -> Dict[str, Any]:
    """Analyze comparison results to provide insights."""
    
    successful_results = {k: v for k, v in results.items() if v.success}
    
    if not successful_results:
        return {"error": "No successful results to analyze"}
    
    # Performance analysis
    latencies = {k: v.latency_ms for k, v in successful_results.items()}
    fastest_provider = min(latencies, key=latencies.get)
    
    # Cost analysis
    cost_tiers = {k: v.cost_tier for k, v in successful_results.items()}
    lowest_cost_provider = min(cost_tiers, key=lambda x: ["very_low", "low", "medium", "high"].index(cost_tiers[x]))
    
    # Token usage analysis
    total_tokens = {k: v.usage.get("total_tokens", 0) for k, v in successful_results.items()}
    
    return {
        "summary": {
            "total_providers": len(results),
            "successful_providers": len(successful_results),
            "success_rate": len(successful_results) / len(results)
        },
        "performance": {
            "fastest_provider": fastest_provider,
            "fastest_time_ms": latencies[fastest_provider],
            "latency_by_provider": latencies,
            "average_latency_ms": sum(latencies.values()) / len(latencies)
        },
        "cost_optimization": {
            "lowest_cost_provider": lowest_cost_provider,
            "cost_by_provider": cost_tiers,
            "estimated_savings": _calculate_cost_savings(cost_tiers, total_tokens)
        },
        "recommendations": _generate_recommendations(successful_results)
    }

def _calculate_cost_savings(cost_tiers: Dict[str, str], token_usage: Dict[str, int]) -> Dict[str, Any]:
    """Calculate potential cost savings between providers."""
    # Simplified cost calculation (use real pricing in production)
    cost_multipliers = {"very_low": 1, "low": 2, "medium": 5, "high": 10}
    
    estimated_costs = {
        provider: token_usage.get(provider, 0) * cost_multipliers[tier] 
        for provider, tier in cost_tiers.items()
    }
    
    if not estimated_costs:
        return {}
    
    cheapest = min(estimated_costs, key=estimated_costs.get)
    most_expensive = max(estimated_costs, key=estimated_costs.get)
    
    savings_percentage = (
        (estimated_costs[most_expensive] - estimated_costs[cheapest]) / 
        estimated_costs[most_expensive] * 100
    ) if estimated_costs[most_expensive] > 0 else 0
    
    return {
        "cheapest_provider": cheapest,
        "most_expensive_provider": most_expensive,
        "potential_savings_percentage": savings_percentage,
        "estimated_costs": estimated_costs
    }

def _generate_recommendations(results: Dict[str, StandardResponse]) -> List[str]:
    """Generate actionable recommendations based on comparison results."""
    recommendations = []
    
    # Performance recommendations
    latencies = {k: v.latency_ms for k, v in results.items() if v.success}
    if latencies:
        fastest = min(latencies, key=latencies.get)
        if latencies[fastest] < 1000:
            recommendations.append(f"🚀 {fastest} provides sub-second responses ({latencies[fastest]}ms) - ideal for real-time applications")
    
    # Cost recommendations 
    nova_providers = [k for k, v in results.items() if v.model_family == "nova" and v.success]
    if nova_providers:
        recommendations.append("💰 Nova models provide significant cost savings (75%+) for high-volume processing")
    
    # Quality recommendations
    claude_providers = [k for k, v in results.items() if v.model_family == "claude" and v.success]
    if claude_providers:
        recommendations.append("🎯 Claude models excel at complex reasoning and creative tasks")
    
    # Efficiency recommendations
    llama_providers = [k for k, v in results.items() if v.model_family == "llama" and v.success]
    if llama_providers:
        recommendations.append("⚡ Llama models offer excellent price/performance ratio for balanced workloads")
    
    return recommendations
```

## 🎛️ Production-Ready Lambda Handler

Here's the complete AWS Lambda handler pattern:

```python
import json
import os
from datetime import datetime
from typing import Dict, Any

def lambda_handler(event, context):
    """
    Production-ready Lambda handler for model switching.
    
    Supported endpoints:
    - POST /analyze/{contentId} - Single model analysis
    - POST /compare/{contentId} - Multi-model comparison
    - POST /analyze/test - Test mode with custom prompts
    """
    
    # CORS headers for web applications
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
    }
    
    try:
        # Parse request
        path_parameters = event.get('pathParameters', {})
        content_id = path_parameters.get('contentId')
        body = json.loads(event.get('body', '{}'))
        resource_path = event.get('resource', '')
        
        # Route to appropriate handler
        if '/analyze/' in resource_path:
            if content_id == "test":
                return handle_test_mode(body, headers)
            return handle_single_analysis(content_id, body, headers)
        elif '/compare/' in resource_path:
            return handle_comparison_analysis(content_id, body, headers)
        else:
            return error_response(405, "Method not allowed", headers)
    
    except Exception as e:
        print(f"Lambda error: {e}")
        return error_response(500, f"Internal server error: {str(e)}", headers)

def handle_single_analysis(content_id: str, body: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
    """Handle single model analysis."""
    
    # Extract configuration
    provider = body.get('provider', 'anthropic')
    model_id = body.get('model', get_default_model(provider))
    temperature = body.get('temperature', 0.7)
    
    # Get content and create prompt
    content_data = get_content_data(content_id)
    if not content_data:
        return error_response(404, "Content not found", headers)
    
    prompt = create_analysis_prompt(content_data)
    
    try:
        # Create and execute agent
        agent = create_strands_agent(provider, model_id, temperature)
        
        start_time = datetime.now()
        strands_result = agent(prompt)
        end_time = datetime.now()
        
        # Process response
        model_info = MODEL_REGISTRY[model_id]
        model_info["model_id"] = model_id
        response = extract_strands_response(strands_result, model_info)
        
        # Calculate latency
        if response.latency_ms == 0:
            response.latency_ms = int((end_time - start_time).total_seconds() * 1000)
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'success': True,
                'contentId': content_id,
                'provider': provider,
                'model': model_id,
                'response': response.__dict__,
                'timestamp': datetime.now().isoformat()
            })
        }
        
    except Exception as e:
        return error_response(500, f"Analysis failed: {str(e)}", headers)

def handle_comparison_analysis(content_id: str, body: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
    """Handle multi-model comparison."""
    
    # Default comparison configuration
    default_providers = [
        {'provider': 'anthropic', 'model': 'claude-3-5-sonnet-20241022'},
        {'provider': 'nova', 'model': 'us.amazon.nova-micro-v1:0'},
        {'provider': 'llama', 'model': 'meta.llama3-1-8b-instruct-v1:0'}
    ]
    
    providers_config = body.get('providers', default_providers)
    temperature = body.get('temperature', 0.7)
    
    # Get content or use test prompt
    if content_id == "test":
        prompt = body.get('prompt', 'Hello! Please identify yourself and your capabilities.')
    else:
        content_data = get_content_data(content_id)
        if not content_data:
            return error_response(404, "Content not found", headers)
        prompt = create_analysis_prompt(content_data)
    
    try:
        # Execute comparison (synchronous for Lambda simplicity)
        results = {}
        
        for config in providers_config:
            provider = config['provider']
            model_id = config['model']
            
            try:
                agent = create_strands_agent(provider, model_id, temperature)
                
                start_time = datetime.now()
                strands_result = agent(prompt)
                end_time = datetime.now()
                
                model_info = MODEL_REGISTRY[model_id]
                model_info["model_id"] = model_id
                response = extract_strands_response(strands_result, model_info)
                
                if response.latency_ms == 0:
                    response.latency_ms = int((end_time - start_time).total_seconds() * 1000)
                
                results[provider] = response.__dict__
                
            except Exception as e:
                results[provider] = {
                    "success": False,
                    "error": str(e),
                    "provider": provider,
                    "model_id": model_id
                }
        
        # Analyze results
        analysis = analyze_comparison_results({k: StandardResponse(**v) for k, v in results.items() if isinstance(v, dict) and v.get('success')})
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'success': True,
                'contentId': content_id,
                'comparison': {
                    'providers': list(results.keys()),
                    'results': results,
                    'analysis': analysis
                },
                'timestamp': datetime.now().isoformat()
            })
        }
        
    except Exception as e:
        return error_response(500, f"Comparison failed: {str(e)}", headers)

def error_response(status_code: int, message: str, headers: Dict[str, str]) -> Dict[str, Any]:
    """Standard error response format."""
    return {
        'statusCode': status_code,
        'headers': headers,
        'body': json.dumps({
            'error': message,
            'timestamp': datetime.now().isoformat()
        })
    }
```

## 🎨 Frontend Integration Example

Here's how to integrate with a React frontend:

```typescript
// types.ts
interface ModelProvider {
  provider: 'anthropic' | 'bedrock' | 'nova' | 'llama';
  model: string;
  temperature: number;
}

interface AnalysisResponse {
  success: boolean;
  provider: string;
  model: string;
  response: {
    content: string;
    model_family: string;
    latency_ms: number;
    cost_tier: string;
    capabilities: string[];
    usage: {
      input_tokens: number;
      output_tokens: number;
      total_tokens: number;
    };
  };
}

// api.ts
class FeedMinerAPI {
  constructor(private baseUrl: string) {}
  
  async analyzeWithModel(
    contentId: string, 
    modelConfig: ModelProvider
  ): Promise<AnalysisResponse> {
    const response = await fetch(`${this.baseUrl}/analyze/${contentId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(modelConfig)
    });
    
    return response.json();
  }
  
  async compareModels(
    contentId: string,
    providers: ModelProvider[],
    temperature: number = 0.7
  ): Promise<{comparison: {results: Record<string, AnalysisResponse>}}> {
    const response = await fetch(`${this.baseUrl}/compare/${contentId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ providers, temperature })
    });
    
    return response.json();
  }
  
  async testModel(modelConfig: ModelProvider, prompt: string): Promise<AnalysisResponse> {
    const response = await fetch(`${this.baseUrl}/analyze/test`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...modelConfig, prompt })
    });
    
    return response.json();
  }
}

// ModelSelector.tsx
import React, { useState } from 'react';

const ModelSelector: React.FC = () => {
  const [selectedModel, setSelectedModel] = useState<ModelProvider>({
    provider: 'anthropic',
    model: 'claude-3-5-sonnet-20241022',
    temperature: 0.7
  });
  
  const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null);
  const [loading, setLoading] = useState(false);
  
  const api = new FeedMinerAPI(process.env.REACT_APP_API_URL);
  
  const handleAnalyze = async () => {
    setLoading(true);
    try {
      const result = await api.analyzeWithModel('your-content-id', selectedModel);
      setAnalysis(result);
    } catch (error) {
      console.error('Analysis failed:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const handleCompare = async () => {
    setLoading(true);
    try {
      const comparison = await api.compareModels('your-content-id', [
        { provider: 'anthropic', model: 'claude-3-5-sonnet-20241022', temperature: 0.7 },
        { provider: 'nova', model: 'us.amazon.nova-micro-v1:0', temperature: 0.7 },
        { provider: 'llama', model: 'meta.llama3-1-8b-instruct-v1:0', temperature: 0.7 }
      ]);
      
      console.log('Comparison results:', comparison);
    } catch (error) {
      console.error('Comparison failed:', error);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="model-selector">
      <h3>AI Model Selection</h3>
      
      {/* Model Selection UI */}
      <select 
        value={selectedModel.model}
        onChange={(e) => setSelectedModel({...selectedModel, model: e.target.value})}
      >
        <option value="claude-3-5-sonnet-20241022">Claude 3.5 Sonnet</option>
        <option value="us.amazon.nova-micro-v1:0">Nova Micro</option>
        <option value="meta.llama3-1-8b-instruct-v1:0">Llama 3.1 8B</option>
      </select>
      
      {/* Temperature Control */}
      <label>
        Temperature: {selectedModel.temperature}
        <input
          type="range"
          min="0"
          max="1"
          step="0.1"
          value={selectedModel.temperature}
          onChange={(e) => setSelectedModel({...selectedModel, temperature: parseFloat(e.target.value)})}
        />
      </label>
      
      {/* Action Buttons */}
      <button onClick={handleAnalyze} disabled={loading}>
        {loading ? 'Analyzing...' : 'Analyze Content'}
      </button>
      
      <button onClick={handleCompare} disabled={loading}>
        {loading ? 'Comparing...' : 'Compare Models'}
      </button>
      
      {/* Results Display */}
      {analysis && (
        <div className="results">
          <h4>Analysis Result</h4>
          <p><strong>Model:</strong> {analysis.response.model_family}</p>
          <p><strong>Latency:</strong> {analysis.response.latency_ms}ms</p>
          <p><strong>Cost Tier:</strong> {analysis.response.cost_tier}</p>
          <div><strong>Response:</strong> {analysis.response.content}</div>
        </div>
      )}
    </div>
  );
};
```

## 📊 Monitoring & Optimization

### CloudWatch Metrics

Add custom metrics for monitoring:

```python
import boto3

cloudwatch = boto3.client('cloudwatch')

def publish_metrics(response: StandardResponse, start_time: datetime):
    """Publish custom metrics to CloudWatch."""
    
    metrics = [
        {
            'MetricName': 'ModelLatency',
            'Dimensions': [
                {'Name': 'ModelFamily', 'Value': response.model_family},
                {'Name': 'Provider', 'Value': response.provider}
            ],
            'Value': response.latency_ms,
            'Unit': 'Milliseconds'
        },
        {
            'MetricName': 'TokenUsage',
            'Dimensions': [
                {'Name': 'ModelFamily', 'Value': response.model_family},
                {'Name': 'TokenType', 'Value': 'Total'}
            ],
            'Value': response.usage.get('total_tokens', 0),
            'Unit': 'Count'
        },
        {
            'MetricName': 'ModelSuccess',
            'Dimensions': [
                {'Name': 'ModelFamily', 'Value': response.model_family}
            ],
            'Value': 1 if response.success else 0,
            'Unit': 'Count'
        }
    ]
    
    cloudwatch.put_metric_data(
        Namespace='FeedMiner/ModelSwitching',
        MetricData=metrics
    )
```

### Cost Optimization Strategies

```python
def get_cost_optimized_model(prompt_length: int, complexity: str, budget: str) -> str:
    """
    Select optimal model based on requirements and budget.
    
    Decision matrix:
    - Simple tasks + Budget conscious → Nova Micro
    - Complex reasoning + Quality focused → Claude Sonnet  
    - Balanced performance + Cost → Llama 8B
    - High volume + Speed → Nova Lite
    """
    
    if budget == "minimal" and prompt_length < 1000:
        return "us.amazon.nova-micro-v1:0"
    elif complexity == "high" and budget in ["premium", "balanced"]:
        return "claude-3-5-sonnet-20241022"
    elif complexity == "medium" and budget == "balanced":
        return "meta.llama3-1-8b-instruct-v1:0"
    elif prompt_length > 5000:  # Large context
        return "meta.llama3-1-70b-instruct-v1:0"
    else:
        return "us.amazon.nova-lite-v1:0"  # Default balanced choice
```

## 🎓 Educational Exercises

### Exercise 1: Basic Model Switching
Implement a simple model switching function that can handle 3 different providers.

### Exercise 2: Performance Comparison
Build a system that compares latency and cost across all available models for a given prompt.

### Exercise 3: Smart Model Selection
Create an algorithm that automatically selects the best model based on prompt characteristics and requirements.

### Exercise 4: Error Handling
Implement comprehensive error handling with fallback models when primary choices fail.

### Exercise 5: Async Processing
Convert the comparison system to use async processing for better performance.

## 🔧 Deployment Considerations

### AWS IAM Permissions
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": [
        "arn:aws:bedrock:*::foundation-model/anthropic.claude*",
        "arn:aws:bedrock:*::foundation-model/amazon.nova*", 
        "arn:aws:bedrock:*::foundation-model/meta.llama*"
      ]
    }
  ]
}
```

### Environment Variables
```bash
AWS_REGION=us-west-2
ANTHROPIC_API_KEY=your-key-here
CONTENT_BUCKET=your-s3-bucket
CONTENT_TABLE=your-dynamodb-table
```

### Lambda Configuration
- Runtime: Python 3.12
- Memory: 1024 MB (for Strands dependencies)
- Timeout: 60 seconds (for complex model comparisons)
- Layers: Include Strands SDK layer

## 📚 Further Reading

1. **Strands Agents Documentation** - Official AWS Strands SDK documentation
2. **AWS Bedrock Model Catalog** - Available models and their capabilities  
3. **Cost Optimization Guide** - AWS Bedrock pricing and optimization strategies
4. **Performance Benchmarking** - Model performance characteristics and use cases

## 🎯 Key Takeaways

1. **Strands Abstraction**: Handles model parameter differences internally
2. **Unified Interface**: Single agent creation pattern for all providers
3. **Response Normalization**: Consistent output format across model families
4. **Performance Monitoring**: Built-in metrics and monitoring capabilities
5. **Cost Optimization**: Smart model selection based on requirements
6. **Error Resilience**: Comprehensive error handling and fallback strategies

This implementation demonstrates production-ready model switching that's both elegant and performant, providing your students with a solid foundation for building AI-powered applications on AWS Bedrock.