"""
Strands-based Model Switching API for FeedMiner v0.2.0.

This API endpoint replaces the custom AI provider abstraction with proper
AWS Strands Agent patterns for switching between Anthropic API and AWS Bedrock.

Endpoints:
- POST /analyze/{contentId} - Analyze content with specific provider/model
- POST /compare/{contentId} - Compare analysis across multiple providers
"""

import json
import os
import sys
import boto3
from datetime import datetime
from typing import Dict, Any, Optional

# Add layers to path for AI providers (if needed for data access)
sys.path.append('/opt/python')

try:
    from strands import Agent
    from strands.models.anthropic import AnthropicModel
    from strands.models.bedrock import BedrockModel
    STRANDS_AVAILABLE = True
except ImportError as e:
    print(f"Strands import error: {e}")
    STRANDS_AVAILABLE = False


def handler(event, context):
    """
    Lambda handler for Strands-based model switching and comparison API.
    
    Supports:
    - POST /analyze/{contentId} - Run analysis with specific provider
    - POST /compare/{contentId} - Compare multiple providers
    """
    
    print(f"Strands model switching API received event: {json.dumps(event)}")
    
    # CORS headers
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
    }
    
    try:
        # Extract path parameters
        path_parameters = event.get('pathParameters', {})
        content_id = path_parameters.get('contentId')
        
        if not content_id:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    'error': 'Content ID is required',
                    'message': 'Please provide a valid content ID in the path'
                })
            }
        
        # Parse request body
        body = {}
        if event.get('body'):
            try:
                body = json.loads(event['body'])
            except json.JSONDecodeError:
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({
                        'error': 'Invalid JSON in request body'
                    })
                }
        
        # Get HTTP method and path
        http_method = event.get('httpMethod', '')
        resource_path = event.get('resource', '')
        
        # Route to appropriate handler
        if http_method == 'POST':
            if '/analyze/' in resource_path:
                # Special test mode for content_id "test"
                if content_id == "test":
                    return handle_test_strands_integration(body, headers)
                return handle_strands_analyze_with_provider(content_id, body, headers)
            elif '/compare/' in resource_path:
                return handle_strands_compare_providers(content_id, body, headers)
        
        # Method not allowed
        return {
            'statusCode': 405,
            'headers': headers,
            'body': json.dumps({
                'error': 'Method not allowed',
                'allowed_methods': ['POST']
            })
        }
    
    except Exception as e:
        print(f"Error in Strands model switching API: {e}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }


def create_strands_agent(provider: str, model_id: str, temperature: float = 0.7) -> Agent:
    """Create a Strands agent with the specified model configuration.
    
    Supports multiple model families:
    - Anthropic Claude (via Anthropic API and Bedrock)
    - Amazon Nova (via Bedrock with inference profiles)
    - Meta Llama (via Bedrock)
    """
    
    system_prompt = """You are an expert at analyzing Instagram saved content. 
    You understand social media trends, content categories, and user behavior patterns.
    Extract meaningful insights from Instagram post data and provide structured analysis."""
    
    if provider == "anthropic":
        # Get API key from environment or creds file
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            # Try to read from creds file (for Lambda environment)
            try:
                with open('../creds/anthropic-apikey', 'r') as f:
                    lines = f.readlines()
                    if len(lines) >= 2:
                        api_key = lines[1].strip()
            except:
                pass
        
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment or creds file")
        
        model = AnthropicModel(
            model_id=model_id,
            api_key=api_key,
            temperature=temperature,
            max_tokens=4096
        )
    elif provider in ["bedrock", "nova", "llama"]:
        # Handle all Bedrock-based models (Claude, Nova, Llama)
        model = create_bedrock_model_for_family(model_id, temperature)
    else:
        raise ValueError(f"Unsupported provider: {provider}")
    
    return Agent(
        name="FeedMiner Content Analysis Agent",
        model=model,
        system_prompt=system_prompt
    )


def create_bedrock_model_for_family(model_id: str, temperature: float) -> BedrockModel:
    """Create Strands BedrockModel with family-specific configuration.
    
    Based on test results:
    - Claude models: Work with standard BedrockModel (no additional fields)
    - Nova models: Work with standard BedrockModel (no additional fields needed)
    - Llama models: Work with standard BedrockModel (no additional fields needed)
    
    The Strands BedrockModel handles parameter differences internally.
    """
    
    # Determine model family
    model_family = detect_model_family(model_id)
    
    # Create base configuration that works for all families
    config = {
        "model_id": model_id,
        "temperature": temperature,
        "region": os.environ.get('AWS_REGION', 'us-west-2')
    }
    
    # Model family-specific adjustments
    if model_family == "nova":
        # Nova models use inference profile IDs and have different parameter names
        # but Strands handles this internally - no additional_request_fields needed
        pass
    elif model_family == "llama":
        # Llama models use different parameter names (max_gen_len vs max_tokens)
        # but Strands handles this internally - no additional_request_fields needed
        pass
    elif model_family == "claude":
        # Claude models work with standard Strands BedrockModel
        pass
    
    return BedrockModel(**config)


def detect_model_family(model_id: str) -> str:
    """Detect model family from model ID."""
    if "nova" in model_id.lower():
        return "nova"
    elif "llama" in model_id.lower():
        return "llama"
    elif "claude" in model_id.lower() or "anthropic" in model_id.lower():
        return "claude"
    else:
        return "unknown"


def extract_strands_response(strands_result, model_family: str = "claude") -> Dict[str, Any]:
    """Extract clean response data from Strands agent result."""
    
    try:
        # Strands can return different types of objects
        # Check if it's a dict with message structure
        if isinstance(strands_result, dict):
            # Handle dictionary result format
            if 'message' in strands_result:
                message = strands_result['message']
                if isinstance(message, dict) and 'content' in message:
                    content_list = message['content']
                    if isinstance(content_list, list) and len(content_list) > 0:
                        content = content_list[0].get('text', str(strands_result))
                    else:
                        content = str(strands_result)
                else:
                    content = str(message)
            # Handle direct message format (common case)
            elif 'content' in strands_result:
                content_list = strands_result['content']
                if isinstance(content_list, list) and len(content_list) > 0:
                    content = content_list[0].get('text', str(content_list[0]))
                else:
                    content = str(content_list)
            # Handle role+content format
            elif 'role' in strands_result and strands_result.get('role') == 'assistant':
                content_list = strands_result.get('content', [])
                if isinstance(content_list, list) and len(content_list) > 0:
                    content = content_list[0].get('text', str(content_list[0]))
                else:
                    content = str(content_list)
            else:
                content = str(strands_result)
            
            # Extract metrics if available
            metrics = strands_result.get('metrics', {})
            usage_info = metrics.get('accumulated_usage', {})
            cycle_durations = metrics.get('cycle_durations', [])
            
            response = {
                "content": content,
                "latency_ms": int(sum(cycle_durations) * 1000) if cycle_durations else 0,
                "usage": {
                    "input_tokens": usage_info.get('inputTokens', 0),
                    "output_tokens": usage_info.get('outputTokens', 0),
                    "total_tokens": usage_info.get('totalTokens', 0)
                },
                "success": True,
                "model_family": model_family
            }
            
            # Add model family-specific metadata
            if model_family == "nova":
                response["cost_tier"] = "very_low"
                response["capabilities"] = ["text", "multimodal"]
            elif model_family == "llama":
                response["cost_tier"] = "low"
                response["capabilities"] = ["text"]
            elif model_family == "claude":
                response["cost_tier"] = "high"
                response["capabilities"] = ["text", "vision", "reasoning"]
            
            return response
        
        # Handle object with attributes
        elif hasattr(strands_result, 'message'):
            # Get the text content from the message
            message = strands_result.message
            if hasattr(message, 'content') and message.content:
                content = message.content[0].text if hasattr(message.content[0], 'text') else str(message.content[0])
            else:
                content = str(message)
            
            # Extract metrics if available
            metrics = getattr(strands_result, 'metrics', {})
            usage_info = getattr(metrics, 'accumulated_usage', {})
            cycle_durations = getattr(metrics, 'cycle_durations', [])
            
            response = {
                "content": content,
                "latency_ms": int(sum(cycle_durations) * 1000) if cycle_durations else 0,
                "usage": {
                    "input_tokens": usage_info.get('inputTokens', 0),
                    "output_tokens": usage_info.get('outputTokens', 0),
                    "total_tokens": usage_info.get('totalTokens', 0)
                },
                "success": True,
                "model_family": model_family
            }
            
            # Add model family-specific metadata
            if model_family == "nova":
                response["cost_tier"] = "very_low"
                response["capabilities"] = ["text", "multimodal"]
            elif model_family == "llama":
                response["cost_tier"] = "low"
                response["capabilities"] = ["text"]
            elif model_family == "claude":
                response["cost_tier"] = "high"
                response["capabilities"] = ["text", "vision", "reasoning"]
            
            return response
        else:
            # Fallback: try to extract text from string representation
            content = str(strands_result)
            return {
                "content": content,
                "latency_ms": 0,
                "usage": {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0},
                "success": True
            }
    except Exception as e:
        print(f"Error extracting Strands response: {e}")
        print(f"Result type: {type(strands_result)}")
        print(f"Result: {strands_result}")
        return {
            "content": str(strands_result),
            "error": f"Response extraction error: {str(e)}",
            "success": False
        }


def handle_strands_analyze_with_provider(content_id: str, request_body: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
    """Handle analysis with specific AI provider using Strands Agent."""
    
    # Check if Strands is available
    if not STRANDS_AVAILABLE:
        return {
            'statusCode': 503,
            'headers': headers,
            'body': json.dumps({
                'error': 'Strands agents not available',
                'message': 'Strands framework is not properly configured'
            })
        }
    
    try:
        # Extract provider configuration from request
        provider = request_body.get('provider', os.environ.get('PRIMARY_AI_PROVIDER', 'anthropic'))
        model = request_body.get('model', '')
        temperature = request_body.get('temperature', 0.7)
        
        # Get default model if not specified
        if not model:
            model = get_default_model(provider)
        
        # Get content from DynamoDB/S3 for real content analysis
        content_data = get_content_data(content_id)
        if not content_data:
            return {
                'statusCode': 404,
                'headers': headers,
                'body': json.dumps({
                    'error': 'Content not found',
                    'contentId': content_id
                })
            }
        
        # Create Strands agent with specified model
        agent = create_strands_agent(provider, model, temperature)
        
        # Create analysis prompt based on content
        prompt = create_analysis_prompt(content_data)
        
        # Run analysis using Strands agent
        start_time = datetime.now()
        strands_result = agent(prompt)
        end_time = datetime.now()
        
        # Extract clean response from Strands result
        model_family = detect_model_family(model)
        response_data = extract_strands_response(strands_result, model_family)
        response_data['provider'] = provider
        response_data['model'] = model
        
        # Calculate actual latency if not provided by Strands
        if response_data.get('latency_ms', 0) == 0:
            response_data['latency_ms'] = int((end_time - start_time).total_seconds() * 1000)
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'success': True,
                'contentId': content_id,
                'provider': provider,
                'model': model,
                'response': response_data,
                'timestamp': datetime.now().isoformat(),
                'test_mode': False
            })
        }
    
    except Exception as e:
        print(f"Error analyzing with Strands provider: {e}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': 'Analysis failed',
                'message': str(e),
                'contentId': content_id
            })
        }


def handle_strands_compare_providers(content_id: str, request_body: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
    """Handle comparison across multiple AI providers using Strands Agents."""
    
    # Check if Strands is available
    if not STRANDS_AVAILABLE:
        return {
            'statusCode': 503,
            'headers': headers,
            'body': json.dumps({
                'error': 'Strands agents not available',
                'message': 'Strands framework is not properly configured'
            })
        }
    
    try:
        # Extract providers to compare
        providers_config = request_body.get('providers', [
            {'provider': 'anthropic', 'model': 'claude-3-5-sonnet-20241022'},
            {'provider': 'bedrock', 'model': 'anthropic.claude-3-5-sonnet-20241022-v2:0'}
        ])
        temperature = request_body.get('temperature', 0.7)
        
        # Handle test mode for comparison
        if content_id == "test":
            # Use a test prompt instead of content data
            test_prompt = request_body.get('prompt', 'Hello! This is a test comparison. Please respond with a brief message identifying your provider.')
            prompt = test_prompt
        else:
            # Get content from DynamoDB/S3
            content_data = get_content_data(content_id)
            if not content_data:
                return {
                    'statusCode': 404,
                    'headers': headers,
                    'body': json.dumps({
                        'error': 'Content not found',
                        'contentId': content_id
                    })
                }
            # Create analysis prompt
            prompt = create_analysis_prompt(content_data)
        
        # Run comparison across providers
        comparison_results = {}
        
        for provider_config in providers_config:
            provider = provider_config['provider']
            model = provider_config['model']
            
            try:
                # Create agent for this provider
                agent = create_strands_agent(provider, model, temperature)
                
                # Run analysis
                start_time = datetime.now()
                strands_result = agent(prompt)
                end_time = datetime.now()
                
                # Extract response
                model_family = detect_model_family(model)
                response_data = extract_strands_response(strands_result, model_family)
                response_data['provider'] = provider
                response_data['model'] = model
                
                # Calculate latency if not provided
                if response_data.get('latency_ms', 0) == 0:
                    response_data['latency_ms'] = int((end_time - start_time).total_seconds() * 1000)
                
                comparison_results[provider] = response_data
                
            except Exception as e:
                print(f"Error with provider {provider}: {e}")
                comparison_results[provider] = {
                    "error": str(e),
                    "success": False,
                    "provider": provider,
                    "model": model
                }
        
        # Calculate comparison metrics
        comparison_summary = calculate_comparison_metrics(comparison_results)
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'success': True,
                'contentId': content_id,
                'comparison': {
                    'providers': list(comparison_results.keys()),
                    'results': comparison_results,
                    'summary': comparison_summary
                },
                'timestamp': datetime.now().isoformat()
            })
        }
    
    except Exception as e:
        print(f"Error comparing Strands providers: {e}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': 'Provider comparison failed',
                'message': str(e),
                'contentId': content_id
            })
        }


def handle_test_strands_integration(body: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
    """
    Test Strands integration with a simple prompt.
    This bypasses content lookup and tests the Strands agent directly.
    """
    
    if not STRANDS_AVAILABLE:
        return {
            'statusCode': 503,
            'headers': headers,
            'body': json.dumps({
                'error': 'Strands agents not available',
                'message': 'Strands framework is not properly configured'
            })
        }
    
    try:
        # Get provider configuration from request
        provider = body.get('provider', 'bedrock')
        model = body.get('model', get_default_model(provider))
        temperature = body.get('temperature', 0.7)
        test_prompt = body.get('prompt', 'Hello! This is a test of Strands integration. Please respond with a brief confirmation.')
        
        # Create Strands agent
        agent = create_strands_agent(provider, model, temperature)
        
        # Run test
        start_time = datetime.now()
        strands_result = agent(test_prompt)
        end_time = datetime.now()
        
        # Extract response
        model_family = detect_model_family(model)
        response_data = extract_strands_response(strands_result, model_family)
        response_data['provider'] = provider
        response_data['model'] = model
        
        # Calculate latency if not provided
        if response_data.get('latency_ms', 0) == 0:
            response_data['latency_ms'] = int((end_time - start_time).total_seconds() * 1000)
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'success': True,
                'test_mode': True,
                'provider': provider,
                'model': model,
                'prompt': test_prompt,
                'response': response_data,
                'timestamp': datetime.utcnow().isoformat()
            })
        }
        
    except Exception as e:
        print(f"Strands test error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': 'Test failed',
                'message': str(e),
                'test_mode': True
            })
        }


def get_content_data(content_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve content data from DynamoDB and S3."""
    try:
        # Get content metadata from DynamoDB
        dynamodb = boto3.resource('dynamodb')
        table_name = os.environ.get('CONTENT_TABLE')
        table = dynamodb.Table(table_name)
        
        response = table.get_item(Key={'contentId': content_id})
        item = response.get('Item')
        
        if not item:
            return None
        
        # Get raw content from S3
        s3 = boto3.client('s3')
        bucket_name = os.environ.get('CONTENT_BUCKET')
        s3_key = item.get('s3Key')
        
        if not s3_key:
            return None
        
        s3_response = s3.get_object(Bucket=bucket_name, Key=s3_key)
        content_data = json.loads(s3_response['Body'].read())
        
        return content_data
    
    except Exception as e:
        print(f"Error retrieving content data: {e}")
        return None


def create_analysis_prompt(content_data: Dict[str, Any]) -> str:
    """Create analysis prompt based on content data."""
    
    # Extract posts from content data
    posts = []
    if 'saved_saved_media' in content_data:
        posts = content_data['saved_saved_media'][:10]  # Sample for analysis
    elif 'content' in content_data and 'saved_posts' in content_data['content']:
        posts = content_data['content']['saved_posts'][:10]
    
    prompt = f"""Analyze these Instagram saved posts and provide insights about behavioral patterns and goals:

Content Sample ({len(posts)} posts):
{json.dumps(posts, indent=2)[:2000]}...

Please provide a structured analysis focusing on:
1. Content categories and themes
2. Behavioral patterns in saving behavior
3. Potential goal-setting opportunities
4. Recommendations for personal development

Keep the response concise and actionable."""
    
    return prompt


def get_default_model(provider: str) -> str:
    """Get default model for provider."""
    defaults = {
        "anthropic": "claude-3-5-sonnet-20241022",
        "bedrock": "anthropic.claude-3-5-sonnet-20241022-v2:0",
        "nova": "us.amazon.nova-micro-v1:0",  # Fastest, lowest cost Nova model
        "llama": "meta.llama3-1-8b-instruct-v1:0"  # Efficient Llama model
    }
    return defaults.get(provider, "")


def calculate_comparison_metrics(results: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate comparison metrics between providers."""
    if not results:
        return {}
    
    # Extract metrics
    latencies = {}
    success_rates = {}
    
    for provider, result in results.items():
        if result.get("success", False):
            latencies[provider] = result.get("latency_ms", 0)
            success_rates[provider] = 1.0
        else:
            success_rates[provider] = 0.0
    
    # Calculate summary statistics
    summary = {
        'providers_tested': len(results),
        'all_successful': all(success_rates.values()),
        'success_by_provider': success_rates
    }
    
    if latencies:
        fastest_provider = min(latencies.keys(), key=lambda p: latencies[p])
        summary['performance_comparison'] = {
            'fastest_provider': fastest_provider,
            'fastest_time_ms': latencies[fastest_provider],
            'latency_by_provider': latencies,
            'average_latency_ms': sum(latencies.values()) / len(latencies)
        }
    
    return summary