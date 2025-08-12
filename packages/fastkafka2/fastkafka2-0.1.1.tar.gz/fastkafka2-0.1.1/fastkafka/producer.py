# fastkafka\producer.py
import orjson
import logging
from typing import Any
from aiokafka import AIOKafkaProducer
from .services.base import BaseKafkaService
from .services.retry import retry_on_connection

logger = logging.getLogger(__name__)


def _serialize_headers(headers: dict[str, str]) -> list[tuple[str, bytes]]:
    return [(k, v.encode()) for k, v in headers.items()]


class KafkaProducer(BaseKafkaService):
    def __init__(self, bootstrap_servers: str) -> None:
        self.bootstrap_servers = bootstrap_servers
        self._producer: AIOKafkaProducer | None = None

    @retry_on_connection()
    async def start(self) -> None:
        self._producer = AIOKafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: orjson.dumps(v),
        )
        await self._producer.start()
        logger.info("KafkaProducer started")

    @retry_on_connection()
    async def send_message(
        self,
        topic: str,
        data: dict[str, Any],
        headers: dict[str, str] | None = None,
        key: str | None = None,
    ) -> None:
        if not self._producer:
            raise RuntimeError("Producer not started")
        try:
            kafka_headers = _serialize_headers(headers or {})
            key_bytes = key.encode() if key else None
            await self._producer.send_and_wait(
                topic=topic,
                value=data,
                headers=kafka_headers,
                key=key_bytes,
            )
        except Exception:
            logger.exception("Failed to send message")
            raise

    async def stop(self) -> None:
        if self._producer:
            await self._producer.flush()
            await self._producer.stop()
            logger.info("KafkaProducer stopped")
