from collections.abc import Awaitable, Callable
from typing import Any, cast
from unittest.mock import AsyncMock

import fakeredis
from redis.asyncio.client import Redis as AsyncRedis
from redis.client import Redis

from archipy.adapters.redis.adapters import AsyncRedisAdapter, RedisAdapter
from archipy.adapters.redis.ports import (
    AsyncRedisPort,
    RedisResponseType,
)
from archipy.configs.config_template import RedisConfig


class RedisMock(RedisAdapter):
    """A Redis adapter implementation using fakeredis for testing."""

    def __init__(self, redis_config: RedisConfig | None = None) -> None:
        # Skip the parent's __init__ which would create real Redis connections
        self.client = fakeredis.FakeRedis(decode_responses=True)
        self.read_only_client = self.client

    def _set_clients(self, configs: RedisConfig) -> None:
        # Override to prevent actual connection setup
        pass

    @staticmethod
    def _get_client(host: str, configs: RedisConfig) -> Redis:
        # Override to return fakeredis instead
        return fakeredis.FakeRedis(decode_responses=configs.DECODE_RESPONSES)


class AsyncRedisMock(AsyncRedisAdapter):
    """An async Redis adapter implementation using fakeredis for testing."""

    def __init__(self, redis_config: RedisConfig | None = None) -> None:
        # Skip the parent's __init__ which would create real Redis connections
        self.client = AsyncMock()
        self.read_only_client = self.client
        self._setup_async_methods()

    def _set_clients(self, configs: RedisConfig) -> None:
        # Override to prevent actual connection setup
        pass

    @staticmethod
    def _get_client(host: str, configs: RedisConfig) -> AsyncRedis:
        # Override to return a mocked async client
        return AsyncMock()

    def _setup_async_methods(self) -> None:
        """Set up all async methods to use a synchronous fakeredis under the hood."""
        # Create a synchronous fakeredis instance to handle the actual operations
        self._fake_redis = fakeredis.FakeRedis(decode_responses=True)

        # For each async method, implement it to use the synchronous fakeredis
        for method_name in dir(AsyncRedisPort):
            if not method_name.startswith("_") and method_name not in ("pubsub", "get_pipeline"):
                sync_method = getattr(self._fake_redis, method_name, None)
                if sync_method and callable(sync_method):
                    async_method = self._create_async_wrapper(method_name, sync_method)
                    setattr(self.client, method_name, async_method)
                    setattr(self.read_only_client, method_name, async_method)

    def _create_async_wrapper(
        self,
        method_name: str,
        sync_method: Callable[..., Any],
    ) -> Callable[..., Awaitable[RedisResponseType]]:
        """Create an async wrapper around a synchronous method."""

        async def wrapper(*args: Any, **kwargs: Any) -> RedisResponseType:
            # Remove 'self' from args when calling the sync method
            if args and args[0] is self:
                args = args[1:]
            return cast(RedisResponseType, sync_method(*args, **kwargs))

        return wrapper
