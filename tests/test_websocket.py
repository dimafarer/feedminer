#!/usr/bin/env python3
"""
Test script for FeedMiner WebSocket API.
Tests real-time streaming functionality.

Run from project root:
    python tests/test_websocket.py
"""

import asyncio
import json
import websockets
import sys
from datetime import datetime

WEBSOCKET_URL = "wss://yzzspgrevg.execute-api.us-west-2.amazonaws.com/dev"

async def test_websocket_connection():
    """Test basic WebSocket connection."""
    print("🔄 Testing WebSocket connection...")
    
    try:
        async with websockets.connect(WEBSOCKET_URL) as websocket:
            print("✅ WebSocket connected successfully!")
            
            # Send a test message
            test_message = {
                "action": "test",
                "message": "Hello from test client!",
                "timestamp": datetime.now().isoformat()
            }
            
            await websocket.send(json.dumps(test_message))
            print(f"📤 Sent: {test_message}")
            
            # Wait for response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                print(f"📥 Received: {response}")
            except asyncio.TimeoutError:
                print("⏰ No response received within 10 seconds")
            
    except Exception as e:
        print(f"❌ WebSocket connection failed: {e}")

async def test_streaming_analysis():
    """Test streaming content analysis."""
    print("🔄 Testing streaming content analysis...")
    
    try:
        async with websockets.connect(WEBSOCKET_URL) as websocket:
            # Send content for analysis
            analysis_request = {
                "action": "analyze_content",
                "content_id": "test_content_123",
                "data": {
                    "type": "instagram_saved",
                    "posts": [
                        {
                            "caption": "Amazing sunset over the mountains! Nature never fails to inspire me. #nature #photography #mountains",
                            "hashtags": ["#nature", "#photography", "#mountains"],
                            "author": "nature_photographer"
                        }
                    ]
                },
                "user_id": "test_user",
                "timestamp": datetime.now().isoformat()
            }
            
            await websocket.send(json.dumps(analysis_request))
            print(f"📤 Sent analysis request")
            
            # Listen for streaming responses
            response_count = 0
            while response_count < 5:  # Listen for up to 5 messages
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                    response_data = json.loads(response)
                    
                    print(f"📥 Stream #{response_count + 1}: {response_data.get('type', 'unknown')} - {response_data.get('message', '')[:100]}...")
                    
                    response_count += 1
                    
                    # Break if we get a completion message
                    if response_data.get('type') == 'completion':
                        break
                        
                except asyncio.TimeoutError:
                    print("⏰ No more responses received")
                    break
                except json.JSONDecodeError:
                    print(f"📥 Raw response: {response}")
                    response_count += 1
                    
    except Exception as e:
        print(f"❌ Streaming analysis failed: {e}")

async def main():
    """Run all WebSocket tests."""
    print("🚀 Starting FeedMiner WebSocket Tests")
    print(f"📍 WebSocket URL: {WEBSOCKET_URL}")
    print("=" * 50)
    
    # Test basic connection
    await test_websocket_connection()
    print()
    
    # Wait a moment
    await asyncio.sleep(2)
    
    # Test streaming analysis
    await test_streaming_analysis()
    
    print("=" * 50)
    print("✅ WebSocket tests completed!")

if __name__ == "__main__":
    asyncio.run(main())