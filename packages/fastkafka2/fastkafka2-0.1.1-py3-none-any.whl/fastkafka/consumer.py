# fastkafka\consumer.py
import asyncio
import orjson
import logging
from aiokafka import AIOKafkaConsumer
from .services.base import BaseKafkaService
from .registry import handlers_registry

logger = logging.getLogger(__name__)


class KafkaConsumerService(BaseKafkaService):
    def __init__(
        self,
        topics: list[str],
        bootstrap_servers: str,
        worker_count: int = 4,
        max_concurrency: int = 100,
    ):
        self._topics = topics
        self._bootstrap = bootstrap_servers
        self._worker_count = worker_count
        self._consumer: AIOKafkaConsumer | None = None
        self._queue: asyncio.Queue = asyncio.Queue(maxsize=1000)
        self._workers: list[asyncio.Task] = []
        self._semaphore = asyncio.Semaphore(max_concurrency)
        self._metrics_task: asyncio.Task | None = None

    async def start(self) -> None:
        self._consumer = AIOKafkaConsumer(
            *self._topics,
            bootstrap_servers=self._bootstrap,
            group_id="fastkafka_group",
            auto_offset_reset="latest",
            value_deserializer=lambda v: orjson.loads(v),
        )
        await self._consumer.start()
        logger.info("KafkaConsumerService started on topics %s", self._topics)

        asyncio.create_task(self._consume_loop())
        self._workers = [
            asyncio.create_task(self._worker_loop()) for _ in range(self._worker_count)
        ]
        self._metrics_task = asyncio.create_task(self._metrics_loop())

    async def stop(self) -> None:
        if self._consumer:
            await self._consumer.stop()
            logger.info("Consumer stopped")
        for w in self._workers:
            w.cancel()
        await asyncio.gather(*self._workers, return_exceptions=True)
        if self._metrics_task:
            self._metrics_task.cancel()
            await asyncio.gather(self._metrics_task, return_exceptions=True)

    async def _consume_loop(self) -> None:
        try:
            async for msg in self._consumer:
                headers = {k: (v.decode() if v else "") for k, v in (msg.headers or [])}
                key = msg.key.decode() if msg.key else None
                await self._queue.put((msg.topic, msg.value, headers, key))
        except Exception:
            logger.exception("Error in consume loop")

    async def _worker_loop(self) -> None:
        while True:
            topic, data, headers, key = await self._queue.get()
            for handler in handlers_registry.get(topic, []):
                await self._semaphore.acquire()
                asyncio.create_task(self._safe_invoke(handler, data, headers, key))
            self._queue.task_done()

    async def _safe_invoke(self, handler, data, headers, key):
        try:
            await handler.handle(data, headers, key)
        except Exception as e:
            logger.warning("Handler error on topic %s: %s", handler.topic, e)
        finally:
            self._semaphore.release()

    async def _metrics_loop(self):
        while True:
            logger.debug(
                f"[Kafka] Queue size: {self._queue.qsize()} | Workers: {len(self._workers)}"
            )
            await asyncio.sleep(10)
