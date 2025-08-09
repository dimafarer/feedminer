# Model Parameter Comparison: Nova vs Llama vs Claude

## Overview

This document compares the inference parameters and integration requirements for different model families in AWS Bedrock, specifically for our Strands-based model switching implementation.

## Model Families & Parameters

### 1. Anthropic Claude Models (Current Implementation)
**Model IDs**: `anthropic.claude-3-5-sonnet-20241022-v2:0`
**Strands Implementation**: Uses `AnthropicModel` with direct API + `BedrockModel` for Bedrock
**Parameters**:
```python
{
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": 4096,
    "temperature": 0.7,
    "messages": [{"role": "user", "content": prompt}]
}
```

### 2. Amazon Nova Models (NEW)
**Model IDs**: 
- `us.amazon.nova-micro-v1:0` (text-only, fastest)
- `us.amazon.nova-lite-v1:0` (multimodal, fast + low-cost)

**Key Differences**:
- Uses **inference profile IDs** instead of direct model IDs
- Different parameter structure
- 128K-300K context windows

**Parameters**:
```python
{
    "maxTokens": 5000,  # Different naming convention
    "temperature": 0.7,
    "topP": 0.9,
    "stopSequences": [],
    "messages": [{"role": "user", "content": [{"text": prompt}]}]  # Different message format
}
```

### 3. Meta Llama Models (NEW)
**Model IDs**: 
- `meta.llama3-1-8b-instruct-v1:0` (efficient)
- `meta.llama3-1-70b-instruct-v1:0` (more capable)

**Key Differences**:
- Uses `max_gen_len` instead of `max_tokens`
- Simple prompt format (not messages)
- No `anthropic_version` required

**Parameters**:
```python
{
    "prompt": prompt,  # Direct prompt, not messages
    "max_gen_len": 4096,  # Different naming
    "temperature": 0.7,
    "top_p": 0.9
}
```

## Strands Integration Challenges

### 1. Nova Models - Inference Profile Requirement
- **Issue**: Nova models may require inference profile IDs
- **Solution**: Check if Strands `BedrockModel` supports inference profiles via `model_id` parameter
- **Fallback**: Use standard model ID and handle via `additional_request_fields`

### 2. Parameter Mapping Differences
| Model Family | Max Tokens | Temperature | Top P | Message Format |
|-------------|------------|-------------|-------|----------------|
| Claude | `max_tokens` | `temperature` | `top_p` | `messages[]` |
| Nova | `maxTokens` | `temperature` | `topP` | `messages[]` |
| Llama | `max_gen_len` | `temperature` | `top_p` | `prompt` |

### 3. Response Format Differences
- **Claude**: Returns structured message format
- **Nova**: Similar to Claude but may have different metadata
- **Llama**: Returns generation in `generation` field

## Implementation Strategy

### Phase 1: Strands BedrockModel Configuration
Test if current Strands `BedrockModel` can handle different parameter formats via:
- `additional_request_fields` for model-specific parameters
- `model_id` for inference profiles vs direct model IDs

### Phase 2: Parameter Adapter Pattern
Create a parameter adapter that maps our standard interface to model-specific formats:

```python
def create_strands_bedrock_model(model_family: str, model_id: str, temperature: float = 0.7):
    if "nova" in model_id:
        # Use inference profile if needed
        additional_fields = {
            "maxTokens": 4096,  # Nova naming
            "topP": 0.9
        }
    elif "llama" in model_id:
        additional_fields = {
            "max_gen_len": 4096,  # Llama naming
            "top_p": 0.9
        }
    else:
        additional_fields = {}
    
    return BedrockModel(
        model_id=model_id,
        temperature=temperature,
        additional_request_fields=additional_fields
    )
```

### Phase 3: Response Parsing Adapter
Handle different response formats in our `extract_strands_response` function.

## Testing Strategy

### 1. Model ID vs Inference Profile Testing
- Test Nova models with direct model ID
- Test with inference profile ID if direct fails
- Document which approach works

### 2. Parameter Validation
- Test each model family with our standard parameters
- Verify temperature, max_tokens equivalent, and top_p work
- Test edge cases and error handling

### 3. Response Format Validation
- Ensure our response extraction works with all model types
- Test that frontend receives consistent format
- Validate performance metrics (latency, tokens) are captured

## Expected Challenges & Solutions

### Challenge 1: Nova Inference Profiles
**Problem**: Nova models might require inference profile ARNs
**Solution**: 
- Try direct model ID first
- Fallback to inference profile format
- Use `additional_request_fields` if needed

### Challenge 2: Llama Prompt Format
**Problem**: Llama uses direct prompt, not messages array
**Solution**: Handle in Strands or via request transformation

### Challenge 3: Parameter Name Variations
**Problem**: Different models use different parameter names
**Solution**: Use `additional_request_fields` in BedrockModel

## Integration Milestones

### Milestone 1: Nova Integration ✅
- [ ] Test Nova Micro with Strands BedrockModel
- [ ] Test Nova Lite with Strands BedrockModel
- [ ] Verify parameter mapping works
- [ ] Test response extraction

### Milestone 2: Llama Integration ✅
- [ ] Test Llama 3.1 8B with Strands BedrockModel
- [ ] Test Llama 3.1 70B with Strands BedrockModel
- [ ] Verify prompt format compatibility
- [ ] Test response extraction

### Milestone 3: Frontend Integration ✅
- [ ] Add Nova and Llama models to frontend dropdown
- [ ] Create model categories (Claude, Nova, Llama)
- [ ] Test comparison mode with new models
- [ ] Verify performance metrics display

### Milestone 4: Production Deployment ✅
- [ ] Deploy updated model switching endpoint
- [ ] Test all models in production
- [ ] Monitor performance and costs
- [ ] Update documentation

## Cost Considerations

### Price Comparison (per 1K tokens)
- **Nova Micro**: $0.000035 input, $0.00014 output (cheapest)
- **Nova Lite**: $0.00006 input, $0.00024 output
- **Llama 3.1 8B**: ~$0.0003 input, ~$0.0006 output (estimate)
- **Claude 3.5 Sonnet**: ~$0.003 input, ~$0.015 output (reference)

Nova models are 75% less expensive than comparable models, making them excellent for high-volume learning scenarios.

## Conclusion

The integration requires:
1. Parameter mapping for different naming conventions
2. Testing inference profile requirements for Nova
3. Response format adaptation for consistent frontend experience
4. Careful testing of each model family

The Strands `BedrockModel` with `additional_request_fields` should handle most differences, but we may need custom parameter mapping for optimal results.