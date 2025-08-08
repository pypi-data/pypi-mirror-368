# Call Context Lib

[![CI](https://github.com/jitokim/call-context-lib/actions/workflows/ci.yml/badge.svg)](https://github.com/jitokim/call-context-lib/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/call-context-lib.svg)](https://badge.fury.io/py/call-context-lib)
[![Python](https://img.shields.io/pypi/pyversions/call-context-lib.svg)](https://pypi.org/project/call-context-lib/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python context management library designed for LLM applications with LangChain callback integration. Manage execution context, metadata, and experiment logging seamlessly across your AI application stack using standard LangChain callback patterns.

## Features

- **Context Management**: Track user sessions, turns, and metadata across function calls
- **LangChain Integration**: Native support for LangChain's BaseCallbackHandler pattern
- **Async Support**: Full support for async/await patterns and async generators
- **Callback System**: Execute callbacks on context completion with standard LangChain interface
- **Metadata Handling**: Store and retrieve metadata with support for multiple values per key
- **Streaming Support**: Built-in support for streaming responses with context preservation
- **Type Safety**: Fully typed with Python type hints

## Installation

```bash
pip install call-context-lib
```

For development:

```bash
pip install call-context-lib[dev]
```

## Quick Start

### Basic Usage with LangChain Integration

```python
from call_context_lib import CallContext, CallContextCallbackHandler
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

# Create a context
ctx = CallContext(user_id="user123", turn_id="turn456")

# Set metadata
ctx.set_meta("request_type", "chat")
ctx.set_meta("model", "gpt-4")

# Create LangChain callback with context
callback = CallContextCallbackHandler(ctx)

# Use with LangChain LLM
llm = ChatOpenAI(model="gpt-4", callbacks=[callback])
result = await llm.ainvoke([HumanMessage(content="Hello")])

# Complete context callbacks
await ctx.on_complete()
```

### Streaming Support with LangChain

```python
from call_context_lib import CallContext, CallContextCallbackHandler
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

async def stream_with_context(input_text: str):
    ctx = CallContext(user_id="user123", turn_id="turn456")
    ctx.set_meta("model", "gpt-4")
    
    # Create callback with context
    callback = CallContextCallbackHandler(ctx)
    
    # Stream with LangChain
    llm = ChatOpenAI(model="gpt-4", streaming=True, callbacks=[callback])
    async for chunk in llm.astream([HumanMessage(content=input_text)]):
        if chunk.content:
            yield chunk.content
    
    # Complete context callbacks
    await ctx.on_complete()

# Usage
async for token in stream_with_context("Tell me about Python"):
    print(token, end="")
```

### Multiple Callback Pattern

```python
from call_context_lib import CallContext, CallContextCallbackHandler
from langchain_core.callbacks import BaseCallbackHandler
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

# Custom experiment logging callback
class ExperimentLogger(BaseCallbackHandler):
    def __init__(self, ctx: CallContext):
        self.ctx = ctx
    
    def on_llm_end(self, response, **kwargs):
        print(f"Experiment completed for user {self.ctx.get_user_id()}")
        print(f"Model: {self.ctx.get_meta('model')}")

async def multi_callback_example():
    ctx = CallContext(user_id="user123", turn_id="turn456")
    ctx.set_meta("model", "gpt-4")
    
    # Combine multiple callbacks
    callbacks = [
        CallContextCallbackHandler(ctx),
        ExperimentLogger(ctx)
    ]
    
    llm = ChatOpenAI(model="gpt-4", callbacks=callbacks)
    result = await llm.ainvoke([HumanMessage(content="Hello")])
    
    await ctx.on_complete()
    return result
```

### Multiple Values for Same Key

```python
ctx.set_meta("tag", "python")
ctx.set_meta("tag", "async")
ctx.set_meta("tag", "context")

# Get the most recent value
latest_tag = ctx.get_meta("tag")  # Returns "context"

# Get all values
all_tags = ctx.get_meta("tag", all_values=True)  # Returns ["python", "async", "context"]
```

## API Reference

### CallContext

The main context class that manages execution state and metadata.

#### Constructor

```python
CallContext(user_id: str, turn_id: str, meta: dict = None, callbacks: list = None)
```

#### Methods

- `get_user_id() -> str`: Get the user ID
- `get_turn_id() -> str`: Get the turn ID  
- `get_meta(key: str, all_values: bool = False) -> Any`: Get metadata value(s)
- `set_meta(key: str, value: Any) -> None`: Set metadata value
- `set_error(error: Exception)`: Set error state
- `on_complete() -> None`: Execute all registered callbacks

### CallContextCallbackHandler

LangChain BaseCallbackHandler integration for context management.

```python
from call_context_lib import CallContextCallbackHandler

# Create callback handler with context
ctx = CallContext(user_id="user123", turn_id="turn456")
callback = CallContextCallbackHandler(ctx)

# Use with any LangChain component
llm = ChatOpenAI(callbacks=[callback])
```

#### Callback Methods

- `on_llm_start(*args, **kwargs)`: Called when LLM starts
- `on_llm_end(response, **kwargs)`: Called when LLM completes
- `on_llm_error(error, **kwargs)`: Called when LLM encounters error

## Examples

The `examples/` directory contains practical examples:

- **FastAPI Integration**: How to use the library with FastAPI streaming applications
- **LangChain Callback Integration**: Examples using CallContextCallbackHandler with LangChain LLMs
- **Custom Experiment Logging**: Implementing custom BaseCallbackHandler for experiment tracking
- **Multiple Callback Patterns**: Combining context callbacks with other LangChain callbacks

### Running Examples

```bash
# Install dependencies
cd examples
uv sync

# Set your OpenAI API key
export OPENAI_API_KEY="your-api-key"

# Run the FastAPI server
python -m uvicorn main:app --reload --port 8001
```

### Example API Endpoints

- `POST /openai-stream-example`: Streaming LLM response with context
- `POST /openai-invoke-example`: Single LLM response with context
- `POST /llm-module-stream-example`: Custom LLM module streaming
- `POST /llm-module-invoke-example`: Custom LLM module invoke

## Development

### Setting up development environment

```bash
# Clone the repository
git clone https://github.com/jitokim/call-context-lib.git
cd call-context-lib

# Install development dependencies
make install-dev

# Run tests
make test

# Run linting
make lint

# Format code
make format
```

### Available Make Commands

- `make install` - Install package
- `make install-dev` - Install with development dependencies  
- `make test` - Run tests
- `make test-cov` - Run tests with coverage
- `make lint` - Run linting
- `make format` - Format code
- `make build` - Build package
- `make publish` - Publish to PyPI
- `make clean` - Clean build artifacts

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes and version history.

## Support

If you encounter any problems or have questions, please [open an issue](https://github.com/jitokim/call-context-lib/issues) on GitHub.