# fastkafka2

Next-generation FastAPI-like DX for Kafka (version 2).

## Installation

``` bash
pip install fastkafka2
```

## Use example
### Project arch
```shell
├── api/
│   ├── kafka/
│   │   ├── handlers/
│   │   │   ├── example/
│   │   │   │   ├─ schemas.py
│   │   │   │   └─ handler.py
│   │   │   └── base_handler.py
│   │   └── lifespan.py
│
├── main.py
```

### Schemas
``` python
# api\kafka\handlers\example\schemas.py
from pydantic import BaseModel


class ExampleSchema(BaseModel):
    msg: str
```

### Handler
``` python
# api\kafka\handlers\example\handler.py
import logging

from fastkafka.handler import KafkaHandler
from fastkafka.message import KafkaMessage
from fastkafka.producer import KafkaProducer


handler = KafkaHandler()

kafka_producer = KafkaProducer(bootstrap_servers="127.0.0.1:9092")


@handler("example")
async def example_handler(message: KafkaMessage):
    t = int(message.headers.get("try")) + 1
    logging.info(f"Пришло: {message}")
    await kafka_producer.send_message(
        topic="example-2", data={"msg": "wddwd"}, headers={"try": f"{t}"}, key=None
    )
    logging.info(f"Отправил: {f'{t}'}")
```


### Grouping of handlers
``` python
# api\kafka\handlers\base_handler.py
from api.kafka.handlers.example.handler import handler as example_handler

from fastkafka.handler import KafkaHandler

base_handler = KafkaHandler()

base_handler.include_handler(example_handler)
```


### Lifespan fastkafka app
``` python
# api/kafka/lifespan.py
import logging
from contextlib import asynccontextmanager
from fastkafka.app import KafkaApp
from api.kafka.handlers.base_handler import base_handler

from api.kafka.handlers.example.handler import kafka_producer


@asynccontextmanager
async def lifespan(app: KafkaApp):
    logging.info("Lifespan: запуск")
    try:
        await kafka_producer.start()
        yield
        logging.info("Lifespan: выполнен")
    finally:
        await kafka_producer.stop()
        logging.info("Lifespan: остановка")


app = KafkaApp(
    title="Kafka Gateway",
    description="Kafka-based microservice",
    bootstrap_servers="127.0.0.1:9092",
    lifespan=lifespan,
)

app.include_handler(base_handler)
```


### Entry point main app
``` python
# main.py
import asyncio
from logging_config import setup_logging
from api.kafka.lifespan import app

if __name__ == "__main__":
    setup_logging()
    asyncio.run(app.run())
```


