"""
WebSocket Connect Handler for FeedMiner.

Handles WebSocket connection establishment.
"""

import json
import os
import boto3
from datetime import datetime, timedelta

def handler(event, context):
    """
    AWS Lambda handler for WebSocket connections.
    
    Stores connection information in DynamoDB.
    """
    print(f"WebSocket connect: {json.dumps(event)}")
    
    try:
        # Get connection ID and user info
        connection_id = event['requestContext']['connectionId']
        domain_name = event['requestContext']['domainName']
        stage = event['requestContext']['stage']
        
        # Initialize DynamoDB
        dynamodb = boto3.resource('dynamodb')
        connections_table = os.environ.get('CONNECTIONS_TABLE')
        table = dynamodb.Table(connections_table)
        
        # Store connection
        ttl = int((datetime.now() + timedelta(hours=2)).timestamp())
        table.put_item(
            Item={
                'connectionId': connection_id,
                'userId': 'anonymous',  # Could extract from auth
                'connectedAt': datetime.now().isoformat(),
                'ttl': ttl,
                'endpoint': f"https://{domain_name}/{stage}"
            }
        )
        
        print(f"Connection stored: {connection_id}")
        
        return {'statusCode': 200}
        
    except Exception as e:
        print(f"Connect error: {e}")
        return {'statusCode': 500}