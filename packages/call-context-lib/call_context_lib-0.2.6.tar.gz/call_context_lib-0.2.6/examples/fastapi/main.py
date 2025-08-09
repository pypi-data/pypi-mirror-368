import logging
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

# Configure logging for FastAPI application
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Set call_context_lib logger to INFO level so it doesn't output debug logs
from call_context_lib import set_log_level

set_log_level(logging.INFO)

# Create logger for this application
logger = logging.getLogger("fastapi_example")

try:
    from service import (
        get_openai_stream_example,
        get_openai_invoke_example,
        get_openai_stream,
        get_llm_module_stream_example,
        get_llm_module_invoke_example,
    )
except ImportError:
    from .service import (
        get_openai_stream_example,
        get_openai_invoke_example,
        get_openai_stream,
        get_llm_module_stream_example,
        get_llm_module_invoke_example,
    )

app = FastAPI()


@app.get("/hello/{name}")
async def say_hello(name: str):
    logger.info(f"Received hello request for name: {name}")
    return {"message": f"Hello {name}"}


@app.post("/openai-stream-example")
async def openai_stream_example():
    """Example endpoint showing new callback pattern with streaming"""
    logger.info("Starting OpenAI stream example")
    return StreamingResponse(get_openai_stream_example(), media_type="text/event-stream")


@app.post("/openai-invoke-example")
async def openai_invoke_example():
    """Example endpoint showing new callback pattern with invoke"""
    logger.info("Starting OpenAI invoke example")
    result = await get_openai_invoke_example()
    logger.info("Completed OpenAI invoke example")
    return result


@app.post("/openai-stream")
async def openai_stream(input_text: str = "한국", model: str = "gpt-4"):
    """Parameterized streaming endpoint"""
    logger.info(f"Starting parameterized stream: input='{input_text}', model='{model}'")
    return StreamingResponse(get_openai_stream(input_text, model), media_type="text/event-stream")


@app.post("/llm-module-stream-example")
async def llm_module_stream_example():
    """Example endpoint using llm_module functions with streaming"""
    return StreamingResponse(get_llm_module_stream_example(), media_type="text/event-stream")


@app.post("/llm-module-invoke-example")
async def llm_module_invoke_example():
    """Example endpoint using llm_module functions with invoke"""
    result = await get_llm_module_invoke_example()
    return result
