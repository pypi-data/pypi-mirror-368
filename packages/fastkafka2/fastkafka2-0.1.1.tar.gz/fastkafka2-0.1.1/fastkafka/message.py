# fastkafka\message.py
from pydantic import BaseModel


class KafkaMessage(BaseModel):
    topic: str
    data: object
    headers: dict[str, str] = {}
    key: str | None = None

    model_config = {"extra": "forbid", "frozen": True, "slots": True}
