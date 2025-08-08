"""
Unit tests for CallContext and CallContextExecutors
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock

import sys
import os

# Add libs to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'libs'))

from call_context_lib import (
    CallContext,
    CallContextCallbackHandler,
    SyncCallContextExecutor,
    AsyncCallContextExecutor,
    StreamCallContextExecutor,
    InvokeCallContextExecutor
)


class MockCallbackHandler(CallContextCallbackHandler):
    def __init__(self, ctx: CallContext):
        super().__init__(ctx)
        self.completed = False
        self.error_occurred = False
    
    async def on_complete(self, ctx: CallContext):
        self.completed = True


class TestCallContext:
    """Test CallContext basic functionality"""
    
    def test_call_context_creation(self):
        """Test CallContext can be created with required fields"""
        ctx = CallContext(user_id="user123", turn_id="turn456")
        
        assert ctx.get_user_id() == "user123"
        assert ctx.get_turn_id() == "turn456"
        assert ctx.error is None
        assert len(ctx.callbacks) == 0
        assert isinstance(ctx.meta, dict)
    
    def test_call_context_optional_fields(self):
        """Test CallContext can be created with optional user_id and turn_id"""
        # Test with both None
        ctx1 = CallContext()
        assert ctx1.get_user_id() is None
        assert ctx1.get_turn_id() is None
        
        # Test with only user_id
        ctx2 = CallContext(user_id="user123")
        assert ctx2.get_user_id() == "user123"
        assert ctx2.get_turn_id() is None
        
        # Test with only turn_id
        ctx3 = CallContext(turn_id="turn456")
        assert ctx3.get_user_id() is None
        assert ctx3.get_turn_id() == "turn456"
    
    def test_call_context_meta_operations(self):
        """Test CallContext metadata operations"""
        ctx = CallContext(user_id="user123", turn_id="turn456")
        
        # Test setting and getting meta
        ctx.set_meta("model", "gpt-4")
        assert ctx.get_meta("model") == "gpt-4"
        
        # Test multiple values for same key
        ctx.set_meta("model", "gpt-3.5-turbo")
        assert ctx.get_meta("model") == "gpt-3.5-turbo"  # Latest value
        assert ctx.get_meta("model", all_values=True) == ["gpt-4", "gpt-3.5-turbo"]
        
        # Test non-existent key
        assert ctx.get_meta("nonexistent") is None
        assert ctx.get_meta("nonexistent", all_values=True) == []
    
    def test_call_context_error_handling(self):
        """Test CallContext error handling"""
        ctx = CallContext(user_id="user123", turn_id="turn456")
        
        error = ValueError("Test error")
        ctx.set_error(error)
        
        assert ctx.error == error
    
    @pytest.mark.asyncio
    async def test_call_context_callback(self):
        """Test CallContext callback functionality"""
        ctx = CallContext(user_id="user123", turn_id="turn456")
        callback = MockCallbackHandler(ctx)
        ctx.callbacks = [callback]
        
        await ctx.on_complete()
        
        assert callback.completed is True


class TestSyncCallContextExecutor:
    """Test SyncCallContextExecutor"""
    
    def test_sync_executor_success(self):
        """Test successful execution with SyncCallContextExecutor"""
        ctx = CallContext(user_id="user123", turn_id="turn456")
        executor = SyncCallContextExecutor()
        
        before_called = False
        completed_called = False
        finally_called = False
        
        def before_hook(ctx):
            nonlocal before_called
            before_called = True
            ctx.set_meta("before", True)
        
        def completed_hook(ctx):
            nonlocal completed_called
            completed_called = True
            ctx.set_meta("completed", True)
        
        def finally_hook(ctx):
            nonlocal finally_called
            finally_called = True
            ctx.set_meta("finally", True)
        
        def test_function(ctx):
            return "test result"
        
        result = (executor
                 .before(before_hook)
                 .on_completed(completed_hook)
                 .finally_hook(finally_hook)
                 .execute(ctx, test_function))
        
        assert result == "test result"
        assert before_called is True
        assert completed_called is True 
        assert finally_called is True
        assert ctx.get_meta("before") is True
        assert ctx.get_meta("completed") is True
        assert ctx.get_meta("finally") is True
    
    def test_sync_executor_error_handling(self):
        """Test error handling with SyncCallContextExecutor"""
        ctx = CallContext(user_id="user123", turn_id="turn456")
        executor = SyncCallContextExecutor()
        
        error_called = False
        finally_called = False
        
        def error_hook(ctx, error):
            nonlocal error_called
            error_called = True
            assert isinstance(error, ValueError)
        
        def finally_hook(ctx):
            nonlocal finally_called
            finally_called = True
        
        def failing_function(ctx):
            raise ValueError("Test error")
        
        with pytest.raises(ValueError):
            executor.on_error(error_hook).finally_hook(finally_hook).execute(ctx, failing_function)
        
        assert error_called is True
        assert finally_called is True
        assert ctx.error is not None
        assert isinstance(ctx.error, ValueError)
    
    def test_sync_executor_with_optional_fields(self):
        """Test SyncCallContextExecutor with optional user_id and turn_id"""
        # Test with both None
        ctx1 = CallContext()
        executor = SyncCallContextExecutor()
        
        def test_function(ctx):
            # Should not raise an error even with None user_id and turn_id
            return "success"
        
        result = executor.execute(ctx1, test_function)
        assert result == "success"
        
        # Test with only user_id
        ctx2 = CallContext(user_id="user123")
        result = executor.execute(ctx2, test_function)
        assert result == "success"
        
        # Test with only turn_id
        ctx3 = CallContext(turn_id="turn456")
        result = executor.execute(ctx3, test_function)
        assert result == "success"


class TestAsyncCallContextExecutor:
    """Test AsyncCallContextExecutor"""
    
    @pytest.mark.asyncio
    async def test_async_executor_success(self):
        """Test successful execution with AsyncCallContextExecutor"""
        ctx = CallContext(user_id="user123", turn_id="turn456")
        executor = AsyncCallContextExecutor()
        
        before_called = False
        before_async_called = False
        completed_called = False
        finally_async_called = False
        
        def before_hook(ctx):
            nonlocal before_called
            before_called = True
        
        async def before_async_hook(ctx):
            nonlocal before_async_called
            before_async_called = True
        
        def completed_hook(ctx):
            nonlocal completed_called
            completed_called = True
        
        async def finally_async_hook(ctx):
            nonlocal finally_async_called
            finally_async_called = True
        
        async def test_function(ctx):
            await asyncio.sleep(0.01)  # Simulate async work
            return "async test result"
        
        result = await (executor
                       .before(before_hook)
                       .before_async(before_async_hook)
                       .on_completed(completed_hook)
                       .finally_async(finally_async_hook)
                       .async_execute(ctx, test_function))
        
        assert result == "async test result"
        assert before_called is True
        assert before_async_called is True
        assert completed_called is True
        assert finally_async_called is True
    
    @pytest.mark.asyncio
    async def test_async_executor_with_optional_fields(self):
        """Test AsyncCallContextExecutor with optional user_id and turn_id"""
        executor = AsyncCallContextExecutor()
        
        async def test_function(ctx):
            await asyncio.sleep(0.01)
            return "async success"
        
        # Test with both None
        ctx1 = CallContext()
        result = await executor.async_execute(ctx1, test_function)
        assert result == "async success"
        
        # Test with only user_id
        ctx2 = CallContext(user_id="user123")
        result = await executor.async_execute(ctx2, test_function)
        assert result == "async success"
        
        # Test with only turn_id
        ctx3 = CallContext(turn_id="turn456")
        result = await executor.async_execute(ctx3, test_function)
        assert result == "async success"


class TestStreamCallContextExecutor:
    """Test StreamCallContextExecutor"""
    
    def test_sync_stream_executor(self):
        """Test sync streaming with StreamCallContextExecutor"""
        ctx = CallContext(user_id="user123", turn_id="turn456")
        executor = StreamCallContextExecutor()
        
        completed_called = False
        
        def completed_hook(ctx):
            nonlocal completed_called
            completed_called = True
        
        def test_generator(ctx):
            for i in range(3):
                yield f"item_{i}"
        
        stream = executor.on_completed(completed_hook).stream_execute(ctx, test_generator)
        results = list(stream)
        
        assert results == ["item_0", "item_1", "item_2"]
        assert completed_called is True
    
    @pytest.mark.asyncio
    async def test_async_stream_executor(self):
        """Test async streaming with StreamCallContextExecutor"""
        ctx = CallContext(user_id="user123", turn_id="turn456")
        executor = StreamCallContextExecutor()
        
        completed_called = False
        
        def completed_hook(ctx):
            nonlocal completed_called
            completed_called = True
        
        async def test_async_generator(ctx):
            for i in range(3):
                await asyncio.sleep(0.01)
                yield f"async_item_{i}"
        
        stream = executor.on_completed(completed_hook).async_stream_execute(ctx, test_async_generator)
        results = []
        async for item in stream:
            results.append(item)
        
        assert results == ["async_item_0", "async_item_1", "async_item_2"]
        assert completed_called is True


class TestInvokeCallContextExecutor:
    """Test InvokeCallContextExecutor"""
    
    def test_invoke_executor_success(self):
        """Test successful execution with InvokeCallContextExecutor"""
        ctx = CallContext(user_id="user123", turn_id="turn456")
        callback = MockCallbackHandler(ctx)
        ctx.callbacks = [callback]
        executor = InvokeCallContextExecutor()
        
        completed_called = False
        
        def completed_hook(ctx):
            nonlocal completed_called
            completed_called = True
        
        def test_function(ctx):
            return "invoke result"
        
        result = executor.on_completed(completed_hook).execute(ctx, test_function)
        
        assert result == "invoke result"
        assert completed_called is True
        # Note: callback completion happens asynchronously, so we can't easily test it here