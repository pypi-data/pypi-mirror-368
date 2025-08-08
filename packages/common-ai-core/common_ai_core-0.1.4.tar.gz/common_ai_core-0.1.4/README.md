# Common AI Core

A flexible Python framework for building AI chat applications with support for multiple LLM providers.

## Features

- 🤖 Support for multiple LLM providers:
  - OpenAI (GPT-3.5, GPT-4) - included by default
  - Anthropic (Claude) - optional
  - Llama (local models) - optional
- 💾 Flexible memory management:
  - Token-based memory limits
  - Prompt-based memory limits
  - System prompt preservation
- 🔄 Multiple chat modes:
  - Streaming responses
  - Completion responses
- 📊 Token counting and cost estimation
- 🎨 Pretty-printed chat history
- 🔍 Content parsing utilities:
  - JSON structure extraction from LLM outputs
  - Python code parsing

## Installation

```bash
# Install the complete framework (includes all features, OpenAI provider ready to use)
pip install common-ai-core

# Add support for Anthropic's Claude (requires anthropic package)
pip install "common-ai-core[anthropic]"

# Add support for Google's Gemini (requires google-generativeai package)
pip install "common-ai-core[gemini]"

# Add support for DeepSeek (uses OpenAI client, no extra package needed)
pip install "common-ai-core[deepseek]"

# Install with all cloud providers (OpenAI, Anthropic, Gemini, DeepSeek)
pip install "common-ai-core[all-cloud]"

# Add support for local Llama models (requires llama-cpp-python package)
pip install "common-ai-core[llama]"

# Install with all providers including Llama
pip install "common-ai-core[all]"

# Development installation (includes testing tools)
pip install "common-ai-core[dev]"
```

## Quick Start

```python
from common_ai_core import ProviderBuilder, ProviderType, SystemTokenLimitedMemory, CompletionChat

# Create a provider (using OpenAI by default)
provider = ProviderBuilder(ProviderType.OPENAI).build()

# Create memory with system prompt
memory = SystemTokenLimitedMemory.from_provider(
    provider=provider,
    system_prompt="You are a helpful assistant.",
    max_tokens=1000
)

# Create chat interface
chatbot = CompletionChat(provider, memory)

# Chat!
response = chatbot.chat("Tell me about Python!")
print(response)
```

## Memory Types

- `TokenLimitedMemory`: Limits conversation by token count
- `PromptLimitedMemory`: Limits conversation by number of exchanges
- `SystemTokenLimitedMemory`: Token-limited with preserved system prompt
- `SystemPromptLimitedMemory`: Prompt-limited with preserved system prompt

## Providers

- **OpenAI** (included by default)
  - Supports GPT-4o-mini (default), GPT-4o, and GPT-3.5 models
  - Includes token counting
  - Streaming support

- **Anthropic** (optional)
  - Supports Claude models
  - Install with: `pip install "common-ai-core[anthropic]"`
  ```python
  provider = ProviderBuilder(ProviderType.ANTHROPIC).build()
  ```

- **Llama** (optional)
  - Supports local models
  - Install with: `pip install "common-ai-core[llama]"`
  ```python
  provider = (ProviderBuilder(ProviderType.LLAMA)
             .set_model_path("path/to/model.gguf")
             .build())
  ```

- **DeepSeek** (optional)
  - Supports DeepSeek models including reasoning models
  - Install with: `pip install "common-ai-core[deepseek]"`
  ```python
  provider = ProviderBuilder(ProviderType.DEEPSEEK).build()
  ```

- **Gemini** (optional)
  - Supports Google's Gemini models
  - Install with: `pip install "common-ai-core[gemini]"`
  ```python
  provider = ProviderBuilder(ProviderType.GEMINI).build()
  ```

## Error Handling

Common AI Core provides clear error messages when optional dependencies are missing:

```python
from common_ai_core import ProviderBuilder, ProviderType

try:
    # This will work if you have openai installed
    provider = ProviderBuilder(ProviderType.OPENAI).build()
    print("OpenAI provider created successfully!")
except Exception as e:
    print(f"Error: {e}")

try:
    # This will fail with a clear message if anthropic is not installed
    provider = ProviderBuilder(ProviderType.ANTHROPIC).build()
except Exception as e:
    print(f"Error: {e}")
    # Output: Error: Anthropic package not installed: No module named 'anthropic'
    # Solution: pip install "common-ai-core[anthropic]"
```

## Parsers

Common AI Core includes utilities for parsing and extracting structured content from LLM outputs:

### JSON Parser

Extract valid JSON structures from LLM text outputs:

```python
from common_ai_core.parsers.json_parser import JsonParser

# Extract JSON from LLM output
llm_output = """This is some text with embedded JSON: 
{\"key\": \"value\", \"nested\": {\"data\": 123}} 
and more text after."""

parser = JsonParser(llm_output)
json_objects = parser.extract_json_structures()

# Process extracted JSON objects
for json_obj in json_objects:
    print(json_obj)  # {'key': 'value', 'nested': {'data': 123}}
```

The JSON parser can extract JSON objects even when they're embedded in markdown code blocks or surrounded by other text.

## Development

```bash
# Clone the repository
git clone https://github.com/commonai/common-ai-core.git

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
