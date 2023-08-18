import abc
from typing import Generic, TypeVar

import redis
from django.conf import settings

from odevlib.models.errors import Error

K = TypeVar("K")
V = TypeVar("V")


class RedisCache(abc.ABC, Generic[K, V]):
    redis_instance: redis.Redis
    timeout: int

    def __init__(
        self,
        timeout: int = 120,
        redis_instance: redis.Redis | None = None,
    ) -> None:
        if redis_instance is not None:
            self.redis_instance = redis_instance
        else:
            url = getattr(settings, "REDIS_CACHE_URL", None)
            if url is None:
                msg = "REDIS_CACHE_URL is not set"
                raise ValueError(msg)

            self.redis_instance = redis.Redis.from_url(url)

        self.timeout = timeout

    @abc.abstractmethod
    def get_original_value(self, key: K) -> V | Error:
        """
        Override this function in your subclass.

        This function should obtain the value that is to be cached in Redis.
        """

    @abc.abstractmethod
    def serialize_key(self, key: K) -> str:
        """
        Override this function in your subclass.

        This function should serialize key into string, that will be used
        internally as a Redis key.
        """

    @abc.abstractmethod
    def serialize_value(self, value: V) -> str:
        """
        Override this function in your subclass.

        This function should serialize value into string, that will be used
        internally as a Redis value.
        """

    @abc.abstractmethod
    def deserialize_key(self, key: str) -> K:
        """
        Override this function in your subclass.

        This function should deserialize key from string, that is used
        internally as a Redis key.
        """

    @abc.abstractmethod
    def deserialize_value(self, value: str) -> V:
        """
        Override this function in your subclass.

        This function should deserialize value from string, that is used
        internally as a Redis value.
        """

    def get(self, key: K) -> V | Error:
        """
        Return the value stored in Redis, or, if cache is empty,
        obtain the original value, store it, and return it.
        """

        converted_key = self.serialize_key(key)

        redis_value = self.redis_instance.get(converted_key)
        if redis_value is not None:
            return self.deserialize_value(redis_value.decode("utf-8"))

        value: V | Error = self.get_original_value(key)
        if isinstance(value, Error):
            return value
        converted_value = self.serialize_value(value)

        self.redis_instance.set(
            converted_key,
            converted_value,
            ex=self.timeout,
        )
        return value

    def force_recache(self, key: K) -> V | Error:
        """
        Force get the original value, store it in Redis, and return it.

        May be helpful when you want to invalidate cache from side job.
        """

        value: V | Error = self.get_original_value(key)
        if isinstance(value, Error):
            return value
        converted_value = self.serialize_value(value)

        self.redis_instance.set(
            self.serialize_key(key),
            converted_value,
            ex=self.timeout,
        )
        return value
