import logging
from call_context_lib import CallContext, CallContextCallbackHandler
from experiment_logger import PrintExperimentLogger
from llm_module import acall_llm_stream, acall_llm, call_llm, acall_stream

logger = logging.getLogger("fastapi_example.service")

experiment_id = "search-llm-ab-1"


async def get_openai_stream_example():
    """Example usage with new callback pattern using llm_module"""
    logger.info("Creating CallContext for streaming example")
    ctx = CallContext(user_id="kim", turn_id="t001")
    ctx.meta["model"] = "gpt-4"
    ctx.meta["experiment_id"] = experiment_id

    # Callback array pattern - mix CallContext callbacks with other LangChain callbacks
    exp_logger = PrintExperimentLogger("experiment-topic")
    exp_logger.set_context(ctx)
    callbacks = [CallContextCallbackHandler(ctx), exp_logger]

    # Use llm_module function with callbacks (capital question format)
    logger.info("Starting streaming LLM call")
    async for chunk in acall_stream("한국", "gpt-4", callbacks=callbacks):
        yield chunk

    # Complete callbacks
    logger.info("Completing callbacks for streaming example")
    await ctx.on_complete()


async def get_openai_invoke_example():
    """Example usage with invoke pattern using llm_module"""
    ctx = CallContext(user_id="kim", turn_id="t002")
    ctx.meta["model"] = "gpt-4"
    ctx.meta["experiment_id"] = experiment_id

    # Callback array pattern - mix CallContext callbacks with other LangChain callbacks
    exp_logger = PrintExperimentLogger("experiment-topic")
    exp_logger.set_context(ctx)
    callbacks = [CallContextCallbackHandler(ctx), exp_logger]

    # Use llm_module invoke function with callbacks
    result = await acall_llm("Hello", "gpt-4", callbacks=callbacks)

    # Complete callbacks
    await ctx.on_complete()

    return {"result": result}


async def get_openai_stream(input_text: str, model: str = "gpt-4"):
    """Parameterized stream function using llm_module"""
    ctx = CallContext(user_id="kim", turn_id="t003")
    ctx.meta["model"] = model
    ctx.meta["experiment_id"] = experiment_id

    # Callback array pattern - mix CallContext callbacks with other LangChain callbacks
    exp_logger = PrintExperimentLogger("experiment-topic")
    exp_logger.set_context(ctx)
    callbacks = [CallContextCallbackHandler(ctx), exp_logger]

    # Use llm_module function with callbacks (capital question format)
    async for chunk in acall_stream(input_text, model, callbacks=callbacks):
        yield chunk

    await ctx.on_complete()


async def get_llm_module_stream_example():
    """Example using llm_module functions with callback pattern"""
    ctx = CallContext(user_id="kim", turn_id="t004")
    ctx.meta["model"] = "gpt-4"
    ctx.meta["experiment_id"] = experiment_id

    exp_logger = PrintExperimentLogger("experiment-topic")
    exp_logger.set_context(ctx)
    callbacks = [CallContextCallbackHandler(ctx), exp_logger]

    # Use llm_module function with callbacks
    async for chunk in acall_llm_stream("Python", "gpt-4", callbacks=callbacks):
        yield chunk

    await ctx.on_complete()


async def get_llm_module_invoke_example():
    """Example using llm_module invoke functions with callback pattern"""
    ctx = CallContext(user_id="kim", turn_id="t005")
    ctx.meta["model"] = "gpt-4"
    ctx.meta["experiment_id"] = experiment_id

    exp_logger = PrintExperimentLogger("experiment-topic")
    exp_logger.set_context(ctx)
    callbacks = [CallContextCallbackHandler(ctx), exp_logger]

    # Use llm_module functions with callbacks
    result_async = await acall_llm("JavaScript", "gpt-4", callbacks=callbacks)
    result_sync = call_llm("TypeScript", "gpt-4", callbacks=callbacks)

    await ctx.on_complete()

    return {"async_result": result_async, "sync_result": result_sync}
