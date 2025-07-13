# FeedMiner API Documentation

## REST API Endpoints

### Base URL
```
https://wqtfb6rv15.execute-api.us-west-2.amazonaws.com/dev
```

### Upload Content
**POST** `/upload`

Upload saved content for analysis.

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
  "s3Key": "uploads/uuid.json"
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
  "status": "analyzed",
  "analysis": {...},
  "rawContent": {...}
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

## Error Handling

All endpoints return consistent error responses:

```json
{
  "error": "Description of the error"
}
```

Common HTTP status codes:
- `200`: Success
- `400`: Bad Request (invalid input)
- `404`: Not Found
- `500`: Internal Server Error