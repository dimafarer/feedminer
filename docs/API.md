# FeedMiner API Documentation

**Version**: 0.2.0 (Multi-Model AI Integration)  
**Status**: Production Ready - Multi-Provider AI Support  
**AI Integration**: Anthropic API + AWS Bedrock with runtime switching

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