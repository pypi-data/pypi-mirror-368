# fastkafka\handler.py
import logging
from typing import Callable, Any
from .registry import kafka_handler

logger = logging.getLogger(__name__)


class KafkaHandler:
    def __init__(self, prefix: str = "") -> None:
        self.prefix = prefix

    def __call__(
        self, topic: str, data_model: Any = None
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        return kafka_handler(topic, data_model)

    def include_handler(self, other: "KafkaHandler") -> None:
        self.prefix += f".{other.prefix}" if other.prefix else ""
