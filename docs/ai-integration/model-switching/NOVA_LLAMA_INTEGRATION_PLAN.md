# Nova & Llama Model Integration Plan

## Executive Summary

This plan outlines the integration of Amazon Nova and Meta Llama models into FeedMiner's Strands-based model switching system, expanding from 2 models (Claude via Anthropic + Bedrock) to 6 models across 3 AI families.

## Selected Models

### Amazon Nova Models
- **Nova Micro** (`us.amazon.nova-micro-v1:0`) - Text-only, fastest, lowest cost
- **Nova Lite** (`us.amazon.nova-lite-v1:0`) - Multimodal, fast and low-cost

### Meta Llama Models  
- **Llama 3.1 8B** (`meta.llama3-1-8b-instruct-v1:0`) - Efficient, good for comparison
- **Llama 3.1 70B** (`meta.llama3-1-70b-instruct-v1:0`) - More capable, higher quality

## Integration Phases

### Phase 1: Strands Compatibility Testing 🧪
**Goal**: Verify Strands BedrockModel can handle Nova and Llama models

**Tasks**:
1. **Test Nova Direct Model IDs**: Try `us.amazon.nova-micro-v1:0` with Strands BedrockModel
2. **Test Nova Inference Profiles**: If direct fails, try inference profile format
3. **Test Llama Models**: Verify `meta.llama3-1-8b-instruct-v1:0` works with Strands
4. **Parameter Mapping**: Test if `additional_request_fields` handles parameter differences
5. **Response Extraction**: Ensure our `extract_strands_response` works with new models

**Expected Challenges**:
- Nova may require inference profile IDs instead of model IDs
- Llama uses different parameter names (`max_gen_len` vs `max_tokens`)
- Response formats may vary between model families

**Success Criteria**:
- All 4 new models respond successfully via Strands BedrockModel
- Parameter mapping works (temperature, max_tokens equivalents)
- Response extraction produces consistent format

### Phase 2: Backend Implementation 🔧
**Goal**: Enhance strands_model_switching.py to support new model families

**Tasks**:
1. **Model Family Detection**: Add Nova and Llama model detection logic
2. **Parameter Mapping**: Create parameter adapters for each model family
3. **Enhanced Agent Creation**: Update `create_strands_agent` for new models
4. **Error Handling**: Add model-specific error handling
5. **Response Processing**: Enhance response extraction for new formats
6. **Default Models**: Add defaults for new model families

**Key Code Changes**:
```python
def get_default_model(provider: str) -> str:
    defaults = {
        "anthropic": "claude-3-5-sonnet-20241022",
        "bedrock": "anthropic.claude-3-5-sonnet-20241022-v2:0",
        "nova": "us.amazon.nova-micro-v1:0",  # NEW
        "llama": "meta.llama3-1-8b-instruct-v1:0"  # NEW
    }
    return defaults.get(provider, "")

def create_strands_agent(provider: str, model_id: str, temperature: float = 0.7) -> Agent:
    # Enhanced logic for Nova and Llama models
    if "nova" in model_id:
        additional_fields = {"maxTokens": 4096, "topP": 0.9}
    elif "llama" in model_id:
        additional_fields = {"max_gen_len": 4096, "top_p": 0.9}
    else:
        additional_fields = {}
    
    model = BedrockModel(
        model_id=model_id,
        temperature=temperature,
        region=os.environ.get('AWS_REGION', 'us-west-2'),
        additional_request_fields=additional_fields
    )
    # ... rest of agent creation
```

**Success Criteria**:
- Backend supports all 6 models (2 Claude + 2 Nova + 2 Llama)
- Parameter mapping works for all model families
- Response extraction handles all response formats
- Error handling provides clear feedback for each model type

### Phase 3: Frontend Enhancement 🎨
**Goal**: Update React frontend to support new model categories

**Tasks**:
1. **Model Categories**: Group models by AI family (Claude, Nova, Llama)
2. **Provider Selection**: Enhance ModelProviderSelector with new options
3. **Model Descriptions**: Add helpful descriptions for each model
4. **Cost Indicators**: Show relative cost information
5. **Performance Hints**: Indicate speed/capability trade-offs
6. **Comparison Matrix**: Allow comparing across model families

**Frontend Changes**:
```typescript
const MODEL_FAMILIES = {
  claude: {
    name: "Anthropic Claude",
    models: [
      { id: "claude-3-5-sonnet-20241022", name: "Claude 3.5 Sonnet", cost: "High", speed: "Medium" },
      { id: "anthropic.claude-3-5-sonnet-20241022-v2:0", name: "Claude 3.5 Sonnet (Bedrock)", cost: "High", speed: "Medium" }
    ]
  },
  nova: {
    name: "Amazon Nova",
    models: [
      { id: "us.amazon.nova-micro-v1:0", name: "Nova Micro", cost: "Very Low", speed: "Very Fast" },
      { id: "us.amazon.nova-lite-v1:0", name: "Nova Lite", cost: "Low", speed: "Fast" }
    ]
  },
  llama: {
    name: "Meta Llama",
    models: [
      { id: "meta.llama3-1-8b-instruct-v1:0", name: "Llama 3.1 8B", cost: "Low", speed: "Fast" },
      { id: "meta.llama3-1-70b-instruct-v1:0", name: "Llama 3.1 70B", cost: "Medium", speed: "Medium" }
    ]
  }
};
```

**Success Criteria**:
- Frontend displays all 6 models in organized categories
- Users can easily compare models across families
- Cost and performance indicators help with selection
- Comparison mode works with any combination of models

### Phase 4: Testing & Validation 🧪
**Goal**: Comprehensive testing of all model combinations

**Tasks**:
1. **Individual Model Testing**: Test each of the 6 models individually
2. **Cross-Family Comparison**: Test comparing models from different families
3. **Performance Benchmarking**: Compare latency and response quality
4. **Cost Analysis**: Monitor actual usage costs for each model
5. **Error Scenario Testing**: Test error handling for each model type
6. **Learning Scenario Testing**: Test educational comparison scenarios

**Test Scenarios**:
```python
# Test matrix: 6 individual + 15 comparison pairs
test_scenarios = [
    # Individual tests
    ("anthropic", "claude-3-5-sonnet-20241022"),
    ("bedrock", "anthropic.claude-3-5-sonnet-20241022-v2:0"),
    ("nova", "us.amazon.nova-micro-v1:0"),
    ("nova", "us.amazon.nova-lite-v1:0"),
    ("llama", "meta.llama3-1-8b-instruct-v1:0"),
    ("llama", "meta.llama3-1-70b-instruct-v1:0"),
    
    # Cross-family comparisons
    ("nova vs claude", [nova_micro, claude_sonnet]),
    ("llama vs claude", [llama_8b, claude_sonnet]),
    ("nova vs llama", [nova_micro, llama_8b]),
    # ... 12 more comparison combinations
]
```

**Success Criteria**:
- All 6 individual models work correctly
- All 15 possible comparison pairs work
- Performance meets expectations (< 30s response time)
- Cost tracking works for all models
- Error handling provides helpful feedback

### Phase 5: Production Deployment 🚀
**Goal**: Deploy enhanced model switching to production

**Tasks**:
1. **Backend Deployment**: Deploy updated strands_model_switching.py
2. **Frontend Deployment**: Deploy enhanced React components
3. **Documentation Update**: Update all documentation
4. **Monitoring Setup**: Add monitoring for new models
5. **Cost Alerts**: Set up cost monitoring for higher-volume models
6. **User Communication**: Update users about new model options

**Deployment Checklist**:
- [ ] SAM build and deploy backend changes
- [ ] Test all models in production environment
- [ ] Deploy frontend via Amplify
- [ ] Update CHANGELOG.md and README.md
- [ ] Create user guide for new models
- [ ] Set up CloudWatch alarms for cost and errors
- [ ] Monitor initial usage and performance

**Success Criteria**:
- All 6 models available in production
- No regression in existing functionality
- Performance and cost within expected ranges
- User feedback positive on new model options

## Technical Implementation Details

### Strands BedrockModel Configuration Strategy

```python
def create_bedrock_model_for_family(model_id: str, temperature: float) -> BedrockModel:
    """Create Strands BedrockModel with family-specific configuration."""
    
    base_config = {
        "model_id": model_id,
        "temperature": temperature,
        "region": os.environ.get('AWS_REGION', 'us-west-2')
    }
    
    # Family-specific parameter handling
    if "nova" in model_id:
        # Nova models may need inference profile handling
        additional_fields = {
            "maxTokens": 4096,  # Nova uses maxTokens
            "topP": 0.9
        }
        # Try inference profile if direct model ID fails
        if model_id.startswith("us.amazon.nova"):
            # This might need to be an inference profile ARN
            pass
            
    elif "llama" in model_id:
        # Llama models use different parameter names
        additional_fields = {
            "max_gen_len": 4096,  # Llama uses max_gen_len
            "top_p": 0.9
        }
        
    else:
        # Claude and other models
        additional_fields = {}
    
    if additional_fields:
        base_config["additional_request_fields"] = additional_fields
    
    return BedrockModel(**base_config)
```

### Response Format Handling

```python
def extract_model_response(strands_result, model_family: str) -> Dict[str, Any]:
    """Extract response with model family-specific handling."""
    
    base_response = extract_strands_response(strands_result)
    
    # Add model family-specific metadata
    if model_family == "nova":
        # Nova models may have different usage tracking
        base_response["model_family"] = "amazon_nova"
        base_response["cost_tier"] = "very_low"
        
    elif model_family == "llama":
        # Llama models may have different response structure
        base_response["model_family"] = "meta_llama"
        base_response["cost_tier"] = "low"
        
    else:
        # Claude models
        base_response["model_family"] = "anthropic_claude"
        base_response["cost_tier"] = "high"
    
    return base_response
```

## Expected Outcomes

### For Users (Learning App)
- **Richer Comparisons**: Compare 6 different AI models across 3 families
- **Cost-Effective Learning**: Nova models provide 75% cost savings for experimentation
- **Performance Variety**: From ultra-fast Nova Micro to capable Llama 70B
- **Educational Value**: See how different AI companies approach the same problems

### For Development
- **Scalable Architecture**: Easy to add more models in the future
- **Cost Optimization**: Users can choose appropriate model for their use case
- **Performance Insights**: Real data on model performance across families
- **Technology Leadership**: Showcase of cutting-edge model integration

## Risk Mitigation

### Technical Risks
1. **Nova Inference Profiles**: May require different integration approach
   - **Mitigation**: Test both direct model ID and inference profile methods
2. **Parameter Incompatibility**: Models may not work with Strands BedrockModel
   - **Mitigation**: Use additional_request_fields and test thoroughly
3. **Performance Degradation**: New models may be slower than expected
   - **Mitigation**: Set appropriate expectations and monitor performance

### Cost Risks
1. **Unexpected High Usage**: Users may overuse expensive models
   - **Mitigation**: Show cost indicators and provide usage guidance
2. **New Model Pricing**: Costs may be higher than documented
   - **Mitigation**: Monitor actual costs and adjust recommendations

### User Experience Risks
1. **Model Confusion**: Too many choices may overwhelm users
   - **Mitigation**: Clear categorization and helpful descriptions
2. **Quality Variations**: Some models may give poor results for certain tasks
   - **Mitigation**: Provide guidance on model strengths and use cases

## Success Metrics

### Technical Metrics
- ✅ All 6 models respond successfully (100% success rate)
- ✅ Response time < 30 seconds for all models
- ✅ Cost tracking accurate within 5%
- ✅ Error rate < 1% for all models

### User Experience Metrics
- ✅ Model selection completion rate > 90%
- ✅ Comparison usage increases by 50%
- ✅ User satisfaction with new models > 4/5
- ✅ Support tickets related to models < 5/week

### Business Metrics
- ✅ Total API costs reduced by 25% (due to Nova usage)
- ✅ User engagement with comparison features increases 40%
- ✅ Educational value ratings improve
- ✅ Feature adoption rate > 60% within 30 days

---

This plan provides a comprehensive roadmap for integrating Nova and Llama models into your learning app, giving users rich comparison capabilities across multiple AI families while maintaining cost efficiency and performance.