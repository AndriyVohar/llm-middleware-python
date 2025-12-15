# LLM Middleware Service - Clean Architecture

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A clean, well-structured FastAPI middleware service for interacting with multiple LLM providers (DeepInfra, OpenAI, Ollama) with text-based tool calling support.

## 🎯 Features

- **Multiple LLM Providers**: DeepInfra, OpenAI, Ollama
- **Text-based Tool Calling**: Automatic tool execution loop
- **Built-in Tools**: Calculator, Web Search, News Search, Web Scraper
- **Clean Architecture**: Proper separation of concerns
- **Type Safety**: Full type hints throughout
- **Error Handling**: Custom exceptions and proper error responses
- **Testing**: Pytest-based test suite
- **Docker Support**: Container-ready with docker-compose
- **Code Quality**: Black, Ruff, MyPy configured

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Development](#development)
- [Testing](#testing)
- [Architecture](#architecture)
- [Contributing](#contributing)

## 🚀 Quick Start

### Using Make (recommended)

```bash
# Install dependencies
make install

# Copy and configure environment
cp .env.example .env
# Edit .env with your API keys

# Run in development mode
make dev
```

### Using Docker

```bash
# Copy and configure environment
cp .env.example .env

# Start with docker-compose
make docker-up
```

Service will be available at `http://localhost:8000`

## 📦 Installation

### Prerequisites

- Python 3.12+
- pip or poetry
- (Optional) Docker and docker-compose
- (Optional) Ollama for local models

### Local Installation

```bash
# Clone repository
git clone <repository-url>
cd llm-middleware-python

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# For development
pip install -r requirements-dev.txt
```

## ⚙️ Configuration

### Environment Variables

Create `.env` file from template:

```bash
cp .env.example .env
```

Configure the following:

```env
# LLM Provider API Keys
DEEPINFRA_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here

# Provider Configuration
DEFAULT_PROVIDER=deepinfra
DEFAULT_MODEL=meta-llama/Llama-3.3-70B-Instruct-Turbo

# Ollama (for local models)
OLLAMA_BASE_URL=http://localhost:11434

# Logging
LOG_LEVEL=INFO
```

### Provider Setup

#### DeepInfra
1. Sign up at https://deepinfra.com
2. Get API key from dashboard
3. Set `DEEPINFRA_API_KEY` in `.env`

#### OpenAI
1. Sign up at https://platform.openai.com
2. Create API key
3. Set `OPENAI_API_KEY` in `.env`

#### Ollama (Local)
1. Install from https://ollama.ai
2. Start server: `ollama serve`
3. Pull model: `ollama pull qwen2.5:7b`

## 📖 Usage

### Start Server

```bash
# Development mode (auto-reload)
make dev

# Or directly with uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### API Examples

#### Simple Chat

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Hello!"}],
    "provider": "ollama"
  }'
```

#### Chat with Calculator

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Calculate 25 * 17 + 33"}],
    "provider": "ollama",
    "tools": ["calculator"]
  }'
```

#### Web Search

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Latest AI news"}],
    "provider": "ollama",
    "tools": ["news_search"]
  }'
```

## 📚 API Documentation

### Endpoints

- **GET /** - Root endpoint
- **GET /api/health** - Health check with system info
- **GET /api/providers** - List available providers
- **GET /api/tools** - List available tools
- **POST /api/chat** - Main chat endpoint
- **GET /api/docs** - Interactive API documentation (Swagger UI)
- **GET /api/redoc** - Alternative API documentation (ReDoc)

### Chat Request Schema

```json
{
  "messages": [
    {"role": "user", "content": "Your message"}
  ],
  "provider": "ollama",
  "model": "qwen2.5:7b",
  "tools": ["calculator", "web_search"],
  "temperature": 0.7,
  "max_tokens": 1000
}
```

### Chat Response Schema

```json
{
  "success": true,
  "message": {
    "role": "assistant",
    "content": "Response text"
  },
  "tool_calls_made": [
    {
      "tool": "calculator",
      "arguments": {"expression": "2+2"},
      "result": {"result": 4}
    }
  ],
  "usage": {
    "prompt_tokens": 150,
    "completion_tokens": 50,
    "total_tokens": 200
  },
  "provider": "ollama",
  "model": "qwen2.5:7b"
}
```

## 🛠️ Development

### Project Structure

```
llm-middleware-python/
├── app/
│   ├── core/              # Core functionality
│   │   ├── constants.py   # Application constants
│   │   ├── dependencies.py # FastAPI dependencies
│   │   ├── exceptions.py  # Custom exceptions
│   │   └── logging.py     # Logging configuration
│   ├── providers/         # LLM providers
│   │   ├── base.py
│   │   ├── deepinfra.py
│   │   ├── ollama.py
│   │   └── openai_provider.py
│   ├── routers/           # API routes
│   │   ├── chat.py
│   │   └── tools.py
│   ├── schemas/           # Pydantic models
│   │   ├── chat.py
│   │   └── tools.py
│   ├── services/          # Business logic
│   │   ├── llm_service.py
│   │   ├── prompt_builder.py
│   │   └── ...
│   ├── tools/             # Tool implementations
│   │   ├── base.py
│   │   ├── calculator.py
│   │   ├── web_search.py
│   │   └── ...
│   └── config.py          # Configuration
├── tests/                 # Test suite
├── main.py               # Application entry point
├── requirements.txt      # Production dependencies
├── requirements-dev.txt  # Development dependencies
├── pyproject.toml       # Project configuration
├── Makefile             # Development commands
└── Dockerfile           # Container definition
```

### Make Commands

```bash
make help          # Show all available commands
make install       # Install dependencies
make install-dev   # Install dev dependencies
make run           # Run application
make dev           # Run with auto-reload
make test          # Run tests
make lint          # Run linters
make format        # Format code
make clean         # Clean cache files
make docker-build  # Build Docker image
make docker-up     # Start containers
```

### Code Quality

The project uses:
- **Black** for code formatting
- **Ruff** for linting
- **MyPy** for type checking
- **Pytest** for testing

```bash
# Format code
make format

# Run linters
make lint

# Run tests
make test
```

## 🧪 Testing

### Run Tests

```bash
# All tests
make test

# Verbose output
make test-verbose

# With coverage
pytest --cov=app --cov-report=html
```

### Test Structure

```
tests/
├── conftest.py           # Test configuration and fixtures
├── test_main.py          # Test main endpoints
├── test_config.py        # Test configuration
├── test_prompt_builder.py # Test prompt utilities
└── ...
```

## 🏗️ Architecture

### Clean Architecture Principles

1. **Separation of Concerns**: Clear boundaries between layers
2. **Dependency Injection**: Services injected via FastAPI dependencies
3. **Abstract Base Classes**: Provider and tool interfaces
4. **Type Safety**: Full type hints throughout
5. **Error Handling**: Custom exceptions with proper error responses
6. **Logging**: Structured logging with proper log levels

### Key Components

#### Core Layer
- **Constants**: Application-wide constants
- **Exceptions**: Custom exception hierarchy
- **Dependencies**: FastAPI dependency injection
- **Logging**: Centralized logging configuration

#### Providers Layer
- Abstract `BaseLLMProvider` class
- Provider implementations (DeepInfra, OpenAI, Ollama)
- Unified interface for all LLM interactions

#### Services Layer
- **LLMService**: Orchestrates chat and tool calling
- **PromptBuilder**: Constructs prompts with tool descriptions
- **ToolExecutor**: Manages tool execution
- **WebIntelligence**: Web scraping and search services

#### Tools Layer
- Abstract `BaseTool` class
- Tool registry for dynamic tool management
- Built-in tools: Calculator, WebSearch, NewsSearch, WebScraper

### Tool Calling Flow

```
1. User sends chat request with tools
2. LLMService adds system prompt with tool descriptions
3. LLM generates response (may include tool call)
4. PromptBuilder parses tool call from response
5. Tool is executed with provided arguments
6. Result is added to conversation context
7. Loop continues until final response (max 10 iterations)
```

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linters (`make check`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Code Style

- Follow PEP 8 guidelines
- Use type hints
- Write docstrings for functions and classes
- Add tests for new features
- Keep functions focused and small

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- Pydantic for data validation
- All LLM providers (DeepInfra, OpenAI, Ollama)

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Check existing documentation
- Review API docs at `/api/docs`

---

**Note**: This is a refactored version with clean architecture principles, improved error handling, type safety, and comprehensive testing support.

