"""Call Context Library

A Python context management library for applications with callback support.
"""

from .base import BaseCallContext
from .core import (
    CallContext,
    CallContextCallbackHandler,
    BaseCallContextExecutor,
    SyncCallContextExecutor,
    AsyncCallContextExecutor,
    StreamCallContextExecutor,
    InvokeCallContextExecutor,
)
from .logger import get_logger, set_log_level, disable_library_logging, enable_library_logging

__version__ = "0.2.5"
__all__ = [
    "CallContext",
    "CallContextCallbackHandler",
    "BaseCallContext",
    "BaseCallContextExecutor",
    "SyncCallContextExecutor",
    "AsyncCallContextExecutor",
    "StreamCallContextExecutor",
    "InvokeCallContextExecutor",
    "get_logger",
    "set_log_level",
    "disable_library_logging",
    "enable_library_logging",
]
