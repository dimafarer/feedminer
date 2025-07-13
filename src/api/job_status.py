"""
Job Status API Handler for FeedMiner.

Returns status of processing jobs.
"""

import json
import os
import boto3

def handler(event, context):
    """
    AWS Lambda handler for job status.
    
    Returns the status of processing jobs.
    """
    print(f"Job status request: {json.dumps(event)}")
    
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
        # Extract job ID from path parameters
        job_id = event.get('pathParameters', {}).get('jobId')
        if not job_id:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'Job ID required'})
            }
        
        # Initialize DynamoDB
        dynamodb = boto3.resource('dynamodb')
        jobs_table = os.environ.get('JOBS_TABLE')
        table = dynamodb.Table(jobs_table)
        
        # Get job status
        response = table.get_item(Key={'jobId': job_id})
        
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'headers': headers,
                'body': json.dumps({'error': 'Job not found'})
            }
        
        job_item = response['Item']
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'jobId': job_item['jobId'],
                'contentId': job_item.get('contentId'),
                'status': job_item.get('status'),
                'createdAt': job_item.get('createdAt'),
                'updatedAt': job_item.get('updatedAt'),
                'result': job_item.get('result')
            })
        }
        
    except Exception as e:
        print(f"Job status error: {e}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': 'Internal server error'})
        }