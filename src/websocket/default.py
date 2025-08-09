"""
WebSocket Default Handler for FeedMiner.

Handles incoming WebSocket messages and routes them appropriately.
"""

import json
import os
import boto3

def handler(event, context):
    """
    AWS Lambda handler for WebSocket messages.
    
    Routes messages based on action type.
    """
    print(f"WebSocket message: {json.dumps(event)}")
    
    try:
        # Get connection info
        connection_id = event['requestContext']['connectionId']
        domain_name = event['requestContext']['domainName']
        stage = event['requestContext']['stage']
        
        # Parse message body
        body = json.loads(event.get('body', '{}'))
        action = body.get('action', 'unknown')
        
        # Initialize API Gateway management client
        apigateway_client = boto3.client(
            'apigatewaymanagementapi',
            endpoint_url=f"https://{domain_name}/{stage}"
        )
        
        # Route based on action
        if action == 'test':
            # Echo test message
            response_message = {
                'type': 'test_response',
                'message': f"Hello! Received: {body.get('message', 'no message')}",
                'timestamp': body.get('timestamp'),
                'connection_id': connection_id
            }
        elif action == 'analyze_content':
            # Simulate content analysis streaming
            response_message = {
                'type': 'analysis_start',
                'message': 'Starting content analysis...',
                'content_id': body.get('content_id')
            }
        elif action == 'stream_reasoning':
            # Handle streaming reasoning step
            response_message = {
                'type': 'reasoning_acknowledged',
                'message': 'Reasoning stream registered',
                'content_id': body.get('content_id'),
                'connection_id': connection_id
            }
        else:
            # Unknown action
            response_message = {
                'type': 'error',
                'message': f"Unknown action: {action}"
            }
        
        # Send response back to client
        apigateway_client.post_to_connection(
            ConnectionId=connection_id,
            Data=json.dumps(response_message)
        )
        
        return {'statusCode': 200}
        
    except Exception as e:
        print(f"Default handler error: {e}")
        return {'statusCode': 500}