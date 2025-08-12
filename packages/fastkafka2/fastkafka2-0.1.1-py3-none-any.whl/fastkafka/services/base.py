# fastkafka\services\base.py
from abc import ABC, abstractmethod

__all__ = ["BaseKafkaService"]


class BaseKafkaService(ABC):
    @abstractmethod
    async def start(self) -> None: ...

    @abstractmethod
    async def stop(self) -> None: ...
