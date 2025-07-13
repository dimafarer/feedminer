"""
Content List API Handler for FeedMiner.

Returns a list of uploaded content items.
"""

import json
import os
import boto3
from boto3.dynamodb.conditions import Key
from decimal import Decimal

class DecimalEncoder(json.JSONEncoder):
    """JSON encoder that handles Decimal objects from DynamoDB."""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

def handler(event, context):
    """
    AWS Lambda handler for listing content.
    
    Returns a paginated list of content items.
    """
    print(f"List request: {json.dumps(event)}")
    
    # CORS headers
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, OPTIONS',
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
        # Initialize DynamoDB
        dynamodb = boto3.resource('dynamodb')
        content_table = os.environ.get('CONTENT_TABLE')
        table = dynamodb.Table(content_table)
        
        # Get query parameters
        query_params = event.get('queryStringParameters') or {}
        user_id = query_params.get('userId', 'anonymous')
        limit = int(query_params.get('limit', 20))
        
        # Query content items
        if user_id != 'all':
            response = table.query(
                IndexName='UserTimeIndex',
                KeyConditionExpression=Key('userId').eq(user_id),
                ScanIndexForward=False,  # Sort by newest first
                Limit=limit
            )
        else:
            # Scan all items (for admin/testing)
            response = table.scan(Limit=limit)
        
        # Format response
        items = []
        for item in response.get('Items', []):
            items.append({
                'contentId': item['contentId'],
                'type': item.get('type', 'unknown'),
                'status': item.get('status', 'unknown'),
                'createdAt': item.get('createdAt'),
                'userId': item.get('userId'),
                'metadata': item.get('metadata', {})
            })
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'items': items,
                'count': len(items),
                'hasMore': 'LastEvaluatedKey' in response
            }, cls=DecimalEncoder)
        }
        
    except Exception as e:
        print(f"List error: {e}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': 'Internal server error'})
        }