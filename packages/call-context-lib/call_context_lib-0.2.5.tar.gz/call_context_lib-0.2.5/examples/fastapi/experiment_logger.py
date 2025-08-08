import logging
from time import sleep

from call_context_lib.base import BaseCallContext
from langchain_core.callbacks import BaseCallbackHandler
import json
import asyncio

logger = logging.getLogger("fastapi_example")


class PrintExperimentLogger(BaseCallbackHandler):
    def __init__(self, topic: str):
        self.topic = topic
        self.ctx = None  # Will be set manually
        # self.producer = YourMQProducer(...)  # 실제 MQ 프로듀서 연동이 필요할 경우

    def set_context(self, ctx: BaseCallContext):
        """Manually set the context for logging"""
        self.ctx = ctx

    def on_llm_start(self, *args, **kwargs):
        """LangChain callback method"""
        if self.ctx:
            self.ctx.meta["hi"] = "hello"

    def on_llm_end(self, response, **kwargs):
        """LangChain callback method"""
        if self.ctx:
            self._log_experiment()

    def _log_experiment(self):
        if not self.ctx:
            return

        experiment_id = self.ctx.get_meta("experiment_id")
        if not experiment_id:
            return  # 실험 정보 없으면 로그 생략

        # Safely include all meta data in the payload
        meta_data = {}
        if hasattr(self.ctx, "meta") and self.ctx.meta is not None:
            try:
                # Convert meta data to a JSON-serializable format
                meta_data = {
                    str(k): str(v) if not isinstance(v, (str, int, float, bool, type(None))) else v
                    for k, v in self.ctx.meta.items()
                }
            except (AttributeError, TypeError) as e:
                logger.warning(f"[WARNING] Failed to process meta data: {e}")

        payload = {
            "turn_id": self.ctx.get_turn_id(),
            "user_id": self.ctx.get_user_id(),
            **meta_data,  # Include processed meta data
        }

        logger.debug(f"[PrintExperimentLogger] topic={self.topic} payload={json.dumps(payload)}")

        # 예시로 asyncio.sleep()만 넣음
        sleep(0.001)

        # 실제 사용 예:
        # await self.producer.send(self.topic, value=payload)
