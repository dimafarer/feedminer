"""
Pytest configuration and shared fixtures for FeedMiner tests.
"""

import os
import pytest
from unittest.mock import Mock, patch
from moto import mock_aws
import boto3

from tests.unit.fixtures.sample_instagram_data import *
from tests.unit.fixtures.malformed_data import *
from tests.unit.fixtures.aws_responses import *


# Legacy fixtures for existing tests
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
    """Legacy sample Instagram data for existing tests."""
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


# New fixtures for unit testing
@pytest.fixture(scope="session")
def aws_credentials():
    """Mock AWS credentials for testing."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-west-2"


@pytest.fixture(scope="function")
def mock_env_vars():
    """Mock environment variables for Lambda functions."""
    env_vars = get_lambda_environment_variables()
    with patch.dict(os.environ, env_vars):
        yield env_vars


@pytest.fixture(scope="function")
def mock_s3_service(aws_credentials):
    """Mock S3 service using moto."""
    with mock_aws():
        # Create test bucket
        s3_client = boto3.client('s3', region_name='us-west-2')
        s3_client.create_bucket(
            Bucket='feedminer-test-bucket',
            CreateBucketConfiguration={'LocationConstraint': 'us-west-2'}
        )
        yield s3_client


@pytest.fixture(scope="function") 
def mock_dynamodb_service(aws_credentials):
    """Mock DynamoDB service using moto."""
    with mock_aws():
        # Create test tables
        dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
        
        # Content table
        content_table = dynamodb.create_table(
            TableName='feedminer-test-content',
            KeySchema=[
                {'AttributeName': 'contentId', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'contentId', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        
        # Jobs table
        jobs_table = dynamodb.create_table(
            TableName='feedminer-test-jobs',
            KeySchema=[
                {'AttributeName': 'jobId', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'jobId', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        
        yield dynamodb


@pytest.fixture(scope="function")
def mock_aws_services(mock_s3_service, mock_dynamodb_service):
    """Combined mock AWS services fixture."""
    return {
        's3': mock_s3_service,
        'dynamodb': mock_dynamodb_service
    }


@pytest.fixture
def sample_complete_export():
    """Complete Instagram export fixture."""
    return get_complete_instagram_export()


@pytest.fixture
def sample_partial_export():
    """Partial Instagram export fixture."""
    return get_partial_instagram_export()


@pytest.fixture
def sample_empty_categories():
    """Empty categories Instagram export fixture."""
    return get_empty_categories_export()


@pytest.fixture
def sample_large_dataset():
    """Large dataset for sampling tests."""
    return get_large_dataset_export()


@pytest.fixture
def malformed_request():
    """Malformed request fixture."""
    return get_missing_required_fields()


@pytest.fixture
def api_gateway_event():
    """API Gateway event fixture."""
    def _create_event(body, method='POST'):
        return get_api_gateway_event(body, method)
    return _create_event


@pytest.fixture
def lambda_context():
    """Lambda context fixture."""
    return get_lambda_context()


@pytest.fixture
def mock_strands_agent():
    """Mock Strands agent for AI testing."""
    mock_agent = Mock()
    
    # Mock successful structured output
    mock_result = Mock()
    mock_result.total_posts = 5
    mock_result.categories = []
    mock_result.insights = []
    mock_result.top_authors = []
    mock_result.date_range = {"earliest": "2025-01-15", "latest": "2025-01-15"}
    mock_result.summary = "Test analysis completed"
    mock_result.metadata = None
    
    mock_agent.structured_output_async.return_value = mock_result
    
    return mock_agent


@pytest.fixture
def mock_strands_failure():
    """Mock Strands agent that fails for error testing."""
    mock_agent = Mock()
    mock_agent.structured_output_async.side_effect = Exception("AI processing failed")
    return mock_agent