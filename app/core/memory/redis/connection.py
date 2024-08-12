from redis.asyncio import Redis, ConnectionPool
from contextlib import asynccontextmanager
from typing import Optional, AsyncGenerator
from uuid import UUID
from app.config import settings
from app.utils.logging import memory_logger

class RedisConnectionError(Exception):
    """Custom exception for Redis connection errors."""
    pass

class RedisConnection:
    def __init__(self, agent_id: UUID):
        self.agent_id = agent_id
        self.redis: Optional[Redis] = None
        self._connection_pool: Optional[ConnectionPool] = None

    async def initialize(self) -> None:
        """
        Initialize the Redis connection.

        Raises:
            RedisConnectionError: If the connection cannot be established.
        """
        if self.redis is None:
            try:
                self._connection_pool = ConnectionPool.from_url(
                    settings.REDIS_URL,
                    encoding="utf-8",
                    decode_responses=True
                )
                self.redis = Redis(connection_pool=self._connection_pool)
                memory_logger.info(f"Redis connection established for agent: {self.agent_id}")
            except Exception as e:
                memory_logger.error(f"Failed to initialize Redis connection: {str(e)}")
                raise RedisConnectionError("Failed to initialize Redis connection") from e

    async def close(self) -> None:
        """Close the Redis connection and connection pool."""
        if self.redis:
            await self.redis.close()
            self.redis = None
        if self._connection_pool:
            await self._connection_pool.disconnect()
            self._connection_pool = None
        memory_logger.info(f"Redis connection closed for agent: {self.agent_id}")

    @asynccontextmanager
    async def get_connection(self) -> AsyncGenerator[Redis, None]:
        """
        Get a Redis connection.

        Yields:
            Redis: An active Redis connection.

        Raises:
            RedisConnectionError: If there's an error with the Redis connection.
        """
        if self.redis is None:
            await self.initialize()
        try:
            yield self.redis
        except Exception as e:
            memory_logger.error(f"Error in Redis connection: {str(e)}")
            raise RedisConnectionError("Error in Redis connection") from e
