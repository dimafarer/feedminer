# FeedMiner API Documentation

**Version**: 0.3.0 (Multi-File Instagram Data Processing - Phase 1)  
**Status**: Production Ready - Complete ZIP Processing Pipeline  
**AI Integration**: Anthropic API + AWS Bedrock with runtime switching  
**Latest Feature**: Multi-file Instagram export ZIP processing with smart sampling

## REST API Endpoints

### Base URL
```
https://wqtfb6rv15.execute-api.us-west-2.amazonaws.com/dev
```

### Upload Content
**POST** `/upload`

Upload saved content for processing and analysis.

**Current Status**: Successfully tested with real Instagram data - supports both native export format and enhanced processing format with goal-oriented analysis.

**Request Body Options:**

*Option 1: Real Instagram Export Format*
```json
{
  "saved_saved_media": [
    {
      "title": "username",
      "string_map_data": {
        "Saved on": {
          "href": "https://www.instagram.com/reel/ABC123/",
          "timestamp": 1733969519
        }
      }
    }
  ]
}
```

*Option 2: FeedMiner Enhanced Format*
```json
{
  "type": "instagram_saved",
  "user_id": "string",
  "content": {
    "saved_posts": [...]
  }
}
```

**Response:**
```json
{
  "contentId": "uuid",
  "message": "Content uploaded successfully",
  "s3Key": "uploads/uuid.json",
  "status": "uploaded",
  "type": "instagram_saved"
}
```

### List Content
**GET** `/content`

**Query Parameters:**
- `userId` (optional): Filter by user ID
- `limit` (optional): Number of items to return (default: 20)

**Response:**
```json
{
  "items": [...],
  "count": 10,
  "hasMore": false
}
```

### Get Content
**GET** `/content/{contentId}`

**Query Parameters:**
- `includeRaw` (optional): Include raw content data

**Response:**
```json
{
  "contentId": "uuid",
  "type": "instagram_saved",
  "status": "uploaded",
  "createdAt": "2025-07-13T10:30:00Z",
  "analysis": null,
  "rawContent": {...}
}
```

**Note**: Analysis field contains results from selected AI provider (Anthropic API or AWS Bedrock).

### Multi-File Upload (NEW v0.3.0)
**POST** `/multi-upload`

Upload Instagram ZIP exports with multiple data types for comprehensive analysis.

**Features:**
- **ZIP Processing**: Automatic extraction of Instagram export archives
- **5 Data Types**: saved_posts, liked_posts, comments, user_posts, following
- **Smart Sampling**: 100 items per category for optimal analysis performance
- **Consolidated Analysis**: Unified insights across all interaction types

**Request Body:**
```json
{
  "type": "instagram_export",
  "dataTypes": ["saved_posts", "liked_posts", "comments", "user_posts", "following"],
  "exportInfo": {
    "exportFolder": "instagram-username-2025-01-15-abc123/",
    "extractedAt": "2025-01-15T10:30:00Z",
    "dataTypes": ["saved_posts", "liked_posts", "comments", "user_posts", "following"]
  },
  "saved_posts": { "saved_saved_media": [...] },
  "liked_posts": { "likes_media_likes": [...] },
  "comments": { "comments_media_comments": [...] },
  "user_posts": [...],
  "following": { "relationships_following": [...] }
}
```

**Response:**
```json
{
  "contentId": "uuid",
  "message": "Instagram export uploaded successfully with 5 data types",
  "s3Key": "uploads/uuid/consolidated.json",
  "status": "uploaded",
  "type": "instagram_export",
  "dataTypes": ["saved_posts", "liked_posts", "comments", "user_posts", "following"],
  "totalItems": 177,
  "dataStructure": {
    "saved_posts": { "count": 35, "s3Key": "uploads/uuid/saved_posts.json" },
    "liked_posts": { "count": 42, "s3Key": "uploads/uuid/liked_posts.json" }
  }
}
```

### Job Status
**GET** `/jobs/{jobId}`

**Response:**
```json
{
  "jobId": "uuid",
  "contentId": "uuid", 
  "status": "completed",
  "result": {...}
}
```

## WebSocket API

### Connection URL
```
wss://yzzspgrevg.execute-api.us-west-2.amazonaws.com/dev
```

### Message Format

**Client to Server:**
```json
{
  "action": "analyze_content",
  "content_id": "uuid",
  "data": {...}
}
```

**Server to Client:**
```json
{
  "type": "analysis_progress",
  "message": "Processing...",
  "progress": 0.5,
  "connection_id": "abc123"
}
```

## Current Implementation Status

**⚠️ Note**: Some documented endpoints are incomplete. See [Incomplete Features](INCOMPLETE_FEATURES.md) for details.

### ✅ Fully Functional
- Content upload and storage (S3 + DynamoDB)
- Content listing with pagination
- Individual content retrieval
- WebSocket connection management
- Multi-provider AI processing (Anthropic + Bedrock)
- Real-time model provider switching
- AI-powered content analysis responses
- Category detection and behavioral insights
- Streaming analysis via WebSocket

### 🆕 New in v0.2.0 (Multi-Model AI Integration)
- **Model Provider Selection**: Choose between Anthropic API and AWS Bedrock at runtime
- **Performance Benchmarking**: Built-in latency and quality comparison between providers
- **Extensible Model Support**: Framework ready for additional Bedrock models
- **Cost Optimization**: Provider switching for cost-effective AI processing

### Analyze with Specific Provider
**POST** `/analyze/{contentId}`

Analyze content using a specific AI provider and model.

**Request Body:**
```json
{
  "provider": "bedrock",
  "model": "anthropic.claude-3-5-sonnet-20241022-v2:0",
  "temperature": 0.7
}
```

**Test Mode** (for contentId = "test"):
```json
{
  "provider": "bedrock",
  "model": "anthropic.claude-3-5-sonnet-20241022-v2:0",
  "prompt": "Custom test prompt"
}
```

**Response:**
```json
{
  "success": true,
  "contentId": "12345",
  "provider": "bedrock",
  "model": "anthropic.claude-3-5-sonnet-20241022-v2:0",
  "response": {
    "content": "AI analysis result...",
    "provider": "bedrock",
    "model": "anthropic.claude-3-5-sonnet-20241022-v2:0",
    "latency_ms": 1037,
    "usage": {
      "input_tokens": 150,
      "output_tokens": 45,
      "total_tokens": 195
    },
    "success": true
  },
  "timestamp": "2025-07-20T20:31:17.334241"
}
```

### Compare Providers
**POST** `/compare/{contentId}`

Compare analysis results across multiple AI providers.

**Request Body:**
```json
{
  "providers": [
    {
      "provider": "anthropic",
      "model": "claude-3-5-sonnet-20241022"
    },
    {
      "provider": "bedrock", 
      "model": "anthropic.claude-3-5-sonnet-20241022-v2:0"
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "contentId": "12345",
  "comparison": {
    "providers": ["anthropic", "bedrock"],
    "results": {
      "anthropic": { "content": "...", "latency_ms": 950 },
      "bedrock": { "content": "...", "latency_ms": 1037 }
    },
    "summary": {
      "fastest_provider": "anthropic",
      "most_cost_effective": "bedrock",
      "quality_comparison": {...}
    }
  }
}
```

## Error Handling

All endpoints return consistent error responses:

```json
{
  "error": "Description of the error",
  "code": "ERROR_CODE",
  "timestamp": "2025-07-13T10:30:00Z"
}
```

Common HTTP status codes:
- `200`: Success
- `400`: Bad Request (invalid input)
- `404`: Not Found
- `500`: Internal Server Error