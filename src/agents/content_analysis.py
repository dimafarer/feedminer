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
            
            # Skip individual data type files - only process main consolidated files
            if '/' in key and key.count('/') > 1:
                # This is a nested file like uploads/content-id/saved_posts.json
                filename = key.split('/')[-1]
                if filename in ['saved_posts.json', 'liked_posts.json', 'comments.json', 'user_posts.json', 'following.json']:
                    print(f"Skipping individual data type file: {filename}")
                    continue
            
            # Download and analyze content
            response = s3.get_object(Bucket=bucket, Key=key)
            content_data = json.loads(response['Body'].read())
            
            # Extract content ID from S3 key
            if '/' in key and key.count('/') > 1:
                # For nested files like uploads/content-id/consolidated.json
                content_id = key.split('/')[-2]
            else:
                # For direct files like uploads/content-id.json
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
                # Single Instagram data type - use existing parser
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
                asyncio.run(agent.save_analysis_result(content_id, analysis))
                
                print(f"Instagram content analyzed for {content_id} successfully")
            
            elif content_type == 'instagram_export':
                # Multi-data-type Instagram export - handle consolidated structure
                print(f"Processing multi-data-type Instagram export for {content_id}")
                
                # Check if this is the consolidated file or individual data type
                if 'exportInfo' in content_data and 'dataTypes' in content_data['exportInfo']:
                    # This is a consolidated multi-data-type export
                    export_info = content_data['exportInfo']
                    data_types = export_info['dataTypes']
                    
                    print(f"Found consolidated export with data types: {data_types}")
                    
                    # Process each data type and create a combined analysis
                    from instagram_parser import InstagramParserAgent
                    import asyncio
                    
                    agent = InstagramParserAgent()
                    
                    # Combine all data types into a single structure for analysis
                    combined_content = {'combined_data': {}}
                    total_items = 0
                    
                    for data_type in data_types:
                        if data_type in content_data:
                            combined_content['combined_data'][data_type] = content_data[data_type]
                            
                            # Count items for logging
                            if data_type == 'saved_posts' and 'saved_saved_media' in content_data[data_type]:
                                total_items += len(content_data[data_type]['saved_saved_media'])
                            elif data_type == 'liked_posts' and 'likes_media_likes' in content_data[data_type]:
                                total_items += len(content_data[data_type]['likes_media_likes'])
                            # Add other data type counting as needed
                    
                    print(f"Processing {total_items} total items across {len(data_types)} data types")
                    
                    # Analyze the combined dataset
                    analysis = asyncio.run(agent.parse_multi_type_instagram_export(combined_content, export_info))
                    asyncio.run(agent.save_analysis_result(content_id, analysis))
                    
                    print(f"Multi-type Instagram export analyzed for {content_id}")
                else:
                    # Individual data type from a ZIP export
                    from instagram_parser import InstagramParserAgent
                    import asyncio
                    
                    agent = InstagramParserAgent()
                    analysis = asyncio.run(agent.parse_instagram_export(content_data))
                    asyncio.run(agent.save_analysis_result(content_id, analysis))
                    
                    print(f"Individual Instagram data type analyzed for {content_id}")
            
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
        print(f"🚨🚨🚨 CRITICAL CONTENT ANALYSIS ERROR: {e}")
        print(f"🚨 ERROR TYPE: {type(e).__name__}")
        print(f"🚨 ERROR DETAILS: {str(e)}")
        
        # Re-raise the error to make it visible and stop processing
        raise Exception(f"🚨 DEVELOPMENT MODE - CONTENT ANALYSIS FAILED: {str(e)}") from e
    
    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Content analysis completed'})
    }