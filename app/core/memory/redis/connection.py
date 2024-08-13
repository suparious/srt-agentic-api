from redis.asyncio import Redis
from contextlib import asynccontextmanager
import traceback
from typing import Optional
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

    async def initialize(self) -> None:
        """
        Initialize the Redis connection.

        Raises:
            RedisConnectionError: If the connection cannot be established.
        """
        if self.redis is None:
            try:
                memory_logger.debug(f"Initializing Redis connection for agent: {self.agent_id}")
                self.redis = Redis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
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
            await self.initialize()
        try:
            yield self.redis
        except Exception as e:
            memory_logger.error(f"Error during Redis operation: {str(e)}")
            memory_logger.error(f"Traceback: {traceback.format_exc()}")
            raise RedisConnectionError(f"Error during Redis operation: {str(e)}") from e

    async def close(self) -> None:
        """Close the Redis connection."""
        if self.redis:
            await self.redis.close()
            self.redis = None
        memory_logger.info(f"Redis connection closed for agent: {self.agent_id}")

    async def ensure_connection(self) -> None:
        """
        Ensure that the Redis connection is initialized and working.

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
