# Strands Model Switching: Step-by-Step Guide

## 🎯 Learning Path Overview

This guide takes you from "Hello World" to production-ready model switching in 7 progressive steps:

1. **Basic Agent Creation** - Your first Strands agent
2. **Model Switching** - Switch between different models
3. **Response Handling** - Extract and normalize responses
4. **Error Handling** - Handle failures gracefully
5. **Multi-Model Comparison** - Compare models side-by-side
6. **Performance Optimization** - Add caching and async processing
7. **Production Deployment** - AWS Lambda with monitoring

Each step builds on the previous one, with complete working code and explanations.

---

## Step 1: Your First Strands Agent 🚀

Let's start with the absolute simplest working example:

### `step1_basic_agent.py`

```python
"""
Step 1: Basic Strands Agent
The simplest possible Strands implementation - just create an agent and ask it a question.
"""

import os
from strands import Agent
from strands.models.bedrock import BedrockModel

def create_basic_agent():
    """Create the simplest possible Strands agent."""
    
    # Create a Bedrock model (assumes AWS credentials are configured)
    model = BedrockModel(
        model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
        temperature=0.7,
        region="us-west-2"
    )
    
    # Create an agent with the model
    agent = Agent(
        name="My First Agent",
        model=model,
        system_prompt="You are a helpful assistant."
    )
    
    return agent

def main():
    """Run a simple question through the agent."""
    
    print("🤖 Creating your first Strands agent...")
    
    # Create the agent
    agent = create_basic_agent()
    
    # Ask a simple question
    question = "Hello! Can you tell me your name and what model you are?"
    
    print(f"❓ Question: {question}")
    print("⏳ Thinking...")
    
    # Get the response
    response = agent(question)
    
    print(f"🗣️  Response: {response}")

if __name__ == "__main__":
    main()
```

### Running Step 1

```bash
# Make sure AWS credentials are configured
aws configure

# Install Strands (if not already installed)
pip install strands-agents

# Run the basic example
python step1_basic_agent.py
```

### What You Learned
- ✅ How to create a BedrockModel
- ✅ How to create a Strands Agent
- ✅ How to send a prompt and get a response
- ✅ Basic Strands workflow

---

## Step 2: Model Switching 🔄

Now let's add the ability to switch between different models:

### `step2_model_switching.py`

```python
"""
Step 2: Model Switching
Learn to create agents with different models and see the differences.
"""

import os
from strands import Agent
from strands.models.bedrock import BedrockModel
from strands.models.anthropic import AnthropicModel

def create_agent_with_model(model_name: str):
    """Create an agent with a specific model."""
    
    system_prompt = "You are a helpful assistant. Please identify yourself and your capabilities."
    
    if model_name == "claude-bedrock":
        model = BedrockModel(
            model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
            temperature=0.7,
            region="us-west-2"
        )
    elif model_name == "claude-api":
        model = AnthropicModel(
            model_id="claude-3-5-sonnet-20241022",
            api_key=os.environ.get('ANTHROPIC_API_KEY'),
            temperature=0.7
        )
    elif model_name == "nova-micro":
        model = BedrockModel(
            model_id="us.amazon.nova-micro-v1:0",
            temperature=0.7,
            region="us-west-2"
        )
    elif model_name == "llama-8b":
        model = BedrockModel(
            model_id="meta.llama3-1-8b-instruct-v1:0",
            temperature=0.7,
            region="us-west-2"
        )
    else:
        raise ValueError(f"Unknown model: {model_name}")
    
    return Agent(
        name=f"Agent-{model_name}",
        model=model,
        system_prompt=system_prompt
    )

def test_model(model_name: str, question: str):
    """Test a specific model with a question."""
    
    print(f"\n🤖 Testing {model_name}...")
    
    try:
        # Create agent
        agent = create_agent_with_model(model_name)
        
        # Ask question
        print(f"❓ Question: {question}")
        print("⏳ Thinking...")
        
        response = agent(question)
        
        print(f"🗣️  {model_name} Response: {response}")
        
        return response
        
    except Exception as e:
        print(f"❌ Error with {model_name}: {e}")
        return None

def main():
    """Test multiple models with the same question."""
    
    question = "In one sentence, tell me who you are and one thing you're good at."
    
    # Available models (comment out any you don't have access to)
    models_to_test = [
        "claude-bedrock",
        # "claude-api",  # Requires ANTHROPIC_API_KEY
        "nova-micro",
        "llama-8b"
    ]
    
    print("🔄 Testing Model Switching")
    print("=" * 50)
    
    responses = {}
    
    for model_name in models_to_test:
        response = test_model(model_name, question)
        if response:
            responses[model_name] = response
    
    # Summary
    print("\n📊 Summary of Responses:")
    print("=" * 50)
    for model_name, response in responses.items():
        print(f"🤖 {model_name}: {str(response)[:100]}...")

if __name__ == "__main__":
    main()
```

### What You Learned
- ✅ How to create agents with different models
- ✅ Difference between Bedrock and Anthropic API access
- ✅ How different models respond differently
- ✅ Basic error handling for unavailable models

---

## Step 3: Response Handling 📊

Let's add proper response parsing and data extraction:

### `step3_response_handling.py`

```python
"""
Step 3: Response Handling
Learn to extract useful information from Strands responses.
"""

import time
from datetime import datetime
from typing import Dict, Any
from dataclasses import dataclass
from strands import Agent
from strands.models.bedrock import BedrockModel

@dataclass
class ModelResponse:
    """Clean, structured response from any model."""
    content: str
    model_name: str
    latency_ms: int
    success: bool
    error: str = None
    
    def __str__(self):
        status = "✅" if self.success else "❌"
        return f"{status} {self.model_name} ({self.latency_ms}ms): {self.content[:100]}..."

def create_agent_with_model(model_id: str) -> Agent:
    """Create an agent with specified model."""
    
    model = BedrockModel(
        model_id=model_id,
        temperature=0.7,
        region="us-west-2"
    )
    
    return Agent(
        name=f"Agent-{model_id}",
        model=model,
        system_prompt="You are a helpful assistant. Be concise and clear."
    )

def extract_response_content(strands_result) -> str:
    """
    Extract text content from Strands response.
    Handles different response formats that Strands might return.
    """
    
    try:
        # Method 1: Check if it's a dict with message structure
        if isinstance(strands_result, dict):
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
        
        # Method 2: Check if it's an object with attributes
        elif hasattr(strands_result, 'message'):
            message = strands_result.message
            if hasattr(message, 'content') and message.content:
                return message.content[0].text if hasattr(message.content[0], 'text') else str(message.content[0])
        
        # Method 3: Fallback to string representation
        return str(strands_result)
        
    except Exception as e:
        return f"[Response parsing error: {e}] {str(strands_result)}"

def ask_model(model_id: str, question: str) -> ModelResponse:
    """Ask a model a question and return structured response."""
    
    print(f"🤖 Asking {model_id}...")
    
    start_time = time.time()
    
    try:
        # Create agent
        agent = create_agent_with_model(model_id)
        
        # Ask question
        strands_result = agent(question)
        
        # Calculate timing
        end_time = time.time()
        latency_ms = int((end_time - start_time) * 1000)
        
        # Extract content
        content = extract_response_content(strands_result)
        
        return ModelResponse(
            content=content,
            model_name=model_id,
            latency_ms=latency_ms,
            success=True
        )
        
    except Exception as e:
        end_time = time.time()
        latency_ms = int((end_time - start_time) * 1000)
        
        return ModelResponse(
            content="",
            model_name=model_id,
            latency_ms=latency_ms,
            success=False,
            error=str(e)
        )

def main():
    """Test response handling with multiple models."""
    
    print("📊 Testing Response Handling")
    print("=" * 50)
    
    # Test question
    question = "What are the three most important things to know about AI?"
    
    # Models to test
    models = [
        "anthropic.claude-3-5-sonnet-20241022-v2:0",
        "us.amazon.nova-micro-v1:0",
        "meta.llama3-1-8b-instruct-v1:0"
    ]
    
    responses = []
    
    print(f"❓ Question: {question}\n")
    
    # Test each model
    for model_id in models:
        response = ask_model(model_id, question)
        responses.append(response)
        print(response)
        print()
    
    # Analysis
    print("📈 Performance Analysis:")
    print("=" * 50)
    
    successful_responses = [r for r in responses if r.success]
    
    if successful_responses:
        fastest = min(successful_responses, key=lambda r: r.latency_ms)
        slowest = max(successful_responses, key=lambda r: r.latency_ms)
        average_latency = sum(r.latency_ms for r in successful_responses) / len(successful_responses)
        
        print(f"🏃 Fastest: {fastest.model_name} ({fastest.latency_ms}ms)")
        print(f"🐌 Slowest: {slowest.model_name} ({slowest.latency_ms}ms)")
        print(f"📊 Average: {average_latency:.0f}ms")
        print(f"✅ Success Rate: {len(successful_responses)}/{len(responses)}")
    
    # Failed responses
    failed_responses = [r for r in responses if not r.success]
    if failed_responses:
        print(f"\n❌ Failed Models:")
        for response in failed_responses:
            print(f"   {response.model_name}: {response.error}")

if __name__ == "__main__":
    main()
```

### What You Learned
- ✅ How to extract text from complex Strands responses
- ✅ Performance measurement and timing
- ✅ Structured data classes for clean code
- ✅ Basic performance analysis and comparison

---

## Step 4: Error Handling & Resilience 🛡️

Add robust error handling and fallback strategies:

### `step4_error_handling.py`

```python
"""
Step 4: Error Handling & Resilience
Learn to handle failures gracefully and implement fallback strategies.
"""

import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
from strands import Agent
from strands.models.bedrock import BedrockModel
from strands.models.anthropic import AnthropicModel

class ModelFamily(Enum):
    CLAUDE = "claude"
    NOVA = "nova"
    LLAMA = "llama"

@dataclass
class ModelConfig:
    """Configuration for a specific model."""
    model_id: str
    family: ModelFamily
    provider: str  # "bedrock" or "anthropic"
    cost_tier: str
    fallback_priority: int  # Lower = higher priority

@dataclass 
class RobustResponse:
    """Response with comprehensive error information."""
    content: str
    model_used: str
    original_model_requested: str
    latency_ms: int
    success: bool
    error: Optional[str] = None
    fallback_used: bool = False
    retry_count: int = 0

# Model registry with fallback priorities
MODEL_REGISTRY = {
    "anthropic.claude-3-5-sonnet-20241022-v2:0": ModelConfig(
        model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
        family=ModelFamily.CLAUDE,
        provider="bedrock",
        cost_tier="high",
        fallback_priority=1
    ),
    "us.amazon.nova-micro-v1:0": ModelConfig(
        model_id="us.amazon.nova-micro-v1:0",
        family=ModelFamily.NOVA,
        provider="bedrock",
        cost_tier="very_low",
        fallback_priority=2
    ),
    "meta.llama3-1-8b-instruct-v1:0": ModelConfig(
        model_id="meta.llama3-1-8b-instruct-v1:0",
        family=ModelFamily.LLAMA,
        provider="bedrock",
        cost_tier="low",
        fallback_priority=3
    )
}

class RobustModelManager:
    """Manages model creation with error handling and fallbacks."""
    
    def __init__(self):
        self.failed_models = set()  # Track failed models
    
    def create_agent(self, model_id: str) -> Agent:
        """Create agent with proper error handling."""
        
        if model_id not in MODEL_REGISTRY:
            raise ValueError(f"Unknown model: {model_id}")
        
        config = MODEL_REGISTRY[model_id]
        
        try:
            if config.provider == "bedrock":
                model = BedrockModel(
                    model_id=model_id,
                    temperature=0.7,
                    region="us-west-2"
                )
            elif config.provider == "anthropic":
                import os
                api_key = os.environ.get('ANTHROPIC_API_KEY')
                if not api_key:
                    raise ValueError("ANTHROPIC_API_KEY not found in environment")
                
                model = AnthropicModel(
                    model_id=model_id,
                    api_key=api_key,
                    temperature=0.7
                )
            else:
                raise ValueError(f"Unknown provider: {config.provider}")
            
            return Agent(
                name=f"RobustAgent-{model_id}",
                model=model,
                system_prompt="You are a helpful assistant. Be clear and concise."
            )
            
        except Exception as e:
            self.failed_models.add(model_id)
            raise Exception(f"Failed to create agent for {model_id}: {e}")
    
    def get_fallback_models(self, original_model: str) -> List[str]:
        """Get ordered list of fallback models."""
        
        if original_model not in MODEL_REGISTRY:
            return []
        
        original_family = MODEL_REGISTRY[original_model].family
        
        # Get models from same family first, then others
        same_family = [
            mid for mid, config in MODEL_REGISTRY.items() 
            if config.family == original_family and mid != original_model and mid not in self.failed_models
        ]
        
        other_family = [
            mid for mid, config in MODEL_REGISTRY.items()
            if config.family != original_family and mid not in self.failed_models
        ]
        
        # Sort by fallback priority
        same_family.sort(key=lambda x: MODEL_REGISTRY[x].fallback_priority)
        other_family.sort(key=lambda x: MODEL_REGISTRY[x].fallback_priority)
        
        return same_family + other_family
    
    def ask_with_fallback(self, model_id: str, question: str, max_retries: int = 2) -> RobustResponse:
        """Ask question with automatic fallback and retry logic."""
        
        original_model = model_id
        models_to_try = [model_id] + self.get_fallback_models(model_id)
        
        for attempt, current_model in enumerate(models_to_try):
            if attempt >= max_retries:
                break
                
            start_time = time.time()
            
            try:
                print(f"🔄 Attempt {attempt + 1}: Trying {current_model}...")
                
                # Create agent
                agent = self.create_agent(current_model)
                
                # Ask question
                strands_result = agent(question)
                
                # Extract content
                content = self._extract_content(strands_result)
                
                # Calculate timing
                end_time = time.time()
                latency_ms = int((end_time - start_time) * 1000)
                
                # Success!
                return RobustResponse(
                    content=content,
                    model_used=current_model,
                    original_model_requested=original_model,
                    latency_ms=latency_ms,
                    success=True,
                    fallback_used=(current_model != original_model),
                    retry_count=attempt
                )
                
            except Exception as e:
                end_time = time.time()
                latency_ms = int((end_time - start_time) * 1000)
                
                print(f"❌ {current_model} failed: {e}")
                self.failed_models.add(current_model)
                
                # If this was the last model to try, return error
                if attempt == len(models_to_try) - 1 or attempt >= max_retries - 1:
                    return RobustResponse(
                        content="",
                        model_used=current_model,
                        original_model_requested=original_model,
                        latency_ms=latency_ms,
                        success=False,
                        error=str(e),
                        fallback_used=(current_model != original_model),
                        retry_count=attempt
                    )
        
        # Should never reach here, but just in case
        return RobustResponse(
            content="",
            model_used="none",
            original_model_requested=original_model,
            latency_ms=0,
            success=False,
            error="All models failed",
            fallback_used=True,
            retry_count=max_retries
        )
    
    def _extract_content(self, strands_result) -> str:
        """Extract content from Strands response."""
        # Same logic as step 3
        try:
            if isinstance(strands_result, dict):
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
                message = strands_result.message
                if hasattr(message, 'content') and message.content:
                    return message.content[0].text if hasattr(message.content[0], 'text') else str(message.content[0])
            
            return str(strands_result)
            
        except Exception as e:
            return f"[Response parsing error: {e}] {str(strands_result)}"

def main():
    """Test robust error handling."""
    
    print("🛡️  Testing Robust Error Handling")
    print("=" * 50)
    
    manager = RobustModelManager()
    
    question = "Explain what makes a good error handling strategy in 2 sentences."
    
    # Test scenarios
    test_scenarios = [
        ("anthropic.claude-3-5-sonnet-20241022-v2:0", "Primary model (should work)"),
        ("us.amazon.nova-micro-v1:0", "Fast, cheap model"),
        ("meta.llama3-1-8b-instruct-v1:0", "Open source model"),
        ("nonexistent-model", "Invalid model (should fail and fallback)")
    ]
    
    print(f"❓ Question: {question}\n")
    
    for model_id, description in test_scenarios:
        print(f"🧪 Testing: {description}")
        print(f"   Model: {model_id}")
        
        response = manager.ask_with_fallback(model_id, question)
        
        if response.success:
            fallback_text = " (using fallback)" if response.fallback_used else ""
            print(f"   ✅ Success{fallback_text}: {response.model_used} ({response.latency_ms}ms)")
            print(f"   📝 Response: {response.content[:100]}...")
        else:
            print(f"   ❌ Failed: {response.error}")
            print(f"   🔄 Retries: {response.retry_count}")
        
        print()
    
    # Summary
    print("📊 Summary:")
    print(f"   Failed models tracked: {manager.failed_models}")
    print(f"   Available models: {set(MODEL_REGISTRY.keys()) - manager.failed_models}")

if __name__ == "__main__":
    main()
```

### What You Learned
- ✅ Comprehensive error handling patterns
- ✅ Fallback strategies and model prioritization
- ✅ Retry logic with tracking
- ✅ State management for failed models

---

## Step 5: Multi-Model Comparison 🏁

Build a system to compare models side-by-side:

### `step5_model_comparison.py`

```python
"""
Step 5: Multi-Model Comparison
Learn to compare multiple models side-by-side and analyze results.
"""

import time
from typing import Dict, List, Any
from dataclasses import dataclass, asdict
from statistics import mean, median
from step4_error_handling import RobustModelManager, RobustResponse, MODEL_REGISTRY

@dataclass
class ComparisonResult:
    """Results from comparing multiple models."""
    question: str
    responses: Dict[str, RobustResponse]
    analysis: Dict[str, Any]
    timestamp: str

class ModelComparator:
    """Handles multi-model comparisons and analysis."""
    
    def __init__(self):
        self.manager = RobustModelManager()
    
    def compare_models(self, question: str, model_ids: List[str]) -> ComparisonResult:
        """Compare multiple models on the same question."""
        
        print(f"🏁 Starting comparison across {len(model_ids)} models...")
        print(f"❓ Question: {question}\n")
        
        responses = {}
        
        # Get responses from each model
        for model_id in model_ids:
            print(f"🤖 Testing {model_id}...")
            response = self.manager.ask_with_fallback(model_id, question)
            responses[model_id] = response
            
            if response.success:
                print(f"   ✅ Success: {response.latency_ms}ms")
            else:
                print(f"   ❌ Failed: {response.error}")
            print()
        
        # Analyze results
        analysis = self._analyze_responses(responses)
        
        return ComparisonResult(
            question=question,
            responses=responses,
            analysis=analysis,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
        )
    
    def _analyze_responses(self, responses: Dict[str, RobustResponse]) -> Dict[str, Any]:
        """Analyze comparison results."""
        
        successful_responses = {k: v for k, v in responses.items() if v.success}
        
        if not successful_responses:
            return {"error": "No successful responses to analyze"}
        
        # Performance analysis
        latencies = {k: v.latency_ms for k, v in successful_responses.items()}
        fastest_model = min(latencies, key=latencies.get)
        slowest_model = max(latencies, key=latencies.get)
        
        # Content analysis
        response_lengths = {k: len(v.content) for k, v in successful_responses.items()}
        most_verbose = max(response_lengths, key=response_lengths.get)
        most_concise = min(response_lengths, key=response_lengths.get)
        
        # Family analysis
        family_performance = {}
        for model_id, response in successful_responses.items():
            if model_id in MODEL_REGISTRY:
                family = MODEL_REGISTRY[model_id].family.value
                if family not in family_performance:
                    family_performance[family] = []
                family_performance[family].append(response.latency_ms)
        
        # Calculate family averages
        family_averages = {
            family: mean(latencies) 
            for family, latencies in family_performance.items()
        }
        
        # Cost analysis
        cost_analysis = {}
        for model_id, response in successful_responses.items():
            if model_id in MODEL_REGISTRY:
                cost_tier = MODEL_REGISTRY[model_id].cost_tier
                if cost_tier not in cost_analysis:
                    cost_analysis[cost_tier] = []
                cost_analysis[cost_tier].append({
                    'model': model_id,
                    'latency': response.latency_ms,
                    'length': len(response.content)
                })
        
        return {
            "performance": {
                "fastest_model": fastest_model,
                "fastest_time_ms": latencies[fastest_model],
                "slowest_model": slowest_model,
                "slowest_time_ms": latencies[slowest_model],
                "average_latency_ms": mean(latencies.values()),
                "median_latency_ms": median(latencies.values()),
                "latency_by_model": latencies
            },
            "content": {
                "most_verbose_model": most_verbose,
                "most_verbose_length": response_lengths[most_verbose],
                "most_concise_model": most_concise,
                "most_concise_length": response_lengths[most_concise],
                "average_length": mean(response_lengths.values()),
                "length_by_model": response_lengths
            },
            "families": {
                "performance_by_family": family_averages,
                "fastest_family": min(family_averages, key=family_averages.get) if family_averages else None
            },
            "cost": {
                "by_tier": cost_analysis
            },
            "success_rate": {
                "successful_models": len(successful_responses),
                "total_models": len(responses),
                "success_percentage": (len(successful_responses) / len(responses)) * 100
            }
        }
    
    def print_comparison_report(self, result: ComparisonResult):
        """Print a comprehensive comparison report."""
        
        print("📊 COMPARISON REPORT")
        print("=" * 60)
        print(f"Question: {result.question}")
        print(f"Timestamp: {result.timestamp}")
        print(f"Models Tested: {len(result.responses)}")
        print()
        
        # Individual responses
        print("🤖 INDIVIDUAL RESPONSES:")
        print("-" * 40)
        for model_id, response in result.responses.items():
            status = "✅" if response.success else "❌"
            fallback = " (fallback)" if response.fallback_used else ""
            
            print(f"{status} {model_id}{fallback}")
            
            if response.success:
                print(f"   ⏱️  Latency: {response.latency_ms}ms")
                print(f"   📝 Response: {response.content[:100]}...")
                if len(response.content) > 100:
                    print(f"   📏 Length: {len(response.content)} characters")
            else:
                print(f"   ❌ Error: {response.error}")
            print()
        
        # Analysis
        analysis = result.analysis
        if "error" not in analysis:
            print("📈 PERFORMANCE ANALYSIS:")
            print("-" * 40)
            perf = analysis["performance"]
            print(f"🏃 Fastest: {perf['fastest_model']} ({perf['fastest_time_ms']}ms)")
            print(f"🐌 Slowest: {perf['slowest_model']} ({perf['slowest_time_ms']}ms)")
            print(f"📊 Average: {perf['average_latency_ms']:.0f}ms")
            print(f"📊 Median: {perf['median_latency_ms']:.0f}ms")
            print()
            
            print("📝 CONTENT ANALYSIS:")
            print("-" * 40)
            content = analysis["content"]
            print(f"📚 Most verbose: {content['most_verbose_model']} ({content['most_verbose_length']} chars)")
            print(f"📋 Most concise: {content['most_concise_model']} ({content['most_concise_length']} chars)")
            print(f"📊 Average length: {content['average_length']:.0f} characters")
            print()
            
            print("👨‍👩‍👧‍👦 FAMILY ANALYSIS:")
            print("-" * 40)
            families = analysis["families"]
            if families["performance_by_family"]:
                for family, avg_latency in families["performance_by_family"].items():
                    print(f"🏷️  {family.title()}: {avg_latency:.0f}ms average")
                if families["fastest_family"]:
                    print(f"🏆 Fastest family: {families['fastest_family'].title()}")
            print()
            
            print("💰 SUCCESS RATE:")
            print("-" * 40)
            success = analysis["success_rate"]
            print(f"✅ Successful: {success['successful_models']}/{success['total_models']} ({success['success_percentage']:.1f}%)")

def main():
    """Run model comparison examples."""
    
    comparator = ModelComparator()
    
    # Test 1: Creative writing comparison
    print("🎨 TEST 1: Creative Writing")
    print("=" * 50)
    
    creative_question = "Write a haiku about artificial intelligence."
    creative_models = [
        "anthropic.claude-3-5-sonnet-20241022-v2:0",
        "us.amazon.nova-micro-v1:0",
        "meta.llama3-1-8b-instruct-v1:0"
    ]
    
    result1 = comparator.compare_models(creative_question, creative_models)
    comparator.print_comparison_report(result1)
    
    print("\n" + "="*80 + "\n")
    
    # Test 2: Technical explanation
    print("🔧 TEST 2: Technical Explanation")
    print("=" * 50)
    
    technical_question = "Explain the difference between machine learning and deep learning in simple terms."
    
    result2 = comparator.compare_models(technical_question, creative_models)
    comparator.print_comparison_report(result2)
    
    # Recommendation engine
    print("\n💡 RECOMMENDATIONS:")
    print("=" * 50)
    
    all_results = [result1, result2]
    
    for i, result in enumerate(all_results, 1):
        print(f"\nTest {i} Recommendations:")
        if "error" not in result.analysis:
            perf = result.analysis["performance"]
            families = result.analysis["families"]
            
            print(f"🏃 For speed: Use {perf['fastest_model']}")
            print(f"💰 For cost: Check Nova models (typically lowest cost)")
            print(f"🎯 For quality: Claude models typically excel at complex tasks")
            
            if families["fastest_family"]:
                print(f"🏷️  Best family overall: {families['fastest_family'].title()}")

if __name__ == "__main__":
    main()
```

### What You Learned
- ✅ Side-by-side model comparison
- ✅ Performance and content analysis
- ✅ Statistical analysis of results
- ✅ Family-based performance grouping
- ✅ Automated recommendation generation

---

## Step 6: Performance Optimization ⚡

Add caching and async processing for production performance:

### `step6_performance_optimization.py`

```python
"""
Step 6: Performance Optimization
Learn to optimize performance with caching and async processing.
"""

import asyncio
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor
from step4_error_handling import RobustModelManager, MODEL_REGISTRY
from step5_model_comparison import ComparisonResult

@dataclass
class CachedResponse:
    """Cached response with metadata."""
    content: str
    model_id: str
    latency_ms: int
    cached_at: float
    cache_hit: bool = False

class OptimizedModelManager:
    """High-performance model manager with caching and async support."""
    
    def __init__(self, cache_ttl: int = 300):  # 5 minute cache
        self.manager = RobustModelManager()
        self.cache_ttl = cache_ttl
        self.response_cache: Dict[str, CachedResponse] = {}
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    def _get_cache_key(self, model_id: str, question: str) -> str:
        """Generate cache key for question/model combination."""
        return f"{model_id}:{hash(question)}"
    
    def _is_cache_valid(self, cached_response: CachedResponse) -> bool:
        """Check if cached response is still valid."""
        return (time.time() - cached_response.cached_at) < self.cache_ttl
    
    def ask_with_cache(self, model_id: str, question: str) -> CachedResponse:
        """Ask model with caching support."""
        
        cache_key = self._get_cache_key(model_id, question)
        
        # Check cache first
        if cache_key in self.response_cache:
            cached = self.response_cache[cache_key]
            if self._is_cache_valid(cached):
                print(f"💾 Cache hit for {model_id}")
                cached.cache_hit = True
                return cached
            else:
                # Remove expired cache entry
                del self.response_cache[cache_key]
        
        # Cache miss - get fresh response
        print(f"🔄 Cache miss for {model_id} - fetching...")
        response = self.manager.ask_with_fallback(model_id, question)
        
        # Cache the response
        cached_response = CachedResponse(
            content=response.content,
            model_id=response.model_used,
            latency_ms=response.latency_ms,
            cached_at=time.time(),
            cache_hit=False
        )
        
        if response.success:
            self.response_cache[cache_key] = cached_response
        
        return cached_response
    
    async def ask_async(self, model_id: str, question: str) -> CachedResponse:
        """Ask model asynchronously."""
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor, 
            self.ask_with_cache, 
            model_id, 
            question
        )
    
    async def compare_models_async(self, question: str, model_ids: List[str]) -> Dict[str, CachedResponse]:
        """Compare multiple models asynchronously."""
        
        print(f"🚀 Starting async comparison of {len(model_ids)} models...")
        
        # Create tasks for all models
        tasks = [
            self.ask_async(model_id, question) 
            for model_id in model_ids
        ]
        
        # Execute all tasks concurrently
        start_time = time.time()
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()
        
        total_time = int((end_time - start_time) * 1000)
        print(f"⚡ Async comparison completed in {total_time}ms")
        
        # Process results
        results = {}
        for model_id, response in zip(model_ids, responses):
            if isinstance(response, Exception):
                print(f"❌ {model_id} failed: {response}")
                results[model_id] = CachedResponse(
                    content="",
                    model_id=model_id,
                    latency_ms=0,
                    cached_at=time.time(),
                    cache_hit=False
                )
            else:
                results[model_id] = response
        
        return results
    
    def clear_cache(self):
        """Clear the response cache."""
        self.response_cache.clear()
        print("🗑️  Cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_entries = len(self.response_cache)
        valid_entries = sum(
            1 for cached in self.response_cache.values() 
            if self._is_cache_valid(cached)
        )
        
        return {
            "total_entries": total_entries,
            "valid_entries": valid_entries,
            "expired_entries": total_entries - valid_entries,
            "cache_size_bytes": sum(
                len(cached.content) for cached in self.response_cache.values()
            )
        }

class PerformanceBenchmark:
    """Benchmark different performance optimization strategies."""
    
    def __init__(self):
        self.basic_manager = RobustModelManager()
        self.optimized_manager = OptimizedModelManager()
    
    def benchmark_sequential_vs_async(self, question: str, model_ids: List[str], rounds: int = 2):
        """Compare sequential vs async performance."""
        
        print("🏁 PERFORMANCE BENCHMARK: Sequential vs Async")
        print("=" * 60)
        print(f"Question: {question}")
        print(f"Models: {model_ids}")
        print(f"Rounds: {rounds}\n")
        
        sequential_times = []
        async_times = []
        
        for round_num in range(rounds):
            print(f"🔄 Round {round_num + 1}/{rounds}")
            
            # Test sequential
            print("   📶 Testing sequential...")
            start_time = time.time()
            
            for model_id in model_ids:
                response = self.basic_manager.ask_with_fallback(model_id, question)
            
            sequential_time = (time.time() - start_time) * 1000
            sequential_times.append(sequential_time)
            print(f"   ⏱️  Sequential: {sequential_time:.0f}ms")
            
            # Test async
            print("   🚀 Testing async...")
            start_time = time.time()
            
            async def run_async():
                return await self.optimized_manager.compare_models_async(question, model_ids)
            
            asyncio.run(run_async())
            async_time = (time.time() - start_time) * 1000
            async_times.append(async_time)
            print(f"   ⚡ Async: {async_time:.0f}ms")
            
            speedup = sequential_time / async_time
            print(f"   📈 Speedup: {speedup:.2f}x\n")
        
        # Summary
        avg_sequential = sum(sequential_times) / len(sequential_times)
        avg_async = sum(async_times) / len(async_times)
        avg_speedup = avg_sequential / avg_async
        
        print("📊 BENCHMARK RESULTS:")
        print(f"   📶 Sequential average: {avg_sequential:.0f}ms")
        print(f"   🚀 Async average: {avg_async:.0f}ms")
        print(f"   📈 Average speedup: {avg_speedup:.2f}x")
        print(f"   💾 Time saved: {avg_sequential - avg_async:.0f}ms per comparison")
    
    def benchmark_caching_performance(self, questions: List[str], model_id: str):
        """Test caching performance benefits."""
        
        print("💾 CACHING PERFORMANCE BENCHMARK")
        print("=" * 60)
        print(f"Model: {model_id}")
        print(f"Questions: {len(questions)}\n")
        
        # Clear cache to start fresh
        self.optimized_manager.clear_cache()
        
        # First pass - populate cache
        print("🔄 First pass (cache population):")
        first_pass_times = []
        
        for i, question in enumerate(questions):
            start_time = time.time()
            response = self.optimized_manager.ask_with_cache(model_id, question)
            end_time = time.time()
            
            elapsed = (end_time - start_time) * 1000
            first_pass_times.append(elapsed)
            
            print(f"   Q{i+1}: {elapsed:.0f}ms (cache: {'HIT' if response.cache_hit else 'MISS'})")
        
        # Second pass - use cache
        print("\n🚀 Second pass (cache utilization):")
        second_pass_times = []
        
        for i, question in enumerate(questions):
            start_time = time.time()
            response = self.optimized_manager.ask_with_cache(model_id, question)
            end_time = time.time()
            
            elapsed = (end_time - start_time) * 1000
            second_pass_times.append(elapsed)
            
            print(f"   Q{i+1}: {elapsed:.0f}ms (cache: {'HIT' if response.cache_hit else 'MISS'})")
        
        # Analysis
        avg_first_pass = sum(first_pass_times) / len(first_pass_times)
        avg_second_pass = sum(second_pass_times) / len(second_pass_times)
        cache_speedup = avg_first_pass / avg_second_pass
        
        cache_stats = self.optimized_manager.get_cache_stats()
        
        print("\n📊 CACHING RESULTS:")
        print(f"   🔄 First pass average: {avg_first_pass:.0f}ms")
        print(f"   💾 Second pass average: {avg_second_pass:.0f}ms")
        print(f"   📈 Cache speedup: {cache_speedup:.2f}x")
        print(f"   💾 Cache entries: {cache_stats['valid_entries']}")
        print(f"   📦 Cache size: {cache_stats['cache_size_bytes']} bytes")

def main():
    """Run performance optimization examples."""
    
    benchmark = PerformanceBenchmark()
    
    # Test models
    test_models = [
        "anthropic.claude-3-5-sonnet-20241022-v2:0",
        "us.amazon.nova-micro-v1:0",
        "meta.llama3-1-8b-instruct-v1:0"
    ]
    
    # Benchmark 1: Sequential vs Async
    async_question = "What are the key benefits of cloud computing?"
    benchmark.benchmark_sequential_vs_async(async_question, test_models, rounds=2)
    
    print("\n" + "="*80 + "\n")
    
    # Benchmark 2: Caching Performance
    cache_questions = [
        "What is machine learning?",
        "Explain neural networks briefly.",
        "What are the benefits of AI?",
        "What is machine learning?",  # Repeat to test cache
        "Explain neural networks briefly."  # Repeat to test cache
    ]
    
    benchmark.benchmark_caching_performance(cache_questions, test_models[0])
    
    print("\n💡 OPTIMIZATION RECOMMENDATIONS:")
    print("=" * 50)
    print("🚀 Use async processing for multi-model comparisons")
    print("💾 Implement caching for repeated questions")
    print("⚡ Consider model warm-up for frequently used models")
    print("📊 Monitor cache hit rates and adjust TTL accordingly")
    print("🔧 Use connection pooling for high-throughput scenarios")

if __name__ == "__main__":
    main()
```

### What You Learned
- ✅ Response caching with TTL
- ✅ Async processing for concurrent requests
- ✅ Performance benchmarking and measurement
- ✅ Cache management and statistics
- ✅ Production optimization strategies

---

## Step 7: Production AWS Lambda 🚀

Finally, let's put it all together in a production-ready AWS Lambda:

### `step7_production_lambda.py`

```python
"""
Step 7: Production AWS Lambda
Complete production-ready implementation with all optimizations.
"""

import json
import os
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from step6_performance_optimization import OptimizedModelManager

# AWS Lambda handler
def lambda_handler(event, context):
    """
    Production AWS Lambda handler for Strands model switching.
    
    Endpoints:
    - POST /analyze/{contentId} - Single model analysis
    - POST /compare/{contentId} - Multi-model comparison
    - POST /test - Test mode with custom prompts
    """
    
    # CORS headers
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
    }
    
    try:
        # Parse request
        path_parameters = event.get('pathParameters', {})
        resource_path = event.get('resource', '')
        body = json.loads(event.get('body', '{}'))
        
        # Initialize optimized manager
        manager = OptimizedModelManager()
        
        # Route to appropriate handler
        if '/analyze/' in resource_path:
            content_id = path_parameters.get('contentId')
            if content_id == 'test':
                return handle_test_mode(manager, body, headers)
            else:
                return handle_single_analysis(manager, content_id, body, headers)
        
        elif '/compare/' in resource_path:
            content_id = path_parameters.get('contentId')
            return handle_comparison(manager, content_id, body, headers)
        
        elif '/test' in resource_path:
            return handle_test_mode(manager, body, headers)
        
        else:
            return error_response(404, "Endpoint not found", headers)
    
    except Exception as e:
        print(f"Lambda error: {e}")
        return error_response(500, f"Internal server error: {str(e)}", headers)

def handle_single_analysis(manager: OptimizedModelManager, content_id: str, body: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
    """Handle single model analysis with caching."""
    
    try:
        # Extract parameters
        model_id = body.get('model', 'anthropic.claude-3-5-sonnet-20241022-v2:0')
        temperature = body.get('temperature', 0.7)
        
        # Get content or use test prompt
        if content_id and content_id != 'test':
            content_data = get_content_data(content_id)
            if not content_data:
                return error_response(404, "Content not found", headers)
            prompt = create_analysis_prompt(content_data)
        else:
            prompt = body.get('prompt', 'Hello! Please introduce yourself.')
        
        # Analyze with caching
        response = manager.ask_with_cache(model_id, prompt)
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'success': True,
                'contentId': content_id,
                'model': response.model_id,
                'response': {
                    'content': response.content,
                    'latency_ms': response.latency_ms,
                    'cached': response.cache_hit
                },
                'timestamp': datetime.now().isoformat()
            })
        }
    
    except Exception as e:
        return error_response(500, f"Analysis failed: {str(e)}", headers)

def handle_comparison(manager: OptimizedModelManager, content_id: str, body: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
    """Handle multi-model comparison with async processing."""
    
    try:
        # Default model set for comparison
        default_models = [
            'anthropic.claude-3-5-sonnet-20241022-v2:0',
            'us.amazon.nova-micro-v1:0',
            'meta.llama3-1-8b-instruct-v1:0'
        ]
        
        # Extract parameters
        model_ids = body.get('models', default_models)
        temperature = body.get('temperature', 0.7)
        
        # Get content or use test prompt
        if content_id and content_id != 'test':
            content_data = get_content_data(content_id)
            if not content_data:
                return error_response(404, "Content not found", headers)
            prompt = create_analysis_prompt(content_data)
        else:
            prompt = body.get('prompt', 'Compare your capabilities and response style.')
        
        # Run async comparison
        async def run_comparison():
            return await manager.compare_models_async(prompt, model_ids)
        
        responses = asyncio.run(run_comparison())
        
        # Analyze results
        analysis = analyze_comparison_results(responses)
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'success': True,
                'contentId': content_id,
                'comparison': {
                    'models_tested': len(model_ids),
                    'results': {
                        model_id: {
                            'content': response.content,
                            'latency_ms': response.latency_ms,
                            'cached': response.cache_hit,
                            'model_used': response.model_id
                        }
                        for model_id, response in responses.items()
                        if response.content  # Only include successful responses
                    },
                    'analysis': analysis
                },
                'timestamp': datetime.now().isoformat()
            })
        }
    
    except Exception as e:
        return error_response(500, f"Comparison failed: {str(e)}", headers)

def handle_test_mode(manager: OptimizedModelManager, body: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
    """Handle test mode for quick model testing."""
    
    try:
        model_id = body.get('model', 'anthropic.claude-3-5-sonnet-20241022-v2:0')
        prompt = body.get('prompt', 'Hello! This is a test. Please respond briefly.')
        
        response = manager.ask_with_cache(model_id, prompt)
        
        # Get cache stats for monitoring
        cache_stats = manager.get_cache_stats()
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'success': True,
                'test_mode': True,
                'model': response.model_id,
                'prompt': prompt,
                'response': {
                    'content': response.content,
                    'latency_ms': response.latency_ms,
                    'cached': response.cache_hit
                },
                'cache_stats': cache_stats,
                'timestamp': datetime.now().isoformat()
            })
        }
    
    except Exception as e:
        return error_response(500, f"Test failed: {str(e)}", headers)

def get_content_data(content_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve content data from DynamoDB/S3."""
    # Implementation would depend on your data storage
    # For this example, return None to trigger test mode
    return None

def create_analysis_prompt(content_data: Dict[str, Any]) -> str:
    """Create analysis prompt from content data."""
    # Simplified implementation
    return "Analyze this content and provide insights."

def analyze_comparison_results(responses: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze comparison results."""
    
    successful_responses = {
        k: v for k, v in responses.items() 
        if v.content and len(v.content) > 0
    }
    
    if not successful_responses:
        return {"error": "No successful responses"}
    
    # Performance analysis
    latencies = {k: v.latency_ms for k, v in successful_responses.items()}
    cache_hits = {k: v.cache_hit for k, v in successful_responses.items()}
    
    fastest_model = min(latencies, key=latencies.get)
    average_latency = sum(latencies.values()) / len(latencies)
    cache_hit_rate = sum(cache_hits.values()) / len(cache_hits)
    
    return {
        'performance': {
            'fastest_model': fastest_model,
            'fastest_time_ms': latencies[fastest_model],
            'average_latency_ms': average_latency,
            'cache_hit_rate': cache_hit_rate
        },
        'models_successful': len(successful_responses),
        'models_total': len(responses),
        'success_rate': len(successful_responses) / len(responses)
    }

def error_response(status_code: int, message: str, headers: Dict[str, str]) -> Dict[str, Any]:
    """Standard error response."""
    return {
        'statusCode': status_code,
        'headers': headers,
        'body': json.dumps({
            'error': message,
            'timestamp': datetime.now().isoformat()
        })
    }

# For local testing
def main():
    """Local testing function."""
    
    print("🚀 Testing Production Lambda Locally")
    print("=" * 50)
    
    # Simulate Lambda events
    test_events = [
        {
            'name': 'Single Analysis Test',
            'event': {
                'resource': '/analyze/{contentId}',
                'pathParameters': {'contentId': 'test'},
                'body': json.dumps({
                    'model': 'us.amazon.nova-micro-v1:0',
                    'prompt': 'Explain quantum computing in one sentence.'
                })
            }
        },
        {
            'name': 'Comparison Test',
            'event': {
                'resource': '/compare/{contentId}',
                'pathParameters': {'contentId': 'test'},
                'body': json.dumps({
                    'prompt': 'What makes you unique as an AI model?',
                    'models': [
                        'anthropic.claude-3-5-sonnet-20241022-v2:0',
                        'us.amazon.nova-micro-v1:0'
                    ]
                })
            }
        }
    ]
    
    for test in test_events:
        print(f"\n🧪 {test['name']}")
        print("-" * 30)
        
        response = lambda_handler(test['event'], {})
        
        print(f"Status: {response['statusCode']}")
        
        if response['statusCode'] == 200:
            body = json.loads(response['body'])
            print(f"Success: {body.get('success', False)}")
            
            if 'response' in body:
                resp = body['response']
                print(f"Content: {resp['content'][:100]}...")
                print(f"Latency: {resp['latency_ms']}ms")
                print(f"Cached: {resp.get('cached', False)}")
            
            elif 'comparison' in body:
                comp = body['comparison']
                print(f"Models tested: {comp['models_tested']}")
                print(f"Results: {len(comp['results'])} successful")
                if 'analysis' in comp:
                    analysis = comp['analysis']
                    if 'performance' in analysis:
                        perf = analysis['performance']
                        print(f"Fastest: {perf.get('fastest_model', 'N/A')} ({perf.get('fastest_time_ms', 0)}ms)")
        else:
            body = json.loads(response['body'])
            print(f"Error: {body.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()
```

### AWS SAM Template for Deployment

Create `template.yaml`:

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: Strands Model Switching Demo

Parameters:
  Environment:
    Type: String
    Default: dev
    AllowedValues: [dev, staging, prod]

Globals:
  Function:
    Runtime: python3.12
    MemorySize: 1024
    Timeout: 60
    Environment:
      Variables:
        AWS_REGION: !Ref AWS::Region

Resources:
  ModelSwitchingFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: .
      Handler: step7_production_lambda.lambda_handler
      Events:
        AnalyzeAPI:
          Type: Api
          Properties:
            Path: /analyze/{contentId}
            Method: post
        CompareAPI:
          Type: Api
          Properties:
            Path: /compare/{contentId}
            Method: post
        TestAPI:
          Type: Api
          Properties:
            Path: /test
            Method: post
      Policies:
        - BedrockInvokeModelPolicy:
            ModelId: "*"

Outputs:
  ApiEndpoint:
    Description: "API Gateway endpoint URL"
    Value: !Sub "https://${ServerlessRestApi}.execute-api.${AWS::Region}.amazonaws.com/Prod/"
```

### Deployment Commands

```bash
# Build and deploy
sam build
sam deploy --guided

# Test deployed API
curl -X POST "https://your-api-url/Prod/test" \
  -H "Content-Type: application/json" \
  -d '{"model": "us.amazon.nova-micro-v1:0", "prompt": "Hello from AWS!"}'
```

### What You Learned
- ✅ Production-ready AWS Lambda implementation
- ✅ Complete error handling and monitoring
- ✅ SAM deployment configuration
- ✅ Performance optimization in serverless environment
- ✅ Real-world API design patterns

---

## 🎓 Learning Path Summary

You've now built a complete model switching system from scratch! Here's what you accomplished:

### **Step 1**: Basic Agent Creation
- ✅ Created your first Strands agent
- ✅ Learned BedrockModel basics
- ✅ Executed simple prompts

### **Step 2**: Model Switching
- ✅ Switched between different models
- ✅ Compared Bedrock vs Anthropic API
- ✅ Handled basic errors

### **Step 3**: Response Handling  
- ✅ Extracted structured data from responses
- ✅ Measured performance metrics
- ✅ Built clean data models

### **Step 4**: Error Handling
- ✅ Implemented robust error handling
- ✅ Added fallback strategies
- ✅ Built retry logic

### **Step 5**: Multi-Model Comparison
- ✅ Created side-by-side comparisons
- ✅ Analyzed performance across models
- ✅ Generated recommendations

### **Step 6**: Performance Optimization
- ✅ Added response caching
- ✅ Implemented async processing
- ✅ Benchmarked performance improvements

### **Step 7**: Production Deployment
- ✅ Built production-ready Lambda
- ✅ Deployed with AWS SAM
- ✅ Created complete API system

## 🚀 Next Steps

1. **Experiment**: Try different models and prompts
2. **Extend**: Add more model families or providers
3. **Monitor**: Implement CloudWatch metrics
4. **Scale**: Add load balancing and auto-scaling
5. **Enhance**: Build a web frontend

You now have a solid foundation for building AI-powered applications with AWS Bedrock and Strands! 🎉