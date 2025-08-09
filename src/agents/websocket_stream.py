"""
WebSocket Streaming Utilities for FeedMiner.

Provides utilities for streaming AI reasoning steps in real-time via WebSocket.
"""

import json
import os
import boto3
from datetime import datetime
from typing import Optional, Dict, Any


class WebSocketStreamer:
    """Utility class for streaming reasoning steps via WebSocket."""
    
    def __init__(self):
        """Initialize the WebSocket streamer."""
        self.apigateway_client = None
        self.domain_name = None
        self.stage = None
        self.connection_id = None
        
    def setup_connection(self, domain_name: str, stage: str, connection_id: str):
        """Set up WebSocket connection parameters."""
        self.domain_name = domain_name
        self.stage = stage
        self.connection_id = connection_id
        
        # Initialize API Gateway management client
        self.apigateway_client = boto3.client(
            'apigatewaymanagementapi',
            endpoint_url=f"https://{domain_name}/{stage}"
        )
        
    def stream_reasoning_step(
        self, 
        content_id: str, 
        step: str, 
        reasoning: str, 
        progress: float,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Stream a reasoning step to connected clients.
        
        Args:
            content_id: ID of the content being analyzed
            step: Current step identifier (e.g., 'analyzing_content_patterns')
            reasoning: The model's current reasoning/thinking process
            progress: Progress percentage (0.0 to 1.0)
            metadata: Optional additional metadata
        """
        if not self.apigateway_client or not self.connection_id:
            print("WebSocket streamer not properly initialized, skipping reasoning step")
            return
            
        try:
            message = {
                'type': 'reasoning_step',
                'content_id': content_id,
                'step': step,
                'reasoning': reasoning,
                'progress': progress,
                'timestamp': datetime.now().isoformat(),
                'metadata': metadata or {}
            }
            
            self.apigateway_client.post_to_connection(
                ConnectionId=self.connection_id,
                Data=json.dumps(message)
            )
            
            print(f"Streamed reasoning step '{step}': {reasoning[:100]}...")
            
        except Exception as e:
            print(f"Failed to stream reasoning step: {e}")
            # Don't raise - we don't want to break analysis if WebSocket fails
            
    def stream_analysis_complete(self, content_id: str, summary: str):
        """Stream analysis completion message."""
        if not self.apigateway_client or not self.connection_id:
            return
            
        try:
            message = {
                'type': 'analysis_complete',
                'content_id': content_id,
                'message': summary,
                'timestamp': datetime.now().isoformat()
            }
            
            self.apigateway_client.post_to_connection(
                ConnectionId=self.connection_id,
                Data=json.dumps(message)
            )
            
        except Exception as e:
            print(f"Failed to stream completion message: {e}")
            
    def stream_error(self, content_id: str, error_message: str):
        """Stream error message."""
        if not self.apigateway_client or not self.connection_id:
            return
            
        try:
            message = {
                'type': 'analysis_error',
                'content_id': content_id,
                'error': error_message,
                'timestamp': datetime.now().isoformat()
            }
            
            self.apigateway_client.post_to_connection(
                ConnectionId=self.connection_id,
                Data=json.dumps(message)
            )
            
        except Exception as e:
            print(f"Failed to stream error message: {e}")


def get_active_connections_for_content(content_id: str) -> list:
    """
    Get active WebSocket connections that should receive updates for this content.
    
    This is a simplified implementation. In production, you might want to:
    - Store content_id -> connection_id mappings in DynamoDB
    - Filter connections by user permissions
    - Handle connection cleanup automatically
    """
    try:
        # For now, get all active connections
        # TODO: Implement content-specific connection filtering
        dynamodb = boto3.resource('dynamodb')
        table_name = os.environ.get('CONNECTIONS_TABLE')
        
        if not table_name:
            print("CONNECTIONS_TABLE not configured")
            return []
            
        table = dynamodb.Table(table_name)
        response = table.scan()
        
        connections = []
        for item in response.get('Items', []):
            connections.append({
                'connectionId': item['connectionId'],
                'userId': item.get('userId', 'unknown')
            })
            
        return connections
        
    except Exception as e:
        print(f"Failed to get active connections: {e}")
        return []


def broadcast_reasoning_step(
    content_id: str, 
    step: str, 
    reasoning: str, 
    progress: float,
    websocket_endpoint: Optional[str] = None
):
    """
    Broadcast a reasoning step to all relevant WebSocket connections.
    
    This is a utility function that can be called from anywhere in the analysis process.
    """
    try:
        # Check if WebSocket streaming is configured
        websocket_api_endpoint = os.environ.get('WEBSOCKET_API_ENDPOINT')
        if not websocket_api_endpoint or websocket_api_endpoint == 'DISABLED':
            print(f"WebSocket API endpoint not configured ({websocket_api_endpoint}) - skipping reasoning step streaming")
            return
            
        print(f"WebSocket streaming enabled for {content_id}: {websocket_api_endpoint}")
        connections = get_active_connections_for_content(content_id)
        
        if not connections:
            print("No active WebSocket connections found")
            return
            
        print(f"Broadcasting reasoning step '{step}' to {len(connections)} connections")
            
        # Parse WebSocket endpoint if provided
        if websocket_endpoint:
            # Extract domain and stage from endpoint URL
            # Format: wss://domain/stage
            parts = websocket_endpoint.replace('wss://', '').split('/')
            domain_name = parts[0]
            stage = parts[1] if len(parts) > 1 else 'dev'
        else:
            # Parse from configured endpoint
            # Format: domain/stage or wss://domain/stage
            endpoint_clean = websocket_api_endpoint.replace('wss://', '').replace('https://', '')
            parts = endpoint_clean.split('/')
            domain_name = parts[0]
            stage = parts[1] if len(parts) > 1 else 'dev'
            
        if not domain_name:
            print("WebSocket domain not configured")
            return
            
        streamer = WebSocketStreamer()
        
        for conn in connections:
            try:
                streamer.setup_connection(domain_name, stage, conn['connectionId'])
                streamer.stream_reasoning_step(content_id, step, reasoning, progress)
            except Exception as e:
                print(f"Failed to stream to connection {conn['connectionId']}: {e}")
                # Continue with other connections
                continue
                
    except Exception as e:
        print(f"Failed to broadcast reasoning step: {e}")
        # Don't raise - we don't want to break analysis if WebSocket fails