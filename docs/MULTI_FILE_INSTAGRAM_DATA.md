# Multi-File Instagram Data Processing Implementation Plan

**Version**: 1.1  
**Status**: Implementation Phase - Performance Optimization Required  
**Target**: v0.3.0 - Enhanced Instagram Data Support  
**Created**: July 25, 2025  
**Updated**: July 26, 2025

## 🚨 Current Implementation Status (July 26, 2025)

**✅ WORKING COMPONENTS:**
- Multi-upload API endpoint (`src/api/multi_upload.py`) - 452 lines of production code
- ZIP file processing and extraction capabilities ✅
- Category selection UI (user can pick data types) ✅
- Hierarchical S3 storage structure implementation ✅
- Enhanced DynamoDB schema for multi-data-type support ✅
- Frontend ZIP upload detection and processing UI ✅

**❌ FAILING COMPONENT:**
- **Analysis Step**: When user clicks "Analyze" button after data upload
- **Timeout Issue**: Analysis times out after ~1 minute
- **Fallback Behavior**: System defaults to static demo data instead of user's actual data

**🔍 SPECIFIC PROBLEM:**
- Upload + category selection works perfectly
- Analysis pipeline fails on real user data (likely due to dataset size)
- Need to debug with small data subsets first

**🔄 CURRENT FOCUS:**
- Testing with smaller data subsets (5-10 items per category)
- Optimizing processing pipeline for incremental analysis
- Implementing batch processing for large datasets

**📋 NEXT STEPS:**
- Implement chunked processing for large datasets
- Add progress tracking for long-running analyses
- Optimize AI processing pipeline

---

## Overview

This document outlines the comprehensive plan to upgrade FeedMiner's Instagram data processing capabilities from single JSON file uploads to full Instagram export processing, including ZIP archives, multiple data types, and hierarchical folder structures.

## Current State Analysis

### Current Limitations
- **Single File Processing**: Upload API only handles single JSON files
- **Simple Schema**: Expects flat Instagram saved posts structure
- **No ZIP Support**: Cannot process Instagram's native ZIP export format
- **Limited Data Types**: Only processes saved posts, ignoring likes, comments, etc.
- **Storage Constraints**: Single S3 object per upload, no hierarchical organization

### Real Instagram Export Structure
Instagram exports contain complex hierarchical data across multiple folders:

```
instagram-username-2025-07-13-xxxxx/
├── your_instagram_activity/
│   ├── saved/
│   │   ├── saved_posts.json          # Main target data
│   │   └── saved_collections.json
│   ├── likes/
│   │   ├── liked_posts.json          # Additional behavioral data
│   │   └── liked_comments.json
│   ├── comments/
│   │   └── post_comments_1.json      # User engagement patterns
│   ├── media/
│   │   ├── posts_1.json              # User's own content
│   │   ├── reels.json
│   │   └── stories.json
│   └── shopping/
│       └── recently_viewed_items.json
├── media/
│   └── posts/                        # Actual image/video files
│       ├── 201501/
│       ├── 201502/
│       └── ...
├── connections/
│   └── followers_and_following/
│       ├── followers_1.json
│       └── following.json
└── ads_information/
    └── ads_and_topics/
        └── ads_viewed.json
```

### Data Schema Differences
Each file type has different structures:

**saved_posts.json**:
```json
{
  "saved_saved_media": [
    {
      "title": "username",
      "string_map_data": {
        "Saved on": {
          "href": "https://www.instagram.com/reel/xxx/",
          "timestamp": 1752408896
        }
      }
    }
  ]
}
```

**liked_posts.json**:
```json
{
  "likes_media_likes": [
    {
      "title": "username",
      "string_list_data": [
        {
          "href": "https://www.instagram.com/reel/xxx/",
          "value": "👍",
          "timestamp": 1751717736
        }
      ]
    }
  ]
}
```

## Implementation Plan

### Phase 1: Frontend ZIP Upload Support

#### 1.1 Update UploadDemo.tsx
- **Goal**: Handle ZIP files and provide clear user guidance
- **Priority**: High
- **Estimated Effort**: 2-3 hours

**Changes Required**:
```typescript
// Add ZIP handling in UploadDemo.tsx
const handleZipUpload = async (zipFile: File) => {
  // Client-side ZIP validation
  // Extract and preview Instagram folder structure
  // Guide user through data selection
};
```

**Features**:
- ZIP file detection and validation
- Instagram export structure recognition
- Folder selection interface (saved posts, likes, comments, etc.)
- Data type preview before upload
- Progress indicators for extraction

#### 1.2 Create Data Type Selection UI
- **Goal**: Allow users to choose which Instagram data types to analyze
- **Priority**: Medium
- **Components**:
  - Checkbox interface for data types
  - Preview of data volume per type
  - Explanation of each data type's analysis value

#### 1.3 Enhanced Progress Tracking
- **Goal**: Show detailed progress for multi-file processing
- **Features**:
  - File extraction progress
  - Individual file processing status
  - Data consolidation progress

### Phase 2: Backend Multi-File Processing API

#### 2.1 Create Multi-Upload Lambda Function
- **File**: `src/api/multi_upload.py`
- **Goal**: Handle ZIP files and complex Instagram data structures
- **Priority**: High
- **Estimated Effort**: 4-6 hours

**Core Functionality**:
```python
import zipfile
import json
from typing import Dict, List, Any

def process_instagram_export(zip_content: bytes) -> Dict[str, Any]:
    """
    Extract and process Instagram ZIP export
    Returns structured data with metadata
    """
    with zipfile.ZipFile(io.BytesIO(zip_content)) as zip_file:
        # Extract Instagram folder structure
        # Identify data types available
        # Parse each JSON file type
        # Consolidate related data
        # Generate processing metadata
```

**Features**:
- ZIP file extraction and validation
- Instagram folder structure detection
- Multi-file JSON parsing
- Data type identification and categorization
- Error handling for corrupted or incomplete exports
- Memory-efficient processing for large exports

#### 2.2 Data Type Processors
- **Goal**: Create specialized processors for each Instagram data type
- **Structure**:
```python
class InstagramDataProcessor:
    def process_saved_posts(self, data: dict) -> dict:
        """Process saved_posts.json with specific schema"""
    
    def process_liked_posts(self, data: dict) -> dict:
        """Process liked_posts.json with different schema"""
    
    def process_comments(self, data: dict) -> dict:
        """Process comment data"""
    
    def consolidate_activity(self, all_data: dict) -> dict:
        """Merge all data types into unified structure"""
```

#### 2.3 Enhanced API Endpoints
- **New Endpoint**: `POST /multi-upload` - Handle ZIP/multi-file uploads
- **Enhanced Endpoint**: `POST /upload` - Maintain backward compatibility
- **New Endpoint**: `GET /content/{id}/structure` - Return data type breakdown

### Phase 3: Enhanced Data Storage

#### 3.1 New DynamoDB Schema
- **Goal**: Support hierarchical Instagram data with multiple data types
- **Priority**: High

**Enhanced Schema**:
```json
{
  "contentId": "uuid",
  "userId": "string",
  "type": "instagram_export",  // New type for multi-file
  "status": "processed",
  "createdAt": "ISO8601",
  "dataStructure": {
    "saved_posts": {
      "count": 177,
      "s3Key": "uploads/uuid/saved_posts.json",
      "lastActivity": "2025-01-15"
    },
    "liked_posts": {
      "count": 2341,
      "s3Key": "uploads/uuid/liked_posts.json", 
      "lastActivity": "2025-01-14"
    },
    "comments": {
      "count": 89,
      "s3Key": "uploads/uuid/comments.json",
      "lastActivity": "2025-01-10"
    }
  },
  "metadata": {
    "exportDate": "2025-07-13",
    "totalFiles": 15,
    "totalDataPoints": 2607,
    "analyzableTypes": ["saved_posts", "liked_posts", "comments"]
  }
}
```

#### 3.2 S3 Hierarchical Storage
- **Goal**: Organize Instagram data by type and user
- **Structure**:
```
feedminer-content-dev/
└── uploads/
    └── {contentId}/
        ├── metadata.json           # Export summary
        ├── raw_export.zip          # Original ZIP file
        ├── saved_posts.json        # Processed saved posts
        ├── liked_posts.json        # Processed liked posts
        ├── comments.json           # Processed comments
        └── consolidated.json       # Merged analysis-ready data
```

#### 3.3 Data Consolidation Logic
- **Goal**: Merge related Instagram data for comprehensive analysis
- **Features**:
  - Temporal correlation (posts saved near posts liked)
  - Content theme correlation across data types
  - User engagement pattern analysis
  - Interest evolution tracking

### Phase 4: Analysis Engine Updates

#### 4.1 Enhanced AI Agents
- **File**: `src/agents/instagram_multi_parser.py`
- **Goal**: Analyze comprehensive Instagram activity, not just saved posts
- **Priority**: High

**Enhanced Analysis Capabilities**:
```python
class ComprehensiveInstagramAnalyzer:
    def analyze_behavioral_patterns(self, multi_data: dict) -> dict:
        """
        Analyze patterns across all Instagram activity:
        - Saving vs. liking behavior differences
        - Content engagement evolution over time
        - Cross-platform interest correlation
        - Social influence pattern detection
        """
    
    def generate_holistic_goals(self, analysis: dict) -> dict:
        """
        Generate goals based on comprehensive activity:
        - Goals informed by both consumption and creation
        - Recommendations considering engagement patterns
        - Social behavior optimization suggestions
        """
```

#### 4.2 Multi-Source Analysis
- **Goal**: Combine insights from multiple Instagram data types
- **Features**:
  - **Consumption Analysis**: What content is saved/liked and why
  - **Creation Analysis**: User's own posts and engagement patterns
  - **Social Analysis**: Following patterns and community insights
  - **Temporal Analysis**: Activity patterns and evolution over time

#### 4.3 Selective Analysis Options
- **Goal**: Allow analysis of specific data types or combinations
- **API Enhancement**:
```python
# Analyze only saved posts (current functionality)
POST /analyze/{contentId}
{
  "provider": "bedrock",
  "dataTypes": ["saved_posts"]
}

# Comprehensive analysis (new functionality)
POST /analyze/{contentId}
{
  "provider": "bedrock", 
  "dataTypes": ["saved_posts", "liked_posts", "comments"],
  "analysisType": "comprehensive"
}
```

### Phase 5: Advanced Features

#### 5.1 Batch Processing
- **Goal**: Handle large Instagram exports efficiently
- **Implementation**:
  - Queue-based processing for large ZIP files
  - Progress tracking for long-running analyses
  - Partial result availability during processing

#### 5.2 Privacy Controls
- **Goal**: Give users control over sensitive data processing
- **Features**:
  - Data type selection (exclude personal messages, etc.)
  - Temporal filtering (analyze only recent activity)
  - Content filtering (exclude specific topics/keywords)

#### 5.3 Data Visualization Enhancements
- **Goal**: Visualize multi-dimensional Instagram activity
- **Frontend Components**:
  - Activity timeline across all data types
  - Cross-correlation heat maps
  - Interest evolution charts
  - Social network analysis visualizations

#### 5.4 Export and Sharing
- **Goal**: Allow users to export and share insights
- **Features**:
  - PDF report generation
  - Shareable insight cards
  - Data export in standard formats
  - Privacy-safe sharing options

## Technical Considerations

### Performance Optimization
- **Memory Management**: Stream processing for large ZIP files
- **Storage Efficiency**: Compress processed data, optional raw data retention
- **Processing Speed**: Parallel processing of independent data types
- **API Response Time**: Asynchronous processing with status endpoints

### Security and Privacy
- **Data Encryption**: Encrypt all stored Instagram data at rest
- **Access Controls**: Ensure users can only access their own data
- **Data Retention**: Configurable retention policies for different data types
- **Anonymization**: Remove or hash personally identifiable information

### Backward Compatibility
- **API Compatibility**: Maintain existing single-file upload functionality
- **Data Structure**: Ensure existing analyses continue to work
- **Frontend Graceful Degradation**: Handle both old and new data formats

### Error Handling
- **Corrupted ZIP Files**: Graceful handling and user feedback
- **Incomplete Exports**: Process available data, report missing components
- **Large File Limits**: Clear limits and guidance for oversized exports
- **Format Changes**: Robust parsing for Instagram export format evolution

## Migration Strategy

### Phase 1 Deployment
- Deploy new multi-upload endpoint alongside existing upload
- Update frontend to detect and handle ZIP files
- Maintain full backward compatibility

### Phase 2 Deployment  
- Roll out enhanced storage schema
- Migrate existing data to new format (optional)
- Deploy enhanced analysis capabilities

### Testing Strategy
- **Unit Tests**: Individual data type processors
- **Integration Tests**: End-to-end ZIP upload and analysis
- **Performance Tests**: Large Instagram export processing
- **User Acceptance Tests**: Real Instagram export data validation

## Success Metrics

### Technical Metrics
- **ZIP Processing Time**: < 30 seconds for typical Instagram export
- **Data Extraction Accuracy**: 99%+ successful extraction of known formats
- **Storage Efficiency**: < 50% overhead for hierarchical organization
- **API Response Time**: < 2 seconds for processing status endpoints

### User Experience Metrics
- **Upload Success Rate**: > 95% for valid Instagram exports
- **Feature Adoption**: % of users using multi-file analysis vs single-file
- **Analysis Completeness**: Average % of available data types processed
- **User Satisfaction**: Feedback on enhanced insights quality

### Business Metrics
- **Analysis Depth**: Increase in average insights per user
- **User Retention**: Impact of comprehensive analysis on user engagement
- **Goal Success Rate**: Improvement in goal achievement with better data

## Timeline and Resources

### Phase 1 (Frontend ZIP Support): 1 week
- **Developer Time**: 16-20 hours
- **Testing Time**: 8 hours
- **Dependencies**: None

### Phase 2 (Backend Multi-File API): 2 weeks  
- **Developer Time**: 32-40 hours
- **Testing Time**: 16 hours
- **Dependencies**: AWS Lambda layer updates

### Phase 3 (Enhanced Storage): 1 week
- **Developer Time**: 16-20 hours
- **Testing Time**: 12 hours  
- **Dependencies**: Database schema migration

### Phase 4 (Analysis Engine): 2 weeks
- **Developer Time**: 32-40 hours
- **Testing Time**: 20 hours
- **Dependencies**: AI model updates

### Phase 5 (Advanced Features): 3 weeks
- **Developer Time**: 48-60 hours
- **Testing Time**: 24 hours
- **Dependencies**: All previous phases

**Total Estimated Timeline**: 9 weeks  
**Total Development Effort**: 144-180 hours

## Risk Assessment

### High Risk
- **Instagram Format Changes**: Instagram may change export format
- **Mitigation**: Robust parsing with fallback to known formats

### Medium Risk  
- **Performance Issues**: Large ZIP files may cause timeouts
- **Mitigation**: Implement streaming and batch processing

### Low Risk
- **User Adoption**: Users may prefer simple single-file uploads
- **Mitigation**: Maintain backward compatibility and clear migration benefits

## Conclusion

This multi-file Instagram data processing implementation will transform FeedMiner from a simple saved-posts analyzer to a comprehensive Instagram activity intelligence platform. The phased approach ensures backward compatibility while delivering significant value increments at each stage.

The enhanced capabilities will provide users with much deeper insights into their social media behavior, leading to more accurate and actionable goal recommendations. This positions FeedMiner as a truly comprehensive personal development platform powered by social media intelligence.

---

**Next Steps**:
1. Review and approve this implementation plan
2. Begin Phase 1 development
3. Create detailed technical specifications for each phase
4. Set up project tracking and milestone management

**Document Status**: ✅ Ready for Development  
**Approval Required**: Product Owner, Technical Lead  
**Est. Business Impact**: High - Enables processing of complete Instagram exports
