#!/usr/bin/env python3
"""
Tests for simple CallContext examples

This module tests the A/B testing and LLM integration examples.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from main import (
    ABTestLLMSelector,
    PrintExperimentCallback,
    call_llm,
    acall_llm,
    call_llm_stream,
    acall_llm_stream,
    sync_example,
    async_example,
    invoke_example,
    stream_example,
    async_stream_example,
)
from call_context_lib import CallContext, CallContextCallbackHandler


class TestABTestLLMSelector:
    """Test A/B testing LLM selector"""

    def test_consistent_selection(self):
        """Test that the same user always gets the same model"""
        selector = ABTestLLMSelector()

        # Same user should always get the same model
        user_id = "test_user_123"
        model1 = selector.get_model_for_user(user_id)
        model2 = selector.get_model_for_user(user_id)
        model3 = selector.get_model_for_user(user_id)

        assert model1 == model2 == model3
        assert model1 in ["gpt-4", "gpt-3.5-turbo"]

    def test_distribution(self):
        """Test that models are distributed across users"""
        selector = ABTestLLMSelector()

        # Test with many users to see distribution
        models = []
        for i in range(100):
            user_id = f"user_{i}"
            model = selector.get_model_for_user(user_id)
            models.append(model)

        # Both models should appear
        unique_models = set(models)
        assert len(unique_models) >= 2
        assert "gpt-4" in unique_models
        assert "gpt-3.5-turbo" in unique_models

    def test_hash_consistency(self):
        """Test that hash-based selection is consistent"""
        selector = ABTestLLMSelector()

        # Test specific known values to ensure consistency
        # These should be stable across runs
        test_cases = [
            ("user_123", selector.get_model_for_user("user_123")),
            ("user_456", selector.get_model_for_user("user_456")),
            ("user_789", selector.get_model_for_user("user_789")),
        ]

        # Run multiple times to ensure consistency
        for user_id, expected_model in test_cases:
            for _ in range(10):
                assert selector.get_model_for_user(user_id) == expected_model


class TestPrintExperimentCallback:
    """Test the experiment callback handler"""

    def test_callback_initialization(self):
        """Test callback handler initialization"""
        ctx = CallContext(user_id="test_user", turn_id="test_turn")
        callback = PrintExperimentCallback(ctx)

        assert callback.ctx == ctx
        assert isinstance(callback, CallContextCallbackHandler)


class TestCallLLM:
    """Test call_llm function"""

    @patch.dict("os.environ", {}, clear=True)
    def test_call_llm_without_api_key(self):
        """Test call_llm without API key (uses mock)"""
        ctx = CallContext(user_id="test_user", turn_id="test_turn")
        ctx.set_meta("selected_model", "gpt-4")

        result = call_llm(ctx, "Python")

        assert isinstance(result, str)
        assert len(result) > 0
        assert ctx.get_meta("input") == "Python"
        assert ctx.get_meta("response") is not None

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test_key"})
    @patch("main.ChatOpenAI")
    def test_call_llm_with_api_key(self, mock_chat_openai):
        """Test call_llm with API key (mocked OpenAI)"""
        # Mock the ChatOpenAI instance and its invoke method
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = "Mocked GPT response"
        mock_llm.invoke.return_value = mock_response
        mock_chat_openai.return_value = mock_llm

        ctx = CallContext(user_id="test_user", turn_id="test_turn")
        ctx.set_meta("selected_model", "gpt-4")

        result = call_llm(ctx, "Python")

        assert result == "Mocked GPT response"
        assert ctx.get_meta("input") == "Python"
        assert ctx.get_meta("response") == "Mocked GPT response"

        # Verify ChatOpenAI was called with correct parameters
        mock_chat_openai.assert_called_once()
        call_args = mock_chat_openai.call_args
        assert call_args[1]["model"] == "gpt-4"
        assert call_args[1]["api_key"] == "test_key"


class TestAsyncCallLLM:
    """Test async call_llm function"""

    @pytest.mark.asyncio
    @patch.dict("os.environ", {}, clear=True)
    async def test_acall_llm_without_api_key(self):
        """Test acall_llm without API key (uses mock)"""
        ctx = CallContext(user_id="test_user", turn_id="test_turn")
        ctx.set_meta("selected_model", "gpt-3.5-turbo")

        result = await acall_llm(ctx, "JavaScript")

        assert isinstance(result, str)
        assert len(result) > 0
        assert ctx.get_meta("input") == "JavaScript"
        assert ctx.get_meta("response") is not None

    @pytest.mark.asyncio
    @patch.dict("os.environ", {"OPENAI_API_KEY": "test_key"})
    @patch("main.ChatOpenAI")
    async def test_acall_llm_with_api_key(self, mock_chat_openai):
        """Test acall_llm with API key (mocked OpenAI)"""
        # Mock the ChatOpenAI instance and its ainvoke method
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = "Async mocked GPT response"
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)
        mock_chat_openai.return_value = mock_llm

        ctx = CallContext(user_id="test_user", turn_id="test_turn")
        ctx.set_meta("selected_model", "gpt-3.5-turbo")

        result = await acall_llm(ctx, "JavaScript")

        assert result == "Async mocked GPT response"
        assert ctx.get_meta("input") == "JavaScript"
        assert ctx.get_meta("response") == "Async mocked GPT response"


class TestStreamingCalls:
    """Test streaming LLM calls"""

    def test_call_llm_stream_without_api_key(self):
        """Test streaming call without API key"""
        ctx = CallContext(user_id="test_user", turn_id="test_turn")
        ctx.set_meta("selected_model", "gpt-4")

        chunks = list(call_llm_stream(ctx, "Rust"))

        assert len(chunks) > 0
        assert all(isinstance(chunk, str) for chunk in chunks)
        assert ctx.get_meta("input") == "Rust"
        assert ctx.get_meta("response") is not None

    @pytest.mark.asyncio
    async def test_acall_llm_stream_without_api_key(self):
        """Test async streaming call without API key"""
        ctx = CallContext(user_id="test_user", turn_id="test_turn")
        ctx.set_meta("selected_model", "gpt-3.5-turbo")

        chunks = []
        async for chunk in acall_llm_stream(ctx, "TypeScript"):
            chunks.append(chunk)

        assert len(chunks) > 0
        assert all(isinstance(chunk, str) for chunk in chunks)
        assert ctx.get_meta("input") == "TypeScript"
        assert ctx.get_meta("response") is not None


class TestExampleFunctions:
    """Test the example functions"""

    @patch("main.call_llm")
    def test_sync_example(self, mock_call_llm):
        """Test synchronous example"""
        mock_call_llm.return_value = "Mock sync response"

        # Should run without errors
        sync_example()

        # Verify the mock was called
        assert mock_call_llm.called

    @pytest.mark.asyncio
    @patch("main.acall_llm")
    async def test_async_example(self, mock_acall_llm):
        """Test asynchronous example"""
        mock_acall_llm.return_value = "Mock async response"

        # Should run without errors
        await async_example()

        # Verify the mock was called
        assert mock_acall_llm.called

    @patch("main.call_llm")
    def test_invoke_example(self, mock_call_llm):
        """Test invoke example"""
        mock_call_llm.return_value = "Mock invoke response"

        # Should run without errors
        invoke_example()

        # Verify the mock was called
        assert mock_call_llm.called

    @patch("main.call_llm_stream")
    def test_stream_example(self, mock_call_llm_stream):
        """Test stream example"""
        mock_call_llm_stream.return_value = ["Mock", "stream", "response"]

        # Should run without errors
        stream_example()

        # Verify the mock was called
        assert mock_call_llm_stream.called

    @pytest.mark.asyncio
    @patch("main.acall_llm_stream")
    async def test_async_stream_example(self, mock_acall_llm_stream):
        """Test async stream example"""

        # Create async generator mock
        async def mock_async_gen():
            for chunk in ["Mock", "async", "stream"]:
                yield chunk

        mock_acall_llm_stream.return_value = mock_async_gen()

        # Should run without errors
        await async_stream_example()

        # Verify the mock was called
        assert mock_acall_llm_stream.called


class TestCallContextIntegration:
    """Test CallContext integration"""

    def test_context_callback_handler(self):
        """Test CallContext with callback handler"""
        ctx = CallContext(user_id="callback_user", turn_id="callback_turn")
        handler = CallContextCallbackHandler(ctx)
        ctx.callbacks.append(handler)

        # Test that handler is properly attached
        assert len(ctx.callbacks) == 1
        assert isinstance(ctx.callbacks[0], CallContextCallbackHandler)
        assert ctx.callbacks[0].ctx == ctx

    def test_context_metadata_operations(self):
        """Test context metadata operations"""
        ctx = CallContext(user_id="meta_user", turn_id="meta_turn")

        # Test setting and getting metadata
        ctx.set_meta("test_key", "test_value")
        assert ctx.get_meta("test_key") == "test_value"

        # Test multiple values for same key
        ctx.set_meta("test_key", "second_value")
        assert ctx.get_meta("test_key") == "second_value"
        assert ctx.get_meta("test_key", all_values=True) == ["test_value", "second_value"]

        # Test non-existent key
        assert ctx.get_meta("non_existent") is None

    def test_context_error_handling(self):
        """Test context error handling"""
        ctx = CallContext(user_id="error_user", turn_id="error_turn")

        # Initially no error
        assert ctx.error is None

        # Set error
        test_error = ValueError("Test error")
        ctx.set_error(test_error)
        assert ctx.error == test_error


class TestABTestingIntegration:
    """Test A/B testing integration with CallContext"""

    def test_ab_testing_model_selection_consistency(self):
        """Test that A/B testing gives consistent results"""
        selector = ABTestLLMSelector()

        # Test multiple contexts with the same user
        user_id = "consistent_user"
        contexts = []
        selected_models = []

        for i in range(5):
            ctx = CallContext(user_id=user_id, turn_id=f"turn_{i}")
            model = selector.get_model_for_user(user_id)
            ctx.set_meta("selected_model", model)

            contexts.append(ctx)
            selected_models.append(model)

        # All should have the same model
        assert len(set(selected_models)) == 1

        # All contexts should have the same metadata
        for ctx in contexts:
            assert ctx.get_meta("selected_model") == selected_models[0]

    def test_ab_testing_with_different_users(self):
        """Test A/B testing with different users"""
        selector = ABTestLLMSelector()

        # Create contexts for different users
        users_and_models = []
        for i in range(20):
            user_id = f"user_{i}"
            ctx = CallContext(user_id=user_id, turn_id="test_turn")
            model = selector.get_model_for_user(user_id)
            ctx.set_meta("selected_model", model)

            users_and_models.append((user_id, model, ctx))

        # Should have both models represented
        models = [model for _, model, _ in users_and_models]
        unique_models = set(models)
        assert len(unique_models) >= 2

        # Each user should be consistent
        for user_id, expected_model, ctx in users_and_models:
            # Re-select to verify consistency
            new_model = selector.get_model_for_user(user_id)
            assert new_model == expected_model
            assert ctx.get_meta("selected_model") == expected_model
