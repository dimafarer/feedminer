"""
Processing Orchestrator for FeedMiner.

Coordinates processing workflow between different agents.
"""

import json
import os
import boto3
from datetime import datetime

def handler(event, context):
    """
    AWS Lambda handler for processing orchestration.
    
    Triggered by DynamoDB streams to coordinate agent processing.
    """
    print(f"Orchestrator triggered: {json.dumps(event)}")
    
    try:
        # Process DynamoDB stream records
        for record in event.get('Records', []):
            if record['eventName'] in ['INSERT', 'MODIFY']:
                # Extract content information
                if 'dynamodb' in record and 'NewImage' in record['dynamodb']:
                    new_image = record['dynamodb']['NewImage']
                    content_id = new_image.get('contentId', {}).get('S')
                    status = new_image.get('status', {}).get('S')
                    content_type = new_image.get('type', {}).get('S')
                    
                    print(f"Processing content {content_id} with status {status}")
                    
                    # Route based on status and type
                    if status == 'uploaded' and content_type in ['instagram_saved', 'instagram_export']:
                        # Trigger Instagram analysis
                        print(f"Triggering analysis for Instagram content: {content_id}")
                        
                        # Update status to processing
                        dynamodb = boto3.resource('dynamodb')
                        table_name = os.environ.get('CONTENT_TABLE')
                        table = dynamodb.Table(table_name)
                        
                        table.update_item(
                            Key={'contentId': content_id},
                            UpdateExpression='SET #status = :status, processingStarted = :timestamp',
                            ExpressionAttributeNames={'#status': 'status'},
                            ExpressionAttributeValues={
                                ':status': 'processing',
                                ':timestamp': datetime.now().isoformat()
                            }
                        )
                        
                        # Invoke the Instagram parser Lambda function
                        lambda_client = boto3.client('lambda')
                        function_name = os.environ.get('INSTAGRAM_PARSER_FUNCTION')
                        
                        if function_name:
                            # Create payload for the Instagram parser
                            payload = {
                                'contentId': content_id,
                                'contentType': content_type,
                                's3Key': new_image.get('s3Key', {}).get('S'),
                                'metadata': new_image.get('metadata', {})
                            }
                            
                            # Invoke the function asynchronously
                            response = lambda_client.invoke(
                                FunctionName=function_name,
                                InvocationType='Event',  # Async invocation
                                Payload=json.dumps(payload)
                            )
                            print(f"Invoked Instagram parser function: {function_name}, Response: {response['StatusCode']}")
                        else:
                            print("INSTAGRAM_PARSER_FUNCTION environment variable not set")
                        
        return {'statusCode': 200}
        
    except Exception as e:
        print(f"Orchestrator error: {e}")
        return {'statusCode': 500}