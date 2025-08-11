# RAGVenture
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![LangChain](https://img.shields.io/badge/powered%20by-LangChain-blue.svg)](https://github.com/hwchase17/langchain)
[![Sentence Transformers](https://img.shields.io/badge/powered%20by-Sentence%20Transformers-blue.svg)](https://www.sbert.net/)
[![CI](https://github.com/valginer0/rag_startups/actions/workflows/ci.yml/badge.svg)](https://github.com/valginer0/rag_startups/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/valginer0/rag_startups/graph/badge.svg)](https://codecov.io/gh/valginer0/rag_startups)

RAGVenture is an intelligent startup idea generator powered by Retrieval-Augmented Generation (RAG). It helps entrepreneurs generate innovative startup ideas by learning from successful companies, combining the power of large language models with real-world startup data.

## Why RAGVenture?

Traditional startup ideation tools either rely on expensive API calls or generate ideas without real-world context. RAGVenture solves this by:
- **Completely FREE**: Runs entirely on your machine with no API costs - zero API keys required!
- **Smart Model Management**: Automatically handles model deprecation and failures with intelligent fallback
- **Data-Driven**: Learns from real startup data to ground suggestions in reality
- **Context-Aware**: Understands patterns from successful startups
- **Intelligent**: Uses RAG to combine LLM capabilities with precise information retrieval
- **Resilient**: Works offline with local models when external APIs are unavailable
- **Production-Ready**: 177 tests with comprehensive coverage, Docker runtime fixes, and monitoring

## System Requirements

- Python 3.11 or higher
- 8GB RAM minimum (16GB recommended)
- 2GB disk space for models and data
- Operating Systems:
  - Linux (recommended)
  - macOS
  - Windows (with WSL for best performance)

## Quick Start

1. **Installation**:
```bash
# Clone the repository
git clone https://github.com/valginer0/RAGVenture.git
cd RAGVenture

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On Unix or MacOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install spaCy language model for market analysis
python -m spacy download en_core_web_sm
```

2. **Environment Setup** (Optional - system works completely FREE without any setup!):
```bash
# Optional: HuggingFace token for enhanced remote models (system works completely FREE without it)
export HUGGINGFACE_TOKEN="your-token-here"  # Get from huggingface.co

# Smart model management (enabled by default)
export RAG_SMART_MODELS=true
export RAG_MODEL_CHECK_INTERVAL=3600
export RAG_MODEL_TIMEOUT=60

# Optional: LangChain tracing (debugging)
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
export LANGCHAIN_API_KEY="your-langsmith-api-key"
export LANGCHAIN_PROJECT="your-project-name"
```

3. **Generate Ideas**:
```bash
# Generate 3 startup ideas in the AI domain
python -m rag_startups.cli generate-all "AI" --num-ideas 3

# Generate ideas without market analysis
python -m rag_startups.cli generate-all "fintech" --num-ideas 2 --no-market

# Check model health and status
python -m rag_startups.cli models status

# Use custom startup data file
python -m rag_startups.cli generate-all "education" --file custom_startups.json
```

## Features & Capabilities

### Core Features
- Intelligent Idea Generation:
  - Uses RAG to combine LLM knowledge with real startup data
  - Generates contextually relevant and grounded ideas
  - Provides structured output with problem, solution, and market analysis

### Command-Line Interface
Commands:
- `generate-all`: Generate startup ideas with market analysis
  - Required argument: Topic or domain (e.g., "AI", "fintech")
  - Options:
    - `--num-ideas`: Number of ideas (1-5, default: 1)
    - `--file`: Custom startup data file (default: yc_startups.json)
    - `--market/--no-market`: Include/exclude market analysis
    - `--temperature`: Model creativity (0.0-1.0)
    - `--print-examples`: Show relevant examples

### Smart Model Management
- **Automatic Fallback**: Falls back to local models when external APIs fail
- **Model Migration Intelligence**: Handles model deprecation (e.g., Mistral v0.2→v0.3) automatically
- **Health Monitoring**: Continuous model health checks and status reporting
- **Local Resilience**: Works completely offline with local models
- **CLI Management**: `models` command for status, testing, and diagnostics

### Technical Features
- Smart Analysis:
  - Semantic search for relevant examples
  - Automatic metadata extraction
  - Pattern recognition from successful startups
- Performance Optimized:
  - One-time embedding generation (~22s)
  - Fast idea generation (~0.5s per idea)
  - Efficient data processing (~0.1s load time)
- Production Quality:
  - 31 comprehensive unit tests
  - Automated code formatting
  - Extensive error handling

## Performance

Typical processing times on a standard machine:
- Initial Setup: ~22s (one-time embedding generation)
- Data Loading: ~0.1s
- Idea Generation: ~0.5s per idea

## Docker Support

For containerized deployment, we provide both CPU and GPU support.

### Prerequisites
- Docker and Docker Compose
- For GPU support:
  - NVIDIA GPU with CUDA
  - NVIDIA Container Toolkit
  - nvidia-docker2

### Quick Start with Docker
```bash
# CPU Version (recommended - fully tested)
docker-compose up app-cpu

# GPU Version (with NVIDIA support)
docker-compose up app-gpu

# Run with custom data file
docker-compose run --rm app-cpu python -m rag_startups.cli generate-all fintech --num-ideas 1 --file /app/yc_startups.json
```

**Docker Status**: ✅ **Production Ready** - All runtime issues resolved, works end-to-end with real data.

## Development Setup

1. Clone and setup:
```bash
git clone https://github.com/valginer0/RAGVenture.git
cd RAGVenture
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install development dependencies:
```bash
pip install -r requirements.txt
pre-commit install  # Sets up automatic code formatting
```

3. Run tests:
```bash
pytest tests/  # Should show 178 passing tests
```

### Testing & Offline Policy

This project enforces fully offline, deterministic tests:

- Tests block outbound HTTP(S) by default via an autouse fixture in `tests/conftest.py` that patches `requests.sessions.Session.request`.
- Autouse fixtures also mock model-loading/network paths:
  - `huggingface_hub.model_info` in `rag_startups/cli.py` preflight
  - `transformers.pipeline` at all call sites (e.g., `rag_startups.embed_master`, `rag_startups.core.rag_chain`, CLI)
  - `huggingface_hub.InferenceClient` and the bound imports used by `rag_startups/idea_generator/generator.py`
  - `rag_startups.embed_master.calculate_result` is replaced with a deterministic helper during tests
- Offline env vars are forced: `HUGGINGFACE_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`.
- To explicitly allow network in a specific test, add the marker: `@pytest.mark.allow_network`.

Runtime (non-test) CLI runs are allowed to use the network and will honor your `.env`.

## Data Requirements

RAGVenture works with startup data in JSON format. Two options:

1. Use YC Data (Recommended):
   - Download from [Y Combinator](https://www.ycombinator.com/companies)
   - Convert CSV to JSON:
     ```bash
     python -m rag_startups.data.convert_yc_data input.csv -o startups.json
     ```

2. Use Custom Data:
   - Prepare JSON file with required fields
   - See `docs/data_format.md` for schema

## Troubleshooting

1. Embedding Generation Time:
   - First run takes ~22s to generate embeddings
   - Subsequent runs use cached embeddings
   - GPU can significantly speed up this process

2. Common Issues:
   - Missing HUGGINGFACE_TOKEN: Sign up at huggingface.co
   - Memory errors: Reduce batch size with --max-lines
   - GPU errors: Ensure CUDA toolkit is properly installed

## Documentation

- `docs/api.md`: API documentation
- `docs/examples.md`: Usage examples
- `docs/data_format.md`: Data schema
- `CONTRIBUTING.md`: Development guidelines

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

## Startup Names and Legal Considerations

### Name Generation
- Each generated startup name includes a unique identifier (e.g., "TechStartup-x7y9z")
- This identifier ensures technical uniqueness within the tool
- The unique identifier is NOT a substitute for legal name verification

### Important Notes for Users
- Generated names are suggestions only
- The uniqueness of a name at generation time does not guarantee its availability
- Users must perform their own due diligence before using any name

### Name Verification Resources
- USPTO Trademark Database: https://www.uspto.gov/trademarks
- State Business Registries
- Domain Name Availability Tools
- Professional Legal Counsel

### Future Features
- Name availability checking tool (planned)
- Integration with business registry APIs
