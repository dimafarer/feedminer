# FeedMiner - Claude Code Memory

## Project Overview

FeedMiner is a serverless AWS application that processes exported saved content from social media platforms (Instagram, Twitter, Reddit, etc.) and provides AI-powered analysis for goal-setting and behavioral insights. The project uses AWS SAM, Python 3.12+, and integrates with multiple AI providers through AWS Bedrock including Anthropic Claude, Amazon Nova, and Meta Llama models.

**Status**: Public open-source project (February 2025)  
**Version**: v0.4.0 (Multi-Model AI Integration - 6 models across 3 AI families)

## Architecture & Technology Stack

### Core Infrastructure (Python/AWS)
- **AWS SAM**: Serverless Application Model for infrastructure as code
- **AWS Lambda**: Python 3.12 runtime for all serverless functions  
- **Amazon API Gateway**: REST and WebSocket APIs
- **Amazon DynamoDB**: NoSQL database with GSIs
- **Amazon S3**: Object storage for content and analysis results
- **AI Providers**: Anthropic Claude, Amazon Nova, Meta Llama via Strands Agents (6 models, 3 families)

### Frontend (React)
- **React 18**: Modern React with TypeScript
- **Vite**: Fast build tool and dev server
- **Tailwind CSS**: Utility-first CSS framework
- **AWS Amplify**: Production deployment and hosting - [Live Demo](https://main.d1txsc36hbt4ub.amplifyapp.com/)
- **Vitest**: Testing framework for React components

### Key Directories
- `src/`: Main Python application code (agents, API, orchestrator, websocket)
- `layers/ai-providers/`: Shared AI provider abstraction layer (Python)
- `tests/`: Python test suite with unit and integration tests
- `docs/`: Technical documentation and analysis reports
- `frontend-demo/`: Production React frontend deployed on AWS Amplify
- `scripts/`: Deployment and utility scripts (Python/Bash)

## Critical Development Directives

### Python/SAM Backend Only
**These directives apply ONLY to Python backend and AWS SAM operations:**

#### 1. Virtual Environment Usage (Python Only)
**ALWAYS use the pre-existing virtual environment for ALL Python operations:**
- Activate before any Python/pip/sam commands: `source feedminer-env/bin/activate`
- Never run pip, python, or sam commands without activating the virtual environment first
- The virtual environment contains all required dependencies and correct Python version
- **Does NOT apply to**: React frontend work in `frontend-demo/`

#### 2. SAM Deployment (Python Backend Only)
**ALWAYS use --no-confirm-changeset flag:**
- Use: `sam deploy --no-confirm-changeset`
- Never prompt for changeset approval - deploy automatically
- This ensures smooth CI/CD and automated deployments
- **Does NOT apply to**: Frontend deployments (handled by Amplify)

#### 3. SAM Validate with Linting (Python Backend Only)
**ALWAYS run sam validate with --lint flag:**
- Use: `sam validate --lint`
- Never run `sam validate` without linting
- Catches configuration issues and validates CloudFormation template
- **Does NOT apply to**: React frontend builds (use `npm run build`)

### React Frontend (frontend-demo/)
**For React frontend work, use standard Node.js/npm commands:**
- `npm install` - Install dependencies
- `npm run dev` - Start development server
- `npm run build` - Build for production

- `npm run test` - Run Vitest tests
- `npm run lint` - Run ESLint (if configured)

## Development Standards

### Python Code Style (Backend)
- Use Python 3.12+ features and type hints
- Follow PEP 8 with 4-space indentation
- Use Pydantic models for data validation and structured AI responses
- All Lambda functions should have proper error handling and logging
- Use environment variables for all configuration (no hardcoded values)

### React Code Style (Frontend)
- Use TypeScript for all components
- Follow React 18 best practices with hooks
- Use Tailwind CSS for styling
- Implement proper error boundaries and loading states
- Follow existing component patterns in `frontend-demo/src/components/`

### AWS Best Practices (Backend)
- All resources use consistent naming: `feedminer-{resource}-{environment}`
- Implement least-privilege IAM roles
- Use CloudFormation parameters for environment-specific values
- Enable comprehensive CloudWatch logging
- S3 objects organized: `uploads/`, `analysis/`, `exports/`

### AI Integration Patterns (Backend)
- Use `src/ai/providers.py` abstraction for all AI calls
- Support both Anthropic API and AWS Bedrock seamlessly
- Implement structured output with Pydantic models
- Always include usage tracking (input/output tokens)
- Graceful fallback between providers when possible

## Common Commands

### Python Backend Development
```bash
# Environment setup (Python only)
./scripts/setup.sh
source feedminer-env/bin/activate  # ALWAYS activate first

# Build and validate (with required flags)
sam build --lint
sam validate --lint
```

### React Frontend Development
```bash
# Frontend setup (separate from Python env)
cd frontend-demo/
npm install

# Development
npm run dev        # Start dev server
npm run build      # Build for production
npm run test       # Run tests
```

### Testing

#### Python Backend Tests
```bash
# ALWAYS activate virtual environment first
source feedminer-env/bin/activate

# Run all tests
./scripts/run_tests.sh

# Run specific test suites
pytest tests/unit/ -v
pytest tests/unit/test_instagram_parser.py -v
pytest tests/unit/test_multi_upload.py -v
```

#### React Frontend Tests  
```bash
cd frontend-demo/
npm run test       # Run Vitest tests
```

### Deployment

#### Python Backend Deployment
```bash
# ALWAYS activate virtual environment first
source feedminer-env/bin/activate

# Deploy with Anthropic API (no changeset confirmation)
./scripts/deploy.sh dev your-anthropic-key
# OR manually:
sam build --lint
sam deploy --no-confirm-changeset --parameter-overrides AnthropicApiKey=your-key
```

#### React Frontend Deployment
Frontend is automatically deployed via AWS Amplify when changes are pushed to the repository.

### Code Quality Workflow

#### Python Backend
```bash
# MANDATORY sequence before any commits
source feedminer-env/bin/activate  # 1. Activate environment
sam build --lint                   # 2. Build with linting
pytest tests/unit/ -v              # 3. Run tests
```

#### React Frontend
```bash
cd frontend-demo/
npm run build      # Ensure it builds
npm run test       # Run tests
# npm run lint     # If ESLint is configured
```

## Project Phases & Status

### ✅ Complete Phases
- **Phase 1a**: Infrastructure & Basic Instagram Parser (v0.1.0)
- **Phase 1b**: Real Data Testing (July 14-15) - 177 Instagram posts processed
- **Phase 1c**: Multi-Model AI Integration (v0.2.0)
- **Phase 2**: Multi-File Instagram Processing (v0.3.0)
- **Phase 3**: Security Audit & Public Release (v0.3.1)
- **Phase 4**: Strands Agent Model Switching (v0.4.0) - COMPLETED August 2, 2025
- **Nova/Llama Phase 1**: Strands Compatibility Testing - COMPLETED February 2, 2025
- **Nova/Llama Phase 2**: Backend Multi-Model Integration - COMPLETED February 2, 2025

### 🎯 v0.4.0+ Multi-Model Achievements (February 2025)
- **6-Model Integration**: Successfully integrated 2 Claude + 2 Nova + 2 Llama models (100% success rate)
- **3-Family Support**: Anthropic Claude, Amazon Nova, Meta Llama all working via Strands
- **Performance Excellence**: Nova (986-1203ms), Llama (504-861ms), Claude (1242-1849ms)
- **Cost Optimization**: Nova models provide 75% cost savings vs Claude
- **Clean Architecture**: No complex parameter mapping needed - Strands handles internally
- **Educational Value**: Users can now compare responses across 3 different AI company approaches

### 🔄 Current Focus (Nova/Llama Phase 3)
- **Frontend Enhancement**: Adding Nova and Llama models to React interface
- **Model Categories**: Organizing models by AI family with cost/performance indicators
- **6-Model Comparison**: Enabling full comparison matrix across all families

## Important Files & Context

### Configuration Files (Python Backend)
- `template.yaml`: AWS SAM CloudFormation template (main infrastructure)
- `.env.example` & `.env.template`: Environment variable templates
- `requirements*.txt`: Python dependencies for different contexts

### Key Source Files (Python Backend)
- `src/agents/instagram_parser.py`: Main Instagram analysis agent (uses Strands)
- `src/api/multi_upload.py`: Multi-file ZIP processing endpoint
- `src/api/strands_model_switching.py`: **NEW v0.4.0** - Strands-based model switching and comparison
- `src/ai/providers.py`: Legacy AI provider abstraction layer (deprecated in v0.4.0)
- `layers/ai-providers/ai/providers.py`: Shared AI provider implementation

### Frontend Files (React)
- `frontend-demo/src/App.tsx`: Main React application
- `frontend-demo/src/components/`: React components
- `frontend-demo/src/services/feedminerApi.ts`: API integration
- `frontend-demo/package.json`: Node.js dependencies and scripts

### Documentation
- `docs/REAL_DATA_ANALYSIS_REPORT.md`: Successful real data testing results
- `docs/MULTI_FILE_INSTAGRAM_DATA.md`: Multi-file processing implementation
- `docs/TESTING_STRATEGY.md`: Comprehensive testing approach
- `docs/STRANDS_MODEL_SWITCHING.md`: **NEW v0.4.0** - Complete Strands implementation guide
- `SECURITY.md`: Security audit results (95% confidence, public-ready)

## Security & Public Release

- Repository underwent comprehensive security audit (July 31, 2025)
- All sensitive data uses environment variables or AWS parameter store
- Template files use generic examples (`first.last@company.com`)
- No hardcoded credentials, API keys, or PII exposure
- Ready for public contributions and community involvement

## Working with This Project

### When Adding Python Backend Features
1. **ALWAYS activate virtual environment first**: `source feedminer-env/bin/activate`
2. Follow existing patterns in `src/agents/` for AI processing
3. Add comprehensive tests in `tests/unit/` with fixtures
4. Update relevant documentation
5. Use the AI provider abstraction for consistency
6. Test with both Anthropic API and Bedrock if applicable

### When Adding React Frontend Features
1. **Work in `frontend-demo/` directory**
2. Use `npm install` for dependencies (no virtual environment needed)
3. Follow existing component patterns
4. Add tests using Vitest framework
5. Ensure TypeScript compliance
6. Test responsive design and accessibility

### When Modifying Infrastructure (Python Backend)
1. **ALWAYS activate virtual environment first**: `source feedminer-env/bin/activate`
2. Update `template.yaml` with proper parameterization
3. Build with linting: `sam build --lint`
4. Deploy without confirmation: `sam deploy --no-confirm-changeset`
5. Maintain environment-specific deployment capability
6. Follow AWS Well-Architected Framework principles

## AI Analysis Capabilities

The system processes Instagram exports using **6 AI models across 3 families** and provides:
- **Content Categorization**: Technology, fitness, business, etc.
- **Behavioral Pattern Analysis**: Interests, habits, goals
- **Goal-Setting Insights**: Specific, measurable recommendations
- **Temporal Analysis**: Activity patterns and consistency
- **Multi-Source Correlation**: Across saved posts, likes, comments, following
- **Cross-Family AI Comparison**: Compare Claude vs Nova vs Llama approaches

### Available AI Models (v0.4.0+)
**Anthropic Claude** (High capability, premium cost):
- `claude-3-5-sonnet-20241022` (Anthropic API)
- `anthropic.claude-3-5-sonnet-20241022-v2:0` (Bedrock)

**Amazon Nova** (Very low cost, fast, multimodal):
- `us.amazon.nova-micro-v1:0` (Ultra-fast, text-only)
- `us.amazon.nova-lite-v1:0` (Fast, text + multimodal)

**Meta Llama** (Low cost, efficient, open-source):
- `meta.llama3-1-8b-instruct-v1:0` (Efficient 8B model)
- `meta.llama3-1-70b-instruct-v1:0` (Capable 70B model)

Focus on goal-oriented analysis that helps users discover and achieve meaningful objectives based on their social media behavior patterns while comparing different AI approaches.