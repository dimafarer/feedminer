#!/usr/bin/env python3
"""
Test script for FeedMiner REST API endpoints.
Tests upload, list, get content, and job status functionality.

Run from project root:
    python tests/test_api.py
"""

import json
import requests
import time
import sys
from datetime import datetime

# Your deployed endpoints
REST_API_BASE = "https://wqtfb6rv15.execute-api.us-west-2.amazonaws.com/dev"
WEBSOCKET_API = "wss://yzzspgrevg.execute-api.us-west-2.amazonaws.com/dev"

def test_upload_content():
    """Test content upload endpoint."""
    print("🔄 Testing content upload...")
    
    # Sample Instagram saved content
    instagram_data = {
        "type": "instagram_saved",
        "user_id": "test_user_123",
        "metadata": {
            "exported_at": datetime.now().isoformat(),
            "total_items": 3
        },
        "content": {
            "saved_posts": [
                {
                    "post_id": "C8vXyZwA1bN",
                    "author": "coffee_roaster_daily",
                    "caption": "Perfect morning brew ☕ Ethiopian single origin with notes of chocolate and citrus. What's your favorite brewing method?",
                    "media_type": "photo",
                    "saved_at": "2024-12-15T09:30:00Z",
                    "hashtags": ["#coffee", "#ethiopian", "#singleorigin", "#brewing"],
                    "location": "Portland, Oregon"
                },
                {
                    "post_id": "C8wABcDE2fG", 
                    "author": "ai_research_hub",
                    "caption": "New paper on transformer architectures and their applications in multimodal learning. Link in bio for full research.",
                    "media_type": "carousel",
                    "saved_at": "2024-12-14T14:15:00Z",
                    "hashtags": ["#AI", "#MachineLearning", "#Research", "#Transformers"],
                    "engagement": {"likes": 2847, "comments": 156}
                },
                {
                    "post_id": "C8xYzAB3gH",
                    "author": "sustainable_living_tips",
                    "caption": "5 ways to reduce plastic waste in your daily routine. Small changes, big impact! 🌱",
                    "media_type": "reel",
                    "saved_at": "2024-12-13T16:45:00Z",
                    "hashtags": ["#sustainability", "#zerowaste", "#ecofriendly", "#environment"],
                    "duration": 45
                }
            ]
        }
    }
    
    response = requests.post(
        f"{REST_API_BASE}/upload",
        json=instagram_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Upload successful! Content ID: {result.get('contentId')}")
        return result.get('contentId')
    else:
        print(f"❌ Upload failed: {response.status_code} - {response.text}")
        return None

def test_list_content():
    """Test content listing endpoint."""
    print("🔄 Testing content listing...")
    
    response = requests.get(f"{REST_API_BASE}/content")
    
    if response.status_code == 200:
        content_list = response.json()
        print(f"✅ Listed {len(content_list.get('items', []))} content items")
        return content_list
    else:
        print(f"❌ List failed: {response.status_code} - {response.text}")
        return None

def test_get_content(content_id):
    """Test get specific content endpoint."""
    if not content_id:
        print("⏭️ Skipping get content test (no content ID)")
        return None
        
    print(f"🔄 Testing get content for ID: {content_id}")
    
    response = requests.get(f"{REST_API_BASE}/content/{content_id}")
    
    if response.status_code == 200:
        content = response.json()
        print(f"✅ Retrieved content: {content.get('type', 'unknown type')}")
        return content
    else:
        print(f"❌ Get content failed: {response.status_code} - {response.text}")
        return None

def test_job_status(job_id):
    """Test job status endpoint."""
    if not job_id:
        print("⏭️ Skipping job status test (no job ID)")
        return None
        
    print(f"🔄 Testing job status for ID: {job_id}")
    
    response = requests.get(f"{REST_API_BASE}/jobs/{job_id}")
    
    if response.status_code == 200:
        job = response.json()
        print(f"✅ Job status: {job.get('status', 'unknown')}")
        return job
    else:
        print(f"❌ Job status failed: {response.status_code} - {response.text}")
        return None

def main():
    """Run all API tests."""
    print("🚀 Starting FeedMiner API Tests")
    print(f"📍 REST API Base: {REST_API_BASE}")
    print("=" * 50)
    
    # Test upload
    content_id = test_upload_content()
    print()
    
    # Wait a moment for processing
    time.sleep(2)
    
    # Test list
    content_list = test_list_content()
    print()
    
    # Test get specific content
    test_get_content(content_id)
    print()
    
    # Test job status (if we have job IDs from the list)
    if content_list and content_list.get('items'):
        for item in content_list['items'][:1]:  # Test first job
            if 'jobId' in item:
                test_job_status(item['jobId'])
                break
    
    print("=" * 50)
    print("✅ API tests completed!")

if __name__ == "__main__":
    main()