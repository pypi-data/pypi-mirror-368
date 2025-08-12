# fastkafka\dependencies.py
import logging
from .admin import KafkaAdminService
from .consumer import KafkaConsumerService
from .registry import handlers_registry

logger = logging.getLogger(__name__)
_admin = KafkaAdminService()
_consumer: KafkaConsumerService | None = None


async def start_kafka(bootstrap_servers: str) -> None:
    global _consumer
    try:
        await _admin.start()
        for topic in handlers_registry:
            await _admin.create_topic(topic)
        _consumer = KafkaConsumerService(
            topics=list(handlers_registry), bootstrap_servers=bootstrap_servers
        )
        await _consumer.start()
        logger.info("Dependencies started")
    except Exception:
        logger.exception("Failed to start Kafka dependencies")
        raise


async def stop_kafka() -> None:
    try:
        if _consumer:
            await _consumer.stop()
        await _admin.stop()
        logger.info("Dependencies stopped")
    except Exception:
        logger.exception("Failed to stop Kafka dependencies")
        raise
