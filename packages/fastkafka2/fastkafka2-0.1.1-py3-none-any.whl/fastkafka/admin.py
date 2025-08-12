# fastkafka\admin.py
import logging
from aiokafka.admin import AIOKafkaAdminClient, NewTopic
from aiokafka.errors import TopicAlreadyExistsError
from .services.base import BaseKafkaService
from .services.retry import retry_on_connection

logger = logging.getLogger(__name__)


class KafkaAdminService(BaseKafkaService):
    def __init__(self, bootstrap_servers: str = "localhost:9092") -> None:
        self._bootstrap = bootstrap_servers
        self._client: AIOKafkaAdminClient | None = None

    async def start(self) -> None:
        await self._start()

    async def stop(self) -> None:
        await self._stop()

    @retry_on_connection()
    async def _start(self) -> None:
        self._client = AIOKafkaAdminClient(bootstrap_servers=self._bootstrap)
        await self._client.start()
        logger.info("KafkaAdminService started")

    async def create_topic(self, topic: str) -> None:
        if not self._client:
            raise RuntimeError("Admin client not initialized")
        try:
            await self._client.create_topics(
                new_topics=[
                    NewTopic(name=topic, num_partitions=1, replication_factor=1)
                ]
            )
            logger.info("Topic created: %s", topic)
        except TopicAlreadyExistsError:
            logger.debug("Topic already exists: %s", topic)
        except Exception:
            logger.exception("Error creating topic %s", topic)
            raise

    async def _stop(self) -> None:
        if self._client:
            await self._client.close()
            logger.info("KafkaAdminService stopped")
