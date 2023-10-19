import abc
import logging
from collections.abc import AsyncIterator
from typing import Iterator

from redis.asyncio.client import Redis as AIORedis
from redis import Redis as SyncRedis


class MessageBroker(abc.ABC):
    """
    Abstract class for implementing message brokers.
    """

    @abc.abstractmethod
    async def publish(self, channel: str, message: str) -> None:
        """
        Publish the message to the specified channel.
        Operates on strings, so you need to serialize
        your data before publishing.

        JSON is a preferred format for serialization,
        since it is supported by all languages.
        """

    @abc.abstractmethod
    async def asubscribe(self, channel: str) -> AsyncIterator[str]:
        """
        Asynchronously subscribes to the specified channel and
        returns async generator which yields messages.
        """


class RedisMessageBroker(MessageBroker):
    """
    Implementation of MessageBroker using Redis.

    Uses xadd/xread commands to publish/subscribe,
    plus allows to specify last_id to get new messages
    even after worker downtime.
    """

    redis_client: AIORedis

    def __init__(self, redis_pool: AIORedis) -> None:
        self.redis_client = redis_pool

    async def publish(self, channel: str, message: str) -> None:
        await self.redis_client.xadd(channel, {"message": message})

    async def asubscribe(
        self,
        channel: str,
        last_id: str,
    ) -> AsyncIterator[tuple[str, str]]:
        stream_id = last_id if last_id else "0"

        while True:
            # Continuosly poll for new messages,
            # sleeping for 1s if no messages are present.
            events = await self.redis_client.xread({channel: stream_id}, block=1000, count=10)
            for _, es in events:
                for e in es:
                    stream_id = e[0].decode()

                    if b"message" not in e[1]:
                        logging.warning("Malformed message, skipping")
                        continue

                    message = e[1][b"message"].decode()
                    yield (stream_id, message)



class RedisSyncMessageBroker(MessageBroker):
    """
    Implementation of MessageBroker using Redis.

    Uses xadd/xread commands to publish/subscribe,
    plus allows to specify last_id to get new messages
    even after worker downtime.
    """

    redis_client: SyncRedis

    def __init__(self, redis_pool: SyncRedis) -> None:
        self.redis_client = redis_pool

    def publish(self, channel: str, message: str) -> None:
        self.redis_client.xadd(channel, {"message": message})

    def asubscribe(
        self,
        channel: str,
        last_id: str,
    ) -> Iterator[tuple[str, str]]:
        stream_id = last_id if last_id else "0"

        while True:
            # Continuosly poll for new messages,
            # sleeping for 1s if no messages are present.
            events = self.redis_client.xread({channel: stream_id}, block=1000, count=10)
            for _, es in events:
                for e in es:
                    stream_id = e[0].decode()

                    if b"message" not in e[1]:
                        logging.warning("Malformed message, skipping")
                        continue

                    message = e[1][b"message"].decode()
                    yield (stream_id, message)
