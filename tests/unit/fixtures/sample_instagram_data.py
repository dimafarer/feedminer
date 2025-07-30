"""
Sample Instagram data fixtures for testing.
Contains realistic data structures for different test scenarios.
"""

from datetime import datetime, timezone
import json


def get_sample_saved_posts(count=5):
    """Generate sample saved posts data."""
    posts = []
    for i in range(count):
        posts.append({
            "title": f"test_user_{i}",
            "string_map_data": {
                "Saved on": {
                    "href": f"https://www.instagram.com/reel/ABC{i}23/",
                    "timestamp": 1733969519 + i * 3600
                }
            }
        })
    return posts


def get_sample_liked_posts(count=3):
    """Generate sample liked posts data."""
    posts = []
    for i in range(count):
        posts.append({
            "title": f"liked_user_{i}",
            "string_list_data": [
                {
                    "href": f"https://www.instagram.com/p/DEF{i}56/",
                    "value": f"liked_user_{i}",
                    "timestamp": 1733969519 + i * 7200
                }
            ]
        })
    return posts


def get_sample_comments(count=4):
    """Generate sample comments data."""
    comments = []
    for i in range(count):
        comments.append({
            "string_map_data": {
                "Comment": {
                    "value": f"Great post! Comment number {i}"
                },
                "Media Owner": {
                    "value": f"media_owner_{i}"
                },
                "Time": {
                    "timestamp": 1733969519 + i * 5400
                }
            }
        })
    return comments


def get_sample_user_posts(count=2):
    """Generate sample user posts data."""
    posts = []
    for i in range(count):
        posts.append({
            "media": [
                {
                    "creation_timestamp": 1733969519 + i * 86400,
                    "title": f"My post {i}",
                    "media_metadata": {
                        "photo_metadata": {
                            "exif_data": []
                        }
                    }
                }
            ]
        })
    return posts


def get_sample_following(count=6):
    """Generate sample following data."""
    following = []
    for i in range(count):
        following.append({
            "string_list_data": [
                {
                    "value": f"following_user_{i}",
                    "timestamp": 1733969519 + i * 10800
                }
            ]
        })
    return following


def get_complete_instagram_export():
    """Generate a complete Instagram export with all data types."""
    return {
        "type": "instagram_export",
        "dataTypes": ["saved_posts", "liked_posts", "comments", "user_posts", "following"],
        "exportInfo": {
            "exportFolder": "instagram-testuser-2025-01-15-abc123/",
            "extractedAt": "2025-01-15T10:30:00Z",
            "dataTypes": ["saved_posts", "liked_posts", "comments", "user_posts", "following"]
        },
        "saved_posts": {
            "saved_saved_media": get_sample_saved_posts(5)
        },
        "liked_posts": {
            "likes_media_likes": get_sample_liked_posts(3)
        },
        "comments": {
            "comments_media_comments": get_sample_comments(4)
        },
        "user_posts": get_sample_user_posts(2),
        "following": {
            "relationships_following": get_sample_following(6)
        }
    }


def get_partial_instagram_export():
    """Generate an Instagram export with only some data types."""
    return {
        "type": "instagram_export", 
        "dataTypes": ["saved_posts", "comments"],
        "exportInfo": {
            "exportFolder": "instagram-partialuser-2025-01-15-xyz789/",
            "extractedAt": "2025-01-15T11:00:00Z",
            "dataTypes": ["saved_posts", "comments"]
        },
        "saved_posts": {
            "saved_saved_media": get_sample_saved_posts(10)  # Larger dataset
        },
        "comments": {
            "comments_media_comments": get_sample_comments(7)
        }
        # No liked_posts, user_posts, or following
    }


def get_empty_categories_export():
    """Generate an Instagram export with empty categories."""
    return {
        "type": "instagram_export",
        "dataTypes": ["saved_posts", "liked_posts", "comments"],
        "exportInfo": {
            "exportFolder": "instagram-emptyuser-2025-01-15-def456/",
            "extractedAt": "2025-01-15T12:00:00Z", 
            "dataTypes": ["saved_posts", "liked_posts", "comments"]
        },
        "saved_posts": {
            "saved_saved_media": get_sample_saved_posts(3)
        },
        "liked_posts": {
            "likes_media_likes": []  # Empty
        },
        "comments": {
            "comments_media_comments": []  # Empty
        }
    }


def get_large_dataset_export():
    """Generate a large Instagram export for sampling tests."""
    return {
        "type": "instagram_export",
        "dataTypes": ["saved_posts", "liked_posts"],
        "exportInfo": {
            "exportFolder": "instagram-largeuser-2025-01-15-ghi789/",
            "extractedAt": "2025-01-15T13:00:00Z",
            "dataTypes": ["saved_posts", "liked_posts"] 
        },
        "saved_posts": {
            "saved_saved_media": get_sample_saved_posts(150)  # Triggers sampling
        },
        "liked_posts": {
            "likes_media_likes": get_sample_liked_posts(200)  # Triggers sampling
        }
    }


def get_minimal_real_test_data():
    """Generate minimal data for real AI integration test (cost-effective)."""
    return {
        "type": "instagram_export",
        "dataTypes": ["saved_posts"],
        "exportInfo": {
            "exportFolder": "instagram-realtest-2025-01-15-real123/",
            "extractedAt": "2025-01-15T14:00:00Z",
            "dataTypes": ["saved_posts"]
        },
        "saved_posts": {
            "saved_saved_media": [
                {
                    "title": "fitness_motivation",
                    "string_map_data": {
                        "Saved on": {
                            "href": "https://www.instagram.com/reel/fitness123/",
                            "timestamp": 1733969519
                        }
                    }
                },
                {
                    "title": "coding_tutorial", 
                    "string_map_data": {
                        "Saved on": {
                            "href": "https://www.instagram.com/p/coding456/",
                            "timestamp": 1733972519
                        }
                    }
                },
                {
                    "title": "travel_inspiration",
                    "string_map_data": {
                        "Saved on": {
                            "href": "https://www.instagram.com/p/travel789/",
                            "timestamp": 1733975519
                        }
                    }
                }
            ]
        }
    }


# Export all fixtures for easy importing
__all__ = [
    'get_sample_saved_posts',
    'get_sample_liked_posts', 
    'get_sample_comments',
    'get_sample_user_posts',
    'get_sample_following',
    'get_complete_instagram_export',
    'get_partial_instagram_export',
    'get_empty_categories_export',
    'get_large_dataset_export',
    'get_minimal_real_test_data'
]