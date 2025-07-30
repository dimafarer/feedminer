"""
Multi-File Instagram Data Upload API Handler for FeedMiner.

Handles ZIP file uploads with complex Instagram export structures,
extracting and processing multiple data types.
"""

import json
import os
import boto3
import uuid
import zipfile
import io
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

def handler(event, context):
    """
    AWS Lambda handler for multi-file Instagram data upload.
    
    Processes ZIP files containing Instagram exports with multiple data types.
    Supports both single data type extraction and consolidated multi-type uploads.
    """
    print(f"Multi-upload request: {json.dumps(event)}")
    
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
        
        # Extract parameters
        upload_type = body.get('type', 'instagram_export')
        user_id = body.get('user_id', 'anonymous')
        selected_data_types = body.get('dataTypes', ['saved_posts'])
        
        # Check if this is a ZIP file upload (consolidated data)
        if upload_type == 'instagram_export' and 'exportInfo' in body:
            # This is a consolidated multi-type upload from frontend
            content_id = str(uuid.uuid4())
            
            # Process consolidated data
            result = process_consolidated_instagram_data(
                body, content_id, user_id, selected_data_types
            )
            
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps(result)
            }
        
        # Check if this is a single data type from ZIP
        elif upload_type.startswith('instagram_') and upload_type != 'instagram_saved':
            # Single data type extracted from ZIP
            data_type = upload_type.replace('instagram_', '')
            content_id = str(uuid.uuid4())
            
            result = process_single_instagram_data_type(
                body, content_id, user_id, data_type
            )
            
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps(result)
            }
        
        else:
            # Fall back to regular upload for backward compatibility
            return fallback_to_regular_upload(body, user_id)
            
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'headers': headers,
            'body': json.dumps({'error': 'Invalid JSON in request body'})
        }
    except Exception as e:
        print(f"Multi-upload error: {e}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': 'Internal server error'})
        }


def process_consolidated_instagram_data(body: Dict, content_id: str, user_id: str, data_types: List[str]) -> Dict:
    """
    Process consolidated Instagram data with multiple data types.
    
    Args:
        body: Request body containing consolidated Instagram data
        content_id: Unique identifier for this content
        user_id: User identifier
        data_types: List of data types included
        
    Returns:
        Response dictionary with upload status and metadata
    """
    print(f"Processing consolidated Instagram data for {len(data_types)} data types")
    
    # Initialize AWS clients
    s3 = boto3.client('s3')
    dynamodb = boto3.resource('dynamodb')
    
    # Environment variables
    content_bucket = os.environ.get('CONTENT_BUCKET')
    content_table = os.environ.get('CONTENT_TABLE')
    
    # Extract export info
    export_info = body.get('exportInfo', {})
    export_folder = export_info.get('exportFolder', 'unknown')
    extracted_at = export_info.get('extractedAt')
    
    # Process each data type and store individually
    data_structure = {}
    total_items = 0
    
    for data_type in data_types:
        if data_type in body:
            data = body[data_type]
            item_count = count_items_in_data_type(data_type, data)
            total_items += item_count
            
            # Store individual data type in S3
            s3_key = f"uploads/{content_id}/{data_type}.json"
            s3.put_object(
                Bucket=content_bucket,
                Key=s3_key,
                Body=json.dumps(data),
                ContentType='application/json',
                Metadata={
                    'dataType': data_type,
                    'itemCount': str(item_count),
                    'contentId': content_id,
                    'userId': user_id
                }
            )
            
            data_structure[data_type] = {
                'count': item_count,
                's3Key': s3_key,
                'extractedAt': extracted_at
            }
            
            print(f"Stored {data_type}: {item_count} items")
    
    # Store consolidated metadata in S3 with proper type for analysis
    consolidated_s3_key = f"uploads/{content_id}/consolidated.json"
    
    # Add type field to the consolidated data for ContentAnalysisAgent
    consolidated_data = {
        **body,
        'type': 'instagram_export'  # This tells ContentAnalysisAgent how to process it
    }
    
    s3.put_object(
        Bucket=content_bucket,
        Key=consolidated_s3_key,
        Body=json.dumps(consolidated_data),
        ContentType='application/json',
        Metadata={
            'type': 'consolidated',
            'dataTypes': ','.join(data_types),
            'totalItems': str(total_items),
            'contentId': content_id,
            'userId': user_id
        }
    )
    
    # Create enhanced DynamoDB record
    table = dynamodb.Table(content_table)
    table.put_item(
        Item={
            'contentId': content_id,
            'userId': user_id,
            'type': 'instagram_export',
            'status': 'uploaded',
            'createdAt': datetime.now().isoformat(),
            's3Key': consolidated_s3_key,
            'dataStructure': data_structure,
            'metadata': {
                'exportFolder': export_folder,
                'totalFiles': len(data_types),
                'totalDataPoints': total_items,
                'analyzableTypes': data_types,
                'extractedAt': extracted_at
            }
        }
    )
    
    print(f"Consolidated Instagram export uploaded: {content_id} with {total_items} total items")
    
    return {
        'contentId': content_id,
        'message': f'Instagram export uploaded successfully with {len(data_types)} data types',
        's3Key': consolidated_s3_key,
        'status': 'uploaded',
        'type': 'instagram_export',
        'dataTypes': data_types,
        'totalItems': total_items,
        'dataStructure': data_structure
    }


def process_single_instagram_data_type(body: Dict, content_id: str, user_id: str, data_type: str) -> Dict:
    """
    Process a single Instagram data type extracted from ZIP.
    
    Args:
        body: Request body containing single data type
        content_id: Unique identifier for this content
        user_id: User identifier  
        data_type: Type of Instagram data (saved_posts, liked_posts, etc.)
        
    Returns:
        Response dictionary with upload status and metadata
    """
    print(f"Processing single Instagram data type: {data_type}")
    
    # Initialize AWS clients
    s3 = boto3.client('s3')
    dynamodb = boto3.resource('dynamodb')
    
    # Environment variables
    content_bucket = os.environ.get('CONTENT_BUCKET')
    content_table = os.environ.get('CONTENT_TABLE')
    
    # Count items in the data
    item_count = count_items_in_data_type(data_type, body)
    
    # Store in S3
    s3_key = f"uploads/{content_id}.json"
    s3.put_object(
        Bucket=content_bucket,
        Key=s3_key,
        Body=json.dumps(body),
        ContentType='application/json',
        Metadata={
            'dataType': data_type,
            'itemCount': str(item_count),
            'contentId': content_id,
            'userId': user_id
        }
    )
    
    # Create DynamoDB record
    table = dynamodb.Table(content_table)
    table.put_item(
        Item={
            'contentId': content_id,
            'userId': user_id,
            'type': f'instagram_{data_type}',
            'status': 'uploaded',
            'createdAt': datetime.now().isoformat(),
            's3Key': s3_key,
            'metadata': {
                'dataType': data_type,
                'itemCount': item_count,
                'extractedFromZip': True
            }
        }
    )
    
    print(f"Single {data_type} uploaded: {content_id} with {item_count} items")
    
    return {
        'contentId': content_id,
        'message': f'Instagram {data_type} uploaded successfully',
        's3Key': s3_key,
        'status': 'uploaded',
        'type': f'instagram_{data_type}',
        'itemCount': item_count
    }


def count_items_in_data_type(data_type: str, data: Dict) -> int:
    """
    Count items in different Instagram data types.
    
    Args:
        data_type: Type of Instagram data
        data: The data dictionary
        
    Returns:
        Number of items in the data
    """
    try:
        if data_type == 'saved_posts' and 'saved_saved_media' in data:
            return len(data['saved_saved_media'])
        elif data_type == 'liked_posts' and 'likes_media_likes' in data:
            return len(data['likes_media_likes'])
        elif data_type == 'comments' and 'comments_media_comments' in data:
            return len(data['comments_media_comments'])
        elif data_type == 'user_posts' and isinstance(data, list):
            return len(data)
        elif data_type == 'following' and 'relationships_following' in data:
            return len(data['relationships_following'])
        else:
            # Try to count any list-like structure
            for key, value in data.items():
                if isinstance(value, list):
                    return len(value)
            return 1
    except Exception as e:
        print(f"Error counting items for {data_type}: {e}")
        return 0


def fallback_to_regular_upload(body: Dict, user_id: str) -> Dict:
    """
    Fallback to regular upload for backward compatibility.
    
    Args:
        body: Request body
        user_id: User identifier
        
    Returns:
        Response from regular upload process
    """
    print("Falling back to regular upload process")
    
    # Import the regular upload handler
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from api.upload import handler as upload_handler
    
    # Create event structure for regular upload
    regular_event = {
        'httpMethod': 'POST',
        'body': json.dumps(body)
    }
    
    # Call regular upload handler
    return upload_handler(regular_event, {})


# Additional utility functions for data processing

def detect_instagram_export_structure(zip_content: bytes) -> Tuple[bool, Optional[str], List[str]]:
    """
    Analyze ZIP content to detect Instagram export structure.
    
    Args:
        zip_content: Raw ZIP file content
        
    Returns:
        Tuple of (is_instagram_export, export_folder, available_data_types)
    """
    try:
        with zipfile.ZipFile(io.BytesIO(zip_content)) as zip_file:
            files = zip_file.namelist()
            
            # Look for Instagram export folder pattern (can be nested under meta-* folder)
            # Pattern matches: meta-*/instagram-username-YYYY-MM-DD-hash/ or instagram-username-YYYY-MM-DD-hash/
            instagram_folder_pattern = re.compile(r'(?:meta-[^/]+/)?instagram-[^/]+-\d{4}-\d{2}-\d{2}-[^/]+/')
            export_folder = None
            
            for file_path in files:
                match = instagram_folder_pattern.match(file_path)
                if match:
                    export_folder = match.group(0)
                    break
            
            if not export_folder:
                return False, None, []
            
            # Check for available data types
            available_data_types = []
            data_type_paths = {
                'saved_posts': f'{export_folder}your_instagram_activity/saved/saved_posts.json',
                'liked_posts': f'{export_folder}your_instagram_activity/likes/liked_posts.json',
                'comments': f'{export_folder}your_instagram_activity/comments/post_comments_1.json',
                'user_posts': f'{export_folder}your_instagram_activity/media/posts_1.json',
                'following': f'{export_folder}connections/followers_and_following/following.json'
            }
            
            for data_type, path in data_type_paths.items():
                if path in files:
                    available_data_types.append(data_type)
            
            return True, export_folder, available_data_types
            
    except Exception as e:
        print(f"Error analyzing ZIP structure: {e}")
        return False, None, []


def extract_instagram_data_from_zip(zip_content: bytes, data_types: List[str], export_folder: str) -> Dict[str, Any]:
    """
    Extract specific Instagram data types from ZIP file.
    
    Args:
        zip_content: Raw ZIP file content
        data_types: List of data types to extract
        export_folder: Instagram export folder path
        
    Returns:
        Dictionary with extracted data for each type
    """
    extracted_data = {}
    
    try:
        with zipfile.ZipFile(io.BytesIO(zip_content)) as zip_file:
            data_type_paths = {
                'saved_posts': f'{export_folder}your_instagram_activity/saved/saved_posts.json',
                'liked_posts': f'{export_folder}your_instagram_activity/likes/liked_posts.json',
                'comments': f'{export_folder}your_instagram_activity/comments/post_comments_1.json',
                'user_posts': f'{export_folder}your_instagram_activity/media/posts_1.json',
                'following': f'{export_folder}connections/followers_and_following/following.json'
            }
            
            for data_type in data_types:
                if data_type in data_type_paths:
                    file_path = data_type_paths[data_type]
                    if file_path in zip_file.namelist():
                        try:
                            file_content = zip_file.read(file_path).decode('utf-8')
                            extracted_data[data_type] = json.loads(file_content)
                            print(f"Extracted {data_type} from ZIP")
                        except Exception as e:
                            print(f"Error extracting {data_type}: {e}")
                            
    except Exception as e:
        print(f"Error extracting from ZIP: {e}")
    
    return extracted_data