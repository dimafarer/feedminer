"""
Content Analysis Agent for FeedMiner.

Main orchestration agent that determines content type and routes to specialized agents.
"""

import json
import os
import boto3
from datetime import datetime
from typing import Dict, Any

def handler(event, context):
    """
    AWS Lambda handler for content analysis orchestration.
    
    This function is triggered when content is uploaded to S3.
    It analyzes the content type and routes to appropriate specialized agents.
    """
    print(f"Content analysis triggered with event: {json.dumps(event)}")
    
    # Initialize AWS clients
    s3 = boto3.client('s3')
    dynamodb = boto3.resource('dynamodb')
    lambda_client = boto3.client('lambda')
    
    # Environment variables
    content_table = os.environ.get('CONTENT_TABLE')
    jobs_table = os.environ.get('JOBS_TABLE')
    
    try:
        # Process S3 event
        for record in event.get('Records', []):
            bucket = record['s3']['bucket']['name']
            key = record['s3']['object']['key']
            
            print(f"Processing S3 object: s3://{bucket}/{key}")
            
            # Download and analyze content
            response = s3.get_object(Bucket=bucket, Key=key)
            content_data = json.loads(response['Body'].read())
            
            # Extract content ID from S3 key
            content_id = key.split('/')[-1].replace('.json', '')
            
            # Determine content type and route to appropriate agent
            content_type = content_data.get('type', 'unknown')
            
            # Update content status
            table = dynamodb.Table(content_table)
            table.update_item(
                Key={'contentId': content_id},
                UpdateExpression='SET #status = :status, processingStarted = :timestamp',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={
                    ':status': 'processing',
                    ':timestamp': datetime.now().isoformat()
                }
            )
            
            # Route to specialized agent based on content type
            if content_type == 'instagram_saved':
                # Invoke Instagram parser agent
                payload = {
                    'content_id': content_id,
                    'bucket': bucket,
                    'key': key,
                    'content_data': content_data
                }
                
                # For now, process inline (in production, you'd invoke another Lambda)
                from instagram_parser import InstagramParserAgent
                import asyncio
                
                agent = InstagramParserAgent()
                analysis = asyncio.run(agent.parse_instagram_export(content_data))
                await agent.save_analysis_result(content_id, analysis)
                
                print(f"Instagram content analyzed for {content_id}")
            
            else:
                print(f"Unknown content type: {content_type}")
                # Update status as unknown
                table.update_item(
                    Key={'contentId': content_id},
                    UpdateExpression='SET #status = :status',
                    ExpressionAttributeNames={'#status': 'status'},
                    ExpressionAttributeValues={':status': 'unknown_type'}
                )
    
    except Exception as e:
        print(f"Error in content analysis: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
    
    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Content analysis completed'})
    }