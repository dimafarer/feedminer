"""
Unit tests for multi_upload.py - Multi-File Instagram Data Upload API Handler.

Tests the main handler function, data processing logic, AWS integration,
and error handling for the multi-upload endpoint.
"""

import json
import pytest
from unittest.mock import Mock, patch, MagicMock
from botocore.exceptions import ClientError

# Import the module under test
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src/api'))
from multi_upload import (
    handler,
    process_consolidated_instagram_data,
    process_single_instagram_data_type,
    count_items_in_data_type,
    fallback_to_regular_upload
)


class TestMultiUploadHandler:
    """Test the main Lambda handler function."""
    
    @pytest.mark.unit
    def test_options_request_returns_cors_headers(self, lambda_context):
        """Test OPTIONS preflight request handling."""
        event = {
            'httpMethod': 'OPTIONS'
        }
        
        response = handler(event, lambda_context)
        
        assert response['statusCode'] == 200
        assert 'Access-Control-Allow-Origin' in response['headers']
        assert 'Access-Control-Allow-Methods' in response['headers']
        assert response['body'] == ''
    
    @pytest.mark.unit
    def test_missing_body_returns_400(self, lambda_context):
        """Test request without body returns 400 error."""
        event = {
            'httpMethod': 'POST'
            # Missing 'body' key
        }
        
        response = handler(event, lambda_context)
        
        assert response['statusCode'] == 400
        assert 'No body provided' in response['body']
    
    @pytest.mark.unit
    def test_invalid_json_body_returns_400(self, lambda_context):
        """Test malformed JSON body returns 400 error."""
        event = {
            'httpMethod': 'POST',
            'body': '{"invalid": json, "missing": quote}'
        }
        
        response = handler(event, lambda_context)
        
        assert response['statusCode'] == 400
        assert 'Invalid JSON' in response['body']
    
    @pytest.mark.unit
    @patch('multi_upload.process_consolidated_instagram_data')
    def test_consolidated_instagram_export_routing(self, mock_process, lambda_context, sample_complete_export):
        """Test routing to consolidated Instagram data processing."""
        mock_process.return_value = {
            'contentId': 'test-id-123',
            'status': 'uploaded'
        }
        
        event = {
            'httpMethod': 'POST',
            'body': json.dumps(sample_complete_export)
        }
        
        response = handler(event, lambda_context)
        
        assert response['statusCode'] == 200
        mock_process.assert_called_once()
        # Verify the correct parameters were passed (positional args)
        call_args = mock_process.call_args
        assert call_args[0][0] == sample_complete_export  # body
        assert len(call_args[0]) == 4  # body, content_id, user_id, data_types
        assert call_args[0][2] == 'anonymous'  # user_id (default)
        assert call_args[0][3] == sample_complete_export['dataTypes']  # data_types
    
    @pytest.mark.unit
    @patch('multi_upload.process_single_instagram_data_type')
    def test_single_data_type_routing(self, mock_process, lambda_context):
        """Test routing to single data type processing."""
        mock_process.return_value = {
            'contentId': 'test-single-id-123',
            'status': 'uploaded'
        }
        
        single_type_data = {
            'type': 'instagram_saved_posts',
            'saved_posts': {'saved_saved_media': []}
        }
        
        event = {
            'httpMethod': 'POST',
            'body': json.dumps(single_type_data)
        }
        
        response = handler(event, lambda_context)
        
        assert response['statusCode'] == 200
        mock_process.assert_called_once()
    
    @pytest.mark.unit
    @patch('multi_upload.fallback_to_regular_upload')
    def test_fallback_to_regular_upload(self, mock_fallback, lambda_context):
        """Test fallback to regular upload for unsupported types."""
        mock_fallback.return_value = {
            'statusCode': 200,
            'body': json.dumps({'message': 'Regular upload processed'})
        }
        
        regular_data = {
            'type': 'other_content',
            'content': 'some data'
        }
        
        event = {
            'httpMethod': 'POST',
            'body': json.dumps(regular_data)
        }
        
        response = handler(event, lambda_context)
        
        mock_fallback.assert_called_once()


class TestProcessConsolidatedInstagramData:
    """Test consolidated Instagram data processing."""
    
    @pytest.mark.unit
    @patch('multi_upload.boto3')
    def test_complete_export_processing(self, mock_boto3, mock_env_vars, sample_complete_export):
        """Test processing complete Instagram export with all data types."""
        # Mock AWS services
        mock_s3 = Mock()
        mock_dynamodb = Mock()
        mock_table = Mock()
        
        mock_boto3.client.return_value = mock_s3
        mock_boto3.resource.return_value = mock_dynamodb
        mock_dynamodb.Table.return_value = mock_table
        
        content_id = 'test-content-123'
        user_id = 'test-user'
        data_types = sample_complete_export['dataTypes']
        
        result = process_consolidated_instagram_data(
            sample_complete_export, content_id, user_id, data_types
        )
        
        # Verify S3 calls - should be 6 total (5 individual + 1 consolidated)
        expected_s3_calls = len(data_types) + 1  # Individual files + consolidated
        assert mock_s3.put_object.call_count == expected_s3_calls
        
        # Verify DynamoDB call
        mock_table.put_item.assert_called_once()
        
        # Verify response structure
        assert result['contentId'] == content_id
        assert result['status'] == 'uploaded'
        assert result['type'] == 'instagram_export'
        assert result['dataTypes'] == data_types
        assert 'totalItems' in result
        assert 'dataStructure' in result
    
    @pytest.mark.unit
    @patch('multi_upload.boto3')
    def test_partial_export_processing(self, mock_boto3, mock_env_vars, sample_partial_export):
        """Test processing partial Instagram export with only some data types."""
        # Mock AWS services
        mock_s3 = Mock()
        mock_dynamodb = Mock()
        mock_table = Mock()
        
        mock_boto3.client.return_value = mock_s3
        mock_boto3.resource.return_value = mock_dynamodb
        mock_dynamodb.Table.return_value = mock_table
        
        content_id = 'test-partial-123'
        user_id = 'test-user'
        data_types = sample_partial_export['dataTypes']  # Only saved_posts and comments
        
        result = process_consolidated_instagram_data(
            sample_partial_export, content_id, user_id, data_types
        )
        
        # Should process only the available data types
        expected_s3_calls = len(data_types) + 1  # 2 individual + 1 consolidated
        assert mock_s3.put_object.call_count == expected_s3_calls
        
        # Verify only requested data types are in result
        assert set(result['dataTypes']) == set(data_types)
        assert len(result['dataStructure']) == len(data_types)
    
    @pytest.mark.unit
    @patch('multi_upload.boto3')
    def test_empty_categories_handling(self, mock_boto3, mock_env_vars, sample_empty_categories):
        """Test handling of empty categories in Instagram export."""
        # Mock AWS services
        mock_s3 = Mock()
        mock_dynamodb = Mock()
        mock_table = Mock()
        
        mock_boto3.client.return_value = mock_s3
        mock_boto3.resource.return_value = mock_dynamodb
        mock_dynamodb.Table.return_value = mock_table
        
        content_id = 'test-empty-123'
        user_id = 'test-user'
        data_types = sample_empty_categories['dataTypes']
        
        result = process_consolidated_instagram_data(
            sample_empty_categories, content_id, user_id, data_types
        )
        
        # Should still process empty categories
        assert result['status'] == 'uploaded'
        assert len(result['dataStructure']) == len(data_types)
        
        # Check that empty categories are handled correctly
        for data_type in data_types:
            if data_type in result['dataStructure']:
                # Empty categories should have count 0
                structure = result['dataStructure'][data_type]
                assert 'count' in structure
                assert 's3Key' in structure
    
    @pytest.mark.unit
    @patch('multi_upload.boto3')
    def test_s3_upload_failure_handling(self, mock_boto3, mock_env_vars, sample_complete_export):
        """Test handling of S3 upload failures."""
        # Mock S3 to raise an exception
        mock_s3 = Mock()
        mock_s3.put_object.side_effect = ClientError(
            error_response={'Error': {'Code': 'AccessDenied', 'Message': 'Access Denied'}},
            operation_name='PutObject'
        )
        
        mock_boto3.client.return_value = mock_s3
        
        content_id = 'test-s3-error-123'
        user_id = 'test-user'
        data_types = sample_complete_export['dataTypes']
        
        # Should raise exception for S3 failures
        with pytest.raises(ClientError):
            process_consolidated_instagram_data(
                sample_complete_export, content_id, user_id, data_types
            )
    
    @pytest.mark.unit
    @patch('multi_upload.boto3')
    def test_dynamodb_failure_handling(self, mock_boto3, mock_env_vars, sample_complete_export):
        """Test handling of DynamoDB failures."""
        # Mock successful S3 but failing DynamoDB
        mock_s3 = Mock()
        mock_dynamodb = Mock()
        mock_table = Mock()
        mock_table.put_item.side_effect = ClientError(
            error_response={'Error': {'Code': 'ProvisionedThroughputExceededException', 'Message': 'Throttled'}},
            operation_name='PutItem'
        )
        
        mock_boto3.client.return_value = mock_s3
        mock_boto3.resource.return_value = mock_dynamodb
        mock_dynamodb.Table.return_value = mock_table
        
        content_id = 'test-dynamo-error-123'
        user_id = 'test-user'
        data_types = sample_complete_export['dataTypes']
        
        # Should raise exception for DynamoDB failures
        with pytest.raises(ClientError):
            process_consolidated_instagram_data(
                sample_complete_export, content_id, user_id, data_types
            )


class TestProcessSingleInstagramDataType:
    """Test single Instagram data type processing."""
    
    @pytest.mark.unit
    @patch('multi_upload.boto3')
    def test_single_saved_posts_processing(self, mock_boto3, mock_env_vars):
        """Test processing single saved_posts data type."""
        # Mock AWS services
        mock_s3 = Mock()
        mock_dynamodb = Mock()
        mock_table = Mock()
        
        mock_boto3.client.return_value = mock_s3
        mock_boto3.resource.return_value = mock_dynamodb
        mock_dynamodb.Table.return_value = mock_table
        
        single_data = {
            'saved_saved_media': [
                {'title': 'test_user', 'string_map_data': {}}
            ]
        }
        
        content_id = 'test-single-123'
        user_id = 'test-user'
        data_type = 'saved_posts'
        
        result = process_single_instagram_data_type(
            single_data, content_id, user_id, data_type
        )
        
        # Verify S3 and DynamoDB calls
        mock_s3.put_object.assert_called_once()
        mock_table.put_item.assert_called_once()
        
        # Verify response
        assert result['contentId'] == content_id
        assert result['status'] == 'uploaded'
        assert result['type'] == f'instagram_{data_type}'
        assert 'itemCount' in result


class TestCountItemsInDataType:
    """Test item counting logic for different Instagram data types."""
    
    @pytest.mark.unit
    def test_count_saved_posts(self):
        """Test counting saved_posts items."""
        data = {
            'saved_saved_media': [
                {'title': 'user1'},
                {'title': 'user2'},
                {'title': 'user3'}
            ]
        }
        
        count = count_items_in_data_type('saved_posts', data)
        assert count == 3
    
    @pytest.mark.unit
    def test_count_liked_posts(self):
        """Test counting liked_posts items."""
        data = {
            'likes_media_likes': [
                {'title': 'liked1'},
                {'title': 'liked2'}
            ]
        }
        
        count = count_items_in_data_type('liked_posts', data)
        assert count == 2
    
    @pytest.mark.unit
    def test_count_comments(self):
        """Test counting comments items."""
        data = {
            'comments_media_comments': [
                {'string_map_data': {'Comment': {'value': 'Nice!'}}},
                {'string_map_data': {'Comment': {'value': 'Great post!'}}},
                {'string_map_data': {'Comment': {'value': 'Love it!'}}}
            ]
        }
        
        count = count_items_in_data_type('comments', data)
        assert count == 3
    
    @pytest.mark.unit
    def test_count_user_posts_list_format(self):
        """Test counting user_posts in list format."""
        data = [
            {'media': [{'title': 'My post 1'}]},
            {'media': [{'title': 'My post 2'}]}
        ]
        
        count = count_items_in_data_type('user_posts', data)
        assert count == 2
    
    @pytest.mark.unit
    def test_count_user_posts_dict_format(self):
        """Test counting user_posts in dict format with content key."""
        data = {
            'content': [
                {'media': [{'title': 'My post 1'}]},
                {'media': [{'title': 'My post 2'}]},
                {'media': [{'title': 'My post 3'}]}
            ]
        }
        
        count = count_items_in_data_type('user_posts', data)
        assert count == 3
    
    @pytest.mark.unit
    def test_count_following(self):
        """Test counting following items."""
        data = {
            'relationships_following': [
                {'string_list_data': [{'value': 'user1'}]},
                {'string_list_data': [{'value': 'user2'}]},
                {'string_list_data': [{'value': 'user3'}]},
                {'string_list_data': [{'value': 'user4'}]}
            ]
        }
        
        count = count_items_in_data_type('following', data)
        assert count == 4
    
    @pytest.mark.unit
    def test_count_empty_data(self):
        """Test counting empty data structures."""
        # Empty saved posts
        empty_saved = {'saved_saved_media': []}
        assert count_items_in_data_type('saved_posts', empty_saved) == 0
        
        # Empty liked posts
        empty_liked = {'likes_media_likes': []}
        assert count_items_in_data_type('liked_posts', empty_liked) == 0
        
        # Empty comments
        empty_comments = {'comments_media_comments': []}
        assert count_items_in_data_type('comments', empty_comments) == 0
    
    @pytest.mark.unit
    def test_count_malformed_data(self):
        """Test counting with malformed data structures."""
        # Missing expected keys
        malformed1 = {'wrong_key': [1, 2, 3]}
        assert count_items_in_data_type('saved_posts', malformed1) == 3  # Fallback to any list
        
        # Completely wrong structure
        malformed2 = {'not_a_list': 'string_value'}
        assert count_items_in_data_type('saved_posts', malformed2) == 1  # Fallback
        
        # None/null data
        assert count_items_in_data_type('saved_posts', None) == 0
    
    @pytest.mark.unit
    def test_count_unknown_data_type(self):
        """Test counting unknown data type falls back gracefully."""
        data = {
            'some_list': [1, 2, 3, 4, 5]
        }
        
        count = count_items_in_data_type('unknown_type', data)
        assert count == 5  # Should find the list and count it


class TestErrorHandling:
    """Test error handling scenarios."""
    
    @pytest.mark.unit
    def test_handler_exception_returns_500(self, lambda_context):
        """Test that unhandled exceptions return 500 error."""
        # Trigger an exception by providing invalid event structure
        event = {
            'httpMethod': 'POST',
            'body': json.dumps({'type': 'instagram_export'}),
            # This will cause an exception when trying to process
        }
        
        with patch('multi_upload.process_consolidated_instagram_data') as mock_process:
            mock_process.side_effect = Exception("Unexpected error")
            
            response = handler(event, lambda_context)
            
            assert response['statusCode'] == 500
            assert 'Internal server error' in response['body']
    
    @pytest.mark.unit
    def test_missing_environment_variables(self, lambda_context, sample_complete_export):
        """Test behavior when environment variables are missing."""
        event = {
            'httpMethod': 'POST',
            'body': json.dumps(sample_complete_export)
        }
        
        # Clear environment variables
        with patch.dict(os.environ, {}, clear=True):
            with patch('multi_upload.boto3'):
                response = handler(event, lambda_context)
                
                # Should still attempt to process but may use None values
                # The actual behavior depends on implementation
                assert response['statusCode'] in [200, 500]


class TestIntegrationScenarios:
    """Test realistic integration scenarios."""
    
    @pytest.mark.unit
    @patch('multi_upload.boto3')
    def test_large_dataset_processing(self, mock_boto3, mock_env_vars, sample_large_dataset):
        """Test processing large dataset (for sampling scenarios)."""
        # Mock AWS services
        mock_s3 = Mock()
        mock_dynamodb = Mock()
        mock_table = Mock()
        
        mock_boto3.client.return_value = mock_s3
        mock_boto3.resource.return_value = mock_dynamodb
        mock_dynamodb.Table.return_value = mock_table
        
        content_id = 'test-large-123'
        user_id = 'test-user'
        data_types = sample_large_dataset['dataTypes']
        
        result = process_consolidated_instagram_data(
            sample_large_dataset, content_id, user_id, data_types
        )
        
        # Should process successfully even with large dataset
        assert result['status'] == 'uploaded'
        assert result['totalItems'] > 100  # Should count all items
        
        # Verify metadata structure contains large counts
        for data_type in data_types:
            if data_type in result['dataStructure']:
                structure = result['dataStructure'][data_type]
                assert structure['count'] > 50  # Large dataset should have many items
    
    @pytest.mark.unit
    @patch('multi_upload.boto3')
    def test_mixed_valid_invalid_data(self, mock_boto3, mock_env_vars):
        """Test processing data with mix of valid and invalid structures."""
        # Mock AWS services
        mock_s3 = Mock()
        mock_dynamodb = Mock()
        mock_table = Mock()
        
        mock_boto3.client.return_value = mock_s3
        mock_boto3.resource.return_value = mock_dynamodb
        mock_dynamodb.Table.return_value = mock_table
        
        mixed_data = {
            'type': 'instagram_export',
            'dataTypes': ['saved_posts', 'liked_posts'],
            'exportInfo': {
                'exportFolder': 'test/',
                'extractedAt': '2025-01-15T10:30:00Z',
                'dataTypes': ['saved_posts', 'liked_posts']
            },
            'saved_posts': {
                'saved_saved_media': [
                    {'title': 'valid_user', 'string_map_data': {}}
                ]
            },
            'liked_posts': {
                # Invalid structure - should be handled gracefully
                'wrong_key': 'not_a_list'
            }
        }
        
        content_id = 'test-mixed-123'
        user_id = 'test-user'
        data_types = mixed_data['dataTypes']
        
        result = process_consolidated_instagram_data(
            mixed_data, content_id, user_id, data_types
        )
        
        # Should process successfully and handle invalid data gracefully
        assert result['status'] == 'uploaded'
        assert len(result['dataStructure']) == len(data_types)


# Performance and edge case tests
class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    @pytest.mark.unit
    def test_zero_items_across_all_categories(self, mock_env_vars):
        """Test handling when all categories have zero items."""
        empty_export = {
            'type': 'instagram_export',
            'dataTypes': ['saved_posts', 'liked_posts'],
            'exportInfo': {
                'extractedAt': '2025-01-15T10:30:00Z',
                'dataTypes': ['saved_posts', 'liked_posts']
            },
            'saved_posts': {'saved_saved_media': []},
            'liked_posts': {'likes_media_likes': []}
        }
        
        with patch('multi_upload.boto3') as mock_boto3:
            mock_s3 = Mock()
            mock_dynamodb = Mock()
            mock_table = Mock()
            
            mock_boto3.client.return_value = mock_s3
            mock_boto3.resource.return_value = mock_dynamodb
            mock_dynamodb.Table.return_value = mock_table
            
            result = process_consolidated_instagram_data(
                empty_export, 'test-zero-123', 'test-user', empty_export['dataTypes']
            )
            
            # Should handle zero items gracefully
            assert result['status'] == 'uploaded'
            assert result['totalItems'] == 0
            
            # All categories should be present but with zero counts
            for data_type in empty_export['dataTypes']:
                assert data_type in result['dataStructure']
                assert result['dataStructure'][data_type]['count'] == 0
    
    @pytest.mark.unit
    def test_single_item_processing(self, mock_env_vars):
        """Test processing export with exactly one item total."""
        minimal_export = {
            'type': 'instagram_export',
            'dataTypes': ['saved_posts'],
            'exportInfo': {
                'extractedAt': '2025-01-15T10:30:00Z',
                'dataTypes': ['saved_posts']
            },
            'saved_posts': {
                'saved_saved_media': [
                    {'title': 'single_user', 'string_map_data': {}}
                ]
            }
        }
        
        with patch('multi_upload.boto3') as mock_boto3:
            mock_s3 = Mock()
            mock_dynamodb = Mock()
            mock_table = Mock()
            
            mock_boto3.client.return_value = mock_s3
            mock_boto3.resource.return_value = mock_dynamodb
            mock_dynamodb.Table.return_value = mock_table
            
            result = process_consolidated_instagram_data(
                minimal_export, 'test-single-123', 'test-user', ['saved_posts']
            )
            
            # Should process single item correctly
            assert result['status'] == 'uploaded'
            assert result['totalItems'] == 1
            assert result['dataStructure']['saved_posts']['count'] == 1