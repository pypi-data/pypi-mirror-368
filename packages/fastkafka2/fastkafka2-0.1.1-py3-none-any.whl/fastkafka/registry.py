# fastkafka\registry.py
import logging
from inspect import signature, iscoroutinefunction
from typing import Any, Callable
from pydantic import BaseModel
from fastkafka.message import KafkaMessage
from fastkafka.di.di_container import resolve

__all__ = ["kafka_handler"]

logger = logging.getLogger(__name__)
handlers_registry: dict[str, list["CompiledHandler"]] = {}


class CompiledHandler:
    __slots__ = ("topic", "func", "sig", "data_model", "dependencies")

    def __init__(
        self, topic: str, func: Callable[..., Any], data_model: type[BaseModel] | None
    ):
        self.topic = topic
        self.func = func
        self.sig = signature(func)
        self.data_model = data_model

        self.dependencies: dict[str, Any] = {}
        for name, param in self.sig.parameters.items():
            if param.annotation not in (KafkaMessage, data_model):
                self.dependencies[name] = resolve(param.annotation)

    async def handle(
        self, raw_data: Any, headers: dict[str, str] | None, key: str | None
    ):
        msg_data = self.data_model(**raw_data) if self.data_model else raw_data
        message = KafkaMessage(
            topic=self.topic, data=msg_data, headers=headers or {}, key=key
        )

        kwargs = {
            name: (
                self.dependencies.get(name)
                if param.annotation not in (KafkaMessage, self.data_model)
                else message
            )
            for name, param in self.sig.parameters.items()
        }

        return await self.func(**kwargs)


def kafka_handler(topic: str, data_model: type[BaseModel] | None = None):
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        if not iscoroutinefunction(func):
            raise TypeError("Handler must be async")
        handlers_registry.setdefault(topic, []).append(
            CompiledHandler(topic, func, data_model)
        )
        logger.debug("Registered handler %s for topic %s", func.__name__, topic)
        return func

    return decorator
