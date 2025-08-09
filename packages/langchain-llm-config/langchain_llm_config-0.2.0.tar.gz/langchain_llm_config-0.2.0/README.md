# Langchain LLM Config

Yet another redundant Langchain abstraction: comprehensive Python package for managing and using multiple LLM providers (OpenAI, VLLM, Gemini, Infinity) with a unified interface for both chat assistants and embeddings.

[![PyPI version](https://badge.fury.io/py/langchain-llm-config.svg)](https://badge.fury.io/py/langchain-llm-config) [![Python package](https://github.com/liux2/Langchain-LLM-Config/actions/workflows/python-package.yml/badge.svg?branch=main)](https://github.com/liux2/Langchain-LLM-Config/actions/workflows/python-package.yml)

## Features

- 🤖 **Multiple Chat Providers**: Support for OpenAI, VLLM, and Gemini
- 🔗 **Multiple Embedding Providers**: Support for OpenAI, VLLM, and Infinity
- ⚙️ **Unified Configuration**: Single YAML configuration file for all providers
- 🚀 **Easy Setup**: CLI tool for quick configuration initialization
- 🔄 **Easy Context Concatenation**: Simplified process for combining contexts into chat
- 🔒 **Environment Variables**: Secure API key management
- 📦 **Self-Contained**: No need to import specific paths
- ⚡ **Async Support**: Full async/await support for all operations
- 🌊 **Streaming Chat**: Real-time streaming responses for interactive experiences
- 🛠️ **Enhanced CLI**: Environment setup and validation commands
- 🪶 **Lightweight Core**: Minimal dependencies with optional provider-specific packages
- 🎯 **Flexible Installation**: Install only the providers you need

## Installation

### Basic Installation

The package has a lightweight core with optional dependencies for specific providers.

**Core installation (minimal dependencies):**

```bash
# Using uv (recommended)
uv add langchain-llm-config

# Using pip
pip install langchain-llm-config
```

### Provider-Specific Installation

**With OpenAI support:**

```bash
uv add "langchain-llm-config[openai]"
pip install "langchain-llm-config[openai]"
```

**With VLLM support:**

```bash
uv add "langchain-llm-config[vllm]"
pip install "langchain-llm-config[vllm]"
```

**With Gemini support:**

```bash
uv add "langchain-llm-config[gemini]"
pip install "langchain-llm-config[gemini]"
```

**With Infinity embeddings support:**

```bash
uv add "langchain-llm-config[infinity]"
pip install "langchain-llm-config[infinity]"
```

**With local models support (sentence-transformers):**

```bash
uv add "langchain-llm-config[local-models]"
pip install "langchain-llm-config[local-models]"
```

### Convenience Groups

**All assistant providers (OpenAI, VLLM, Gemini):**

```bash
uv add "langchain-llm-config[assistants]"
pip install "langchain-llm-config[assistants]"
```

**All embedding providers (Infinity, local models):**

```bash
uv add "langchain-llm-config[embeddings]"
pip install "langchain-llm-config[embeddings]"
```

**Everything (all providers and features):**

```bash
uv add "langchain-llm-config[all]"
pip install "langchain-llm-config[all]"
```

### Development Installation

```bash
git clone https://github.com/liux2/Langchain-LLM-Config.git
cd langchain-llm-config
uv sync --dev
uv run pip install -e .
```

## Dependency Optimization

This package is designed with a **lightweight core** approach:

### Core Dependencies (Always Installed)

- `langchain-core` - Core abstractions only (much lighter than full `langchain`)
- `langchain-openai` - OpenAI and VLLM provider support
- `pydantic` - Data validation and parsing
- `pyyaml` - Configuration file parsing
- `python-dotenv` - Environment variable management
- `openai` - OpenAI client library

### Optional Dependencies

- **Gemini**: `langchain-google-genai` - Only installed with `[gemini]` extra
- **Infinity**: `langchain-community` - Only installed with `[infinity]` extra
- **Local Models**: `sentence-transformers` - Only installed with `[local-models]` extra

### Benefits

- ✅ **Smaller installation size** - No heavy ML dependencies unless needed
- ✅ **Faster installation** - Skip unnecessary packages
- ✅ **Cleaner environments** - Only install what you use
- ✅ **Better compatibility** - Avoid conflicts from unused dependencies

## Quick Start

### 1. Initialize Configuration

```bash
# Initialize config in current directory
llm-config init

# Or specify a custom location
llm-config init ~/.config/api.yaml
```

This creates an `api.yaml` file with all supported providers configured.

### 2. Set Up Environment Variables

```bash
# Set up environment variables and create .env file
llm-config setup-env

# Or with custom config path
llm-config setup-env --config-path ~/.config/.env
```

This creates a `.env` file with placeholders for your API keys.

### 3. Configure Your Providers

Edit the generated `api.yaml` file with your API keys and settings:

```yaml
llm:
  openai:
    chat:
      api_base: "https://api.openai.com/v1"
      api_key: "${OPENAI_API_KEY}"
      model_name: "gpt-3.5-turbo"
      temperature: 0.7
      max_tokens: 8192
    embeddings:
      api_base: "https://api.openai.com/v1"
      api_key: "${OPENAI_API_KEY}"
      model_name: "text-embedding-ada-002"
  
  vllm:
    chat:
      api_base: "http://localhost:8000/v1"
      api_key: "${OPENAI_API_KEY}"
      model_name: "meta-llama/Llama-2-7b-chat-hf"
      temperature: 0.6
      extra_body:
        return_reasoning: false  # Set to true for reasoning output
  
  default:
    chat_provider: "openai"
    embedding_provider: "openai"
```

### 4. Set Environment Variables

Edit the `.env` file with your actual API keys:

```bash
OPENAI_API_KEY=your-openai-api-key
GEMINI_API_KEY=your-gemini-api-key
```

### 5. Use in Your Code

#### Basic Usage (Synchronous)

```python
from langchain_llm_config import create_assistant, create_embedding_provider
from pydantic import BaseModel, Field
from typing import List


# Define your response model
class ArticleAnalysis(BaseModel):
    summary: str = Field(..., description="Article summary")
    keywords: List[str] = Field(..., description="Key topics")
    sentiment: str = Field(..., description="Overall sentiment")


# Create an assistant without response model (raw text mode)
assistant = create_assistant(
    response_model=None,  # Explicitly set to None for raw text
    system_prompt="You are a helpful article analyzer.",
    provider="openai",  # or "vllm" (core), "gemini" (requires [gemini] extra)
    auto_apply_parser=False,
)

# Use the assistant for raw text output
print("=== Raw Text Mode ===")
result = assistant.ask("Analyze this article: ...")
print(result)

# Apply parser to the same assistant (modifies in place)
print("\n=== Applying Parser ===")
assistant.apply_parser(response_model=ArticleAnalysis)

# Now use the same assistant for structured output
print("\n=== Structured Mode ===")
result = assistant.ask("Analyze this article: ...")
print(result)

# Create an embedding provider
embedding_provider = create_embedding_provider(
    provider="openai"  # or "vllm" (core), "infinity" (requires [infinity] extra)
)

# Get embeddings (synchronous)
texts = ["Hello world", "How are you?"]
embeddings = embedding_provider.embed_texts(texts)
```

#### Advanced Usage (Asynchronous)

```python
import asyncio

# Use the assistant (asynchronous)
result = await assistant.ask_async("Analyze this article: ...")
print(result["summary"])

# Get embeddings (asynchronous)
embeddings = await embedding_provider.embed_texts_async(texts)
```

#### Streaming Chat

```python
import asyncio
from langchain_llm_config import create_chat_streaming


async def main():
    """Main async function to run the streaming chat example"""
    # Create streaming chat assistant
    # Try with OpenAI first to test streaming
    streaming_chat = create_chat_streaming(
        provider="vllm",
        system_prompt="You are a helpful assistant.",
        auto_apply_parser=False,
    )

    print("🤖 Starting streaming chat...")
    print("Response: ", end="", flush=True)

    try:
        # Stream responses in real-time
        async for chunk in streaming_chat.chat_stream("Tell me a story"):
            if chunk["type"] == "stream":
                print(chunk["content"], end="", flush=True)
            elif chunk["type"] == "final":
                print(f"\n\nProcessing time: {chunk['processing_time']:.2f}s")
                print(f"Model used: {chunk['model_used']}")
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")


if __name__ == "__main__":
    # Run the async function
    asyncio.run(main())
```

## Supported Providers

### Chat Providers

| Provider | Models | Features | Installation |
|----------|--------|----------|-------------|
| **OpenAI** | GPT-3.5, GPT-4, etc. | Streaming, function calling, structured output | ✅ Core (always available) |
| **VLLM** | Any HuggingFace model | Local deployment, high performance | ✅ Core (always available) |
| **Gemini** | Gemini Pro, etc. | Google's latest models | 📦 `[gemini]` extra required |

### Embedding Providers

| Provider | Models | Features | Installation |
|----------|--------|----------|-------------|
| **OpenAI** | text-embedding-ada-002, etc. | High quality, reliable | ✅ Core (always available) |
| **VLLM** | BGE, sentence-transformers | Local deployment | ✅ Core (always available) |
| **Infinity** | Various embedding models | Fast inference | 📦 `[infinity]` extra required |

## CLI Commands

```bash
# Initialize a new configuration file
llm-config init [path]

# Set up environment variables and create .env file
llm-config setup-env [path] [--force]

# Validate existing configuration
llm-config validate [path]

# Show package information
llm-config info
```

## Advanced Usage

### Custom Configuration Path

```python
from langchain_llm_config import create_assistant

assistant = create_assistant(
    response_model=MyModel,
    config_path="/path/to/custom/api.yaml"
)
```

### Context-Aware Conversations

```python
# Add context to your queries
result = await assistant.ask_async(
    query="What are the main points?",
    context="This is a research paper about machine learning...",
    extra_system_prompt="Focus on technical details."
)
```

### Direct Provider Usage

```python
from langchain_llm_config import VLLMAssistant, OpenAIEmbeddingProvider

# Core providers (always available)
vllm_assistant = VLLMAssistant(
    config={"api_base": "http://localhost:8000/v1", "model_name": "llama-2"},
    response_model=MyModel
)

openai_embeddings = OpenAIEmbeddingProvider(
    config={"api_key": "your-key", "model_name": "text-embedding-ada-002"}
)

# Optional providers (require extras)
# from langchain_llm_config import GeminiAssistant  # requires [gemini]
# from langchain_llm_config import InfinityEmbeddingProvider  # requires [infinity]
```

### Complete Example with Error Handling

```python
import asyncio
from langchain_llm_config import create_assistant, create_embedding_provider
from pydantic import BaseModel, Field
from typing import List

class ChatResponse(BaseModel):
    message: str = Field(..., description="The assistant's response message")
    confidence: float = Field(..., description="Confidence score", ge=0.0, le=1.0)
    suggestions: List[str] = Field(default_factory=list, description="Follow-up questions")

async def main():
    try:
        # Create assistant
        assistant = create_assistant(
            response_model=ChatResponse,
            provider="openai",
            system_prompt="You are a helpful AI assistant."
        )
        
        # Chat conversation
        response = await assistant.ask_async("What is the capital of France?")
        print(f"Assistant: {response['message']}")
        print(f"Confidence: {response['confidence']:.2f}")
        
        # Create embedding provider
        embedding_provider = create_embedding_provider(provider="openai")
        
        # Get embeddings
        texts = ["Hello world", "How are you?"]
        embeddings = await embedding_provider.embed_texts_async(texts)
        print(f"Generated {len(embeddings)} embeddings")
        
    except Exception as e:
        print(f"Error: {e}")

# Run the example
asyncio.run(main())
```

## Configuration Reference

### Environment Variables

The package supports environment variable substitution in configuration:

```yaml
api_key: "${OPENAI_API_KEY}"  # Will be replaced with actual value
```

### Configuration Structure

```yaml
llm:
  provider_name:
    chat:
      api_base: "https://api.example.com/v1"
      api_key: "${API_KEY}"
      model_name: "model-name"
      temperature: 0.7
      max_tokens: 8192
      top_p: 1.0
      connect_timeout: 60
      read_timeout: 60
      model_kwargs: {}
      extra_body:
        return_reasoning: false  # Enable reasoning output (vLLM)
      # ... other parameters
    embeddings:
      api_base: "https://api.example.com/v1"
      api_key: "${API_KEY}"
      model_name: "embedding-model"
      # ... other parameters
  default:
    chat_provider: "provider_name"
    embedding_provider: "provider_name"
```

## Development

### Testing with Different Provider Combinations

```bash
# Test core functionality only
uv sync --extra test
uv run pytest

# Test with all providers
uv sync --extra test --extra all
uv run pytest

# Test specific provider combinations
uv sync --extra test --extra gemini
uv run pytest tests/test_providers.py -k gemini
```

### Running Tests

```bash
uv run pytest
```

### Code Formatting

```bash
uv run black .
uv run isort .
```

### Type Checking

```bash
uv run mypy .
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

- 📖 [Documentation](https://github.com/liux2/Langchain-LLM-Config#readme)
- 🐛 [Issue Tracker](https://github.com/liux2/Langchain-LLM-Config/issues)
- 💬 [Discussions](https://github.com/liux2/Langchain-LLM-Config/discussions)
