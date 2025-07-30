"""
Malformed and edge case data fixtures for error testing.
"""


def get_malformed_json():
    """Invalid JSON structure."""
    return '{"invalid": json, "missing": quote}'


def get_missing_required_fields():
    """Missing required fields in Instagram export."""
    return {
        # Missing 'type' field
        "dataTypes": ["saved_posts"],
        "saved_posts": {
            "saved_saved_media": []
        }
    }


def get_invalid_data_types():
    """Invalid data types in the request."""
    return {
        "type": "instagram_export",
        "dataTypes": "not_an_array",  # Should be array
        "exportInfo": {
            "dataTypes": None  # Should be array
        }
    }


def get_corrupted_instagram_structure():
    """Corrupted Instagram data structure."""
    return {
        "type": "instagram_export",
        "dataTypes": ["saved_posts", "liked_posts"],
        "saved_posts": {
            # Missing 'saved_saved_media' key
            "corrupted_data": []
        },
        "liked_posts": {
            "likes_media_likes": [
                {
                    # Missing string_list_data structure
                    "invalid_structure": "bad_data"
                }
            ]
        }
    }


def get_extremely_nested_data():
    """Extremely nested or circular reference data."""
    circular_ref = {"type": "instagram_export"}
    circular_ref["self_reference"] = circular_ref
    return circular_ref


def get_oversized_data():
    """Data that might cause memory issues."""
    return {
        "type": "instagram_export",
        "dataTypes": ["saved_posts"],
        "saved_posts": {
            "saved_saved_media": [
                {
                    "title": "x" * 10000,  # Very long string
                    "string_map_data": {
                        "Saved on": {
                            "href": "https://example.com/" + "x" * 1000,
                            "timestamp": 1733969519
                        }
                    }
                }
            ]
        }
    }


def get_invalid_timestamps():
    """Invalid timestamp values."""
    return {
        "type": "instagram_export",
        "dataTypes": ["saved_posts"],
        "saved_posts": {
            "saved_saved_media": [
                {
                    "title": "test_user",
                    "string_map_data": {
                        "Saved on": {
                            "href": "https://www.instagram.com/p/test/",
                            "timestamp": "not_a_number"  # Invalid timestamp
                        }
                    }
                },
                {
                    "title": "test_user_2",
                    "string_map_data": {
                        "Saved on": {
                            "href": "https://www.instagram.com/p/test2/",
                            "timestamp": -1  # Negative timestamp
                        }
                    }
                }
            ]
        }
    }


def get_empty_request():
    """Completely empty request."""
    return {}


def get_null_values():
    """Request with null/None values."""
    return {
        "type": None,
        "dataTypes": None,
        "exportInfo": None,
        "saved_posts": None
    }


def get_wrong_content_type():
    """Data that looks like Instagram but isn't."""
    return {
        "type": "twitter_export",  # Wrong type
        "dataTypes": ["saved_posts"],
        "saved_posts": {
            "tweets": []  # Wrong structure
        }
    }


def get_mixed_valid_invalid_data():
    """Mix of valid and invalid data in same request."""
    return {
        "type": "instagram_export",
        "dataTypes": ["saved_posts", "liked_posts"],
        "exportInfo": {
            "exportFolder": "valid-folder/",
            "extractedAt": "2025-01-15T10:30:00Z",
            "dataTypes": ["saved_posts", "liked_posts"]
        },
        "saved_posts": {
            "saved_saved_media": [
                {
                    "title": "valid_user",
                    "string_map_data": {
                        "Saved on": {
                            "href": "https://www.instagram.com/p/valid/",
                            "timestamp": 1733969519
                        }
                    }
                }
            ]
        },
        "liked_posts": {
            # Invalid structure mixed with valid export info
            "corrupted_likes": "not_an_array"
        }
    }


# Export all fixtures
__all__ = [
    'get_malformed_json',
    'get_missing_required_fields',
    'get_invalid_data_types',
    'get_corrupted_instagram_structure',
    'get_extremely_nested_data',
    'get_oversized_data',
    'get_invalid_timestamps',
    'get_empty_request',
    'get_null_values',
    'get_wrong_content_type',
    'get_mixed_valid_invalid_data'
]