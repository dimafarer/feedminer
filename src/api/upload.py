"""
Content Upload API Handler for FeedMiner.

Handles content upload requests and stores them in S3 and DynamoDB.
"""

import json
import os
import boto3
import uuid
from datetime import datetime

def handler(event, context):
    """
    AWS Lambda handler for content upload.
    
    Accepts content uploads, stores them in S3, and creates DynamoDB records.
    """
    print(f"Upload request: {json.dumps(event)}")
    
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
        # Parse request body
        if 'body' not in event:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'No body provided'})
            }
        
        body = json.loads(event['body'])
        
        # Generate unique content ID
        content_id = str(uuid.uuid4())
        
        # Initialize AWS clients
        s3 = boto3.client('s3')
        dynamodb = boto3.resource('dynamodb')
        
        # Environment variables
        content_bucket = os.environ.get('CONTENT_BUCKET')
        content_table = os.environ.get('CONTENT_TABLE')
        
        # Store content in S3
        s3_key = f"uploads/{content_id}.json"
        s3.put_object(
            Bucket=content_bucket,
            Key=s3_key,
            Body=json.dumps(body),
            ContentType='application/json'
        )
        
        # Create DynamoDB record
        table = dynamodb.Table(content_table)
        item = {
            'contentId': content_id,
            'userId': body.get('user_id', 'anonymous'),
            'type': body.get('type', 'unknown'),
            'status': 'uploaded',
            'createdAt': datetime.now().isoformat(),
            's3Key': s3_key,
            'metadata': body.get('metadata', {})
        }
        
        # Add model preference if provided
        if 'modelPreference' in body:
            item['modelPreference'] = body['modelPreference']
            print(f"Model preference stored: {body['modelPreference']}")
        
        table.put_item(Item=item)
        
        print(f"Content uploaded successfully: {content_id}")
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'contentId': content_id,
                'message': 'Content uploaded successfully',
                's3Key': s3_key
            })
        }
        
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'headers': headers,
            'body': json.dumps({'error': 'Invalid JSON in request body'})
        }
    except Exception as e:
        print(f"Upload error: {e}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': 'Internal server error'})
        }