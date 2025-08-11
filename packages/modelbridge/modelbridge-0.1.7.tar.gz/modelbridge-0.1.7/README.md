# ModelBridge

[![PyPI version](https://badge.fury.io/py/modelbridge.svg)](https://badge.fury.io/py/modelbridge)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

**Simple Multi-Provider LLM Gateway**

ModelBridge is a Python library that provides unified access to multiple AI providers. It simplifies working with OpenAI, Anthropic, Google, and Groq APIs through a single interface.

## ✨ What it Does

- **Multi-Provider Support**: Works with OpenAI, Groq, Google, and Anthropic
- **Smart Model Selection**: Automatically picks models based on your task
- **Cost Tracking**: Shows you how much each request costs
- **Simple API**: One function (`ask`) for most use cases
- **Environment Variables**: Secure API key management

## 🚀 Quick Start

### Installation

```bash
pip install modelbridge
```

### Basic Usage

```python
import asyncio
from modelbridge.simple import ask

# Set your API keys as environment variables:
# export OPENAI_API_KEY='your_openai_key'
# export GROQ_API_KEY='your_groq_key'

async def main():
    response = await ask("What is the capital of France?")
    print(f"Answer: {response.content}")
    print(f"Model: {response.model_id}")
    print(f"Provider: {response.provider_name}")
    print(f"Cost: ${response.cost:.4f}")

asyncio.run(main())
```

### Advanced Usage

```python
# Specify a particular model
response = await ask("Write Python code", model="gpt-4")

# Optimize for speed, cost, or quality
response = await ask("Simple math", optimize_for="cost")
response = await ask("Complex analysis", optimize_for="quality")

# Set maximum cost limit
response = await ask("Quick question", max_cost=0.001)

# Other useful functions
from modelbridge.simple import code, translate, summarize

# Generate code
response = await code("Create a sorting function", language="python")

# Translate text
response = await translate("Hello world", "Spanish")

# Summarize text
response = await summarize("Long article text here...", length="short")
```

## Configuration

### API Keys

Set your API keys as environment variables:

```bash
# Add the providers you want to use
export OPENAI_API_KEY='sk-your-openai-key'
export GROQ_API_KEY='gsk_your-groq-key'
export GOOGLE_API_KEY='your-google-key'
export ANTHROPIC_API_KEY='sk-ant-your-anthropic-key'
```

You need at least one API key for ModelBridge to work.

## Supported Providers

- **OpenAI**: GPT-4, GPT-3.5-turbo, GPT-5-mini
- **Groq**: Llama 3.3 (very fast)
- **Google**: Gemini models
- **Anthropic**: Claude models

## How It Works

1. You call `ask("your question")`
2. ModelBridge analyzes your prompt
3. It picks the best model for the task
4. Returns response with cost tracking
5. Automatically handles errors and retries

## License

MIT License

---

**Simple AI provider integration.**