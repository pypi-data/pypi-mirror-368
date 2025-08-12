# fastkafka\services\retry.py
import asyncio
import logging
from aiokafka.errors import KafkaConnectionError
from typing import Callable, TypeVar, Awaitable

__all__ = ["retry_on_connection"]

Logger = logging.getLogger(__name__)
F = TypeVar("F", bound=Callable[..., Awaitable[None]])


def retry_on_connection(delay: int = 5) -> Callable[[F], F]:
    def decorator(fn: F) -> F:
        async def wrapper(*args, **kwargs):
            while True:
                try:
                    return await fn(*args, **kwargs)
                except KafkaConnectionError as e:
                    Logger.warning(
                        "Retrying %s due to connection error: %s", fn.__name__, e
                    )
                    await asyncio.sleep(delay)

        return wrapper  # type: ignore

    return decorator
