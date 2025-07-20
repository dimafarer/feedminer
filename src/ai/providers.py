"""
AI Provider Abstraction Layer for FeedMiner.

This module provides a unified interface for multiple AI providers,
enabling runtime switching between Anthropic API and AWS Bedrock.
"""

import json
import os
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import boto3
from anthropic import Anthropic
from pydantic import BaseModel


class ModelProvider(ABC):
    """Abstract base class for AI model providers."""
    
    @abstractmethod
    async def generate(self, prompt: str, model_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate AI response from prompt."""
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Get provider name for logging and metrics."""
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """Get list of available models for this provider."""
        pass


class AnthropicProvider(ModelProvider):
    """Anthropic API provider for Claude models."""
    
    def __init__(self, api_key: str = None):
        """Initialize Anthropic provider."""
        self.api_key = api_key or os.environ.get('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("Anthropic API key is required")
        
        self.client = Anthropic(api_key=self.api_key)
        self.provider_name = "anthropic"
        
    async def generate(self, prompt: str, model_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate response using Anthropic API."""
        start_time = time.time()
        
        # Default model configuration
        config = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 4000,
            "temperature": 0.7,
            **(model_config or {})
        }
        
        try:
            response = self.client.messages.create(
                model=config["model"],
                max_tokens=config["max_tokens"],
                temperature=config["temperature"],
                messages=[{"role": "user", "content": prompt}]
            )
            
            end_time = time.time()
            
            return {
                "content": response.content[0].text,
                "provider": self.provider_name,
                "model": config["model"],
                "latency_ms": int((end_time - start_time) * 1000),
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens
                },
                "success": True
            }
            
        except Exception as e:
            end_time = time.time()
            return {
                "content": None,
                "provider": self.provider_name,
                "model": config.get("model", "unknown"),
                "latency_ms": int((end_time - start_time) * 1000),
                "error": str(e),
                "success": False
            }
    
    def get_provider_name(self) -> str:
        """Get provider name."""
        return self.provider_name
    
    def get_available_models(self) -> List[str]:
        """Get available Anthropic models."""
        return [
            "claude-3-5-sonnet-20241022",
            "claude-3-haiku-20240307",
            "claude-3-opus-20240229"
        ]


class BedrockProvider(ModelProvider):
    """AWS Bedrock provider for multiple model families."""
    
    def __init__(self, region: str = None):
        """Initialize Bedrock provider."""
        self.region = region or os.environ.get('AWS_REGION', 'us-west-2')
        self.client = boto3.client('bedrock-runtime', region_name=self.region)
        self.provider_name = "bedrock"
    
    async def generate(self, prompt: str, model_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate response using AWS Bedrock."""
        start_time = time.time()
        
        # Default model configuration
        config = {
            "model": "anthropic.claude-3-5-sonnet-20241022-v2:0",
            "max_tokens": 4000,
            "temperature": 0.7,
            **(model_config or {})
        }
        
        try:
            # Prepare request based on model family
            if "anthropic" in config["model"]:
                body = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": config["max_tokens"],
                    "temperature": config["temperature"],
                    "messages": [{"role": "user", "content": prompt}]
                }
            elif "amazon.titan" in config["model"]:
                body = {
                    "inputText": prompt,
                    "textGenerationConfig": {
                        "maxTokenCount": config["max_tokens"],
                        "temperature": config["temperature"],
                        "topP": 0.9,
                        "stopSequences": []
                    }
                }
            elif "cohere" in config["model"]:
                body = {
                    "prompt": prompt,
                    "max_tokens": config["max_tokens"],
                    "temperature": config["temperature"],
                    "p": 0.9,
                    "k": 0,
                    "stop_sequences": [],
                    "return_likelihoods": "NONE"
                }
            elif "ai21" in config["model"]:
                body = {
                    "prompt": prompt,
                    "maxTokens": config["max_tokens"],
                    "temperature": config["temperature"],
                    "topP": 0.9,
                    "stopSequences": [],
                    "countPenalty": {"scale": 0},
                    "presencePenalty": {"scale": 0},
                    "frequencyPenalty": {"scale": 0}
                }
            elif "meta.llama" in config["model"]:
                body = {
                    "prompt": prompt,
                    "max_gen_len": config["max_tokens"],
                    "temperature": config["temperature"],
                    "top_p": 0.9
                }
            elif "mistral" in config["model"]:
                body = {
                    "prompt": prompt,
                    "max_tokens": config["max_tokens"],
                    "temperature": config["temperature"],
                    "top_p": 0.9,
                    "top_k": 50
                }
            else:
                # Generic format for other models
                body = {
                    "inputText": prompt,
                    "textGenerationConfig": {
                        "maxTokenCount": config["max_tokens"],
                        "temperature": config["temperature"]
                    }
                }
            
            response = self.client.invoke_model(
                modelId=config["model"],
                contentType="application/json",
                accept="application/json",
                body=json.dumps(body)
            )
            
            end_time = time.time()
            
            # Parse response based on model family
            response_body = json.loads(response['body'].read())
            
            if "anthropic" in config["model"]:
                content = response_body["content"][0]["text"]
                usage = response_body.get("usage", {})
                input_tokens = usage.get("input_tokens", 0)
                output_tokens = usage.get("output_tokens", 0)
            elif "amazon.titan" in config["model"]:
                content = response_body.get("outputText", "")
                input_tokens = response_body.get("inputTextTokenCount", 0)
                output_tokens = response_body.get("outputTextTokenCount", 0)
            elif "cohere" in config["model"]:
                generations = response_body.get("generations", [])
                content = generations[0].get("text", "") if generations else ""
                input_tokens = response_body.get("prompt_tokens", 0)
                output_tokens = response_body.get("completion_tokens", 0)
            elif "ai21" in config["model"]:
                completions = response_body.get("completions", [])
                content = completions[0].get("data", {}).get("text", "") if completions else ""
                input_tokens = response_body.get("prompt", {}).get("tokens", [])
                input_tokens = len(input_tokens) if isinstance(input_tokens, list) else 0
                output_tokens = len(content.split()) if content else 0  # Rough estimate
            elif "meta.llama" in config["model"]:
                content = response_body.get("generation", "")
                input_tokens = response_body.get("prompt_token_count", 0)
                output_tokens = response_body.get("generation_token_count", 0)
            elif "mistral" in config["model"]:
                outputs = response_body.get("outputs", [])
                content = outputs[0].get("text", "") if outputs else ""
                input_tokens = response_body.get("prompt_tokens", 0)
                output_tokens = response_body.get("completion_tokens", 0)
            else:
                # Generic parsing for other models
                content = response_body.get("outputText", response_body.get("generations", [{}])[0].get("text", ""))
                input_tokens = response_body.get("inputTextTokenCount", 0)
                output_tokens = response_body.get("outputTextTokenCount", 0)
            
            return {
                "content": content,
                "provider": self.provider_name,
                "model": config["model"],
                "latency_ms": int((end_time - start_time) * 1000),
                "usage": {
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": input_tokens + output_tokens
                },
                "success": True
            }
            
        except Exception as e:
            end_time = time.time()
            return {
                "content": None,
                "provider": self.provider_name,
                "model": config.get("model", "unknown"),
                "latency_ms": int((end_time - start_time) * 1000),
                "error": str(e),
                "success": False
            }
    
    def get_provider_name(self) -> str:
        """Get provider name."""
        return self.provider_name
    
    def get_available_models(self) -> List[str]:
        """Get available Bedrock models."""
        return [
            # Anthropic Claude models (recommended for FeedMiner)
            "anthropic.claude-3-5-sonnet-20241022-v2:0",
            "anthropic.claude-3-haiku-20240307-v1:0",
            "anthropic.claude-3-opus-20240229-v1:0",
            "anthropic.claude-instant-v1",
            
            # Amazon Titan models
            "amazon.titan-text-express-v1",
            "amazon.titan-text-lite-v1",
            "amazon.titan-text-premier-v1:0",
            
            # Cohere models
            "cohere.command-text-v14",
            "cohere.command-light-text-v14",
            "cohere.command-r-v1:0",
            "cohere.command-r-plus-v1:0",
            
            # AI21 models
            "ai21.j2-ultra-v1",
            "ai21.j2-mid-v1",
            "ai21.jamba-instruct-v1:0",
            
            # Meta Llama models
            "meta.llama2-13b-chat-v1",
            "meta.llama2-70b-chat-v1",
            "meta.llama3-8b-instruct-v1:0",
            "meta.llama3-70b-instruct-v1:0",
            
            # Mistral AI models
            "mistral.mistral-7b-instruct-v0:2",
            "mistral.mixtral-8x7b-instruct-v0:1",
            "mistral.mistral-large-2402-v1:0"
        ]


class ModelProviderFactory:
    """Factory for creating AI model providers."""
    
    @staticmethod
    def create_provider(provider_type: str, **kwargs) -> ModelProvider:
        """Create provider instance based on type."""
        if provider_type.lower() == "anthropic":
            return AnthropicProvider(**kwargs)
        elif provider_type.lower() == "bedrock":
            return BedrockProvider(**kwargs)
        else:
            raise ValueError(f"Unknown provider type: {provider_type}")
    
    @staticmethod
    def get_available_providers() -> List[str]:
        """Get list of available provider types."""
        return ["anthropic", "bedrock"]


class ModelConfiguration(BaseModel):
    """Configuration for AI model requests."""
    provider: str
    model: str
    temperature: float = 0.7
    max_tokens: int = 4000
    additional_params: Dict[str, Any] = {}


class AIProviderManager:
    """Manager for multiple AI providers with fallback support."""
    
    def __init__(self, primary_provider: str = None, fallback_provider: str = None):
        """Initialize AI provider manager."""
        self.providers = {}
        self.primary_provider = primary_provider or os.environ.get('PRIMARY_AI_PROVIDER', 'anthropic')
        self.fallback_provider = fallback_provider or os.environ.get('FALLBACK_AI_PROVIDER', 'bedrock')
        
        # Initialize providers
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize available providers."""
        try:
            # Try to initialize Anthropic provider
            if os.environ.get('ANTHROPIC_API_KEY'):
                self.providers['anthropic'] = ModelProviderFactory.create_provider('anthropic')
        except Exception as e:
            print(f"Failed to initialize Anthropic provider: {e}")
        
        try:
            # Try to initialize Bedrock provider
            self.providers['bedrock'] = ModelProviderFactory.create_provider('bedrock')
        except Exception as e:
            print(f"Failed to initialize Bedrock provider: {e}")
    
    async def generate(self, prompt: str, config: ModelConfiguration = None) -> Dict[str, Any]:
        """Generate AI response with fallback support."""
        if not config:
            config = ModelConfiguration(
                provider=self.primary_provider,
                model=self._get_default_model(self.primary_provider)
            )
        
        # Try primary provider
        if config.provider in self.providers:
            result = await self.providers[config.provider].generate(
                prompt,
                {
                    "model": config.model,
                    "temperature": config.temperature,
                    "max_tokens": config.max_tokens,
                    **config.additional_params
                }
            )
            
            if result["success"]:
                return result
            
            print(f"Primary provider {config.provider} failed: {result.get('error')}")
        
        # Try fallback provider if primary fails
        if self.fallback_provider and self.fallback_provider in self.providers:
            fallback_model = self._get_default_model(self.fallback_provider)
            result = await self.providers[self.fallback_provider].generate(
                prompt,
                {
                    "model": fallback_model,
                    "temperature": config.temperature,
                    "max_tokens": config.max_tokens,
                    **config.additional_params
                }
            )
            
            result["used_fallback"] = True
            result["original_provider"] = config.provider
            return result
        
        # No providers available
        return {
            "content": None,
            "provider": "none",
            "model": "none",
            "latency_ms": 0,
            "error": "No AI providers available",
            "success": False
        }
    
    def _get_default_model(self, provider: str) -> str:
        """Get default model for provider."""
        defaults = {
            "anthropic": "claude-3-5-sonnet-20241022",
            "bedrock": "anthropic.claude-3-5-sonnet-20241022-v2:0"
        }
        return defaults.get(provider, "")
    
    def get_available_providers(self) -> List[str]:
        """Get list of initialized providers."""
        return list(self.providers.keys())
    
    def get_provider_models(self, provider: str) -> List[str]:
        """Get available models for a provider."""
        if provider in self.providers:
            return self.providers[provider].get_available_models()
        return []
    
    def compare_providers(self, prompt: str, providers: List[str] = None) -> Dict[str, Any]:
        """Compare multiple providers on the same prompt."""
        if not providers:
            providers = list(self.providers.keys())
        
        results = {}
        for provider in providers:
            if provider in self.providers:
                config = ModelConfiguration(
                    provider=provider,
                    model=self._get_default_model(provider)
                )
                result = self.generate(prompt, config)
                results[provider] = result
        
        return results