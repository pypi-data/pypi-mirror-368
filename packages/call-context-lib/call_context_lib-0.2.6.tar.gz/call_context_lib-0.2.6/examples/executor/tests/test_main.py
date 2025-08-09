#!/usr/bin/env python3
"""
Tests for BaseCallContextExecutor implementation examples

This module tests the executor examples that demonstrate the chaining API and hook system.
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch, AsyncMock, call

from main import (
    simple_sync_function,
    simple_async_function,
    simple_stream_function,
    simple_async_stream_function,
    demonstrate_sync_executor,
    demonstrate_async_executor,
    demonstrate_stream_executor,
    demonstrate_invoke_executor,
    demonstrate_error_handling,
    demonstrate_multiple_hooks,
    demonstrate_context_metadata,
    demonstrate_async_stream_executor,
)
from call_context_lib import (
    CallContext,
    CallContextCallbackHandler,
    SyncCallContextExecutor,
    AsyncCallContextExecutor,
    StreamCallContextExecutor,
    InvokeCallContextExecutor,
)


class TestSimpleFunctions:
    """Test the simple functions used by executors"""

    def test_simple_sync_function(self):
        """Test simple synchronous function"""
        ctx = CallContext(user_id="test_user", turn_id="test_turn")
        ctx.set_meta("name", "TestName")

        result = simple_sync_function(ctx)

        assert result == "Hello, TestName!"
        assert ctx.get_meta("result") == "Hello, TestName!"

    def test_simple_sync_function_default_name(self):
        """Test simple sync function with default name"""
        ctx = CallContext(user_id="test_user", turn_id="test_turn")
        # Don't set name, should use default

        result = simple_sync_function(ctx)

        assert result == "Hello, World!"
        assert ctx.get_meta("result") == "Hello, World!"

    @pytest.mark.asyncio
    async def test_simple_async_function(self):
        """Test simple asynchronous function"""
        ctx = CallContext(user_id="test_user", turn_id="test_turn")
        ctx.set_meta("name", "AsyncTest")

        result = await simple_async_function(ctx)

        assert result == "Hello from async, AsyncTest!"
        assert ctx.get_meta("result") == "Hello from async, AsyncTest!"

    @pytest.mark.asyncio
    async def test_simple_async_function_default_name(self):
        """Test simple async function with default name"""
        ctx = CallContext(user_id="test_user", turn_id="test_turn")
        # Don't set name, should use default

        result = await simple_async_function(ctx)

        assert result == "Hello from async, Async World!"
        assert ctx.get_meta("result") == "Hello from async, Async World!"

    def test_simple_stream_function(self):
        """Test simple streaming function"""
        ctx = CallContext(user_id="test_user", turn_id="test_turn")
        ctx.set_meta("name", "StreamTest")

        chunks = list(simple_stream_function(ctx))

        assert len(chunks) > 0
        assert all(isinstance(chunk, str) for chunk in chunks)
        result = "".join(chunks).strip()
        assert "Hello from stream, StreamTest!" in result
        assert ctx.get_meta("result") == "Hello from stream, StreamTest!"

    @pytest.mark.asyncio
    async def test_simple_async_stream_function(self):
        """Test simple async streaming function"""
        ctx = CallContext(user_id="test_user", turn_id="test_turn")
        ctx.set_meta("name", "AsyncStreamTest")

        chunks = []
        async for chunk in simple_async_stream_function(ctx):
            chunks.append(chunk)

        assert len(chunks) > 0
        assert all(isinstance(chunk, str) for chunk in chunks)
        result = "".join(chunks).strip()
        assert "Hello from async stream, AsyncStreamTest!" in result
        assert ctx.get_meta("result") == "Hello from async stream, AsyncStreamTest!"


class TestExecutorIntegration:
    """Test executor integration with hook system"""

    def test_sync_executor_with_hooks(self):
        """Test sync executor with hook chaining"""
        ctx = CallContext(user_id="hook_user", turn_id="hook_turn")
        ctx.set_meta("name", "HookTest")

        before_called = []
        completed_called = []
        finally_called = []

        executor = SyncCallContextExecutor()
        result = (
            executor.before(lambda c: before_called.append(c.user_id))
            .on_completed(lambda c: completed_called.append(c.get_meta("result")))
            .finally_hook(lambda c: finally_called.append(c.turn_id))
            .execute(ctx, simple_sync_function)
        )

        assert result == "Hello, HookTest!"
        assert before_called == ["hook_user"]
        assert completed_called == ["Hello, HookTest!"]
        assert finally_called == ["hook_turn"]

    @pytest.mark.asyncio
    async def test_async_executor_with_hooks(self):
        """Test async executor with hook chaining"""
        ctx = CallContext(user_id="async_hook_user", turn_id="async_hook_turn")
        ctx.set_meta("name", "AsyncHookTest")

        before_called = []
        completed_called = []
        finally_called = []

        executor = AsyncCallContextExecutor()
        result = await (
            executor.before(lambda c: before_called.append(c.user_id))
            .on_completed(lambda c: completed_called.append(c.get_meta("result")))
            .finally_hook(lambda c: finally_called.append(c.turn_id))
            .async_execute(ctx, simple_async_function)
        )

        assert result == "Hello from async, AsyncHookTest!"
        assert before_called == ["async_hook_user"]
        assert completed_called == ["Hello from async, AsyncHookTest!"]
        assert finally_called == ["async_hook_turn"]

    def test_stream_executor_with_hooks(self):
        """Test stream executor with hook chaining"""
        ctx = CallContext(user_id="stream_hook_user", turn_id="stream_hook_turn")
        ctx.set_meta("name", "StreamHookTest")

        before_called = []
        completed_called = []
        finally_called = []

        executor = StreamCallContextExecutor()
        stream = (
            executor.before(lambda c: before_called.append(c.user_id))
            .on_completed(lambda c: completed_called.append(c.get_meta("result")))
            .finally_hook(lambda c: finally_called.append(c.turn_id))
            .stream_execute(ctx, simple_stream_function)
        )

        chunks = list(stream)

        assert len(chunks) > 0
        assert before_called == ["stream_hook_user"]
        assert len(completed_called) == 1
        assert "Hello from stream, StreamHookTest!" in completed_called[0]
        assert finally_called == ["stream_hook_turn"]

    def test_invoke_executor_with_hooks(self):
        """Test invoke executor with hook chaining and callbacks"""
        ctx = CallContext(user_id="invoke_hook_user", turn_id="invoke_hook_turn")
        ctx.set_meta("name", "InvokeHookTest")

        # Add callback handler
        ctx.callbacks.append(CallContextCallbackHandler(ctx))

        before_called = []
        completed_called = []
        finally_called = []

        executor = InvokeCallContextExecutor()
        result = (
            executor.before(lambda c: before_called.append(c.user_id))
            .on_completed(lambda c: completed_called.append(c.get_meta("result")))
            .finally_hook(lambda c: finally_called.append(c.turn_id))
            .execute(ctx, simple_sync_function)
        )

        assert result == "Hello, InvokeHookTest!"
        assert before_called == ["invoke_hook_user"]
        assert completed_called == ["Hello, InvokeHookTest!"]
        assert finally_called == ["invoke_hook_turn"]

    @pytest.mark.asyncio
    async def test_invoke_executor_callback_handler_on_complete_called(self):
        """Test that CallContextCallbackHandler.on_complete is called when running in async context"""
        # InvokeCallContextExecutor only calls on_complete when an event loop is running
        # We need to run the executor in an async task

        ctx = CallContext(user_id="callback_test_user", turn_id="callback_test_turn")
        ctx.set_meta("name", "CallbackTest")

        # Create a mock callback handler
        mock_callback = Mock(spec=CallContextCallbackHandler)
        mock_callback.ctx = ctx
        mock_callback.on_llm_start = Mock()
        mock_callback.on_llm_end = Mock()
        mock_callback.on_llm_error = Mock()
        mock_callback.on_complete = AsyncMock(return_value=None)

        # Add the mock callback to context
        ctx.callbacks.append(mock_callback)

        # Run executor in an async task
        async def run_executor():
            executor = InvokeCallContextExecutor()
            return executor.execute(ctx, simple_sync_function)

        # Execute in async context
        result = await asyncio.create_task(run_executor())

        # Wait a bit for the on_complete task to finish
        await asyncio.sleep(0.1)

        # Verify the function executed correctly
        assert result == "Hello, CallbackTest!"

        # Verify on_complete was called (this is the only callback method called by InvokeCallContextExecutor)
        mock_callback.on_complete.assert_called_once_with(ctx)

    def test_invoke_executor_with_real_callback_handler(self):
        """Test InvokeCallContextExecutor with real CallContextCallbackHandler"""
        ctx = CallContext(user_id="real_callback_user", turn_id="real_callback_turn")
        ctx.set_meta("name", "RealCallbackTest")

        # Add the real CallContextCallbackHandler
        callback_handler = CallContextCallbackHandler(ctx)
        ctx.callbacks.append(callback_handler)

        executor = InvokeCallContextExecutor()
        result = executor.execute(ctx, simple_sync_function)

        # Verify the function executed correctly
        assert result == "Hello, RealCallbackTest!"

        # Note: CallContextCallbackHandler's on_llm_* methods are not called by InvokeCallContextExecutor
        # They are designed to be called by LangChain when using LLM models
        # The executor only calls on_complete() asynchronously if an event loop is running
        assert ctx.error is None  # No error should be set for successful execution

    def test_callback_handler_manual_method_calls(self):
        """Test CallContextCallbackHandler methods when called manually"""
        ctx = CallContext(user_id="manual_callback_user", turn_id="manual_callback_turn")

        # Create a real CallContextCallbackHandler
        callback_handler = CallContextCallbackHandler(ctx)

        # Manually call on_llm_start
        callback_handler.on_llm_start()
        assert ctx.get_meta("llm_started") is True

        # Manually call on_llm_end
        callback_handler.on_llm_end(response="test response")
        assert ctx.get_meta("llm_ended") is True

        # Manually call on_llm_error
        test_error = ValueError("test error")
        callback_handler.on_llm_error(test_error)
        assert ctx.error == test_error


class TestErrorHandling:
    """Test error handling in executors"""

    def test_sync_executor_error_handling(self):
        """Test sync executor error handling"""

        def error_function(ctx: CallContext) -> str:
            raise ValueError("Test error")

        ctx = CallContext(user_id="error_user", turn_id="error_turn")

        before_called = []
        error_called = []
        finally_called = []

        executor = SyncCallContextExecutor()

        with pytest.raises(ValueError, match="Test error"):
            (
                executor.before(lambda c: before_called.append(True))
                .on_error(lambda c, e: error_called.append(type(e).__name__))
                .finally_hook(lambda c: finally_called.append(True))
                .execute(ctx, error_function)
            )

        assert before_called == [True]
        assert error_called == ["ValueError"]
        assert finally_called == [True]
        assert ctx.error is not None
        assert isinstance(ctx.error, ValueError)

    @pytest.mark.asyncio
    async def test_async_executor_error_handling(self):
        """Test async executor error handling"""

        async def async_error_function(ctx: CallContext) -> str:
            raise RuntimeError("Async test error")

        ctx = CallContext(user_id="async_error_user", turn_id="async_error_turn")

        before_called = []
        error_called = []
        finally_called = []

        executor = AsyncCallContextExecutor()

        with pytest.raises(RuntimeError, match="Async test error"):
            await (
                executor.before(lambda c: before_called.append(True))
                .on_error(lambda c, e: error_called.append(type(e).__name__))
                .finally_hook(lambda c: finally_called.append(True))
                .async_execute(ctx, async_error_function)
            )

        assert before_called == [True]
        assert error_called == ["RuntimeError"]
        assert finally_called == [True]
        assert ctx.error is not None
        assert isinstance(ctx.error, RuntimeError)


class TestMultipleHooks:
    """Test multiple hooks of the same type"""

    def test_multiple_before_hooks(self):
        """Test multiple before hooks are called in order"""
        ctx = CallContext(user_id="multi_user", turn_id="multi_turn")
        ctx.set_meta("name", "MultiTest")

        call_order = []

        executor = SyncCallContextExecutor()
        result = (
            executor.before(lambda c: call_order.append("before1"))
            .before(lambda c: call_order.append("before2"))
            .before(lambda c: call_order.append("before3"))
            .execute(ctx, simple_sync_function)
        )

        assert result == "Hello, MultiTest!"
        assert call_order == ["before1", "before2", "before3"]

    def test_multiple_completed_hooks(self):
        """Test multiple completed hooks are called"""
        ctx = CallContext(user_id="multi_user", turn_id="multi_turn")
        ctx.set_meta("name", "MultiTest")

        completed_calls = []

        executor = SyncCallContextExecutor()
        result = (
            executor.on_completed(lambda c: completed_calls.append("completed1"))
            .on_completed(lambda c: completed_calls.append("completed2"))
            .execute(ctx, simple_sync_function)
        )

        assert result == "Hello, MultiTest!"
        assert completed_calls == ["completed1", "completed2"]

    def test_multiple_finally_hooks(self):
        """Test multiple finally hooks are called"""
        ctx = CallContext(user_id="multi_user", turn_id="multi_turn")
        ctx.set_meta("name", "MultiTest")

        finally_calls = []

        executor = SyncCallContextExecutor()
        result = (
            executor.finally_hook(lambda c: finally_calls.append("finally1"))
            .finally_hook(lambda c: finally_calls.append("finally2"))
            .execute(ctx, simple_sync_function)
        )

        assert result == "Hello, MultiTest!"
        assert finally_calls == ["finally1", "finally2"]


class TestMetadataHandling:
    """Test context metadata handling"""

    def test_metadata_operations(self):
        """Test metadata setting and retrieval"""

        def metadata_function(ctx: CallContext) -> str:
            start_time = ctx.get_meta("start_time")
            user_pref = ctx.get_meta("user_preference") or "default"

            ctx.set_meta("processing_time", time.time() - start_time)
            ctx.set_meta("function_called", "metadata_function")

            return f"Processed with preference: {user_pref}"

        ctx = CallContext(user_id="meta_user", turn_id="meta_turn")
        ctx.set_meta("start_time", time.time())
        ctx.set_meta("user_preference", "advanced")

        metadata_captured = {}

        executor = SyncCallContextExecutor()
        result = (
            executor.before(lambda c: c.set_meta("before_hook_executed", True))
            .on_completed(lambda c: metadata_captured.update({"processing_time": c.get_meta("processing_time")}))
            .finally_hook(lambda c: metadata_captured.update({"total_meta_items": len(c.meta)}))
            .execute(ctx, metadata_function)
        )

        assert result == "Processed with preference: advanced"
        assert ctx.get_meta("before_hook_executed") is True
        assert ctx.get_meta("function_called") == "metadata_function"
        assert metadata_captured["processing_time"] is not None
        assert metadata_captured["total_meta_items"] >= 4


class TestDemoFunctionsMocked:
    """Test demo functions with mocking to avoid output"""

    @patch("builtins.print")
    def test_demonstrate_sync_executor(self, mock_print):
        """Test sync executor demonstration function"""
        demonstrate_sync_executor()

        # Verify print was called (indicating the function ran)
        assert mock_print.called

        # Check that expected output patterns are present
        print_calls = [call.args[0] for call in mock_print.call_args_list if call.args]
        output_text = " ".join(str(call) for call in print_calls)

        assert "Sync Executor Example" in output_text
        assert "Processing for user user123" in output_text
        assert "Hello, Synchronous!" in output_text

    @pytest.mark.asyncio
    @patch("builtins.print")
    async def test_demonstrate_async_executor(self, mock_print):
        """Test async executor demonstration function"""
        await demonstrate_async_executor()

        # Verify print was called
        assert mock_print.called

        # Check output patterns
        print_calls = [call.args[0] for call in mock_print.call_args_list if call.args]
        output_text = " ".join(str(call) for call in print_calls)

        assert "Async Executor Example" in output_text
        assert "Async processing for user user456" in output_text
        assert "Hello from async, Asynchronous!" in output_text

    @patch("builtins.print")
    def test_demonstrate_stream_executor(self, mock_print):
        """Test stream executor demonstration function"""
        demonstrate_stream_executor()

        # Verify print was called
        assert mock_print.called

        # Check output patterns
        print_calls = [call.args[0] for call in mock_print.call_args_list if call.args]
        output_text = " ".join(str(call) for call in print_calls)

        assert "Stream Executor Example" in output_text
        assert "Starting stream for user user789" in output_text

    @patch("builtins.print")
    def test_demonstrate_invoke_executor(self, mock_print):
        """Test invoke executor demonstration function"""
        demonstrate_invoke_executor()

        # Verify print was called
        assert mock_print.called

        # Check output patterns
        print_calls = [call.args[0] for call in mock_print.call_args_list if call.args]
        output_text = " ".join(str(call) for call in print_calls)

        assert "Invoke Executor Example" in output_text
        assert "Invoke processing for user user999" in output_text

    @patch("builtins.print")
    def test_demonstrate_error_handling(self, mock_print):
        """Test error handling demonstration function"""
        demonstrate_error_handling()

        # Verify print was called
        assert mock_print.called

        # Check error handling patterns
        print_calls = [call.args[0] for call in mock_print.call_args_list if call.args]
        output_text = " ".join(str(call) for call in print_calls)

        assert "Error Handling Example" in output_text
        assert "Error caught: ValueError" in output_text
        assert "Context has error: True" in output_text

    @patch("builtins.print")
    def test_demonstrate_multiple_hooks(self, mock_print):
        """Test multiple hooks demonstration function"""
        demonstrate_multiple_hooks()

        # Verify print was called
        assert mock_print.called

        # Check multiple hooks patterns
        print_calls = [call.args[0] for call in mock_print.call_args_list if call.args]
        output_text = " ".join(str(call) for call in print_calls)

        assert "Multiple Hooks Example" in output_text
        assert "Before Hook 1" in output_text
        assert "Before Hook 2" in output_text
        assert "Before Hook 3" in output_text

    @patch("builtins.print")
    def test_demonstrate_context_metadata(self, mock_print):
        """Test context metadata demonstration function"""
        demonstrate_context_metadata()

        # Verify print was called
        assert mock_print.called

        # Check metadata patterns
        print_calls = [call.args[0] for call in mock_print.call_args_list if call.args]
        output_text = " ".join(str(call) for call in print_calls)

        assert "Context Metadata Example" in output_text
        assert "Processing time:" in output_text
        assert "Final metadata:" in output_text

    @pytest.mark.asyncio
    @patch("builtins.print")
    async def test_demonstrate_async_stream_executor(self, mock_print):
        """Test async stream executor demonstration function"""
        await demonstrate_async_stream_executor()

        # Verify print was called
        assert mock_print.called

        # Check async stream patterns
        print_calls = [call.args[0] for call in mock_print.call_args_list if call.args]
        output_text = " ".join(str(call) for call in print_calls)

        assert "Async Stream" in output_text
        assert "Starting async stream" in output_text
