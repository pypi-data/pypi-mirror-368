import warnings
from abc import ABC, abstractmethod
from typing import Optional, Union, cast

try:
    from redis import Redis
except ModuleNotFoundError:
    warnings.warn("Failed to import Redis. RedisCache class not available to use")


class Cache(ABC):
    @abstractmethod
    def get(self, key: str) -> Optional[Union[str, bytes]]:
        raise NotImplementedError()  # pragma: no cover

    @abstractmethod
    def set(self, key: str, value: str, **kwargs: dict) -> Optional[bool]:
        raise NotImplementedError()  # pragma: no cover


class DictCache(Cache):
    store: dict = {}

    def get(self, key: str) -> Optional[str]:
        return self.store.get(key, None)

    def set(self, key: str, value: str, **kwargs: dict) -> Optional[bool]:
        self.store[key] = value
        return True


class RedisCache(Cache):
    def __init__(self, connection_url: str) -> None:
        self.connection = Redis.from_url(connection_url)

    def get(self, key: str) -> Optional[bytes]:
        return self.connection.get(key)

    def set(self, key: str, value: str, **kwargs: dict) -> Optional[bool]:
        ex = kwargs.pop("ex", None)
        if ex is not None and not isinstance(ex, int):
            raise ValueError(
                "Expire flag `ex` is in seconds, and must be an integer or None"
            )
        return self.connection.set(key, value, ex=cast(Optional[int], ex))
