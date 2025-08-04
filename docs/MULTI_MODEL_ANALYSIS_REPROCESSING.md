# Multi-Model Personal Analysis Reprocessing

## Overview
Implementation plan for adding multi-model analysis capabilities to the Personal Analysis page, allowing users to reprocess their data with different AI models and compare results.

## Implementation Plan

### Phase 1: Foundation (Core Reprocessing) - IN PROGRESS
**Goal**: Basic model switching with Claude (Anthropic API + AWS Bedrock)

#### Starting Configuration
- **Models**: Claude 3.5 Sonnet via Anthropic API + AWS Bedrock
- **Progress**: Real-time WebSocket updates
- **Component**: AnalysisDashboard.tsx
- **Model Indicator**: Badge/chip at top of analysis page

#### WebSocket Implications for Real-time Updates
**Pros:**
- Instant progress feedback to users
- No polling overhead or delays
- Better UX for long-running analysis tasks
- Scales well with existing WebSocket infrastructure

**Cons:**
- Requires maintaining WebSocket connections
- More complex error handling (connection drops)
- Need connection recovery logic
- Higher server resource usage for persistent connections

**Technical Requirements:**
- Extend existing WebSocket handlers for reprocessing events
- Add connection management for analysis progress
- Implement reconnection logic for dropped connections
- Handle multiple concurrent reprocessing jobs per user

#### Backend Tasks - Phase 1
- [x] **Database Schema Extension** ✅ COMPLETED 2025-08-04
  - Extend DynamoDB to store multiple analyses per content item
  - Schema: `{contentId}#{modelProvider}#{modelName}#{timestamp}`
  - Add analysis metadata (model, cost, processing time, created date)

- [x] **Reprocessing API Endpoint** ✅ COMPLETED 2025-08-04
  - Create `POST /content/{id}/reprocess` endpoint
  - Accept model selection parameters
  - Validate user has access to content
  - Check if analysis already exists (caching)

- [ ] **WebSocket Progress Integration**
  - Extend existing WebSocket handlers for analysis progress
  - Event types: `analysis_started`, `analysis_progress`, `analysis_complete`, `analysis_error`
  - Include progress percentage, current step, estimated time remaining

- [ ] **Analysis Storage Logic**
  - Store multiple analysis results per content item
  - Implement 7-day TTL for analysis cache
  - Add cleanup job for expired analyses

#### Frontend Tasks - Phase 1
- [x] **ModelSelector Integration** ✅ COMPLETED 2025-08-04
  - Add ModelSelector component to AnalysisDashboard.tsx
  - Show only Claude models initially (Anthropic API + Bedrock)
  - Include cost/time estimates for each model

- [x] **Current Model Badge** ✅ COMPLETED 2025-08-04
  - Display prominent badge showing current analysis model
  - Include model family, provider, and processing timestamp
  - Make badge clickable to open model selector

- [x] **Reprocessing UI Flow** ✅ COMPLETED 2025-08-04
  - Add "Reprocess with Different Model" button
  - Show model selection modal/dropdown
  - Display cost/time estimates before processing

- [x] **Loading States & Progress** ✅ COMPLETED 2025-08-04
  - Implement loading overlay during reprocessing
  - Show real-time progress from WebSocket
  - Display current processing step
  - Add cancel reprocessing option

- [x] **WebSocket Progress Integration** ✅ COMPLETED 2025-08-04
  - Connect to existing WebSocket infrastructure
  - Handle analysis progress events
  - Update UI in real-time
  - Implement connection recovery logic

#### API Service Updates - Phase 1
- [x] **Reprocessing Service Methods** ✅ COMPLETED 2025-08-04
  - `reprocessContent(contentId, modelConfig)` - Start reprocessing
  - `getAnalysisHistory(contentId)` - Get all analyses for content
  - `cancelReprocessing(contentId, jobId)` - Cancel running job

- [x] **WebSocket Event Handlers** ✅ COMPLETED 2025-08-04
  - Handle analysis progress events
  - Update component state from WebSocket messages
  - Manage connection lifecycle

#### Testing - Phase 1
- [ ] **Backend Testing**
  - Test reprocessing API with both Claude variants
  - Validate WebSocket progress events
  - Test concurrent reprocessing jobs
  - Verify analysis caching works correctly

- [ ] **Frontend Testing**
  - Test model switching UI flow
  - Validate real-time progress updates
  - Test WebSocket connection recovery
  - Verify loading states and error handling

---

### Phase 2: Full Model Support + UX Polish (PLANNED)
**Goal**: All 6 models + enhanced UX

#### Enhancements
- Support all 6 AI models (Claude, Nova, Llama)
- Enhanced cost/time estimation system
- Improved loading animations and progress visualization
- Model performance comparison indicators
- Better error handling and retry logic

---

### Phase 3: Multi-Analysis Management (PLANNED)
**Goal**: Analysis history and batch processing

#### Features
- Analysis history management interface
- Quick switching between cached analyses
- "Reprocess All Models" batch option
- Analysis metadata display and filtering
- Storage optimization and cleanup

---

### Phase 4: Model Comparison (FUTURE)
**Goal**: Side-by-side model comparison

#### Features
- Desktop: Side-by-side comparison view
- Mobile: Swipe/tab comparison interface
- Difference highlighting between model outputs
- Export comparison reports

---

## Technical Architecture

### Database Schema Extension
```typescript
// DynamoDB Item Structure
{
  contentId: string,
  analysisId: string, // {modelProvider}#{modelName}#{timestamp}
  modelProvider: 'anthropic' | 'bedrock' | 'nova' | 'llama',
  modelName: string,
  analysis: AnalysisResult,
  metadata: {
    processingTime: number,
    estimatedCost: number,
    createdAt: string,
    processingSteps: string[]
  },
  ttl: number // 7 days from creation
}
```

### WebSocket Event Schema
```typescript
// Analysis Progress Events
{
  type: 'analysis_started' | 'analysis_progress' | 'analysis_complete' | 'analysis_error',
  contentId: string,
  jobId: string,
  data: {
    progress?: number, // 0-100
    currentStep?: string,
    estimatedTimeRemaining?: number,
    result?: AnalysisResult,
    error?: string
  }
}
```

### API Endpoints
```
POST /content/{id}/reprocess
GET /content/{id}/analyses
DELETE /content/{id}/analyses/{analysisId}
GET /content/{id}/analyses/{analysisId}
```

---

## Current Status: Phase 1 Starting
- **Started**: 2025-08-04
- **Current Phase**: Phase 1 - Foundation
- **Next Milestone**: Core reprocessing with Claude models
- **WebSocket Integration**: Real-time progress updates

---

## Progress Log

### 2025-08-04 - Project Initiation
- Created implementation plan
- Defined phased approach
- Selected Phase 1 models (Claude Anthropic API + Bedrock)
- Chose WebSocket for real-time progress updates
- Ready to begin Phase 1 implementation