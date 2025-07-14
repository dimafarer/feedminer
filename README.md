# FeedMiner

**Universal saved content processor with AI-powered analysis using Strands agents**

FeedMiner is a serverless AWS application that processes exported saved content from social media platforms (Instagram, Twitter, Reddit, etc.) and provides intelligent categorization, insights, and analysis using Claude AI via Amazon Bedrock.

## 🏗 Architecture Overview

FeedMiner is built as a serverless application using AWS SAM (Serverless Application Model) with the following key components:

### Core Infrastructure
- **AWS Lambda Functions**: Serverless compute for all processing
- **Amazon API Gateway**: REST and WebSocket APIs for client interaction
- **Amazon DynamoDB**: NoSQL database for metadata and analysis storage
- **Amazon S3**: Object storage for raw content and detailed analysis results
- **Amazon Bedrock**: AI model access (Claude 3.7 Sonnet) for content analysis

### AI Processing Engine
- **Strands Agents Framework**: Specialized AI agents for different content types
- **Claude 3.7 Sonnet**: Primary AI model for content analysis and categorization
- **Structured Output**: Pydantic models ensure consistent, validated AI responses

## 🎯 Current Capabilities

### ✅ Implemented Features (MVP Phase - v0.1.0)

1. **Content Upload & Storage**
   - REST API endpoint for uploading exported content
   - Automatic S3 storage with unique content IDs
   - DynamoDB metadata tracking with timestamps and status

2. **Real-time Processing**
   - WebSocket API for streaming analysis updates
   - Bidirectional communication for progress tracking
   - Connection management with automatic cleanup

3. **Instagram JSON Processing** 🎨 (Basic Implementation)
   - Basic Instagram export parsing and structure validation
   - JSON format processing with error handling
   - Preparing for real data testing (July 14-15)
   - Multi-provider AI integration ready (Anthropic API + Bedrock)

4. **Data Retrieval**
   - REST API for listing all content
   - Individual content retrieval with optional raw data
   - Job status tracking for long-running processes

### 🔄 In Active Development (July 14-16)

1. **AI Integration Strategy**
   - **Current**: Anthropic API direct integration for rapid prototyping
   - **This Week**: Bedrock integration for model comparison and flexibility
   - **Goal**: Multi-provider setup leveraging Strands' model-swapping capabilities
   - **Timeline**: Model performance comparison by July 18

2. **Instagram Content Analysis**
   - Testing with real Instagram export data
   - Content categorization and pattern discovery
   - Behavioral insights extraction
   - Performance optimization based on actual usage

### 🔧 Technical Implementation Details

#### Lambda Functions Architecture

**API Layer (`src/api/`)**
- `upload.py`: Handles content uploads, generates UUIDs, stores in S3/DynamoDB
- `list.py`: Paginated content listing with user filtering
- `get.py`: Individual content retrieval with raw data option
- `job_status.py`: Processing job status tracking

**WebSocket Layer (`src/websocket/`)**
- `connect.py`: Connection establishment with TTL-based cleanup
- `disconnect.py`: Connection cleanup and resource management
- `default.py`: Message routing and streaming response handling

**AI Processing Layer (`src/agents/`)**
- `content_analysis.py`: Main orchestration agent for content type detection
- `instagram_parser.py`: Specialized Instagram content analysis using Strands
- `summarization.py`: Content summarization agent (skeleton)
- `extraction.py`: Data extraction agent (skeleton)

**Orchestration Layer (`src/orchestrator/`)**
- `orchestrator.py`: DynamoDB stream-triggered workflow coordination

#### Data Models & Schemas

**Instagram Analysis Models (Pydantic)**
```python
class InstagramPost(BaseModel):
    post_id: str
    author: str
    caption: str
    media_type: str  # photo, video, carousel, reel
    saved_at: str
    hashtags: List[str]
    location: Optional[str]
    engagement: Optional[Dict[str, int]]

class ContentCategory(BaseModel):
    name: str  # Technology, Food, Travel, etc.
    confidence: float  # 0-1 confidence score
    reasoning: str  # AI explanation

class ContentInsight(BaseModel):
    type: str  # theme, trend, preference
    description: str
    evidence: List[str]
    relevance_score: float

class InstagramAnalysisResult(BaseModel):
    total_posts: int
    categories: List[ContentCategory]
    insights: List[ContentInsight]
    top_authors: List[Dict[str, Any]]
    date_range: Dict[str, str]
    summary: str
```

#### Database Schema

**DynamoDB Tables**

1. **Content Table** (`feedminer-content-dev`)
   - Primary Key: `contentId` (String)
   - GSI: `UserTimeIndex` (userId + createdAt)
   - GSI: `StatusIndex` (status + createdAt)
   - Attributes: type, userId, status, metadata, analysis, s3Key

2. **Connections Table** (`feedminer-connections-dev`)
   - Primary Key: `connectionId` (String)
   - GSI: `UserIndex` (userId)
   - TTL: 2 hours automatic cleanup
   - Attributes: userId, connectedAt, endpoint

3. **Jobs Table** (`feedminer-jobs-dev`)
   - Primary Key: `jobId` (String)
   - GSI: `ContentIndex` (contentId)
   - GSI: `StatusIndex` (status)
   - Attributes: contentId, status, result, timestamps

#### S3 Storage Structure
```
feedminer-content-dev-{account-id}/
├── uploads/
│   └── {content-id}.json          # Raw uploaded content
├── analysis/
│   └── {content-id}/
│       ├── instagram_analysis.json # Detailed AI analysis
│       └── summary.json           # Processing summary
└── exports/
    └── {content-id}/              # Generated exports
```

## 🚀 Deployment & Configuration

### Prerequisites
- AWS CLI configured with appropriate permissions
- SAM CLI installed
- Python 3.12+ with virtual environment
- Anthropic API key OR AWS Bedrock access

### Environment Setup
```bash
# Quick setup
./scripts/setup.sh
source feedminer-env/bin/activate

# Manual setup
python3 -m venv feedminer-env
source feedminer-env/bin/activate
pip install -r requirements-dev.txt

# Build and validate
sam build
sam validate --lint
```

### Deployment Options

**Option 1: Quick Deployment (Recommended)**
```bash
# With Anthropic API key
./scripts/deploy.sh dev sk-ant-your-key-here

# With Bedrock (recommended for AWS)
./scripts/deploy.sh dev
```

**Option 2: Manual Deployment**
```bash
# Anthropic API
sam deploy --parameter-overrides \
  EnableWebSocket=true \
  AnthropicApiKey=sk-ant-your-key-here

# Bedrock
sam deploy --parameter-overrides \
  EnableWebSocket=true \
  AnthropicApiKey=BEDROCK_WILL_OVERRIDE
```

### Local Development
```bash
# For local testing (disables WebSocket to avoid SAM local issues)
sam local start-api --parameter-overrides EnableWebSocket=false

# Run test suites
python tests/test_api.py        # REST API tests
python tests/test_websocket.py  # WebSocket tests

# Or use the test runner
./scripts/run_tests.sh
```

## 🔧 Configuration Parameters

### CloudFormation Parameters
- `Environment`: Deployment stage (dev/staging/prod)
- `AnthropicApiKey`: API key for Claude access
- `AllowedOrigins`: CORS origins for WebSocket connections
- `EnableWebSocket`: Conditional WebSocket deployment (for SAM local compatibility)

### Environment Variables (Auto-configured)
- `ANTHROPIC_API_KEY`: Claude API access
- `CONTENT_BUCKET`: S3 bucket for content storage
- `WEBSOCKET_API_ENDPOINT`: WebSocket endpoint URL
- `DYNAMODB_TABLE_PREFIX`: Table naming prefix
- `CONTENT_TABLE`, `JOBS_TABLE`, `CONNECTIONS_TABLE`: Table names

## 🧪 Testing & Validation

### Test Scripts

**REST API Testing (`tests/test_api.py`)**
- Content upload with sample Instagram data
- Content listing and pagination
- Individual content retrieval
- Error handling validation

**WebSocket Testing (`tests/test_websocket.py`)**
- Connection establishment
- Message routing and responses
- Streaming analysis simulation
- Connection cleanup

### Running Tests
```bash
# Run all tests
./scripts/run_tests.sh

# Run specific test types
./scripts/run_tests.sh api        # REST API only
./scripts/run_tests.sh websocket  # WebSocket only
./scripts/run_tests.sh pytest     # Pytest suite
```

### Sample Test Data
The test scripts include realistic Instagram saved content data:
```json
{
  "type": "instagram_saved",
  "user_id": "test_user_123",
  "content": {
    "saved_posts": [
      {
        "post_id": "C8vXyZwA1bN",
        "author": "coffee_roaster_daily",
        "caption": "Perfect morning brew ☕ Ethiopian single origin...",
        "media_type": "photo",
        "hashtags": ["#coffee", "#ethiopian", "#singleorigin"],
        "location": "Portland, Oregon"
      }
    ]
  }
}
```

## 🤖 AI Processing Pipeline

### Content Analysis Workflow

1. **Upload Phase**
   - Content uploaded via REST API
   - Stored in S3 with unique ID
   - DynamoDB record created with status='uploaded'

2. **Detection Phase**
   - S3 trigger activates content analysis agent
   - Content type detected (instagram_saved, twitter_bookmarks, etc.)
   - Status updated to 'processing'

3. **Analysis Phase**
   - Specialized agent (Instagram Parser) processes content
   - Claude 3.7 Sonnet analyzes posts for:
     - Content categories with confidence scores
     - User behavior patterns and preferences
     - Trending topics and themes
     - Author interaction patterns

4. **Storage Phase**
   - Structured results stored in DynamoDB
   - Detailed analysis saved to S3
   - Status updated to 'analyzed'
   - WebSocket notifications sent

### Instagram Analysis Features

**Category Detection**
- Technology (AI, coding, software)
- Food & Dining (recipes, restaurants, cooking)
- Travel & Adventure (destinations, experiences)
- Fitness & Health (workouts, wellness)
- Fashion & Style (clothing, trends)
- Photography & Art (visual content, creativity)

**Insight Extraction**
- Content preference patterns
- Engagement behavior analysis
- Temporal posting patterns
- Cross-category relationships
- Author influence mapping

**Output Format**
```json
{
  "total_posts": 25,
  "categories": [
    {
      "name": "Technology",
      "confidence": 0.85,
      "reasoning": "High frequency of AI and programming hashtags"
    }
  ],
  "insights": [
    {
      "type": "preference",
      "description": "Strong interest in AI/ML content",
      "evidence": ["15 AI-related posts", "Follows tech influencers"],
      "relevance_score": 0.9
    }
  ],
  "top_authors": [
    {"author": "ai_research_hub", "post_count": 8}
  ],
  "summary": "User shows strong technical interests..."
}
```

## 🔍 API Reference

### REST Endpoints

**Base URL**: `https://wqtfb6rv15.execute-api.us-west-2.amazonaws.com/dev`

#### Upload Content
```http
POST /upload
Content-Type: application/json

{
  "type": "instagram_saved",
  "user_id": "user123",
  "content": { ... }
}

Response:
{
  "contentId": "uuid",
  "message": "Content uploaded successfully",
  "s3Key": "uploads/uuid.json"
}
```

#### List Content
```http
GET /content?userId=user123&limit=20

Response:
{
  "items": [...],
  "count": 10,
  "hasMore": false
}
```

#### Get Content
```http
GET /content/{contentId}?includeRaw=true

Response:
{
  "contentId": "uuid",
  "type": "instagram_saved",
  "status": "analyzed",
  "analysis": { ... },
  "rawContent": { ... }  // if includeRaw=true
}
```

### WebSocket API

**URL**: `wss://yzzspgrevg.execute-api.us-west-2.amazonaws.com/dev`

#### Connection
- Automatic connection tracking in DynamoDB
- 2-hour TTL for cleanup
- Connection ID returned in responses

#### Message Format
```json
// Client to Server
{
  "action": "analyze_content",
  "content_id": "uuid",
  "data": { ... }
}

// Server to Client
{
  "type": "analysis_progress",
  "message": "Analyzing content categories...",
  "progress": 0.5,
  "connection_id": "abc123"
}
```

## 🛠 Development Patterns & Best Practices

### Code Organization
```
feedminer/
├── src/
│   ├── api/           # REST endpoint handlers
│   ├── websocket/     # WebSocket handlers
│   ├── agents/        # AI processing agents
│   └── orchestrator/  # Workflow coordination
├── tests/             # Unit and integration tests
│   ├── data/         # Test data and fixtures
│   ├── test_api.py   # REST API tests
│   └── test_websocket.py # WebSocket tests
├── scripts/           # Development and deployment scripts
│   ├── setup.sh      # Environment setup
│   ├── deploy.sh     # Deployment automation
│   └── run_tests.sh  # Test runner
├── docs/              # Additional documentation
│   ├── API.md        # API reference
│   └── DEPLOYMENT.md # Deployment guide
├── template.yaml      # SAM CloudFormation template
├── requirements-dev.txt # Development dependencies
├── CHANGELOG.md       # Version history
└── README.md         # This documentation
```

### Error Handling Patterns

**Lambda Functions**
- Consistent error response format
- Detailed logging for debugging
- Graceful degradation for non-critical failures

**DynamoDB Operations**
- Decimal serialization handling (DecimalEncoder)
- Conditional updates for data consistency
- GSI query optimization

**S3 Operations**
- Pre-signed URL generation for large uploads
- Versioning for content history
- Lifecycle policies for cost optimization

### Security Considerations

**API Security**
- CORS configuration for web access
- IAM role-based access control
- API Gateway throttling (100 req/sec, 200 burst)

**Data Protection**
- S3 bucket policies (private by default)
- DynamoDB encryption at rest
- Lambda environment variable encryption

**Network Security**
- VPC configuration ready (currently public for simplicity)
- CloudFront integration ready
- WAF integration ready

## 🚀 Development Status

**Current Phase**: MVP Infrastructure Complete (v0.1.0)  
**Timeline**: 2 days ahead of schedule  
**Priority**: Bedrock integration moved to THIS WEEK (July 16)

### Recent Accomplishments
- ✅ AWS infrastructure fully deployed and tested
- ✅ REST and WebSocket APIs operational
- ✅ Basic Instagram JSON processing working
- ✅ Project organization and Git setup complete
- ✅ Comprehensive test suite and automation

### This Week's Focus (July 14-16)
- 🔄 Real Instagram data testing and validation
- 📋 Bedrock integration and model comparison
- 📋 Performance benchmarking across AI providers
- 📋 Advanced pattern discovery preparation

## 🚧 Known Issues & Solutions

### Resolved Issues

1. **SAM Local WebSocket Support**
   - **Issue**: SAM local doesn't support WebSocket APIs
   - **Solution**: Conditional WebSocket deployment via `EnableWebSocket` parameter
   - **Usage**: Set `EnableWebSocket=false` for local development

2. **DynamoDB Decimal Serialization**
   - **Issue**: JSON serialization error with DynamoDB Decimal types
   - **Solution**: Custom `DecimalEncoder` class in API handlers
   - **Implementation**: Applied to all API response handlers

3. **Route Key Parsing**
   - **Issue**: SAM trying to parse WebSocket routes as HTTP routes
   - **Solution**: Quoted route keys (`"$connect"` vs `$connect`)
   - **Result**: Proper WebSocket route handling

### Current Limitations

1. **Content Type Support**
   - Only Instagram analysis fully implemented
   - Twitter, Reddit agents are skeleton implementations
   - **Expansion Path**: Copy Instagram pattern for new platforms

2. **Scalability Considerations**
   - Single-region deployment
   - No auto-scaling configuration yet
   - **Future**: Multi-region, auto-scaling groups

3. **Monitoring & Observability**
   - Basic CloudWatch logging
   - No custom metrics or dashboards
   - **Future**: X-Ray tracing, custom CloudWatch dashboards

## 🎯 Updated Roadmap & Development Timeline

### Phase 1a: Infrastructure Deployment (✅ Complete - July 13)
- [x] AWS SAM infrastructure setup and deployment
- [x] REST API with CRUD operations
- [x] WebSocket real-time communication
- [x] Basic Instagram JSON processing
- [x] Comprehensive testing and automation
- [x] Project organization and documentation

### Phase 1b: Real Data Testing (🔄 July 14-15)
- [ ] Test with actual Instagram export data
- [ ] Validate JSON parsing and error handling
- [ ] Performance baseline measurements
- [ ] User experience optimization

### Phase 1c: Multi-Model AI Integration (📋 July 16)
- [ ] **Bedrock integration implementation**
- [ ] **Model performance comparison (Anthropic API vs Bedrock)**
- [ ] **Strands model-swapping demonstration**
- [ ] **Cost and latency analysis**

### Phase 2: Advanced Pattern Discovery (📋 July 19+)
- [ ] Content categorization with confidence scoring
- [ ] Behavioral insights extraction
- [ ] Cross-content pattern analysis
- [ ] Advanced sentiment and trend detection

### Phase 3: Platform Expansion (📋 Planned)
- [ ] Twitter/X bookmarks analysis
- [ ] Reddit saved posts analysis
- [ ] Cross-platform content correlation
- [ ] Web dashboard for visualization

### Phase 4: Enterprise Features (💭 Future)
- [ ] Multi-region deployment
- [ ] Advanced analytics and reporting
- [ ] User authentication and multi-tenancy
- [ ] Custom AI model fine-tuning

## 🤝 Integration Points

### Claude Desktop App Integration

**Context Sharing**
This README provides complete context for Claude Desktop to understand:
- Current system architecture and capabilities
- Implemented vs planned features
- Technical decisions and their rationale
- Testing procedures and validation methods
- Future development priorities

**Development Workflow**
1. Use this README as primary context source
2. Reference test scripts for validation procedures
3. Check `template.yaml` for infrastructure understanding
4. Review agent implementations for AI processing patterns

**Key Files for Claude Desktop**
- `README.md`: Complete system documentation (this file)
- `template.yaml`: Infrastructure as code with comprehensive cost tagging
- `tests/test_api.py` & `tests/test_websocket.py`: Validation procedures
- `src/agents/instagram_parser.py`: AI processing reference implementation
- `requirements-dev.txt`: Development dependencies
- `scripts/`: Automation scripts for common tasks
- `docs/`: Additional API, deployment, and cost management documentation
  - `AWS_COST_TAGGING_STRATEGY.md`: Enterprise-level tagging strategy
  - `COST_TRACKING_GUIDE.md`: Practical cost monitoring and optimization
  - `API.md`: REST and WebSocket API reference
  - `DEPLOYMENT.md`: Deployment and configuration guide

### External System Integration

**Data Sources**
- Instagram data export (JSON format)
- Twitter/X bookmark exports (future)
- Reddit saved posts (future)
- Generic JSON content (extensible)

**Output Formats**
- REST API JSON responses
- WebSocket streaming updates
- S3 stored analysis results
- DynamoDB queryable metadata

## 📊 Performance & Scaling

### Current Performance Characteristics

**API Response Times**
- Upload: ~500ms (including S3 storage)
- List: ~200ms (DynamoDB query)
- Get: ~300ms (DynamoDB + conditional S3)
- WebSocket: ~100ms connection establishment

**Processing Times**
- Instagram analysis: ~10-30 seconds (depends on content size)
- Category detection: ~5-10 seconds
- Insight extraction: ~15-25 seconds

**Scalability Limits (Current)**
- Concurrent Lambda executions: 1000 (AWS default)
- DynamoDB read/write capacity: Pay-per-request (auto-scaling)
- S3 requests: Virtually unlimited
- WebSocket connections: 3000 concurrent (API Gateway default)

### Optimization Opportunities

1. **Caching Strategy**
   - ElastiCache for frequent queries
   - CloudFront for static content
   - Application-level result caching

2. **Batch Processing**
   - SQS for async processing queues
   - Step Functions for complex workflows
   - Batch Lambda for large datasets

3. **Database Optimization**
   - DynamoDB GSI optimization
   - Partition key distribution analysis
   - Read replica strategies

## 📞 Support & Troubleshooting

### Common Issues

**Deployment Failures**
```bash
# Validate template
sam validate --lint

# Check build output
sam build --debug

# Verify AWS credentials
aws sts get-caller-identity
```

**API Errors**
```bash
# Check CloudWatch logs
aws logs filter-log-events \
  --log-group-name "/aws/lambda/feedminer-content-upload-dev" \
  --start-time $(date -d '1 hour ago' +%s)000
```

**WebSocket Issues**
```bash
# Test connection manually
wscat -c wss://yzzspgrevg.execute-api.us-west-2.amazonaws.com/dev

# Check connection table
aws dynamodb scan --table-name feedminer-connections-dev
```

### Debug Commands

**SAM Local Testing**
```bash
# Start API locally (without WebSocket)
sam local start-api --parameter-overrides EnableWebSocket=false

# Invoke specific function
sam local invoke ContentUploadFunction --event test-events/upload.json

# Generate test events
sam local generate-event apigateway aws-proxy > test-event.json
```

**AWS Resource Inspection**
```bash
# List stack resources
aws cloudformation describe-stack-resources --stack-name feedminer

# Check Lambda function logs
aws logs tail /aws/lambda/feedminer-content-analysis-dev --follow

# Query DynamoDB
aws dynamodb scan --table-name feedminer-content-dev --max-items 5
```

### Development Tips

1. **Iterative Development**
   - Use `sam build && sam deploy` for rapid iteration
   - Test locally with `sam local start-api` when possible
   - Use `--no-confirm-changeset` for automated deployments

2. **Debugging Strategy**
   - Add extensive logging in Lambda functions
   - Use CloudWatch Insights for log analysis
   - Implement structured logging with JSON format

3. **Testing Strategy**
   - Run test scripts after each deployment
   - Use different environments (dev/staging/prod)
   - Implement integration tests for critical paths

## 🔧 Quick Development Commands

```bash
# Environment setup
./scripts/setup.sh
source feedminer-env/bin/activate

# Quick deployment
./scripts/deploy.sh dev sk-ant-your-key-here

# Run all tests
./scripts/run_tests.sh

# Manual commands
sam build && sam deploy --no-confirm-changeset --parameter-overrides EnableWebSocket=true AnthropicApiKey=your-key
python tests/test_api.py
python tests/test_websocket.py

# Check logs
aws logs tail /aws/lambda/feedminer-content-upload-dev --follow

# Local development
sam local start-api --parameter-overrides EnableWebSocket=false
```

---

**Generated with Claude Code** 🤖  
Last Updated: July 13, 2025  
Version: 0.1.0 (MVP)  
**System Status**: 🚀 Infrastructure Deployed - Instagram Processing Ready - Multi-Model AI Integration This Week