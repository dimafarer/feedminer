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
                    if status == 'uploaded' and content_type == 'instagram_saved':
                        # Trigger content analysis
                        print(f"Triggering analysis for Instagram content: {content_id}")
                        # In a real implementation, you'd invoke the content analysis Lambda
                        
        return {'statusCode': 200}
        
    except Exception as e:
        print(f"Orchestrator error: {e}")
        return {'statusCode': 500}