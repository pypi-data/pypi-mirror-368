import os
from typing import List, Optional
from langchain_core.callbacks import BaseCallbackHandler
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

api_key = os.getenv("OPENAI_API_KEY")


async def acall_llm_stream(
    input: str, model: str = "gpt-4", callbacks: Optional[List[BaseCallbackHandler]] = None
):
    """Async streaming LLM call"""
    llm = ChatOpenAI(model=model, api_key=api_key, streaming=True, callbacks=callbacks or [])

    async for chunk in llm.astream([HumanMessage(content=f"{input}에 대해 알려주세요.")]):
        if hasattr(chunk, "content") and chunk.content:
            yield chunk.content


def call_llm_stream(
    input: str, model: str = "gpt-4", callbacks: Optional[List[BaseCallbackHandler]] = None
):
    """Sync streaming LLM call (wrapper around async)"""
    import asyncio

    async def _async_wrapper():
        llm = ChatOpenAI(model=model, api_key=api_key, streaming=True, callbacks=callbacks or [])

        async for chunk in llm.astream([HumanMessage(content=f"{input}에 대해 알려주세요.")]):
            if hasattr(chunk, "content") and chunk.content:
                yield chunk.content

    # Convert async generator to sync generator
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        async_gen = _async_wrapper()
        while True:
            try:
                yield loop.run_until_complete(async_gen.__anext__())
            except StopAsyncIteration:
                break
    finally:
        loop.close()


async def acall_llm(
    input: str, model: str = "gpt-4", callbacks: Optional[List[BaseCallbackHandler]] = None
) -> str:
    """Async LLM invoke call"""
    llm = ChatOpenAI(model=model, api_key=api_key, callbacks=callbacks or [])

    result = await llm.ainvoke([HumanMessage(content=f"{input}에 대해 알려주세요.")])
    return result.content if hasattr(result, "content") else str(result)


def call_llm(
    input: str, model: str = "gpt-4", callbacks: Optional[List[BaseCallbackHandler]] = None
) -> str:
    """Sync LLM invoke call"""
    llm = ChatOpenAI(model=model, api_key=api_key, callbacks=callbacks or [])

    result = llm.invoke([HumanMessage(content=f"{input}에 대해 알려주세요.")])
    return result.content if hasattr(result, "content") else str(result)


async def acall_stream(
    input: str, model: str = "gpt-4", callbacks: Optional[List[BaseCallbackHandler]] = None
):
    """Async streaming LLM call (capital question format)"""
    llm = ChatOpenAI(model=model, api_key=api_key, streaming=True, callbacks=callbacks or [])

    async for chunk in llm.astream([HumanMessage(content=f"{input}의 수도는 어디인가요?")]):
        if hasattr(chunk, "content") and chunk.content:
            yield chunk.content
