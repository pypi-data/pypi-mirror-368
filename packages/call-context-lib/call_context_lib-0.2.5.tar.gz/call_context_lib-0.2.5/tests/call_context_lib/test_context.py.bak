import os
import sys
from unittest.mock import patch

import pytest

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from examples.service import experiment_id, get_invoke_data, get_root_stream, get_v2_stream
from libs.call_context_lib.core import CallContext, CallContextCallback

# Test data
TEST_USER_ID = "test_user"
TEST_TURN_ID = "test_turn_001"
TEST_MODEL = "gpt-4"


class MockCallback(CallContextCallback):
    def __init__(self):
        self.called = False

    async def call(self, ctx):
        self.called = True
        self.ctx = ctx


@pytest.fixture
def mock_callback():
    return MockCallback()


@pytest.fixture
def mock_call_llm():
    async def mock(*args, **kwargs):
        return "mocked response"

    return mock


@pytest.fixture
def mock_llm_stream():
    async def mock_stream(*args, **kwargs):
        for word in ["Hello", " ", "World"]:
            yield word

    return mock_stream


@pytest.fixture
def mock_mq_experiment_logger():
    class MockMQExperimentLogger(CallContextCallback):
        def __init__(self, topic):
            self.topic = topic
            self.log_called = False

        async def call(self, ctx):
            self.log_called = True
            self.ctx = ctx

    return MockMQExperimentLogger("test-topic")


@pytest.fixture
def mock_call_context(mock_mq_experiment_logger):
    ctx = CallContext(user_id=TEST_USER_ID, turn_id=TEST_TURN_ID)
    ctx.callbacks.append(mock_mq_experiment_logger)
    return ctx


@pytest.mark.asyncio
async def test_get_root_stream(mock_llm_stream, mock_mq_experiment_logger):
    with (
        patch("examples.service.acall_llm_stream", new_callable=lambda: mock_llm_stream),
        patch("examples.service.MQExperimentLogger", return_value=mock_mq_experiment_logger),
    ):
        # Call the function
        stream = await get_root_stream()

        # Verify the stream produces expected values
        results = []
        async for item in stream:
            results.append(item)

        # Assertions
        assert results == ["Hello", " ", "World"]
        assert mock_mq_experiment_logger.log_called


@pytest.mark.asyncio
async def test_get_v2_stream(mock_llm_stream, mock_mq_experiment_logger):
    with (
        patch("examples.service.call_llm_stream", new_callable=lambda: mock_llm_stream),
        patch("examples.service.MQExperimentLogger", return_value=mock_mq_experiment_logger),
    ):
        # Call the function
        stream = await get_v2_stream()

        # Verify the stream produces expected values
        results = []
        async for item in stream:
            results.append(item)

        # Assertions
        assert results == ["Hello", " ", "World"]
        assert mock_mq_experiment_logger.log_called


@pytest.mark.asyncio
async def test_get_invoke_data(mock_call_llm, mock_mq_experiment_logger):
    with (
        patch("examples.service.call_llm", new=mock_call_llm),
        patch("examples.service.acall_llm", new=mock_call_llm),
        patch("examples.service.MQExperimentLogger", return_value=mock_mq_experiment_logger),
    ):
        # Call the function
        result = await get_invoke_data()

        # Assertions
        assert result == {"result": "mocked response", "result2": "mocked response"}
        assert mock_mq_experiment_logger.log_called


def test_experiment_id():
    assert experiment_id == "search-llm-ab-1"
