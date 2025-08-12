# fastkafka\logging_utils.py
import logging


def suppress_external_logs() -> None:
    suppressed = [
        "aiokafka",
        "kafka",
        "asyncio",
        "aiokafka.consumer.fetcher",
        "aiokafka.cluster",
        "aiokafka.producer.producer",
        "aiokafka.consumer.group_coordinator",
        "aiokafka.consumer.subscription_state",
    ]
    for name in suppressed:
        lg = logging.getLogger(name)
        lg.setLevel(logging.CRITICAL)
        lg.propagate = False
