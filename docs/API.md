# FeedMiner API Documentation

**Version**: 0.1.0 (MVP)  
**Status**: Infrastructure Complete - Real Data Testing This Week  
**AI Integration**: Anthropic API (current) + Bedrock (July 16)

## REST API Endpoints

### Base URL
```
https://wqtfb6rv15.execute-api.us-west-2.amazonaws.com/dev
```

### Upload Content
**POST** `/upload`

Upload saved content for processing and analysis.

**Current Status**: Basic JSON processing implemented, real data testing in progress.

**Request Body:**
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

**Note**: Analysis field will be populated once AI processing is implemented (July 16).

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

### 🔄 In Development (July 14-16)
- Real Instagram data processing and validation
- Bedrock AI integration and model comparison
- Advanced error handling and retry logic

### 📋 Coming Soon (July 16+)
- AI-powered content analysis responses
- Category detection and insights
- Streaming analysis via WebSocket

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