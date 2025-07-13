"""
Content Get API Handler for FeedMiner.

Retrieves specific content items and their analysis results.
"""

import json
import os
import boto3
from decimal import Decimal

class DecimalEncoder(json.JSONEncoder):
    """JSON encoder that handles Decimal objects from DynamoDB."""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

def handler(event, context):
    """
    AWS Lambda handler for getting specific content.
    
    Retrieves content metadata and analysis results.
    """
    print(f"Get request: {json.dumps(event)}")
    
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
        # Extract content ID from path parameters
        content_id = event.get('pathParameters', {}).get('contentId')
        if not content_id:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'Content ID required'})
            }
        
        # Initialize AWS clients
        dynamodb = boto3.resource('dynamodb')
        s3 = boto3.client('s3')
        
        content_table = os.environ.get('CONTENT_TABLE')
        content_bucket = os.environ.get('CONTENT_BUCKET')
        
        # Get content metadata from DynamoDB
        table = dynamodb.Table(content_table)
        response = table.get_item(Key={'contentId': content_id})
        
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'headers': headers,
                'body': json.dumps({'error': 'Content not found'})
            }
        
        content_item = response['Item']
        
        # Get raw content from S3 if requested
        query_params = event.get('queryStringParameters') or {}
        include_raw = query_params.get('includeRaw', 'false').lower() == 'true'
        
        result = {
            'contentId': content_item['contentId'],
            'type': content_item.get('type'),
            'status': content_item.get('status'),
            'createdAt': content_item.get('createdAt'),
            'userId': content_item.get('userId'),
            'metadata': content_item.get('metadata', {}),
            'analysis': content_item.get('analysis')
        }
        
        if include_raw and 's3Key' in content_item:
            try:
                s3_response = s3.get_object(
                    Bucket=content_bucket,
                    Key=content_item['s3Key']
                )
                raw_content = json.loads(s3_response['Body'].read())
                result['rawContent'] = raw_content
            except Exception as e:
                print(f"Error fetching raw content: {e}")
                result['rawContentError'] = str(e)
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps(result, cls=DecimalEncoder)
        }
        
    except Exception as e:
        print(f"Get error: {e}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': 'Internal server error'})
        }