__version__ = "0.1.0"

from .logging_utils import suppress_external_logs
from .app import KafkaApp
from .handler import KafkaHandler
from .message import KafkaMessage
from .producer import KafkaProducer

suppress_external_logs()

__all__ = ["KafkaApp", "KafkaHandler", "KafkaMessage", "KafkaProducer"]

def __getattr__(name: str):
    if name in __all__:
        return globals()[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name}")

def __dir__():
    return __all__ + [n for n in globals() if n.startswith("_")]
