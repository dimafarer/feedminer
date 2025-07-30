# FeedMiner Incomplete Features Documentation

**Version**: 1.0  
**Created**: July 26, 2025  
**Purpose**: Track features referenced in infrastructure but not yet implemented

## 🚨 Current Analysis Pipeline Issue

### Analysis Timeout Problem (HIGH PRIORITY)

**Status**: ❌ Analysis step failing on real user data  
**Symptoms**: 
- ZIP upload works ✅
- Category selection works ✅  
- Analysis times out after ~1 minute ❌
- Falls back to static demo data ❌

**Root Cause**: Unknown (needs debugging)
**Impact**: Core functionality broken for real user data
**Priority**: CRITICAL - blocks main user workflow

**Debug Strategy**:
1. Test with tiny data subsets (1-5 items per category)
2. Identify where timeout occurs in pipeline
3. Gradually increase data size once working
4. Optimize bottleneck components

---

## 🚧 Missing Implementation Files

### 1. Model Switching API (`src/api/model_switching.py`)

**Status**: ❌ Referenced but not implemented  
**Referenced In**: 
- `template.yaml:967` - `ModelSwitchingFunction`
- `docs/API.md:159` - `/analyze/{contentId}` endpoint
- `docs/API.md:204` - `/compare/{contentId}` endpoint

**Intended Functionality**:
- Runtime AI provider selection (Anthropic API vs AWS Bedrock)
- Model performance comparison and benchmarking
- Cost optimization through provider switching
- Multi-model analysis capabilities

**API Endpoints That Should Exist**:
```http
POST /analyze/{contentId}
POST /compare/{contentId}
```

**Current Impact**:
- Template deployment may fail if function handler doesn't exist
- API documentation describes non-functional endpoints
- Demo functionality for model comparison unavailable

**Priority**: Medium (Demo feature, not core functionality)

### 2. AI Providers Layer (`layers/ai-providers/`)

**Status**: ❌ Referenced but directory missing  
**Referenced In**:
- `template.yaml:608` - `AIProvidersLayer`
- Multiple Lambda functions reference this layer

**Intended Contents**:
- Anthropic API client dependencies
- AWS Bedrock client libraries  
- Multi-provider abstraction libraries
- Common AI processing utilities

**Current Impact**:
- Lambda functions may fail to import AI dependencies
- Model switching functionality cannot work
- Deployment may fail due to missing layer content

**Priority**: High (Required for AI functionality)

### 3. Enhanced Instagram Parser (`src/agents/instagram_parser_v2.py`)

**Status**: ⚠️ File may exist but functionality incomplete  
**Referenced In**:
- `template.yaml:1033` - `EnhancedInstagramParserFunction`
- Documentation references enhanced multi-model parsing

**Intended Functionality**:
- Multi-provider AI analysis integration
- Enhanced Instagram data processing
- Performance optimizations

**Current Status**: Need to verify existence and functionality

## 📋 Recommended Implementation Order

### Phase 1: Core Dependencies (High Priority)
1. **Create `layers/ai-providers/` structure**
   - Set up requirements.txt with AI client libraries
   - Create provider abstraction layer
   - Test layer packaging and deployment

### Phase 2: Model Switching API (Medium Priority)  
2. **Implement `src/api/model_switching.py`**
   - Basic provider switching functionality
   - Simple model comparison endpoint
   - Error handling and validation

### Phase 3: Enhanced Features (Low Priority)
3. **Complete `instagram_parser_v2.py`** 
   - Integrate with model switching capabilities
   - Add performance optimizations
   - Multi-provider processing logic

## 🛠 Implementation Guidelines

### Layer Structure Template
```
layers/ai-providers/
├── requirements.txt
├── python/
│   ├── lib/
│   │   └── python3.12/
│   │       └── site-packages/
│   └── ai_providers/
│       ├── __init__.py
│       ├── anthropic_client.py
│       ├── bedrock_client.py
│       └── provider_factory.py
```

### Model Switching API Template
```python
# src/api/model_switching.py
def handler(event, context):
    """Handle model switching and comparison requests"""
    if event['path'].endswith('/analyze'):
        return analyze_with_provider(event, context)
    elif event['path'].endswith('/compare'):
        return compare_providers(event, context)
    else:
        return error_response(400, "Unknown endpoint")
```

## 📊 Current Workarounds

**For Development/Testing**:
- Model switching endpoints return 404 errors
- Single-provider analysis works through existing agents
- Layer dependencies may cause import errors

**For Production**:
- Remove model switching references from template.yaml temporarily
- Use single-provider mode until implementation complete
- Document known limitations in API responses

## 🔍 Verification Commands

**Check if files exist**:
```bash
ls -la src/api/model_switching.py
ls -la layers/ai-providers/
ls -la src/agents/instagram_parser_v2.py
```

**Test layer deployment**:
```bash
sam build --use-container
sam validate --lint
```

**Test API endpoints**:
```bash
curl -X POST https://api-url/analyze/test-id
curl -X POST https://api-url/compare/test-id
```

## 📝 Next Actions

1. **Immediate** (to fix deployment issues):
   - Verify which files actually exist
   - Comment out missing references in template.yaml if needed
   - Update API documentation to reflect actual endpoints

2. **Short-term** (to complete v0.2.0):
   - Implement basic AI providers layer
   - Create minimal model switching functionality
   - Test multi-provider capabilities

3. **Long-term** (for full feature completion):
   - Add comprehensive model comparison features
   - Implement performance benchmarking
   - Create user-facing model selection UI

---

**Note**: This document should be updated as features are implemented and removed when functionality is complete.