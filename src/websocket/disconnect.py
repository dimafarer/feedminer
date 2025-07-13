"""
WebSocket Disconnect Handler for FeedMiner.

Handles WebSocket disconnection cleanup.
"""

import json
import os
import boto3

def handler(event, context):
    """
    AWS Lambda handler for WebSocket disconnections.
    
    Removes connection information from DynamoDB.
    """
    print(f"WebSocket disconnect: {json.dumps(event)}")
    
    try:
        # Get connection ID
        connection_id = event['requestContext']['connectionId']
        
        # Initialize DynamoDB
        dynamodb = boto3.resource('dynamodb')
        connections_table = os.environ.get('CONNECTIONS_TABLE')
        table = dynamodb.Table(connections_table)
        
        # Remove connection
        table.delete_item(Key={'connectionId': connection_id})
        
        print(f"Connection removed: {connection_id}")
        
        return {'statusCode': 200}
        
    except Exception as e:
        print(f"Disconnect error: {e}")
        return {'statusCode': 500}