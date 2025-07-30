"""
Unit tests for instagram_parser.py - Instagram JSON Parser Agent.

Tests the smart sampling logic, multi-type data processing, explicit error handling,
metadata generation, and AI integration for Instagram content analysis.
"""

import json
import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from decimal import Decimal
import os

# Import the module under test
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src/agents'))
from instagram_parser import (
    InstagramParserAgent,
    InstagramPost,
    ContentCategory,
    ContentInsight,
    InstagramAnalysisResult
)


class TestInstagramParserAgent:
    """Test the main InstagramParserAgent class."""
    
    @pytest.mark.unit
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key-123', 'CONTENT_TABLE': 'test-table'})
    def test_agent_initialization_success(self):
        """Test successful agent initialization with API key."""
        agent = InstagramParserAgent()
        
        assert agent.agent is not None
        assert agent.dynamodb is not None
        assert agent.s3 is not None
        assert agent.content_table_name is not None
    
    @pytest.mark.unit
    def test_agent_initialization_missing_api_key(self):
        """Test agent initialization fails without API key."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="ANTHROPIC_API_KEY environment variable is not set"):
                InstagramParserAgent()


class TestSmartSamplingLogic:
    """Test the smart sampling logic implemented in Phase 1."""
    
    @pytest.mark.unit
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key-123'})
    @patch('instagram_parser.boto3')
    def test_zero_items_fallback_to_100_samples(self, mock_boto3, mock_strands_agent):
        """Test that zero total items defaults to 100 samples per type (our recent fix)."""
        agent = InstagramParserAgent()
        agent.agent = mock_strands_agent
        
        # Create export with empty data
        zero_items_export = {
            'saved_posts': {'saved_saved_media': []},
            'liked_posts': {'likes_media_likes': []},
            'comments': {'comments_media_comments': []}
        }
        export_info = {
            'dataTypes': ['saved_posts', 'liked_posts', 'comments'],
            'extractedAt': '2025-01-15T10:30:00Z'
        }
        
        # Mock the agent response (must be async)
        mock_result = Mock()
        mock_result.total_posts = 0
        mock_result.metadata = None
        mock_strands_agent.structured_output_async = AsyncMock(return_value=mock_result)
        
        # Call the method
        import asyncio
        result = asyncio.run(agent.parse_multi_type_instagram_export(zero_items_export, export_info))
        
        # Verify sampling logic
        assert result.metadata['total_items_available'] == 0
        assert result.metadata['sample_size_per_type'] == 100  # Our fallback fix
        assert result.metadata['debug_mode'] == True
        assert 'smart sampling' in str(result.metadata).lower() or result.metadata['sample_size_per_type'] == 100
    
    @pytest.mark.unit  
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key-123'})
    @patch('instagram_parser.boto3')
    def test_small_dataset_samples_all_available(self, mock_boto3, mock_strands_agent, sample_complete_export):
        """Test small datasets sample all available items."""
        agent = InstagramParserAgent()
        agent.agent = mock_strands_agent
        
        # Create small dataset (total ~20 items)
        small_export = {
            'saved_posts': {'saved_saved_media': [{'title': f'user_{i}'} for i in range(5)]},
            'liked_posts': {'likes_media_likes': [{'title': f'liked_{i}'} for i in range(3)]},
            'comments': {'comments_media_comments': [{'string_map_data': {}} for i in range(2)]}
        }
        export_info = {
            'dataTypes': ['saved_posts', 'liked_posts', 'comments'],
            'extractedAt': '2025-01-15T10:30:00Z'
        }
        
        mock_result = Mock()
        mock_result.total_posts = 10
        mock_result.metadata = None
        mock_strands_agent.structured_output_async = AsyncMock(return_value=mock_result)
        
        import asyncio
        result = asyncio.run(agent.parse_multi_type_instagram_export(small_export, export_info))
        
        # Should sample more than just 1 per type for small datasets
        assert result.metadata['sample_size_per_type'] >= 10
        assert result.metadata['total_items_available'] == 10  # 5 + 3 + 2
    
    @pytest.mark.unit
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key-123'})  
    @patch('instagram_parser.boto3')
    def test_large_dataset_samples_100_per_type(self, mock_boto3, mock_strands_agent, sample_large_dataset):
        """Test large datasets trigger 100-item sampling."""
        agent = InstagramParserAgent()
        agent.agent = mock_strands_agent
        
        # Create large dataset
        large_export = {
            'saved_posts': {'saved_saved_media': [{'title': f'user_{i}'} for i in range(150)]},
            'liked_posts': {'likes_media_likes': [{'title': f'liked_{i}'} for i in range(200)]},
            'comments': {'comments_media_comments': [{'string_map_data': {}} for i in range(180)]}
        }
        export_info = {
            'dataTypes': ['saved_posts', 'liked_posts', 'comments'],
            'extractedAt': '2025-01-15T10:30:00Z'
        }
        
        mock_result = Mock()
        mock_result.total_posts = 300  # Will be sampled down
        mock_result.metadata = None
        mock_strands_agent.structured_output_async = AsyncMock(return_value=mock_result)
        
        import asyncio
        result = asyncio.run(agent.parse_multi_type_instagram_export(large_export, export_info))
        
        # Should use 100 samples per type for large datasets
        assert result.metadata['sample_size_per_type'] == 100
        assert result.metadata['total_items_available'] == 530  # 150 + 200 + 180
        assert result.metadata['total_items_processed'] == 300  # Sampled: 100 + 100 + 100
    
    @pytest.mark.unit
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key-123'})
    @patch('instagram_parser.boto3')
    def test_uneven_distribution_sampling(self, mock_boto3, mock_strands_agent):
        """Test sampling with uneven distribution across data types."""
        agent = InstagramParserAgent()
        agent.agent = mock_strands_agent
        
        # Uneven distribution: some categories have many items, others few
        uneven_export = {
            'saved_posts': {'saved_saved_media': [{'title': f'user_{i}'} for i in range(200)]},  # Large
            'liked_posts': {'likes_media_likes': [{'title': f'liked_{i}'} for i in range(5)]},    # Small
            'comments': {'comments_media_comments': []},  # Empty
            'following': {'relationships_following': [{'string_list_data': [{'value': f'follow_{i}'}]} for i in range(50)]}  # Medium
        }
        export_info = {
            'dataTypes': ['saved_posts', 'liked_posts', 'comments', 'following'],
            'extractedAt': '2025-01-15T10:30:00Z'
        }
        
        mock_result = Mock()
        mock_result.total_posts = 155  # Will be processed according to sampling
        mock_result.metadata = None
        mock_strands_agent.structured_output_async = AsyncMock(return_value=mock_result)
        
        import asyncio
        result = asyncio.run(agent.parse_multi_type_instagram_export(uneven_export, export_info))
        
        # Should handle uneven distribution gracefully
        assert result.metadata['total_items_available'] == 255  # 200 + 5 + 0 + 50
        assert result.metadata['sample_size_per_type'] == 50  # Medium dataset sampling
        # Actual processing should respect available items (can't sample more than exist)
        assert result.metadata['total_items_processed'] <= result.metadata['total_items_available']


class TestMultiTypeDataProcessing:
    """Test multi-type Instagram data processing edge cases."""
    
    @pytest.mark.unit
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key-123'})
    @patch('instagram_parser.boto3')
    def test_missing_data_types_handling(self, mock_boto3, mock_strands_agent):
        """Test when requested data types don't exist in the export."""
        agent = InstagramParserAgent()
        agent.agent = mock_strands_agent
        
        # Export missing some requested data types
        partial_export = {
            'saved_posts': {'saved_saved_media': [{'title': 'user1'}]},
            # Missing: liked_posts, comments, user_posts, following
        }
        export_info = {
            'dataTypes': ['saved_posts', 'liked_posts', 'comments', 'user_posts', 'following'],  # Request all
            'extractedAt': '2025-01-15T10:30:00Z'
        }
        
        mock_result = Mock()
        mock_result.total_posts = 1
        mock_result.metadata = None
        mock_strands_agent.structured_output_async = AsyncMock(return_value=mock_result)
        
        import asyncio
        result = asyncio.run(agent.parse_multi_type_instagram_export(partial_export, export_info))
        
        # Should handle missing data types gracefully
        assert result.metadata['data_types_analyzed'] == export_info['dataTypes']
        assert result.metadata['total_items_available'] == 1  # Only saved_posts exists
    
    @pytest.mark.unit
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key-123'})
    @patch('instagram_parser.boto3')
    def test_corrupted_data_structures(self, mock_boto3, mock_strands_agent):
        """Test handling of corrupted Instagram data structures."""
        agent = InstagramParserAgent()
        agent.agent = mock_strands_agent
        
        # Valid export info but corrupted post data
        corrupted_export = {
            'saved_posts': {
                'wrong_key': [{'invalid': 'structure'}]  # Should be 'saved_saved_media'
            },
            'liked_posts': {
                'likes_media_likes': [{'title': 'valid_liked_post'}]  # Valid structure
            },
            'comments': None  # Null data
        }
        export_info = {
            'dataTypes': ['saved_posts', 'liked_posts', 'comments'],
            'extractedAt': '2025-01-15T10:30:00Z'
        }
        
        mock_result = Mock()
        mock_result.total_posts = 1  # Should have 1 valid liked post
        mock_result.metadata = None
        mock_strands_agent.structured_output_async = AsyncMock(return_value=mock_result)
        
        import asyncio
        # Should not crash, should handle gracefully
        result = asyncio.run(agent.parse_multi_type_instagram_export(corrupted_export, export_info))
        
        # Should process without crashing, even with corrupted data
        assert result.metadata is not None
        assert result.metadata['total_items_available'] >= 0
    
    @pytest.mark.unit
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key-123'})
    @patch('instagram_parser.boto3')
    def test_single_data_type_processing(self, mock_boto3, mock_strands_agent):
        """Test minimum viable case - single data type."""
        agent = InstagramParserAgent()
        agent.agent = mock_strands_agent
        
        single_type_export = {
            'saved_posts': {'saved_saved_media': [
                {'title': 'single_user', 'string_map_data': {'Saved on': {'timestamp': 1733969519}}}
            ]}
        }
        export_info = {
            'dataTypes': ['saved_posts'],
            'extractedAt': '2025-01-15T10:30:00Z'
        }
        
        mock_result = Mock()
        mock_result.total_posts = 1
        mock_result.metadata = None
        mock_strands_agent.structured_output_async = AsyncMock(return_value=mock_result)
        
        import asyncio
        result = asyncio.run(agent.parse_multi_type_instagram_export(single_type_export, export_info))
        
        # Should handle single data type correctly
        assert len(result.metadata['data_types_analyzed']) == 1
        assert result.metadata['data_types_analyzed'][0] == 'saved_posts'
        assert result.metadata['total_items_available'] == 1


class TestExplicitErrorHandling:
    """Test explicit error handling (no graceful fallbacks)."""
    
    @pytest.mark.unit
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key-123'})
    @patch('instagram_parser.boto3')
    def test_ai_api_failure_raises_exception(self, mock_boto3):
        """Test AI API failures raise explicit exceptions with 🚨 alerts."""
        agent = InstagramParserAgent()
        
        # Mock AI agent to fail
        mock_agent = Mock()
        mock_agent.structured_output_async = AsyncMock(side_effect=Exception("AI API failed"))
        agent.agent = mock_agent
        
        simple_export = {
            'saved_posts': {'saved_saved_media': [{'title': 'test_user'}]}
        }
        export_info = {
            'dataTypes': ['saved_posts'],
            'extractedAt': '2025-01-15T10:30:00Z'
        }
        
        import asyncio
        # Should raise exception with 🚨 alert message
        with pytest.raises(Exception) as exc_info:
            asyncio.run(agent.parse_multi_type_instagram_export(simple_export, export_info))
        
        # Verify explicit error message
        error_message = str(exc_info.value)
        assert "Multi-type Instagram analysis failed" in error_message
        # The underlying error should be preserved
        assert "AI API failed" in error_message
    
    @pytest.mark.unit
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key-123'})
    @patch('instagram_parser.boto3')
    def test_strands_agent_initialization_failure(self, mock_boto3):
        """Test Strands agent initialization failures."""
        # Mock Strands to fail during initialization
        with patch('instagram_parser.Agent') as mock_agent_class:
            mock_agent_class.side_effect = Exception("Strands initialization failed")
            
            with pytest.raises(Exception, match="Strands initialization failed"):
                InstagramParserAgent()
    
    @pytest.mark.unit
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key-123'})
    @patch('instagram_parser.boto3')
    def test_memory_usage_logging(self, mock_boto3, mock_strands_agent):
        """Test memory usage logging during processing."""
        agent = InstagramParserAgent()
        agent.agent = mock_strands_agent
        
        mock_result = Mock()
        mock_result.total_posts = 5
        mock_result.metadata = None
        mock_strands_agent.structured_output_async = AsyncMock(return_value=mock_result)
        
        # Mock psutil for memory logging
        with patch('instagram_parser.psutil') as mock_psutil:
            mock_process = Mock()
            mock_memory_info = Mock()
            mock_memory_info.rss = 1024 * 1024 * 100  # 100MB
            mock_memory_info.vms = 1024 * 1024 * 200  # 200MB
            mock_process.memory_info.return_value = mock_memory_info
            mock_psutil.Process.return_value = mock_process
            
            simple_export = {
                'saved_posts': {'saved_saved_media': [{'title': 'test_user'}]}
            }
            export_info = {
                'dataTypes': ['saved_posts'],
                'extractedAt': '2025-01-15T10:30:00Z'
            }
            
            import asyncio
            result = asyncio.run(agent.parse_multi_type_instagram_export(simple_export, export_info))
            
            # Verify memory logging was called
            mock_psutil.Process.assert_called()
            mock_process.memory_info.assert_called()
    
    @pytest.mark.unit
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key-123'})
    def test_fallback_analysis_disabled(self):
        """Test that fallback analysis is disabled and raises exception."""
        agent = InstagramParserAgent()
        
        # Try to call the disabled fallback function
        with pytest.raises(Exception, match="DEVELOPMENT MODE: Fallback analysis disabled"):
            agent._create_fallback_analysis([])


class TestMetadataTracking:
    """Test metadata generation and tracking accuracy."""
    
    @pytest.mark.unit
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key-123'})
    @patch('instagram_parser.boto3')
    def test_metadata_accuracy_sample_vs_available(self, mock_boto3, mock_strands_agent):
        """Test that metadata correctly tracks sampled vs available counts."""
        agent = InstagramParserAgent()
        agent.agent = mock_strands_agent
        
        # Large dataset that will be sampled
        large_export = {
            'saved_posts': {'saved_saved_media': [{'title': f'user_{i}'} for i in range(150)]},
            'liked_posts': {'likes_media_likes': [{'title': f'liked_{i}'} for i in range(75)]}
        }
        export_info = {
            'dataTypes': ['saved_posts', 'liked_posts'],
            'extractedAt': '2025-01-15T10:30:00Z'
        }
        
        mock_result = Mock()
        mock_result.total_posts = 100  # Will be sampled (50 + 50 from each type)
        mock_result.metadata = None
        mock_strands_agent.structured_output_async = AsyncMock(return_value=mock_result)
        
        import asyncio
        result = asyncio.run(agent.parse_multi_type_instagram_export(large_export, export_info))
        
        # Verify metadata accuracy
        metadata = result.metadata
        assert metadata['total_items_available'] == 225  # 150 + 75 (actual counts)
        assert metadata['total_items_processed'] == 100  # Sampled count sent to AI (50 per type)
        assert metadata['sampled_items_analyzed'] == metadata['total_items_processed']
        assert metadata['sample_size_per_type'] == 50  # Medium dataset sampling
        assert metadata['data_types_analyzed'] == ['saved_posts', 'liked_posts']
        assert metadata['analysis_type'] == 'multi_type_consolidated'
        assert metadata['debug_mode'] == True
    
    @pytest.mark.unit
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key-123'})
    @patch('instagram_parser.boto3')
    def test_export_info_preservation(self, mock_boto3, mock_strands_agent):
        """Test that export info is preserved in metadata."""
        agent = InstagramParserAgent()
        agent.agent = mock_strands_agent
        
        export_info = {
            'dataTypes': ['saved_posts'],
            'extractedAt': '2025-01-15T14:30:00Z',
            'exportFolder': 'instagram-testuser-2025-01-15-abc123/'
        }
        
        simple_export = {
            'saved_posts': {'saved_saved_media': [{'title': 'test_user'}]}
        }
        
        mock_result = Mock()
        mock_result.total_posts = 1
        mock_result.metadata = None
        mock_strands_agent.structured_output_async = AsyncMock(return_value=mock_result)
        
        import asyncio
        result = asyncio.run(agent.parse_multi_type_instagram_export(simple_export, export_info))
        
        # Verify export info is preserved
        assert result.metadata['export_info'] == export_info


class TestDataTransformation:
    """Test Instagram data transformation to InstagramPost objects."""
    
    @pytest.mark.unit
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key-123'})
    @patch('instagram_parser.boto3')
    def test_saved_posts_transformation(self, mock_boto3, mock_strands_agent):
        """Test transformation of saved_posts to InstagramPost objects."""
        agent = InstagramParserAgent()
        agent.agent = mock_strands_agent
        
        saved_posts_data = {
            'saved_posts': {
                'saved_saved_media': [
                    {
                        'title': 'fitness_user',
                        'string_map_data': {
                            'Saved on': {
                                'href': 'https://www.instagram.com/reel/fitness123/',
                                'timestamp': 1733969519
                            }
                        }
                    }
                ]
            }
        }
        export_info = {
            'dataTypes': ['saved_posts'],
            'extractedAt': '2025-01-15T10:30:00Z'
        }
        
        mock_result = Mock()
        mock_result.total_posts = 1
        mock_result.metadata = None
        mock_strands_agent.structured_output_async = AsyncMock(return_value=mock_result)
        
        import asyncio
        result = asyncio.run(agent.parse_multi_type_instagram_export(saved_posts_data, export_info))
        
        # Verify transformation occurred
        mock_strands_agent.structured_output_async.assert_called_once()
        call_args = mock_strands_agent.structured_output_async.call_args
        
        # The prompt should contain processed post data
        prompt = call_args[1]['prompt']
        assert 'fitness_user' in prompt
        assert 'reel' in prompt.lower()  # Should detect media type
    
    @pytest.mark.unit
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key-123'})
    @patch('instagram_parser.boto3')
    def test_multi_type_interaction_types(self, mock_boto3, mock_strands_agent):
        """Test that different interaction types are properly identified."""
        agent = InstagramParserAgent()
        agent.agent = mock_strands_agent
        
        multi_type_data = {
            'saved_posts': {'saved_saved_media': [{'title': 'saved_user'}]},
            'liked_posts': {'likes_media_likes': [{'title': 'liked_user'}]},
            'comments': {'comments_media_comments': [{
                'string_map_data': {
                    'Comment': {'value': 'Great post!'},
                    'Media Owner': {'value': 'commented_user'},
                    'Time': {'timestamp': 1733969519}
                }
            }]},
            'following': {'relationships_following': [{
                'string_list_data': [{'value': 'following_user', 'timestamp': 1733969519}]
            }]}
        }
        export_info = {
            'dataTypes': ['saved_posts', 'liked_posts', 'comments', 'following'],
            'extractedAt': '2025-01-15T10:30:00Z'
        }
        
        mock_result = Mock()
        mock_result.total_posts = 4
        mock_result.metadata = None
        mock_strands_agent.structured_output_async = AsyncMock(return_value=mock_result)
        
        import asyncio
        result = asyncio.run(agent.parse_multi_type_instagram_export(multi_type_data, export_info))
        
        # Verify all interaction types are processed
        call_args = mock_strands_agent.structured_output_async.call_args
        prompt = call_args[1]['prompt']
        
        # Should contain all interaction types
        assert 'saved' in prompt.lower()
        assert 'liked' in prompt.lower()  
        assert 'commented' in prompt.lower()
        assert 'following' in prompt.lower()


class TestDynamoDBIntegration:
    """Test DynamoDB integration for saving analysis results."""
    
    @pytest.mark.unit
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key-123', 'CONTENT_TABLE': 'test-table', 'CONTENT_BUCKET': 'test-bucket'})
    @patch('instagram_parser.boto3')
    def test_save_analysis_result_success(self, mock_boto3):
        """Test successful saving of analysis results to DynamoDB."""
        agent = InstagramParserAgent()
        
        # Mock DynamoDB and S3
        mock_dynamodb = Mock()
        mock_s3 = Mock()
        mock_table = Mock()
        
        # Set up the mock chain properly
        agent.dynamodb = mock_dynamodb  
        agent.s3 = mock_s3
        mock_dynamodb.Table.return_value = mock_table
        
        # Create analysis result
        analysis_result = InstagramAnalysisResult(
            total_posts=5,
            categories=[],
            insights=[],
            top_authors=[],
            date_range={'earliest': '2025-01-15', 'latest': '2025-01-15'},
            summary='Test analysis',
            metadata={'test': 'data'}
        )
        
        import asyncio
        success = asyncio.run(agent.save_analysis_result('test-content-123', analysis_result))
        
        # Verify DynamoDB update was called
        mock_table.update_item.assert_called_once()
        update_call = mock_table.update_item.call_args
        
        # Verify S3 save was called
        mock_s3.put_object.assert_called_once()
        s3_call = mock_s3.put_object.call_args
        
        assert success == True
        assert update_call[1]['Key']['contentId'] == 'test-content-123'
        assert ':status' in update_call[1]['ExpressionAttributeValues']
        assert update_call[1]['ExpressionAttributeValues'][':status'] == 'completed'
    
    @pytest.mark.unit
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key-123', 'CONTENT_TABLE': 'test-table', 'CONTENT_BUCKET': 'test-bucket'})
    @patch('instagram_parser.boto3')
    def test_decimal_conversion_for_dynamodb(self, mock_boto3):
        """Test that float values are converted to Decimal for DynamoDB."""
        agent = InstagramParserAgent()
        
        # Mock DynamoDB
        mock_dynamodb = Mock()
        mock_s3 = Mock()
        mock_table = Mock()
        
        # Set up the mock chain properly
        agent.dynamodb = mock_dynamodb
        agent.s3 = mock_s3
        mock_dynamodb.Table.return_value = mock_table
        
        # Create analysis result with float values
        analysis_result = InstagramAnalysisResult(
            total_posts=5,
            categories=[ContentCategory(name='Test', confidence=0.85, reasoning='Test')],
            insights=[ContentInsight(type='test', description='Test', evidence=['test'], relevance_score=0.75)],
            top_authors=[],
            date_range={'earliest': '2025-01-15', 'latest': '2025-01-15'},
            summary='Test analysis'
        )
        
        import asyncio
        success = asyncio.run(agent.save_analysis_result('test-content-123', analysis_result))
        
        # Verify DynamoDB was called
        mock_table.update_item.assert_called_once()
        update_call = mock_table.update_item.call_args
        
        # Check that analysis data contains Decimal values, not floats
        analysis_data = update_call[1]['ExpressionAttributeValues'][':analysis']
        
        # Find float values that should be converted
        def find_decimals(obj):
            decimals = []
            if isinstance(obj, dict):
                for v in obj.values():
                    decimals.extend(find_decimals(v))
            elif isinstance(obj, list):
                for item in obj:
                    decimals.extend(find_decimals(item))
            elif isinstance(obj, Decimal):
                decimals.append(obj)
            return decimals
        
        decimal_values = find_decimals(analysis_data)
        assert len(decimal_values) > 0  # Should have converted some floats to Decimals
        assert success == True


@pytest.mark.slow
@pytest.mark.requires_api
class TestRealAIIntegration:
    """Test real AI integration with minimal data (cost-effective)."""
    
    @pytest.mark.unit
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key-123'})
    @patch('instagram_parser.boto3')
    def test_real_anthropic_api_integration(self, mock_boto3):
        """Test real Anthropic API call with minimal data."""
        # Skip if no real API key or in CI environment
        real_api_key = os.environ.get('REAL_ANTHROPIC_API_KEY')
        if not real_api_key or os.environ.get('CI'):
            pytest.skip("Skipping real API test - no API key or in CI environment")
        
        # Use real API key for this test
        with patch.dict(os.environ, {'ANTHROPIC_API_KEY': real_api_key}):
            agent = InstagramParserAgent()
            
            # Use minimal test data (3 posts to minimize cost)
            minimal_data = {
                'saved_posts': {
                    'saved_saved_media': [
                        {
                            'title': 'fitness_motivation',
                            'string_map_data': {
                                'Saved on': {
                                    'href': 'https://www.instagram.com/reel/fitness123/',
                                    'timestamp': 1733969519
                                }
                            }
                        },
                        {
                            'title': 'coding_tutorial',
                            'string_map_data': {
                                'Saved on': {
                                    'href': 'https://www.instagram.com/p/coding456/',
                                    'timestamp': 1733972519
                                }
                            }
                        },
                        {
                            'title': 'travel_inspiration',
                            'string_map_data': {
                                'Saved on': {
                                    'href': 'https://www.instagram.com/p/travel789/',
                                    'timestamp': 1733975519
                                }
                            }
                        }
                    ]
                }
            }
            export_info = {
                'dataTypes': ['saved_posts'],
                'extractedAt': '2025-01-15T14:00:00Z'
            }
            
            import asyncio
            # This will make a real API call
            result = asyncio.run(agent.parse_multi_type_instagram_export(minimal_data, export_info))
            
            # Verify real AI response
            assert result is not None
            assert isinstance(result, InstagramAnalysisResult)
            assert result.total_posts >= 0
            assert result.summary is not None
            assert len(result.summary) > 0
            
            # Verify metadata from real processing
            assert result.metadata is not None
            assert result.metadata['total_items_processed'] == 3
            assert result.metadata['data_types_analyzed'] == ['saved_posts']


class TestBoundaryConditions:
    """Test boundary conditions and edge cases."""
    
    @pytest.mark.unit
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key-123'})
    @patch('instagram_parser.boto3')
    def test_exactly_20_items_boundary(self, mock_boto3, mock_strands_agent):
        """Test the 20-item boundary condition for sampling logic."""
        agent = InstagramParserAgent()
        agent.agent = mock_strands_agent
        
        # Exactly 20 items total
        boundary_export = {
            'saved_posts': {'saved_saved_media': [{'title': f'user_{i}'} for i in range(20)]}
        }
        export_info = {
            'dataTypes': ['saved_posts'],
            'extractedAt': '2025-01-15T10:30:00Z'
        }
        
        mock_result = Mock()
        mock_result.total_posts = 20
        mock_result.metadata = None
        mock_strands_agent.structured_output_async = AsyncMock(return_value=mock_result)
        
        import asyncio
        result = asyncio.run(agent.parse_multi_type_instagram_export(boundary_export, export_info))
        
        # At 20 items, should use the small dataset logic
        assert result.metadata['total_items_available'] == 20
        assert result.metadata['sample_size_per_type'] >= 10  # Should be more than fallback minimum
    
    @pytest.mark.unit
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key-123'})
    @patch('instagram_parser.boto3')
    def test_exactly_500_items_boundary(self, mock_boto3, mock_strands_agent):
        """Test the 500-item boundary condition for sampling logic."""
        agent = InstagramParserAgent()
        agent.agent = mock_strands_agent
        
        # Exactly 500 items total
        boundary_export = {
            'saved_posts': {'saved_saved_media': [{'title': f'user_{i}'} for i in range(500)]}
        }
        export_info = {
            'dataTypes': ['saved_posts'],
            'extractedAt': '2025-01-15T10:30:00Z'
        }
        
        mock_result = Mock()
        mock_result.total_posts = 100  # Will be sampled
        mock_result.metadata = None
        mock_strands_agent.structured_output_async = AsyncMock(return_value=mock_result)
        
        import asyncio
        result = asyncio.run(agent.parse_multi_type_instagram_export(boundary_export, export_info))
        
        # At 500 items, should trigger large dataset sampling
        assert result.metadata['total_items_available'] == 500
        assert result.metadata['sample_size_per_type'] == 50  # Large dataset sampling
    
    @pytest.mark.unit
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key-123'})
    @patch('instagram_parser.boto3')
    def test_exactly_501_items_boundary(self, mock_boto3, mock_strands_agent):
        """Test just over the 500-item boundary triggers max sampling."""
        agent = InstagramParserAgent()
        agent.agent = mock_strands_agent
        
        # Just over 500 items
        boundary_export = {
            'saved_posts': {'saved_saved_media': [{'title': f'user_{i}'} for i in range(501)]}
        }
        export_info = {
            'dataTypes': ['saved_posts'],
            'extractedAt': '2025-01-15T10:30:00Z'
        }
        
        mock_result = Mock()
        mock_result.total_posts = 100  # Will be sampled to max
        mock_result.metadata = None
        mock_strands_agent.structured_output_async = AsyncMock(return_value=mock_result)
        
        import asyncio
        result = asyncio.run(agent.parse_multi_type_instagram_export(boundary_export, export_info))
        
        # Over 500 items should trigger maximum sampling
        assert result.metadata['total_items_available'] == 501
        assert result.metadata['sample_size_per_type'] == 100  # Maximum sampling