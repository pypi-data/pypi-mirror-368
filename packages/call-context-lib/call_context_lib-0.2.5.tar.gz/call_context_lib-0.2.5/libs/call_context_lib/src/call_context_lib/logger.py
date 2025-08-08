"""
Logging configuration for call_context_lib
"""

import logging
from typing import Optional


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for call_context_lib with appropriate configuration.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(f"call_context_lib.{name}")

    # Only configure if not already configured
    if not logger.handlers:
        # Don't add handlers if parent logger already has them
        if not logging.getLogger("call_context_lib").handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)

            # Add handler to root call_context_lib logger
            root_logger = logging.getLogger("call_context_lib")
            root_logger.addHandler(handler)
            root_logger.setLevel(logging.DEBUG)  # Default to DEBUG level
            root_logger.propagate = False  # Don't propagate to root logger

    return logger


def set_log_level(level: int) -> None:
    """
    Set the log level for all call_context_lib loggers.

    Args:
        level: Logging level (logging.DEBUG, logging.INFO, etc.)
    """
    root_logger = logging.getLogger("call_context_lib")
    root_logger.setLevel(level)


def disable_library_logging() -> None:
    """Disable all logging from call_context_lib"""
    logging.getLogger("call_context_lib").setLevel(logging.CRITICAL + 1)


def enable_library_logging(level: int = logging.DEBUG) -> None:
    """
    Enable logging from call_context_lib at specified level.

    Args:
        level: Logging level to enable
    """
    set_log_level(level)
