# fastkafka\di\di_container.py
import logging
from inspect import isclass, signature
from typing import Any, Callable, Type

logger = logging.getLogger(__name__)

_singletons: dict[Type[Any], Any] = {}
_factories: dict[Type[Any], Callable[..., Any]] = {}
_resolving_stack: set[Type[Any]] = set()
_sig_cache: dict[Type[Any], Any] = {}


def register_singleton(cls: Type[Any], instance: Any) -> None:
    _singletons[cls] = instance


def register_factory(cls: Type[Any], factory: Callable[..., Any]) -> None:
    _factories[cls] = factory


def resolve(cls: Type[Any]) -> Any:
    if cls in _singletons:
        return _singletons[cls]
    if cls in _factories:
        return _factories[cls]()
    if not isclass(cls):
        raise TypeError(f"Cannot resolve non-class type: {cls}")
    if cls in _resolving_stack:
        raise RuntimeError(f"Circular dependency detected: {cls.__name__}")

    _resolving_stack.add(cls)
    try:
        sig = _sig_cache.get(cls) or signature(cls.__init__)
        _sig_cache[cls] = sig
        kwargs = {
            name: resolve(param.annotation)
            for name, param in sig.parameters.items()
            if name != "self"
        }
        return cls(**kwargs)
    finally:
        _resolving_stack.remove(cls)
