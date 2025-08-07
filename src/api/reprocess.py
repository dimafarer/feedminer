"""
Content Reprocessing API Handler for FeedMiner.

Handles reprocessing of existing content with different AI models,
enabling multi-model analysis comparison.
"""

import json
import os
import boto3
import uuid
import time
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, Any, Optional

def convert_floats_to_decimal(obj):
    """Recursively convert float values to Decimal for DynamoDB compatibility."""
    if isinstance(obj, dict):
        return {k: convert_floats_to_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_floats_to_decimal(item) for item in obj]
    elif isinstance(obj, float):
        return Decimal(str(obj))
    else:
        return obj

def generate_analysis_id(model_provider: str, model_name: str) -> str:
    """Generate unique analysis ID."""
    timestamp = int(time.time())
    return f"{model_provider}#{model_name}#{timestamp}"

def estimate_processing_cost(model_provider: str, model_name: str, data_size: int) -> Dict[str, Any]:
    """Estimate processing cost and time for different models."""
    
    # Cost estimates per 1K tokens (approximate)
    cost_estimates = {
        'anthropic': {
            'claude-3-5-sonnet-20241022': {'cost_per_1k': 0.003, 'time_seconds': 3.0}
        },
        'bedrock': {
            'anthropic.claude-3-5-sonnet-20241022-v2:0': {'cost_per_1k': 0.003, 'time_seconds': 2.0}
        },
        'nova': {
            'us.amazon.nova-micro-v1:0': {'cost_per_1k': 0.0001, 'time_seconds': 1.0},
            'us.amazon.nova-lite-v1:0': {'cost_per_1k': 0.0002, 'time_seconds': 1.5}
        },
        'llama': {
            'meta.llama3-1-8b-instruct-v1:0': {'cost_per_1k': 0.0003, 'time_seconds': 1.2},
            'meta.llama3-1-70b-instruct-v1:0': {'cost_per_1k': 0.001, 'time_seconds': 2.5}
        }
    }
    
    # Estimate tokens from data size (rough approximation)
    estimated_tokens = data_size / 4  # ~4 chars per token
    estimated_1k_tokens = estimated_tokens / 1000
    
    model_info = cost_estimates.get(model_provider, {}).get(model_name, {
        'cost_per_1k': 0.002,  # Default estimate
        'time_seconds': 2.0
    })
    
    estimated_cost = estimated_1k_tokens * model_info['cost_per_1k']
    estimated_time = model_info['time_seconds'] * max(1, estimated_1k_tokens / 10)
    
    return {
        'estimated_cost_usd': round(estimated_cost, 4),
        'estimated_time_seconds': round(estimated_time, 1),
        'estimated_tokens': int(estimated_tokens),
        'confidence': 'medium'  # Cost estimates are approximate
    }

def send_websocket_message(connections_table, websocket_client, user_id: str, message: Dict[str, Any]):
    """Send progress update via WebSocket."""
    try:
        # Get user connections
        response = connections_table.query(
            IndexName='UserIndex',
            KeyConditionExpression='userId = :user_id',
            ExpressionAttributeValues={':user_id': user_id}
        )
        
        for connection in response.get('Items', []):
            connection_id = connection['connectionId']
            try:
                websocket_client.post_to_connection(
                    ConnectionId=connection_id,
                    Data=json.dumps(message)
                )
            except Exception as e:
                print(f"Failed to send to connection {connection_id}: {e}")
                # Connection might be stale, could clean up here
                
    except Exception as e:
        print(f"WebSocket broadcast error: {e}")

def handler(event, context):
    """
    AWS Lambda handler for content reprocessing.
    
    POST /content/{contentId}/reprocess
    Body: {
        "modelProvider": "anthropic|bedrock|nova|llama", 
        "modelName": "model-name",
        "temperature": 0.7,
        "force": false  // Skip cache check
    }
    """
    print(f"Reprocess request: {json.dumps(event)}")
    
    # CORS headers
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization'
    }
    
    # Handle preflight OPTIONS request
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': ''
        }
    
    try:
        # Extract content ID from path
        content_id = event.get('pathParameters', {}).get('contentId')
        if not content_id:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'Content ID required'})
            }
        
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        model_provider = body.get('modelProvider')
        model_name = body.get('modelName')
        temperature = body.get('temperature', 0.7)
        force_reprocess = body.get('force', False)
        
        if not model_provider or not model_name:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'Model provider and name required'})
            }
        
        # Initialize AWS clients
        dynamodb = boto3.resource('dynamodb')
        s3 = boto3.client('s3')
        websocket_client = boto3.client('apigatewaymanagementapi', 
                                      endpoint_url=os.environ.get('WEBSOCKET_API_ENDPOINT'))
        
        content_table = dynamodb.Table(os.environ.get('CONTENT_TABLE'))
        analysis_table = dynamodb.Table(os.environ.get('ANALYSIS_TABLE'))
        jobs_table = dynamodb.Table(os.environ.get('JOBS_TABLE'))
        connections_table = dynamodb.Table(os.environ.get('CONNECTIONS_TABLE'))
        
        # Get original content
        content_response = content_table.get_item(Key={'contentId': content_id})
        if 'Item' not in content_response:
            return {
                'statusCode': 404,
                'headers': headers,
                'body': json.dumps({'error': 'Content not found'})
            }
        
        content_item = content_response['Item']
        user_id = content_item.get('userId', 'anonymous')
        
        # Generate analysis ID
        analysis_id = generate_analysis_id(model_provider, model_name)
        
        # Check if analysis already exists (unless force=true)
        if not force_reprocess:
            try:
                existing_analysis = analysis_table.get_item(
                    Key={'contentId': content_id, 'analysisId': analysis_id}
                )
                if 'Item' in existing_analysis:
                    return {
                        'statusCode': 200,
                        'headers': headers,
                        'body': json.dumps({
                            'message': 'Analysis already exists',
                            'analysisId': analysis_id,
                            'cached': True,
                            'analysis': existing_analysis['Item'].get('analysis')
                        })
                    }
            except Exception as e:
                print(f"Cache check error: {e}")
        
        # Get raw content from S3 for reprocessing
        s3_key = content_item.get('s3Key')
        content_bucket = os.environ.get('CONTENT_BUCKET')
        
        if not s3_key:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'No raw content available for reprocessing'})
            }
        
        try:
            s3_response = s3.get_object(Bucket=content_bucket, Key=s3_key)
            raw_content = json.loads(s3_response['Body'].read())
        except Exception as e:
            return {
                'statusCode': 500,
                'headers': headers,
                'body': json.dumps({'error': f'Failed to retrieve raw content: {str(e)}'})
            }
        
        # Estimate processing cost and time
        data_size = len(json.dumps(raw_content))
        estimates = estimate_processing_cost(model_provider, model_name, data_size)
        
        # Create processing job
        job_id = str(uuid.uuid4())
        job_item = {
            'jobId': job_id,
            'contentId': content_id,
            'userId': user_id,
            'type': 'reprocess_analysis',
            'status': 'started',
            'modelProvider': model_provider,
            'modelName': model_name,
            'temperature': Decimal(str(temperature)),
            'analysisId': analysis_id,
            'estimates': convert_floats_to_decimal(estimates),
            'createdAt': datetime.now().isoformat(),
            'progress': 0
        }
        
        jobs_table.put_item(Item=job_item)
        
        # Send initial WebSocket notification
        send_websocket_message(connections_table, websocket_client, user_id, {
            'type': 'analysis_started',
            'contentId': content_id,
            'jobId': job_id,
            'analysisId': analysis_id,
            'data': {
                'modelProvider': model_provider,
                'modelName': model_name,
                'estimates': estimates,
                'progress': 0
            }
        })
        
        # TODO: For Phase 1, we'll do synchronous processing
        # In Phase 2, move this to async Lambda or SQS
        
        # Placeholder for actual reprocessing
        # This will be implemented with the actual AI model calls
        mock_analysis = {
            'summary': f'Mock analysis using {model_provider} {model_name}',
            'processed_at': datetime.now().isoformat(),
            'model_info': {
                'provider': model_provider,
                'model': model_name,
                'temperature': Decimal(str(temperature))
            }
        }
        
        # Store analysis result with TTL (7 days)
        ttl = int((datetime.now() + timedelta(days=7)).timestamp())
        analysis_item = {
            'contentId': content_id,
            'analysisId': analysis_id,
            'modelProvider': model_provider,
            'modelName': model_name,
            'analysis': mock_analysis,
            'metadata': convert_floats_to_decimal({
                'processingTime': estimates['estimated_time_seconds'],
                'estimatedCost': estimates['estimated_cost_usd'],
                'createdAt': datetime.now().isoformat(),
                'temperature': temperature
            }),
            'ttl': ttl,
            'createdAt': datetime.now().isoformat()
        }
        
        analysis_table.put_item(Item=analysis_item)
        
        # Update job status
        jobs_table.update_item(
            Key={'jobId': job_id},
            UpdateExpression='SET #status = :status, progress = :progress, completedAt = :completed',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={
                ':status': 'completed',
                ':progress': 100,
                ':completed': datetime.now().isoformat()
            }
        )
        
        # Send completion WebSocket notification
        send_websocket_message(connections_table, websocket_client, user_id, {
            'type': 'analysis_complete',
            'contentId': content_id,
            'jobId': job_id,
            'analysisId': analysis_id,
            'data': {
                'progress': 100,
                'result': mock_analysis
            }
        })
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'message': 'Reprocessing completed',
                'jobId': job_id,
                'analysisId': analysis_id,
                'estimates': estimates,
                'analysis': mock_analysis
            })
        }
        
    except Exception as e:
        print(f"Reprocess error: {e}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': 'Internal server error'})
        }