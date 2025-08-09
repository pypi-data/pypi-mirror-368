"""
CallContextExecutor examples with A/B testing LLM model selection
"""

import asyncio
import hashlib
import os
from typing import AsyncGenerator, Generator, List, Optional
from dotenv import load_dotenv

load_dotenv()

from langchain_core.callbacks import BaseCallbackHandler
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

from call_context_lib import (
    CallContext,
    CallContextCallbackHandler,
    SyncCallContextExecutor,
    AsyncCallContextExecutor,
    StreamCallContextExecutor,
    InvokeCallContextExecutor,
)


class ABTestLLMSelector:
    """A/B test for LLM model selection based on user_id"""

    @staticmethod
    def get_model_for_user(user_id: str) -> str:
        """Select LLM model based on user_id hash for A/B testing"""
        hash_value = int(hashlib.md5(user_id.encode()).hexdigest(), 16)

        if hash_value % 2 == 0:
            return "gpt-3.5-turbo"
        else:
            return "gpt-4"


class PrintExperimentCallback(CallContextCallbackHandler):
    """Experiment logging callback that extends CallContextCallbackHandler"""

    def __init__(self, ctx: CallContext):
        super().__init__(ctx)

    async def on_complete(self, ctx: CallContext):
        model = ctx.get_meta("selected_model")
        print(f"🧪 Experiment completed for user {ctx.user_id}, model: {model}")

        # Print additional meta information
        input_text = ctx.get_meta("input")
        response = ctx.get_meta("response")
        print(f"   Input: {input_text}")
        print(f"   Response length: {len(response) if response else 0} characters")


# LLM call functions adapted from llm_module.py
def call_llm(ctx: CallContext, input_text: str) -> str:
    """Synchronous LLM call using context model"""
    api_key = os.getenv("OPENAI_API_KEY")
    model = ctx.get_meta("selected_model")
    ctx.set_meta("input", input_text)

    if not api_key:
        # Mock response when API key is not available
        response = f"Mock response from {model} for: {input_text}에 대해 알려주세요."
        ctx.set_meta("response", response)
        return response

    llm = ChatOpenAI(
        model=model,
        api_key=api_key,
        callbacks=[ctx_callback for ctx_callback in ctx.callbacks if isinstance(ctx_callback, BaseCallbackHandler)],
    )

    result = llm.invoke([HumanMessage(content=f"{input_text}에 대해 알려주세요.")])
    response = result.content if hasattr(result, "content") else str(result)
    ctx.set_meta("response", response)
    return response


async def acall_llm(ctx: CallContext, input_text: str) -> str:
    """Asynchronous LLM call using context model"""
    api_key = os.getenv("OPENAI_API_KEY")
    model = ctx.get_meta("selected_model")
    ctx.set_meta("input", input_text)

    if not api_key:
        # Mock response when API key is not available
        await asyncio.sleep(0.1)  # Simulate async processing
        response = f"Mock async response from {model} for: {input_text}에 대해 알려주세요."
        ctx.set_meta("response", response)
        return response

    llm = ChatOpenAI(
        model=model,
        api_key=api_key,
        callbacks=[ctx_callback for ctx_callback in ctx.callbacks if isinstance(ctx_callback, BaseCallbackHandler)],
    )

    result = await llm.ainvoke([HumanMessage(content=f"{input_text}에 대해 알려주세요.")])
    response = result.content if hasattr(result, "content") else str(result)
    ctx.set_meta("response", response)
    return response


def call_llm_stream(ctx: CallContext, input_text: str) -> Generator[str, None, None]:
    """Synchronous streaming LLM call using context model"""
    api_key = os.getenv("OPENAI_API_KEY")
    model = ctx.get_meta("selected_model")
    ctx.set_meta("input", input_text)

    if not api_key:
        # Mock streaming response when API key is not available
        response_parts = [f"Mock", "streaming", "from", model, f"for:", f"{input_text}에", "대해", "알려주세요."]
        for part in response_parts:
            yield part
        ctx.set_meta("response", " ".join(response_parts))
        return

    llm = ChatOpenAI(
        model=model,
        api_key=api_key,
        streaming=True,
        callbacks=[ctx_callback for ctx_callback in ctx.callbacks if isinstance(ctx_callback, BaseCallbackHandler)],
    )

    # Convert async generator to sync generator
    import asyncio

    async def _async_wrapper():
        async for chunk in llm.astream([HumanMessage(content=f"{input_text}에 대해 알려주세요.")]):
            if hasattr(chunk, "content") and chunk.content:
                yield chunk.content

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    response_parts = []
    try:
        async_gen = _async_wrapper()
        while True:
            try:
                chunk = loop.run_until_complete(async_gen.__anext__())
                response_parts.append(chunk)
                yield chunk
            except StopAsyncIteration:
                break
    finally:
        loop.close()
        ctx.set_meta("response", "".join(response_parts))


async def acall_llm_stream(ctx: CallContext, input_text: str) -> AsyncGenerator[str, None]:
    """Asynchronous streaming LLM call using context model"""
    api_key = os.getenv("OPENAI_API_KEY")
    model = ctx.get_meta("selected_model")
    ctx.set_meta("input", input_text)

    if not api_key:
        # Mock async streaming response when API key is not available
        response_parts = [
            f"Mock",
            "async",
            "streaming",
            "from",
            model,
            f"for:",
            f"{input_text}에",
            "대해",
            "알려주세요.",
        ]
        for part in response_parts:
            await asyncio.sleep(0.05)  # Simulate async processing
            yield part
        ctx.set_meta("response", " ".join(response_parts))
        return

    llm = ChatOpenAI(
        model=model,
        api_key=api_key,
        streaming=True,
        callbacks=[ctx_callback for ctx_callback in ctx.callbacks if isinstance(ctx_callback, BaseCallbackHandler)],
    )

    response_parts = []
    async for chunk in llm.astream([HumanMessage(content=f"{input_text}에 대해 알려주세요.")]):
        if hasattr(chunk, "content") and chunk.content:
            response_parts.append(chunk.content)
            yield chunk.content

    ctx.set_meta("response", "".join(response_parts))


# Example functions
def sync_example():
    """Synchronous executor example"""
    print("=== Sync Example ===")

    ctx = CallContext(user_id="user123", turn_id="turn456")
    ctx.callbacks = [PrintExperimentCallback(ctx)]

    executor = SyncCallContextExecutor()

    result = (
        executor.before(lambda ctx: ctx.set_meta("selected_model", ABTestLLMSelector.get_model_for_user(ctx.user_id)))
        .before(lambda ctx: print(f"Selected model for {ctx.user_id}: {ctx.get_meta('selected_model')}"))
        .on_completed(lambda ctx: print(f"✅ Completed sync call for {ctx.user_id}"))
        .on_error(lambda ctx, error: print(f"❌ Error in sync call: {error}"))
        .finally_hook(lambda ctx: print(f"🏁 Finally: errors={ctx.error}"))
        .execute(ctx, lambda ctx: call_llm(ctx, "Python"))
    )

    print(f"Result: {result[:100]}...")
    print()


async def async_example():
    """Asynchronous executor example"""
    print("=== Async Example ===")

    ctx = CallContext(user_id="user789", turn_id="turn012")
    ctx.callbacks = [PrintExperimentCallback(ctx)]

    executor = AsyncCallContextExecutor()

    result = await (
        executor.before(lambda ctx: ctx.set_meta("selected_model", ABTestLLMSelector.get_model_for_user(ctx.user_id)))
        .before(lambda ctx: print(f"Selected model for {ctx.user_id}: {ctx.get_meta('selected_model')}"))
        .on_completed(lambda ctx: print(f"✅ Completed async call for {ctx.user_id}"))
        .on_error(lambda ctx, error: print(f"❌ Error in async call: {error}"))
        .finally_hook(lambda ctx: print(f"🏁 Finally: errors={ctx.error}"))
        .finally_async(lambda ctx: ctx.on_complete())
        .async_execute(ctx, lambda ctx: acall_llm(ctx, "JavaScript"))
    )

    print(f"Result: {result[:100]}...")
    print()


def invoke_example():
    """Invoke executor example with automatic callback processing"""
    print("=== Invoke Example ===")

    ctx = CallContext(user_id="user345", turn_id="turn678")
    ctx.callbacks = [PrintExperimentCallback(ctx)]

    executor = InvokeCallContextExecutor()

    result = (
        executor.before(lambda ctx: ctx.set_meta("selected_model", ABTestLLMSelector.get_model_for_user(ctx.user_id)))
        .before(lambda ctx: print(f"Selected model for {ctx.user_id}: {ctx.get_meta('selected_model')}"))
        .on_completed(lambda ctx: print(f"✅ Completed invoke call for {ctx.user_id}"))
        .on_error(lambda ctx, error: print(f"❌ Error in invoke call: {error}"))
        .finally_hook(lambda ctx: print(f"🏁 Finally: errors={ctx.error}, callbacks will be processed"))
        .execute(ctx, lambda ctx: call_llm(ctx, "Go"))
    )

    print(f"Result: {result[:100]}...")
    print()


def stream_example():
    """Streaming executor example"""
    print("=== Stream Example ===")

    ctx = CallContext(user_id="user567", turn_id="turn890")
    ctx.callbacks = [PrintExperimentCallback(ctx)]

    executor = StreamCallContextExecutor()

    stream = (
        executor.before(lambda ctx: ctx.set_meta("selected_model", ABTestLLMSelector.get_model_for_user(ctx.user_id)))
        .before(lambda ctx: print(f"Selected model for {ctx.user_id}: {ctx.get_meta('selected_model')}"))
        .on_completed(lambda ctx: print(f"✅ Completed stream call for {ctx.user_id}"))
        .on_error(lambda ctx, error: print(f"❌ Error in stream call: {error}"))
        .finally_hook(lambda ctx: print(f"🏁 Finally: errors={ctx.error}"))
        .stream_execute(ctx, lambda ctx: call_llm_stream(ctx, "Rust"))
    )

    result_parts = []
    for part in stream:
        print(f"📡 Streamed")
        print(f"\n{part}", end="", flush=True)
        result_parts.append(part)

    print(f"\nFull result: {len(''.join(result_parts))} characters")
    print()


async def async_stream_example():
    """Async streaming executor example"""
    print("=== Async Stream Example ===")

    ctx = CallContext(user_id="user999", turn_id="turn111")
    ctx.callbacks = [PrintExperimentCallback(ctx)]

    executor = StreamCallContextExecutor()

    stream = (
        executor.before(lambda ctx: ctx.set_meta("selected_model", ABTestLLMSelector.get_model_for_user(ctx.user_id)))
        .before(lambda ctx: print(f"Selected model for {ctx.user_id}: {ctx.get_meta('selected_model')}"))
        .on_completed(lambda ctx: print(f"✅ Completed async stream call for {ctx.user_id}"))
        .on_error(lambda ctx, error: print(f"❌ Error in async stream call: {error}"))
        .finally_hook(lambda ctx: print(f"🏁 Finally: errors={ctx.error}"))
        .async_stream_execute(ctx, lambda ctx: acall_llm_stream(ctx, "TypeScript"))
    )

    result_parts = []
    async for part in stream:
        print(f"📡 Async streamed")
        print(f"\n{part}", end="", flush=True)
        result_parts.append(part)

    print(f"\nFull result: {len(''.join(result_parts))} characters")
    print()


async def main():
    """Run all examples"""
    print("🚀 CallContextExecutor Examples with A/B Testing")
    print("=" * 50)

    # Check if API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  OPENAI_API_KEY not set. Using mock responses.")
        print()

    # Run sync example
    sync_example()

    # Run async example
    await async_example()

    # Run invoke example
    invoke_example()

    # Run stream example
    stream_example()

    # Run async stream example
    await async_stream_example()


if __name__ == "__main__":
    asyncio.run(main())
