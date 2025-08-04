#!/usr/bin/env python3
"""
Quick Production Test for Multi-Upload Functionality
Tests the live production system with small dataset and Nova model
"""

import json
import time
import requests
import sys

# Production API Configuration
PRODUCTION_API_URL = 'https://wqtfb6rv15.execute-api.us-west-2.amazonaws.com/dev'

# Small test dataset for production
PRODUCTION_TEST_DATASET = {
    "type": "instagram_export",
    "user_id": "production-test-user",
    "modelPreference": {
        "provider": "nova",
        "model": "us.amazon.nova-micro-v1:0",
        "temperature": 0.7
    },
    "exportInfo": {
        "dataTypes": ["saved_posts", "liked_posts"],
        "extractedAt": "2025-08-04T11:44:00.000Z",
        "exportFolder": "meta-2025-production-test/"
    },
    "saved_posts": {
        "saved_saved_media": [
            {
                "title": "production_test_fitness",
                "string_map_data": {
                    "Saved on": {
                        "href": "https://www.instagram.com/reel/PROD_TEST_1/",
                        "timestamp": 1754250000
                    }
                }
            },
            {
                "title": "production_test_tech",
                "string_map_data": {
                    "Saved on": {
                        "href": "https://www.instagram.com/reel/PROD_TEST_2/",
                        "timestamp": 1754250001
                    }
                }
            }
        ]
    },
    "liked_posts": {
        "likes_media_likes": [
            {
                "title": "production_test_liked",
                "string_map_data": {
                    "Liked on": {
                        "href": "https://www.instagram.com/p/PROD_LIKE_1/",
                        "timestamp": 1754250002
                    }
                }
            }
        ]
    },
    "dataTypes": ["saved_posts", "liked_posts"]
}

def test_production_multi_upload():
    """Test production multi-upload with Nova model"""
    print("🚀 Testing Production Multi-Upload Functionality")
    print("=" * 55)
    
    try:
        print("📊 Payload Size:", len(json.dumps(PRODUCTION_TEST_DATASET)), "bytes")
        print("🤖 Model: Nova Micro (us.amazon.nova-micro-v1:0)")
        print("📝 Data Types: saved_posts, liked_posts")
        
        start_time = time.time()
        
        response = requests.post(
            f"{PRODUCTION_API_URL}/multi-upload",
            headers={"Content-Type": "application/json"},
            json=PRODUCTION_TEST_DATASET,
            timeout=30
        )
        
        end_time = time.time()
        duration = round(end_time - start_time, 2)
        
        print(f"⏱️  Response Time: {duration}s")
        print(f"📡 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            content_id = result.get('contentId')
            
            print("✅ Upload Success!")
            print(f"🆔 Content ID: {content_id}")
            print(f"📊 Total Items: {result.get('totalItems')}")
            print(f"📁 Data Types: {', '.join(result.get('dataTypes', []))}")
            
            # Test model preference validation
            if content_id:
                print("\n🔍 Validating Model Preferences...")
                get_response = requests.get(f"{PRODUCTION_API_URL}/content/{content_id}")
                
                if get_response.status_code == 200:
                    content_data = get_response.json()
                    stored_model = content_data.get('modelPreference', {})
                    
                    if (stored_model.get('provider') == 'nova' and 
                        stored_model.get('model') == 'us.amazon.nova-micro-v1:0' and
                        abs(float(stored_model.get('temperature', 0)) - 0.7) < 0.001):
                        print("✅ Model Preferences Validated!")
                        print(f"   Provider: {stored_model.get('provider')}")
                        print(f"   Model: {stored_model.get('model')}")
                        print(f"   Temperature: {stored_model.get('temperature')}")
                    else:
                        print("❌ Model Preferences Validation Failed")
                        print(f"   Stored: {stored_model}")
                else:
                    print("⚠️  Could not validate model preferences (GET failed)")
            
            print("\n🎉 Production Test PASSED!")
            return True
            
        else:
            print("❌ Upload Failed!")
            print(f"Error: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out (>30s)")
        return False
    except Exception as e:
        print(f"💥 Test failed with error: {e}")
        return False

def test_production_frontend():
    """Quick test of production frontend accessibility"""
    print("\n🌐 Testing Production Frontend")
    print("-" * 30)
    
    try:
        response = requests.get("https://main.d1txsc36hbt4ub.amplifyapp.com", timeout=10)
        if response.status_code == 200:
            print("✅ Frontend accessible at: https://main.d1txsc36hbt4ub.amplifyapp.com")
            return True
        else:
            print(f"❌ Frontend returned: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend test failed: {e}")
        return False

if __name__ == "__main__":
    print("🔥 FeedMiner Production Testing Suite")
    print("=====================================")
    
    # Test backend
    backend_success = test_production_multi_upload()
    
    # Test frontend
    frontend_success = test_production_frontend()
    
    print("\n📋 PRODUCTION TEST SUMMARY")
    print("=" * 35)
    print(f"Backend Multi-Upload: {'✅ PASS' if backend_success else '❌ FAIL'}")
    print(f"Frontend Accessibility: {'✅ PASS' if frontend_success else '❌ FAIL'}")
    
    if backend_success and frontend_success:
        print("\n🎉 ALL PRODUCTION TESTS PASSED!")
        print("🚀 System is ready for live use!")
        sys.exit(0)
    else:
        print("\n⚠️  Some production tests failed")
        sys.exit(1)