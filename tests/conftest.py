"""
Pytest configuration and fixtures for FeedMiner tests.
"""

import pytest
import os


@pytest.fixture
def api_base_url():
    """Base URL for REST API tests."""
    return os.getenv(
        'FEEDMINER_API_URL', 
        'https://wqtfb6rv15.execute-api.us-west-2.amazonaws.com/dev'
    )


@pytest.fixture
def websocket_url():
    """WebSocket URL for real-time tests."""
    return os.getenv(
        'FEEDMINER_WEBSOCKET_URL',
        'wss://yzzspgrevg.execute-api.us-west-2.amazonaws.com/dev'
    )


@pytest.fixture
def sample_instagram_data():
    """Sample Instagram data for testing."""
    return {
        "type": "instagram_saved",
        "user_id": "test_user_pytest",
        "metadata": {
            "exported_at": "2025-07-13T12:00:00Z",
            "total_items": 2
        },
        "content": {
            "saved_posts": [
                {
                    "post_id": "C8vXyZwA1bN",
                    "author": "test_account",
                    "caption": "Test post for automated testing #test #automation",
                    "media_type": "photo",
                    "saved_at": "2024-12-15T09:30:00Z",
                    "hashtags": ["#test", "#automation"],
                    "location": "Test Location"
                },
                {
                    "post_id": "C8wABcDE2fG",
                    "author": "another_test_account",
                    "caption": "Another test post for validation #testing",
                    "media_type": "video",
                    "saved_at": "2024-12-14T14:15:00Z",
                    "hashtags": ["#testing"]
                }
            ]
        }
    }