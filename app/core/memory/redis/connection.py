from redis.asyncio import Redis, ConnectionPool
from contextlib import asynccontextmanager
import asyncio
import traceback
from typing import Optional
from uuid import UUID
from app.config import settings
from app.utils.logging import memory_logger


class RedisConnectionError(Exception):
    """Custom exception for Redis connection errors."""
    pass


class RedisConnection:
    def __init__(self, agent_id: UUID, max_connections: int = 10):
        self.agent_id = agent_id
        self.redis: Optional[Redis] = None
        self._connection_pool: Optional[ConnectionPool] = None
        self.max_connections = max_connections
        self._semaphore = asyncio.Semaphore(max_connections)

    async def initialize(self) -> None:
        """
        Initialize the Redis connection.

        Raises:
            RedisConnectionError: If the connection cannot be established.
        """
        if self.redis is None:
            try:
                memory_logger.debug(f"Initializing Redis connection for agent: {self.agent_id}")
                self._connection_pool = ConnectionPool.from_url(
                    settings.REDIS_URL,
                    encoding="utf-8",
                    decode_responses=True,
                    max_connections=self.max_connections
                )
                self.redis = Redis(connection_pool=self._connection_pool)
                await self.redis.ping()  # Test the connection
                info = await self.redis.info()
                memory_logger.info(f"Redis connection established for agent: {self.agent_id}")
                memory_logger.debug(f"Redis version: {info['redis_version']}")
                memory_logger.debug(f"Connected clients: {info['connected_clients']}")
                memory_logger.debug(f"Used memory: {info['used_memory_human']}")
            except Exception as e:
                memory_logger.error(f"Failed to initialize Redis connection: {str(e)}")
                raise RedisConnectionError("Failed to initialize Redis connection") from e

    @asynccontextmanager
    async def get_connection(self):
        if not self.redis:
            raise RedisConnectionError("Redis connection not initialized")

        async with self._semaphore:
            try:
                yield self.redis
            except Exception as e:
                memory_logger.error(f"Error during Redis operation: {str(e)}")
                memory_logger.error(f"Traceback: {traceback.format_exc()}")
                raise RedisConnectionError(f"Error during Redis operation: {str(e)}") from e

    async def close(self) -> None:
        """Close the Redis connection and connection pool."""
        if self.redis:
            await self.redis.close()
            self.redis = None
        if self._connection_pool:
            await self._connection_pool.disconnect()
            self._connection_pool = None
        memory_logger.info(f"Redis connection closed for agent: {self.agent_id}")

    async def ensure_connection(self) -> None:
        """
        Ensure that the Redis connection is active and working.

        Raises:
            RedisConnectionError: If the connection cannot be established or is not working.
        """
        try:
            if self.redis is None:
                await self.initialize()
            else:
                await self.redis.ping()
        except Exception as e:
            memory_logger.error(f"Error ensuring Redis connection: {str(e)}")
            raise RedisConnectionError("Failed to ensure Redis connection") from e

    def set_max_connections(self, max_connections: int):
        self.max_connections = max_connections
        if self._connection_pool:
            self._connection_pool.max_connections = max_connections
        self._semaphore = asyncio.Semaphore(max_connections)
        memory_logger.info(f"Max connections set to {max_connections} for agent: {self.agent_id}")
