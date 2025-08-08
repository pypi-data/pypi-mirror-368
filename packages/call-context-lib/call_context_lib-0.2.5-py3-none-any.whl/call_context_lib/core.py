from dataclasses import dataclass, field
from typing import Any, Optional, Callable, Awaitable, Union, AsyncGenerator, Generator, TypeVar
from langchain_core.callbacks import BaseCallbackHandler
from .base import BaseCallContext
from .logger import get_logger
import asyncio
from abc import ABC, abstractmethod

T = TypeVar("T")

logger = get_logger(__name__)


class CallContextCallbackHandler(BaseCallbackHandler):
    def __init__(self, ctx: "CallContext"):
        self.ctx = ctx

    def on_llm_start(self, *args, **kwargs):
        self.ctx.set_meta("llm_started", True)

    def on_llm_end(self, response, **kwargs):
        self.ctx.set_meta("llm_ended", True)

    def on_llm_error(self, error: Exception, **kwargs):
        self.ctx.set_error(error)

    async def on_complete(self, ctx: "CallContext"):
        pass


@dataclass
class CallContext(BaseCallContext):
    user_id: Optional[str] = None
    turn_id: Optional[str] = None
    meta: dict[str, Any] = field(default_factory=dict)
    """
    A dictionary to store metadata. 
    If the same key is set multiple times, values will be stored in a list.
    """
    error: Optional[Exception] = None
    callbacks: list[CallContextCallbackHandler] = field(default_factory=list)

    def get_user_id(self) -> Optional[str]:
        return self.user_id

    def get_turn_id(self) -> Optional[str]:
        return self.turn_id

    def get_meta(self, key: str, all_values: bool = False) -> Any:
        """
        Get meta value(s) for the given key.

        Args:
            key: The meta key to retrieve
            all_values: If True, returns a list of all values for the key.
                      If False (default), returns the most recent value.
        """
        if key not in self.meta:
            return None if not all_values else []

        values = self.meta[key]
        if not isinstance(values, list):
            return values if not all_values else [values]

        return values if all_values else values[-1] if values else None

    def set_meta(self, key: str, value: Any) -> None:
        """
        Set a meta value for the given key.
        If the key already exists, the new value will be appended to a list of values.
        """
        if key in self.meta:
            existing = self.meta[key]
            if isinstance(existing, list):
                existing.append(value)
            else:
                self.meta[key] = [existing, value]
        else:
            self.meta[key] = value

    def set_error(self, error: Exception):
        self.error = error

    async def on_complete(self):
        for callback in self.callbacks:
            if callback:
                await callback.on_complete(self)


class BaseCallContextExecutor(ABC):
    def __init__(self):
        self._before_hooks: list[Callable[[CallContext], None]] = []
        self._completed_hooks: list[Callable[[CallContext], None]] = []
        self._error_hooks: list[Callable[[CallContext, Exception], None]] = []
        self._finally_hooks: list[Callable[[CallContext], None]] = []

    def before(self, hook: Callable[[CallContext], None]):
        self._before_hooks.append(hook)
        return self

    def on_completed(self, hook: Callable[[CallContext], None]):
        self._completed_hooks.append(hook)
        return self

    def on_error(self, hook: Callable[[CallContext, Exception], None]):
        self._error_hooks.append(hook)
        return self

    def finally_hook(self, hook: Callable[[CallContext], None]):
        self._finally_hooks.append(hook)
        return self

    def _run_before_hooks(self, ctx: CallContext):
        for hook in self._before_hooks:
            hook(ctx)

    def _run_completed_hooks(self, ctx: CallContext):
        for hook in self._completed_hooks:
            hook(ctx)

    def _run_error_hooks(self, ctx: CallContext, error: Exception):
        for hook in self._error_hooks:
            hook(ctx, error)

    def _run_finally_hooks(self, ctx: CallContext):
        for hook in self._finally_hooks:
            hook(ctx)

    @abstractmethod
    def execute(self, ctx: CallContext, func: Callable[[CallContext], T]) -> T:
        pass


class SyncCallContextExecutor(BaseCallContextExecutor):
    def execute(self, ctx: CallContext, func: Callable[[CallContext], T]) -> T:
        logger.debug(
            f"SyncCallContextExecutor: Starting execution for user {ctx.user_id or 'unknown'}, turn {ctx.turn_id or 'unknown'}"
        )
        self._run_before_hooks(ctx)

        try:
            logger.debug(f"SyncCallContextExecutor: Executing function for user {ctx.user_id or 'unknown'}")
            result = func(ctx)
            self._run_completed_hooks(ctx)
            logger.debug(
                f"SyncCallContextExecutor: Successfully completed execution for user {ctx.user_id or 'unknown'}"
            )
            return result
        except Exception as e:
            logger.debug(f"SyncCallContextExecutor: Error occurred for user {ctx.user_id or 'unknown'}: {e}")
            ctx.set_error(e)
            self._run_error_hooks(ctx, e)
            raise
        finally:
            self._run_finally_hooks(ctx)


class AsyncCallContextExecutor(BaseCallContextExecutor):
    def __init__(self):
        super().__init__()
        self._before_async_hooks: list[Callable[[CallContext], Awaitable[None]]] = []
        self._completed_async_hooks: list[Callable[[CallContext], Awaitable[None]]] = []
        self._error_async_hooks: list[Callable[[CallContext, Exception], Awaitable[None]]] = []
        self._finally_async_hooks: list[Callable[[CallContext], Awaitable[None]]] = []

    def before_async(self, hook: Callable[[CallContext], Awaitable[None]]):
        self._before_async_hooks.append(hook)
        return self

    def on_completed_async(self, hook: Callable[[CallContext], Awaitable[None]]):
        self._completed_async_hooks.append(hook)
        return self

    def on_error_async(self, hook: Callable[[CallContext, Exception], Awaitable[None]]):
        self._error_async_hooks.append(hook)
        return self

    def finally_async(self, hook: Callable[[CallContext], Awaitable[None]]):
        self._finally_async_hooks.append(hook)
        return self

    async def _run_before_async_hooks(self, ctx: CallContext):
        for hook in self._before_async_hooks:
            await hook(ctx)

    async def _run_completed_async_hooks(self, ctx: CallContext):
        for hook in self._completed_async_hooks:
            await hook(ctx)

    async def _run_error_async_hooks(self, ctx: CallContext, error: Exception):
        for hook in self._error_async_hooks:
            await hook(ctx, error)

    async def _run_finally_async_hooks(self, ctx: CallContext):
        for hook in self._finally_async_hooks:
            await hook(ctx)

    def execute(self, ctx: CallContext, func: Callable[[CallContext], T]) -> T:
        raise NotImplementedError("Use async_execute for async operations")

    async def async_execute(self, ctx: CallContext, func: Callable[[CallContext], Awaitable[T]]) -> T:
        logger.debug(
            f"AsyncCallContextExecutor: Starting execution for user {ctx.user_id or 'unknown'}, turn {ctx.turn_id or 'unknown'}"
        )
        self._run_before_hooks(ctx)
        await self._run_before_async_hooks(ctx)

        try:
            logger.debug(f"AsyncCallContextExecutor: Executing async function for user {ctx.user_id or 'unknown'}")
            result = await func(ctx)
            self._run_completed_hooks(ctx)
            await self._run_completed_async_hooks(ctx)
            logger.debug(
                f"AsyncCallContextExecutor: Successfully completed async execution for user {ctx.user_id or 'unknown'}"
            )
            return result
        except Exception as e:
            logger.debug(f"AsyncCallContextExecutor: Error occurred for user {ctx.user_id or 'unknown'}: {e}")
            ctx.set_error(e)
            self._run_error_hooks(ctx, e)
            await self._run_error_async_hooks(ctx, e)
            raise
        finally:
            self._run_finally_hooks(ctx)
            await self._run_finally_async_hooks(ctx)


class StreamCallContextExecutor(BaseCallContextExecutor):
    def execute(self, ctx: CallContext, func: Callable[[CallContext], T]) -> T:
        raise NotImplementedError("Use stream_execute for streaming operations")

    def stream_execute(
        self, ctx: CallContext, func: Callable[[CallContext], Generator[T, None, None]]
    ) -> Generator[T, None, None]:
        logger.debug(
            f"StreamCallContextExecutor: Starting stream execution for user {ctx.user_id or 'unknown'}, turn {ctx.turn_id or 'unknown'}"
        )
        self._run_before_hooks(ctx)

        try:
            logger.debug(f"StreamCallContextExecutor: Beginning stream generation for user {ctx.user_id or 'unknown'}")
            for item in func(ctx):
                yield item
            self._run_completed_hooks(ctx)
            logger.debug(
                f"StreamCallContextExecutor: Successfully completed stream execution for user {ctx.user_id or 'unknown'}"
            )
        except Exception as e:
            logger.debug(f"StreamCallContextExecutor: Error occurred for user {ctx.user_id or 'unknown'}: {e}")
            ctx.set_error(e)
            self._run_error_hooks(ctx, e)
            raise
        finally:
            self._run_finally_hooks(ctx)

    async def async_stream_execute(
        self, ctx: CallContext, func: Callable[[CallContext], AsyncGenerator[T, None]]
    ) -> AsyncGenerator[T, None]:
        self._run_before_hooks(ctx)

        try:
            async for item in func(ctx):
                yield item
            self._run_completed_hooks(ctx)
        except Exception as e:
            ctx.set_error(e)
            self._run_error_hooks(ctx, e)
            raise
        finally:
            self._run_finally_hooks(ctx)


class InvokeCallContextExecutor(BaseCallContextExecutor):
    def execute(self, ctx: CallContext, func: Callable[[CallContext], T]) -> T:
        self._run_before_hooks(ctx)

        try:
            result = func(ctx)
            self._run_completed_hooks(ctx)

            # Try to schedule callback completion if event loop is running
            try:
                loop = asyncio.get_running_loop()
                asyncio.create_task(ctx.on_complete())
            except RuntimeError:
                # No event loop running, skip callback completion
                pass

            return result
        except Exception as e:
            ctx.set_error(e)
            self._run_error_hooks(ctx, e)
            raise
        finally:
            self._run_finally_hooks(ctx)
