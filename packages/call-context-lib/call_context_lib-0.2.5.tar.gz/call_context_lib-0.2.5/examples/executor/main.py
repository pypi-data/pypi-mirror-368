#!/usr/bin/env python3
"""
CallContextExecutor Examples

This module demonstrates the usage of BaseCallContextExecutor implementations
with focus on the chaining API and hook system.
"""

import asyncio
import time
from typing import AsyncGenerator, Generator

from call_context_lib import (
    CallContext,
    CallContextCallbackHandler,
    SyncCallContextExecutor,
    AsyncCallContextExecutor,
    StreamCallContextExecutor,
    InvokeCallContextExecutor,
)


def simple_sync_function(ctx: CallContext) -> str:
    """Simple synchronous function that uses context"""
    name = ctx.get_meta("name") or "World"
    result = f"Hello, {name}!"
    ctx.set_meta("result", result)
    return result


async def simple_async_function(ctx: CallContext) -> str:
    """Simple asynchronous function that uses context"""
    await asyncio.sleep(0.1)  # Simulate async work
    name = ctx.get_meta("name") or "Async World"
    result = f"Hello from async, {name}!"
    ctx.set_meta("result", result)
    return result


def simple_stream_function(ctx: CallContext) -> Generator[str, None, None]:
    """Simple streaming function that yields parts"""
    name = ctx.get_meta("name") or "Stream World"
    message = f"Hello from stream, {name}!"

    # Yield word by word
    for word in message.split():
        yield f"{word} "

    ctx.set_meta("result", message)


async def simple_async_stream_function(ctx: CallContext) -> AsyncGenerator[str, None]:
    """Simple async streaming function"""
    name = ctx.get_meta("name") or "Async Stream World"
    message = f"Hello from async stream, {name}!"

    # Yield word by word with small delays
    for word in message.split():
        await asyncio.sleep(0.05)  # Small delay for demonstration
        yield f"{word} "

    ctx.set_meta("result", message)


def demonstrate_sync_executor():
    """Demonstrate SyncCallContextExecutor with chaining API"""
    print("=== Sync Executor Example ===")

    ctx = CallContext(user_id="user123", turn_id="turn001")
    ctx.set_meta("name", "Synchronous")

    executor = SyncCallContextExecutor()

    # Demonstrate chaining API with hooks
    result = (
        executor.before(lambda c: print(f"🔹 Before: Processing for user {c.user_id}"))
        .on_completed(lambda c: print(f"✅ Completed: Result stored in context"))
        .on_error(lambda c, e: print(f"❌ Error: {e}"))
        .finally_hook(lambda c: print(f"🏁 Finally: Done with {c.turn_id}"))
        .execute(ctx, simple_sync_function)
    )

    print(f"Result: {result}")
    print(f"Context result: {ctx.get_meta('result')}")
    print()


async def demonstrate_async_executor():
    """Demonstrate AsyncCallContextExecutor with chaining API"""
    print("=== Async Executor Example ===")

    ctx = CallContext(user_id="user456", turn_id="turn002")
    ctx.set_meta("name", "Asynchronous")

    executor = AsyncCallContextExecutor()

    # Demonstrate chaining API with async hooks
    result = await (
        executor.before(lambda c: print(f"🔹 Before: Async processing for user {c.user_id}"))
        .on_completed(lambda c: print(f"✅ Completed: Async result ready"))
        .on_error(lambda c, e: print(f"❌ Error: {e}"))
        .finally_hook(lambda c: print(f"🏁 Finally: Async done with {c.turn_id}"))
        .async_execute(ctx, simple_async_function)
    )

    print(f"Result: {result}")
    print(f"Context result: {ctx.get_meta('result')}")
    print()


def demonstrate_stream_executor():
    """Demonstrate StreamCallContextExecutor with chaining API"""
    print("=== Stream Executor Example ===")

    ctx = CallContext(user_id="user789", turn_id="turn003")
    ctx.set_meta("name", "Streaming")

    executor = StreamCallContextExecutor()

    # Demonstrate chaining API for streaming
    stream = (
        executor.before(lambda c: print(f"🔹 Before: Starting stream for user {c.user_id}"))
        .on_completed(lambda c: print(f"✅ Completed: Stream finished"))
        .on_error(lambda c, e: print(f"❌ Error: {e}"))
        .finally_hook(lambda c: print(f"🏁 Finally: Stream cleanup for {c.turn_id}"))
        .stream_execute(ctx, simple_stream_function)
    )

    print("Streaming output: ", end="")
    for chunk in stream:
        print(chunk, end="")

    print(f"\nContext result: {ctx.get_meta('result')}")
    print()


def demonstrate_invoke_executor():
    """Demonstrate InvokeCallContextExecutor with callbacks"""
    print("=== Invoke Executor Example ===")

    ctx = CallContext(user_id="user999", turn_id="turn004")
    ctx.set_meta("name", "Invoke")

    # Add the built-in CallContextCallbackHandler
    ctx.callbacks.append(CallContextCallbackHandler(ctx))

    executor = InvokeCallContextExecutor()

    # Demonstrate invoke pattern with callbacks
    result = (
        executor.before(lambda c: print(f"🔹 Before: Invoke processing for user {c.user_id}"))
        .on_completed(lambda c: print(f"✅ Completed: Invoke result ready"))
        .on_error(lambda c, e: print(f"❌ Error: {e}"))
        .finally_hook(lambda c: print(f"🏁 Finally: Invoke done"))
        .execute(ctx, simple_sync_function)
    )

    print(f"Result: {result}")
    print(f"Context result: {ctx.get_meta('result')}")
    print()


def demonstrate_error_handling():
    """Demonstrate error handling with executors"""
    print("=== Error Handling Example ===")

    def error_function(ctx: CallContext) -> str:
        raise ValueError("Intentional error for demonstration")

    ctx = CallContext(user_id="error_user", turn_id="error_turn")
    executor = SyncCallContextExecutor()

    try:
        result = (
            executor.before(lambda c: print(f"🔹 Before: Processing with potential error"))
            .on_completed(lambda c: print(f"✅ This should not be called"))
            .on_error(lambda c, e: print(f"❌ Error caught: {type(e).__name__}: {e}"))
            .finally_hook(lambda c: print(f"🏁 Finally: Cleanup after error"))
            .execute(ctx, error_function)
        )
    except ValueError as e:
        print(f"Exception propagated: {e}")

    print(f"Context has error: {ctx.error is not None}")
    print()


def demonstrate_multiple_hooks():
    """Demonstrate multiple hooks of the same type"""
    print("=== Multiple Hooks Example ===")

    ctx = CallContext(user_id="multi_user", turn_id="multi_turn")
    ctx.set_meta("name", "Multiple Hooks")

    executor = SyncCallContextExecutor()

    # Add multiple hooks of each type
    result = (
        executor.before(lambda c: print("🔹 Before Hook 1"))
        .before(lambda c: print("🔹 Before Hook 2"))
        .before(lambda c: print("🔹 Before Hook 3"))
        .on_completed(lambda c: print("✅ Completed Hook 1"))
        .on_completed(lambda c: print("✅ Completed Hook 2"))
        .finally_hook(lambda c: print("🏁 Finally Hook 1"))
        .finally_hook(lambda c: print("🏁 Finally Hook 2"))
        .execute(ctx, simple_sync_function)
    )

    print(f"Result: {result}")
    print()


def demonstrate_context_metadata():
    """Demonstrate context metadata usage"""
    print("=== Context Metadata Example ===")

    def metadata_function(ctx: CallContext) -> str:
        # Read metadata
        processing_start = ctx.get_meta("processing_start")
        user_pref = ctx.get_meta("user_preference") or "default"

        # Add processing info
        ctx.set_meta("processing_time", time.time() - processing_start)
        ctx.set_meta("function_called", "metadata_function")

        return f"Processed with preference: {user_pref}"

    ctx = CallContext(user_id="meta_user", turn_id="meta_turn")
    ctx.set_meta("processing_start", time.time())
    ctx.set_meta("user_preference", "advanced")

    executor = SyncCallContextExecutor()

    result = (
        executor.before(lambda c: c.set_meta("before_hook_executed", True))
        .on_completed(lambda c: print(f"📊 Processing time: {c.get_meta('processing_time'):.4f}s"))
        .finally_hook(lambda c: print(f"📋 Final metadata: {len(c.meta)} items"))
        .execute(ctx, metadata_function)
    )

    print(f"Result: {result}")
    print(f"All metadata: {ctx.meta}")
    print()


async def demonstrate_async_stream_executor():
    """Demonstrate async streaming (using InvokeCallContextExecutor)"""
    print("=== Async Stream (via Invoke) Example ===")

    ctx = CallContext(user_id="async_stream_user", turn_id="async_stream_turn")
    ctx.set_meta("name", "Async Streaming")

    executor = InvokeCallContextExecutor()

    # For async streaming, we use invoke executor with async stream function
    result = (
        executor.before(lambda c: print(f"🔹 Before: Starting async stream"))
        .on_completed(lambda c: print(f"✅ Completed: Async stream finished"))
        .finally_hook(lambda c: print(f"🏁 Finally: Async stream cleanup"))
        .execute(ctx, simple_async_stream_function)
    )

    print("Async streaming output: ", end="")
    async for chunk in result:
        print(chunk, end="")

    print(f"\nContext result: {ctx.get_meta('result')}")
    print()


async def main():
    """Main function demonstrating all executor patterns"""
    print("🚀 CallContextExecutor Implementation Examples")
    print("=" * 50)
    print("This demonstrates the BaseCallContextExecutor implementations")
    print("with focus on chaining API and hook system.\n")

    # Sync executor
    demonstrate_sync_executor()

    # Async executor
    await demonstrate_async_executor()

    # Stream executor
    demonstrate_stream_executor()

    # Invoke executor
    demonstrate_invoke_executor()

    # Error handling
    demonstrate_error_handling()

    # Multiple hooks
    demonstrate_multiple_hooks()

    # Context metadata
    demonstrate_context_metadata()

    # Async streaming
    await demonstrate_async_stream_executor()

    print("🎉 All executor examples completed!")


if __name__ == "__main__":
    asyncio.run(main())
