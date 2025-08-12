# fastkafka\app.py
import asyncio
import logging
import signal
from typing import Callable
from contextlib import AbstractAsyncContextManager

from .producer import KafkaProducer
from .admin import KafkaAdminService
from .consumer import KafkaConsumerService
from .registry import handlers_registry
from .handler import KafkaHandler

logger = logging.getLogger(__name__)


class KafkaApp:
    def __init__(
        self,
        title: str,
        description: str,
        bootstrap_servers: str = "localhost:9092",
        lifespan: Callable[["KafkaApp"], AbstractAsyncContextManager] | None = None,
    ) -> None:
        self.title = title
        self.description = description
        self.bootstrap = bootstrap_servers
        self._lifespan = lifespan(self) if lifespan else None

        self._producer = KafkaProducer(self.bootstrap)
        self._admin = KafkaAdminService(self.bootstrap)
        self._consumer: KafkaConsumerService | None = None
        self._groups: list[KafkaHandler] = []

    def include_handler(self, handler: KafkaHandler) -> None:
        self._groups.append(handler)
        logger.debug("Included handler group %s", handler.prefix)

    async def start(self) -> None:
        logger.info("Starting %s", self.title)
        try:
            if self._lifespan:
                await self._lifespan.__aenter__()
            await self._admin.start()
            for topic in handlers_registry:
                await self._admin.create_topic(topic)
            self._consumer = KafkaConsumerService(
                topics=list(handlers_registry), bootstrap_servers=self.bootstrap
            )
            await self._consumer.start()
            logger.info("%s started", self.title)
        except Exception:
            logger.exception("KafkaApp.start failed")
            raise

    async def stop(self) -> None:
        logger.info("Stopping %s", self.title)
        try:
            if self._consumer:
                await self._consumer.stop()
            await self._admin.stop()
            if self._lifespan:
                await self._lifespan.__aexit__(None, None, None)
            logger.info("%s stopped", self.title)
        except Exception:
            logger.exception("KafkaApp.stop failed")
            raise

    async def run(self) -> None:
        loop = asyncio.get_running_loop()
        shutdown_event = asyncio.Event()
        try:
            for sig in (signal.SIGINT, signal.SIGTERM):
                loop.add_signal_handler(sig, shutdown_event.set)
        except (NotImplementedError, AttributeError):
            signal.signal(signal.SIGINT, lambda *_: shutdown_event.set())
        await self.start()
        await shutdown_event.wait()
        await self.stop()
