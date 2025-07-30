"""
AWS service mock responses for testing.
"""

from datetime import datetime


def get_successful_s3_put_response():
    """Successful S3 put_object response."""
    return {
        'ResponseMetadata': {
            'RequestId': 'test-request-id-123',
            'HTTPStatusCode': 200,
            'HTTPHeaders': {
                'content-type': 'application/json',
                'etag': '"test-etag-123"'
            }
        },
        'ETag': '"test-etag-123"'
    }


def get_successful_dynamodb_put_response():
    """Successful DynamoDB put_item response."""
    return {
        'ResponseMetadata': {
            'RequestId': 'test-dynamo-request-123',
            'HTTPStatusCode': 200
        }
    }


def get_successful_dynamodb_update_response():
    """Successful DynamoDB update_item response."""
    return {
        'ResponseMetadata': {
            'RequestId': 'test-dynamo-update-123', 
            'HTTPStatusCode': 200
        },
        'Attributes': {
            'contentId': 'test-content-id-123',
            'status': 'uploaded',
            'updatedAt': datetime.now().isoformat()
        }
    }


def get_s3_access_denied_error():
    """S3 access denied error response."""
    return {
        'Error': {
            'Code': 'AccessDenied',
            'Message': 'Access Denied'
        },
        'ResponseMetadata': {
            'RequestId': 'test-error-request-123',
            'HTTPStatusCode': 403
        }
    }


def get_dynamodb_throttle_error():
    """DynamoDB throttling error response."""
    return {
        'Error': {
            'Code': 'ProvisionedThroughputExceededException',
            'Message': 'The level of configured provisioned throughput for the table was exceeded'
        },
        'ResponseMetadata': {
            'RequestId': 'test-throttle-request-123',
            'HTTPStatusCode': 400
        }
    }


def get_s3_bucket_not_found_error():
    """S3 bucket not found error."""
    return {
        'Error': {
            'Code': 'NoSuchBucket',
            'Message': 'The specified bucket does not exist'
        },
        'ResponseMetadata': {
            'RequestId': 'test-bucket-error-123',
            'HTTPStatusCode': 404
        }
    }


def get_dynamodb_table_not_found_error():
    """DynamoDB table not found error."""
    return {
        'Error': {
            'Code': 'ResourceNotFoundException',
            'Message': 'Requested resource not found'
        },
        'ResponseMetadata': {
            'RequestId': 'test-table-error-123',
            'HTTPStatusCode': 400
        }
    }


def get_network_timeout_error():
    """Network timeout error."""
    return {
        'Error': {
            'Code': 'RequestTimeout',
            'Message': 'Request timeout'
        },
        'ResponseMetadata': {
            'RequestId': 'test-timeout-123',
            'HTTPStatusCode': 408
        }
    }


def get_lambda_environment_variables():
    """Mock Lambda environment variables."""
    return {
        'CONTENT_BUCKET': 'feedminer-test-bucket',
        'CONTENT_TABLE': 'feedminer-test-content',
        'JOBS_TABLE': 'feedminer-test-jobs',
        'DEBUG_MODE': 'true',
        'ANTHROPIC_API_KEY': 'test-key-123'
    }


def get_api_gateway_event(body, http_method='POST'):
    """Generate API Gateway event structure."""
    return {
        'httpMethod': http_method,
        'body': body,
        'headers': {
            'Content-Type': 'application/json',
            'User-Agent': 'test-user-agent'
        },
        'requestContext': {
            'requestId': 'test-request-context-123',
            'stage': 'test'
        }
    }


def get_lambda_context():
    """Generate Lambda context object."""
    class MockLambdaContext:
        def __init__(self):
            self.function_name = 'test-function'
            self.function_version = '$LATEST'
            self.invoked_function_arn = 'arn:aws:lambda:us-west-2:123456789012:function:test-function'
            self.memory_limit_in_mb = 512
            self.remaining_time_in_millis = lambda: 30000
            self.request_id = 'test-lambda-request-123'
            self.log_group_name = '/aws/lambda/test-function'
            self.log_stream_name = 'test-stream'
            
    return MockLambdaContext()


# Export all fixtures
__all__ = [
    'get_successful_s3_put_response',
    'get_successful_dynamodb_put_response', 
    'get_successful_dynamodb_update_response',
    'get_s3_access_denied_error',
    'get_dynamodb_throttle_error',
    'get_s3_bucket_not_found_error',
    'get_dynamodb_table_not_found_error',
    'get_network_timeout_error',
    'get_lambda_environment_variables',
    'get_api_gateway_event',
    'get_lambda_context'
]