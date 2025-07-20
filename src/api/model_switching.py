"""
Model Switching and Comparison API for FeedMiner v0.2.0.

This API endpoint enables runtime switching between AI providers and 
model comparison for content analysis.

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

# Add layers to path for AI providers
sys.path.append('/opt/python')

try:
    from ai.providers import AIProviderManager, ModelConfiguration
    # For now, we'll implement a simpler version without the enhanced parser
    # since the agents module isn't accessible from the api function
    AIProviderManager_available = True
except ImportError as e:
    print(f"AI providers import error: {e}")
    # Fallback for local development
    AIProviderManager = None
    ModelConfiguration = None
    AIProviderManager_available = False


def handler(event, context):
    """
    Lambda handler for model switching and comparison API.
    
    Supports:
    - POST /analyze/{contentId} - Run analysis with specific provider
    - POST /compare/{contentId} - Compare multiple providers
    """
    
    print(f"Model switching API received event: {json.dumps(event)}")
    
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
                    return handle_test_bedrock_integration(body, headers)
                return handle_analyze_with_provider(content_id, body, headers)
            elif '/compare/' in resource_path:
                return handle_compare_providers(content_id, body, headers)
        
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
        print(f"Error in model switching API: {e}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }


def handle_analyze_with_provider(content_id: str, request_body: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
    """Handle analysis with specific AI provider."""
    
    # Check if AI providers are available
    if not AIProviderManager_available:
        return {
            'statusCode': 503,
            'headers': headers,
            'body': json.dumps({
                'error': 'AI providers not available',
                'message': 'Multi-model AI support is not properly configured'
            })
        }
    
    try:
        # Extract provider configuration from request
        provider = request_body.get('provider', os.environ.get('PRIMARY_AI_PROVIDER', 'anthropic'))
        model = request_body.get('model', '')
        temperature = request_body.get('temperature', 0.7)
        max_tokens = request_body.get('max_tokens', 4000)
        
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
        
        # Create provider configuration
        provider_config = ModelConfiguration(
            provider=provider,
            model=model if model else get_default_model(provider),
            temperature=temperature,
            max_tokens=max_tokens,
            additional_params=request_body.get('additional_params', {})
        )
        
        # Initialize enhanced parser
        parser = EnhancedInstagramParserAgent(
            preferred_provider=provider,
            preferred_model=model
        )
        
        # Run analysis
        import asyncio
        analysis_result = asyncio.run(
            parser.parse_instagram_export(content_data, provider_config)
        )
        
        # Save result
        asyncio.run(parser.save_analysis_result(content_id, analysis_result))
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'contentId': content_id,
                'provider': analysis_result.ai_provider,
                'model': analysis_result.ai_model,
                'processing_time_ms': analysis_result.processing_time_ms,
                'analysis': analysis_result.model_dump(),
                'requested_provider': provider,
                'requested_model': model
            })
        }
    
    except Exception as e:
        print(f"Error analyzing with provider: {e}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': 'Analysis failed',
                'message': str(e),
                'contentId': content_id
            })
        }


def handle_compare_providers(content_id: str, request_body: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
    """Handle comparison across multiple AI providers."""
    
    # Check if AI providers are available
    if not AIProviderManager_available:
        return {
            'statusCode': 503,
            'headers': headers,
            'body': json.dumps({
                'error': 'AI providers not available',
                'message': 'Multi-model AI support is not properly configured'
            })
        }
    
    try:
        # Extract providers to compare
        providers = request_body.get('providers', ['anthropic', 'bedrock'])
        temperature = request_body.get('temperature', 0.7)
        max_tokens = request_body.get('max_tokens', 4000)
        
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
        
        # Initialize enhanced parser
        parser = EnhancedInstagramParserAgent()
        
        # Run comparison
        import asyncio
        comparison_results = asyncio.run(
            parser.compare_providers(content_data, providers)
        )
        
        # Calculate comparison metrics
        comparison_summary = calculate_comparison_metrics(comparison_results)
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'contentId': content_id,
                'comparison_summary': comparison_summary,
                'detailed_results': {
                    provider: result.model_dump() 
                    for provider, result in comparison_results.items()
                },
                'providers_compared': list(comparison_results.keys()),
                'comparison_timestamp': datetime.now().isoformat()
            })
        }
    
    except Exception as e:
        print(f"Error comparing providers: {e}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': 'Provider comparison failed',
                'message': str(e),
                'contentId': content_id
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


def get_default_model(provider: str) -> str:
    """Get default model for provider."""
    defaults = {
        "anthropic": "claude-3-5-sonnet-20241022",
        "bedrock": "anthropic.claude-3-5-sonnet-20241022-v2:0"
    }
    return defaults.get(provider, "")


def calculate_comparison_metrics(results: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate comparison metrics between providers."""
    if not results:
        return {}
    
    # Extract metrics
    latencies = {}
    success_rates = {}
    confidence_scores = {}
    
    for provider, result in results.items():
        if hasattr(result, 'processing_time_ms'):
            latencies[provider] = result.processing_time_ms
        if hasattr(result, 'confidence_score'):
            confidence_scores[provider] = result.confidence_score
        success_rates[provider] = 1.0  # All results here are successful
    
    # Calculate summary statistics
    summary = {
        'providers_tested': len(results),
        'all_successful': all(success_rates.values()),
        'performance_comparison': {}
    }
    
    if latencies:
        fastest_provider = min(latencies.keys(), key=lambda p: latencies[p])
        summary['performance_comparison'] = {
            'fastest_provider': fastest_provider,
            'fastest_time_ms': latencies[fastest_provider],
            'latency_by_provider': latencies,
            'average_latency_ms': sum(latencies.values()) / len(latencies)
        }
    
    if confidence_scores:
        highest_confidence_provider = max(confidence_scores.keys(), key=lambda p: confidence_scores[p])
        summary['quality_comparison'] = {
            'highest_confidence_provider': highest_confidence_provider,
            'highest_confidence_score': confidence_scores[highest_confidence_provider],
            'confidence_by_provider': confidence_scores,
            'average_confidence': sum(confidence_scores.values()) / len(confidence_scores)
        }
    
    return summary


def handle_test_bedrock_integration(body: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
    """
    Test Bedrock integration with a simple prompt.
    This bypasses content lookup and tests the AI provider directly.
    """
    
    if not AIProviderManager_available:
        return {
            'statusCode': 503,
            'headers': headers,
            'body': json.dumps({
                'error': 'AI providers not available',
                'message': 'Multi-model AI support is not properly configured'
            })
        }
    
    try:
        # Get provider configuration from request
        provider = body.get('provider', 'bedrock')
        model = body.get('model', 'anthropic.claude-3-5-sonnet-20241022-v2:0')
        test_prompt = body.get('prompt', 'Hello! This is a test of Bedrock integration. Please respond with "Bedrock integration successful!"')
        
        # Create provider manager
        provider_manager = AIProviderManager()
        
        # Create model configuration
        config = ModelConfiguration(
            provider=provider,
            model=model,
            temperature=0.7
        )
        
        # Test the provider (using async event loop)
        import asyncio
        
        async def test_generate():
            return await provider_manager.generate(test_prompt, config)
        
        # Run the async operation
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(test_generate())
        finally:
            loop.close()
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'success': True,
                'test_mode': True,
                'provider': provider,
                'model': model,
                'prompt': test_prompt,
                'response': result,
                'timestamp': datetime.utcnow().isoformat()
            })
        }
        
    except Exception as e:
        print(f"Bedrock test error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': 'Test failed',
                'message': str(e),
                'test_mode': True
            })
        }