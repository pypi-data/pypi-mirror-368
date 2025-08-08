# Call Context Library

A Python context management library for applications with callback support.

## Features

- CallContext for managing user and turn IDs with metadata
- CallContextExecutor classes for different execution patterns
- Support for sync/async/streaming operations
- Built-in callback system

## Installation

```bash
pip install call-context-lib
```

## Usage

```python
from call_context_lib import CallContext, SyncCallContextExecutor

ctx = CallContext(user_id="user123", turn_id="turn456")
executor = SyncCallContextExecutor()

result = executor.execute(ctx, your_function)
```