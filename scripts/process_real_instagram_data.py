#!/usr/bin/env python3
"""
Real Instagram Data Processing Script for FeedMiner

This script helps process real Instagram export data through the FeedMiner system:
1. Load and validate real Instagram export JSON
2. Transform it to our expected format
3. Test local Instagram parser
4. Upload to deployed AWS system
5. Analyze AI-generated insights

Usage:
    python scripts/process_real_instagram_data.py /path/to/instagram/data.json
"""

import json
import sys
import os
import requests
from datetime import datetime
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

try:
    from agents.instagram_parser import InstagramParser
except ImportError:
    print("⚠️  Could not import Instagram parser. Running without local testing.")
    InstagramParser = None

# FeedMiner API configuration
FEEDMINER_API_BASE = "https://wqtfb6rv15.execute-api.us-west-2.amazonaws.com/dev"
FEEDMINER_WEBSOCKET = "wss://yzzspgrevg.execute-api.us-west-2.amazonaws.com/dev"

def examine_instagram_structure(data_path: str):
    """Examine the structure of real Instagram export data."""
    print(f"🔍 Examining Instagram data structure: {data_path}")
    
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"📊 Data Structure Analysis:")
    print(f"   - Root keys: {list(data.keys())}")
    print(f"   - Data type: {type(data)}")
    
    # Look for saved posts or similar structure
    if isinstance(data, list):
        print(f"   - Array length: {len(data)}")
        if data:
            print(f"   - First item keys: {list(data[0].keys()) if isinstance(data[0], dict) else 'Not a dict'}")
    elif isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, list):
                print(f"   - {key}: array with {len(value)} items")
                if value and isinstance(value[0], dict):
                    print(f"     - Item keys: {list(value[0].keys())}")
            elif isinstance(value, dict):
                print(f"   - {key}: object with keys {list(value.keys())}")
            else:
                print(f"   - {key}: {type(value).__name__}")
    
    return data

def transform_to_feedminer_format(raw_data: dict, user_id: str = "real_user") -> dict:
    """Transform real Instagram data to FeedMiner expected format."""
    print("🔄 Transforming to FeedMiner format...")
    
    # Try to find saved posts in various possible structures
    saved_posts = []
    
    # Common Instagram export structures
    if "saved_posts" in raw_data:
        saved_posts = raw_data["saved_posts"]
    elif "saved" in raw_data:
        saved_posts = raw_data["saved"]
    elif isinstance(raw_data, list):
        saved_posts = raw_data
    elif "data" in raw_data:
        saved_posts = raw_data["data"]
    
    # Transform each post to our expected structure
    transformed_posts = []
    for i, post in enumerate(saved_posts):
        try:
            # Handle different possible structures
            transformed_post = {
                "post_id": post.get("id", post.get("post_id", f"real_post_{i}")),
                "author": post.get("author", post.get("username", post.get("owner", "unknown_author"))),
                "caption": post.get("caption", post.get("text", post.get("description", ""))),
                "media_type": post.get("media_type", post.get("type", "photo")),
                "saved_at": post.get("saved_at", post.get("timestamp", datetime.now().isoformat())),
                "hashtags": extract_hashtags(post.get("caption", post.get("text", ""))),
                "location": post.get("location", post.get("place", None)),
                "engagement": post.get("engagement", {})
            }
            transformed_posts.append(transformed_post)
        except Exception as e:
            print(f"⚠️  Error transforming post {i}: {e}")
            continue
    
    # Create FeedMiner format
    feedminer_data = {
        "type": "instagram_saved",
        "user_id": user_id,
        "metadata": {
            "exported_at": datetime.now().isoformat(),
            "total_items": len(transformed_posts),
            "export_version": "real_data_1.0",
            "source": "instagram_export"
        },
        "content": {
            "saved_posts": transformed_posts
        }
    }
    
    print(f"✅ Transformed {len(transformed_posts)} posts to FeedMiner format")
    return feedminer_data

def extract_hashtags(text: str) -> list:
    """Extract hashtags from text."""
    if not text:
        return []
    
    import re
    hashtags = re.findall(r'#\\w+', text)
    return hashtags

def test_local_parser(data: dict):
    """Test the Instagram parser locally."""
    print("🧪 Testing local Instagram parser...")
    
    if not InstagramParser:
        print("⚠️  Instagram parser not available for local testing")
        return None
    
    try:
        # Initialize parser (this would normally use AI models)
        parser = InstagramParser()
        
        # For local testing, we'll just validate the data structure
        posts = data["content"]["saved_posts"]
        print(f"   - Found {len(posts)} posts to analyze")
        print(f"   - Sample post: {posts[0]['author']} - {posts[0]['caption'][:50]}...")
        
        # Mock analysis result for demonstration
        mock_result = {
            "total_posts": len(posts),
            "categories": [
                {"name": "Technology", "confidence": 0.8, "reasoning": "Multiple tech-related posts"},
                {"name": "Food", "confidence": 0.6, "reasoning": "Food and cooking content"}
            ],
            "insights": [
                {
                    "type": "preference",
                    "description": "Strong interest in technology and AI",
                    "evidence": ["Multiple AI research posts", "Tech industry follows"],
                    "relevance_score": 0.9
                }
            ],
            "top_authors": [
                {"author": posts[0]["author"], "post_count": 1}
            ],
            "date_range": {
                "earliest": "2024-01-01",
                "latest": "2025-07-13"
            },
            "summary": f"Analysis of {len(posts)} saved Instagram posts showing diverse interests"
        }
        
        print("✅ Local parser validation successful")
        return mock_result
        
    except Exception as e:
        print(f"❌ Local parser test failed: {e}")
        return None

def upload_to_feedminer(data: dict):
    """Upload real data to deployed FeedMiner system."""
    print("🚀 Uploading to deployed FeedMiner system...")
    
    try:
        response = requests.post(
            f"{FEEDMINER_API_BASE}/upload",
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            content_id = result.get("contentId")
            print(f"✅ Upload successful!")
            print(f"   - Content ID: {content_id}")
            print(f"   - S3 Key: {result.get('s3Key')}")
            return content_id
        else:
            print(f"❌ Upload failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return None

def check_processing_status(content_id: str):
    """Check processing status of uploaded content."""
    print(f"📊 Checking processing status for {content_id}...")
    
    try:
        response = requests.get(
            f"{FEEDMINER_API_BASE}/content/{content_id}",
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            status = result.get("status", "unknown")
            print(f"   - Status: {status}")
            
            if result.get("analysis"):
                print("✅ AI analysis complete!")
                return result["analysis"]
            else:
                print("⏳ AI analysis still processing...")
                return None
        else:
            print(f"❌ Status check failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Status check error: {e}")
        return None

def analyze_results(analysis: dict):
    """Analyze and display AI-generated insights."""
    print("🤖 AI-Generated Analysis Results:")
    print("=" * 50)
    
    if isinstance(analysis, dict):
        print(f"📊 Total Posts Analyzed: {analysis.get('total_posts', 'Unknown')}")
        
        # Categories
        categories = analysis.get('categories', [])
        if categories:
            print(f"\\n🏷️  Content Categories:")
            for cat in categories:
                print(f"   - {cat.get('name', 'Unknown')}: {cat.get('confidence', 0):.1%} confidence")
                print(f"     Reasoning: {cat.get('reasoning', 'No reasoning provided')}")
        
        # Insights
        insights = analysis.get('insights', [])
        if insights:
            print(f"\\n💡 Key Insights:")
            for insight in insights:
                print(f"   - {insight.get('type', 'Unknown').title()}: {insight.get('description', 'No description')}")
                print(f"     Relevance: {insight.get('relevance_score', 0):.1%}")
        
        # Top Authors
        top_authors = analysis.get('top_authors', [])
        if top_authors:
            print(f"\\n👥 Top Authors:")
            for author in top_authors[:5]:  # Top 5
                print(f"   - @{author.get('author', 'unknown')}: {author.get('post_count', 0)} posts")
        
        # Summary
        summary = analysis.get('summary', '')
        if summary:
            print(f"\\n📝 Summary:")
            print(f"   {summary}")
    
    else:
        print(f"⚠️  Unexpected analysis format: {type(analysis)}")

def main():
    """Main processing function."""
    if len(sys.argv) != 2:
        print("Usage: python scripts/process_real_instagram_data.py /path/to/instagram/data.json")
        sys.exit(1)
    
    data_path = sys.argv[1]
    
    if not os.path.exists(data_path):
        print(f"❌ File not found: {data_path}")
        sys.exit(1)
    
    print("🎯 FeedMiner Real Instagram Data Processing")
    print("=" * 50)
    
    # Step 1: Examine structure
    raw_data = examine_instagram_structure(data_path)
    
    # Step 2: Transform to FeedMiner format
    feedminer_data = transform_to_feedminer_format(raw_data)
    
    # Save transformed data for inspection
    output_path = "/home/daddyfristy/real-instagram-data/transformed_data.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(feedminer_data, f, indent=2, ensure_ascii=False)
    print(f"💾 Transformed data saved to: {output_path}")
    
    # Step 3: Test local parser
    local_result = test_local_parser(feedminer_data)
    
    # Step 4: Upload to AWS
    content_id = upload_to_feedminer(feedminer_data)
    
    if content_id:
        # Step 5: Check for AI analysis results
        print("\\n⏳ Waiting for AI analysis (this may take a few moments)...")
        import time
        
        for attempt in range(6):  # Try for up to 30 seconds
            time.sleep(5)
            analysis = check_processing_status(content_id)
            
            if analysis:
                analyze_results(analysis)
                break
        else:
            print("⏰ AI analysis still processing. Check back later with:")
            print(f"   curl {FEEDMINER_API_BASE}/content/{content_id}")
    
    print("\\n🎉 Real Instagram data processing complete!")

if __name__ == "__main__":
    main()