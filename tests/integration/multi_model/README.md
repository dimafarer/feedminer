# Multi-Model AI Integration Test Suite

This comprehensive test suite validates the 6-model AI integration across 3 families (Claude, Nova, Llama) in FeedMiner.

## Test Organization

### Infrastructure Tests
- **`check_bedrock_models.py`**: Verify AWS Bedrock model availability and activation
- **`test_strands_implementation.py`**: Validate Strands framework integration

### Phase-Specific Tests
- **`test_nova_llama_strands.py`**: Phase 1 compatibility testing with Strands framework
- **`test_phase2_backend.py`**: Phase 2 backend implementation validation  
- **`test_frontend_phase3.py`**: Phase 3 frontend enhancement validation

### Production Tests
- **`test_production_nova_llama.py`**: End-to-end production deployment validation
- **`test_optimized_comparison.py`**: Optimized 3-model comparison performance test

### Development Artifacts
- **`prototype_strands_model_switching.py`**: Original prototype for model switching logic

## Quick Start

### Prerequisites
```bash
# Activate virtual environment (required for Python tests)
source feedminer-env/bin/activate

# Ensure AWS credentials are configured
aws configure list

# Verify Anthropic API key is available
echo $ANTHROPIC_API_KEY
```

### Run All Tests
```bash
# From project root
cd tests/integration/multi_model/
python run_all_tests.py
```

### Run Individual Test Categories
```bash
# Infrastructure validation
python check_bedrock_models.py

# Backend implementation tests
python test_phase2_backend.py

# Frontend tests
python test_frontend_phase3.py

# Production validation
python test_production_nova_llama.py

# Performance optimization tests
python test_optimized_comparison.py
```

## Test Coverage

### Model Coverage
- ✅ **Claude Models**: claude-3-5-sonnet-20241022, anthropic.claude-3-5-sonnet-20241022-v2:0
- ✅ **Nova Models**: us.amazon.nova-micro-v1:0, us.amazon.nova-lite-v1:0  
- ✅ **Llama Models**: meta.llama3-1-8b-instruct-v1:0, meta.llama3-1-70b-instruct-v1:0

### Integration Coverage
- ✅ **Strands Framework**: BedrockModel, AnthropicModel compatibility
- ✅ **Backend API**: Individual model and comparison endpoints
- ✅ **Frontend UI**: Model selection, family organization, comparison interface
- ✅ **Production**: Live AWS deployment validation

### Performance Coverage
- ✅ **Individual Models**: Response time and success rate validation
- ✅ **Comparison**: 3-model cross-family comparison optimization
- ✅ **Timeout Handling**: API Gateway limits and optimization
- ✅ **Cost Efficiency**: Model family cost tier validation

## Expected Results

### Successful Test Run
```
✅ Infrastructure: 100% models available and activated
✅ Strands Integration: 100% compatibility confirmed
✅ Backend Implementation: 26/26 tests passed
✅ Frontend Enhancement: 6/6 tests passed  
✅ Production Deployment: 6/6 models working
✅ Optimized Comparison: 3/3 models, <5s response time
```

### Performance Benchmarks
- **Nova Models**: 698-1365ms (very low cost)
- **Llama Models**: 416-617ms (fastest family)
- **Claude Models**: 1887-2208ms (premium capabilities)
- **3-Model Comparison**: <5 seconds total

## Troubleshooting

### Common Issues
1. **Model Access Errors**: Run `check_bedrock_models.py` to verify activation
2. **Virtual Environment**: Ensure `feedminer-env` is activated for Python tests
3. **API Keys**: Verify Anthropic API key is set in environment
4. **Network**: Check AWS region (us-west-2) and internet connectivity

### Debug Mode
Add `-v` flag to any test for verbose output:
```bash
python test_production_nova_llama.py -v
```

## Continuous Integration

### Integration with CI/CD
```yaml
# Example GitHub Actions workflow
- name: Run Multi-Model Tests
  run: |
    source feedminer-env/bin/activate
    cd tests/integration/multi_model/
    python run_all_tests.py --ci-mode
```

### Pre-Deployment Validation
```bash
# Run before any deployment
python test_production_nova_llama.py
python test_optimized_comparison.py
```

## Extending the Test Suite

### Adding New Models
1. Update `check_bedrock_models.py` with new model IDs
2. Add test cases to `test_phase2_backend.py`
3. Update frontend tests in `test_frontend_phase3.py`

### Adding New Families
1. Extend model family detection logic
2. Add family-specific test configurations
3. Update comparison tests with new family representatives

## Test Data and Fixtures

### Mock Responses
Test files include realistic mock responses for offline testing when AWS services are unavailable.

### Test Prompts
Standardized test prompts ensure consistent validation across all model families:
- **Individual Testing**: "Hello! Please respond with 'Working: [Model Name]'"
- **Comparison Testing**: "Explain AI in one sentence, emphasizing your strengths"
- **Performance Testing**: Optimized short prompts for latency measurement

## Maintenance

### Regular Validation
- **Weekly**: Run `test_production_nova_llama.py` to verify live system
- **Before Releases**: Full test suite via `run_all_tests.py`
- **After AWS Updates**: Re-run `check_bedrock_models.py` for new models

### Updating Test Data
- Monitor model performance changes and update benchmarks
- Add new model IDs as they become available
- Update cost tier information as pricing changes

This test suite provides comprehensive validation for the multi-model AI integration and serves as a foundation for future model family additions.