"""
Unit tests for FastAPI service functions
"""

import pytest
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock
import sys
import os

# Add parent directory to path for local development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "libs"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from service import (
    experiment_id,
    get_openai_invoke_example,
    get_openai_stream_example,
    get_openai_stream,
    get_llm_module_invoke_example,
)

from call_context_lib import CallContext


class TestServiceFunctions:
    """Test service layer functions"""

    def test_experiment_id(self):
        """Test experiment ID is set correctly"""
        assert experiment_id == "search-llm-ab-1"

    @pytest.mark.asyncio
    async def test_get_openai_invoke_example(self):
        """Test OpenAI invoke example with mocked LLM"""
        with (
            patch("service.acall_llm") as mock_acall_llm,
            patch("service.PrintExperimentLogger") as mock_logger_class,
        ):
            # Setup mocks
            mock_acall_llm.return_value = "Mocked response"
            mock_logger = MagicMock()
            mock_logger_class.return_value = mock_logger

            # Call function
            result = await get_openai_invoke_example()

            # Assertions
            assert result == {"result": "Mocked response"}
            mock_acall_llm.assert_called_once()

            # Check that PrintExperimentLogger was instantiated
            mock_logger_class.assert_called_once_with("experiment-topic")

    @pytest.mark.asyncio
    async def test_get_openai_stream_example(self):
        """Test OpenAI stream example with mocked LLM"""

        async def mock_stream(*args, **kwargs):
            """Mock async generator for streaming"""
            for chunk in ["Hello", " ", "World"]:
                yield chunk

        with (
            patch("service.acall_stream", new_callable=lambda: mock_stream),
            patch("service.PrintExperimentLogger") as mock_logger_class,
        ):
            mock_logger = MagicMock()
            mock_logger_class.return_value = mock_logger

            # Call function and collect stream results
            results = []
            async for chunk in get_openai_stream_example():
                results.append(chunk)

            # Assertions
            assert results == ["Hello", " ", "World"]
            mock_logger_class.assert_called_once_with("experiment-topic")

    @pytest.mark.asyncio
    async def test_get_openai_stream_with_params(self):
        """Test parameterized OpenAI stream with custom input and model"""

        async def mock_stream(*args, **kwargs):
            """Mock async generator for streaming"""
            input_text, model = args[0], args[1]
            for chunk in [f"Stream", "for", input_text, f"using", model]:
                yield chunk

        with (
            patch("service.acall_stream", new_callable=lambda: mock_stream),
            patch("service.PrintExperimentLogger") as mock_logger_class,
        ):
            mock_logger = MagicMock()
            mock_logger_class.return_value = mock_logger

            # Call function with custom parameters
            results = []
            async for chunk in get_openai_stream("Python", "gpt-3.5-turbo"):
                results.append(chunk)

            # Assertions
            assert "Stream" in results
            assert "Python" in results
            assert "gpt-3.5-turbo" in results
            mock_logger_class.assert_called_once_with("experiment-topic")

    @pytest.mark.asyncio
    async def test_get_llm_module_invoke_example(self):
        """Test LLM module invoke example with mocked functions"""
        with (
            patch("service.acall_llm") as mock_acall_llm,
            patch("service.call_llm") as mock_call_llm,
            patch("service.PrintExperimentLogger") as mock_logger_class,
        ):
            # Setup mocks
            mock_acall_llm.return_value = "Async JavaScript response"
            mock_call_llm.return_value = "Sync TypeScript response"
            mock_logger = MagicMock()
            mock_logger_class.return_value = mock_logger

            # Call function
            result = await get_llm_module_invoke_example()

            # Assertions
            assert result == {
                "async_result": "Async JavaScript response",
                "sync_result": "Sync TypeScript response",
            }
            mock_acall_llm.assert_called_once()
            mock_call_llm.assert_called_once()
            mock_logger_class.assert_called_once_with("experiment-topic")


class TestCallContextIntegration:
    """Test CallContext integration in service functions"""

    @pytest.mark.asyncio
    async def test_context_creation_and_metadata(self):
        """Test that CallContext is created and metadata is set properly"""
        with (
            patch("service.acall_llm") as mock_acall_llm,
            patch("service.call_llm") as mock_call_llm,
            patch("service.PrintExperimentLogger") as mock_logger_class,
        ):
            # Setup mocks
            mock_acall_llm.return_value = "Test response"
            mock_call_llm.return_value = "Test response"
            mock_logger = MagicMock()
            mock_logger_class.return_value = mock_logger

            # Call function that creates CallContext
            await get_llm_module_invoke_example()

            # Verify PrintExperimentLogger was created and set_context was called
            mock_logger_class.assert_called_once_with("experiment-topic")
            mock_logger.set_context.assert_called_once()

            # Get the context that was passed to set_context
            call_args = mock_logger.set_context.call_args[0]
            ctx = call_args[0]

            # Verify context properties
            assert isinstance(ctx, CallContext)
            assert ctx.user_id == "kim"
            assert ctx.turn_id == "t005"
            assert ctx.meta.get("model") == "gpt-4"
            assert ctx.meta.get("experiment_id") == experiment_id

    @pytest.mark.asyncio
    async def test_callback_integration(self):
        """Test that callbacks are properly integrated with LLM calls"""
        with (
            patch("service.acall_llm") as mock_acall_llm,
            patch("service.PrintExperimentLogger") as mock_logger_class,
        ):
            mock_acall_llm.return_value = "Test response"
            mock_logger = MagicMock()
            mock_logger_class.return_value = mock_logger

            await get_openai_invoke_example()

            # Verify that acall_llm was called with callbacks parameter
            mock_acall_llm.assert_called_once()
            call_kwargs = mock_acall_llm.call_args[1]

            # Check that callbacks parameter exists and contains expected callbacks
            assert "callbacks" in call_kwargs
            callbacks = call_kwargs["callbacks"]
            assert len(callbacks) == 2  # CallContextCallbackHandler + PrintExperimentLogger
