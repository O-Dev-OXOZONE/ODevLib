import abc
from typing import AsyncIterator
from redis.asyncio.client import Redis


class MessageBroker(abc.ABC):
    """
    Abstract class for implementing message brokers.
    """

    @abc.abstractmethod
    async def publish(self, channel: str, message: str):
        """
        Published the message to the specified channel.
        Operates on strings, so you need to serialize
        your data before publishing.

        JSON is a preferred format for serialization,
        since it is supported by all languages.
        """
        pass

    @abc.abstractmethod
    async def asubscribe(self, channel: str) -> AsyncIterator[str]:
        """
        Asynchronously subscribes to the specified channel and
        returns async generator which yields messages.
        """
        pass


class RedisMessageBroker(MessageBroker):
    """
    Implementation of MessageBroker using Redis.

    Uses xadd/xread commands to publish/subscribe,
    plus allows to specify last_id to get new messages
    even after worker downtime.
    """

    redis_client: Redis

    def __init__(self, redis_pool: Redis) -> None:
        self.redis_client = redis_pool

    async def publish(self, channel: str, message: str) -> None:
        await self.redis_client.xadd(channel, {"message": message})

    async def asubscribe(
        self,
        channel: str,
        last_id: str,
    ) -> AsyncIterator[tuple[str, str]]:
        if last_id:
            stream_id = last_id
        else:
            stream_id = "0"

        while True:
            # Continuosly poll for new messages,
            # sleeping for 1s if no messages are present.
            events = await self.redis_client.xread(
                {channel: stream_id}, block=1000, count=10
            )
            for _, es in events:
                for e in es:
                    stream_id = e[0].decode()

                    if not b"message" in e[1].keys():
                        print("WARNING: Malfored message, skipping")
                        continue

                    message = e[1][b"message"].decode()
                    yield (stream_id, message)
