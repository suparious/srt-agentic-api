import asyncio
from redis.asyncio import Redis
from redis.exceptions import ConnectionError, TimeoutError
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
        self.max_retries = 3
        self.retry_delay = 1  # Initial delay in seconds

    async def initialize(self) -> None:
        last_error = None
        for attempt in range(self.max_retries):
            try:
                memory_logger.debug(f"Attempting to initialize Redis connection for agent: {self.agent_id} (Attempt {attempt + 1})")
                self.redis = Redis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
                await self.redis.ping()  # Test the connection
                info = await self.redis.info()
                memory_logger.info(f"Redis connection established for agent: {self.agent_id}")
                memory_logger.debug(f"Redis version: {info['redis_version']}")
                memory_logger.debug(f"Connected clients: {info['connected_clients']}")
                memory_logger.debug(f"Used memory: {info['used_memory_human']}")
                return
            except (ConnectionError, TimeoutError) as e:
                last_error = e
                memory_logger.warning(f"Failed to initialize Redis connection (Attempt {attempt + 1}): {str(e)}")
                if attempt == self.max_retries - 1:
                    break
                await asyncio.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff

        memory_logger.error(f"Failed to initialize Redis connection after {self.max_retries} attempts")
        raise RedisConnectionError(f"Failed to initialize Redis connection: {str(last_error)}")

    async def close(self) -> None:
        """Close the Redis connection."""
        if self.redis:
            try:
                await self.redis.close()
                self.redis = None
                memory_logger.info(f"Redis connection closed for agent: {self.agent_id}")
            except Exception as e:
                memory_logger.error(f"Error closing Redis connection for agent {self.agent_id}: {str(e)}")
                raise RedisConnectionError(f"Failed to close Redis connection: {str(e)}")

    @asynccontextmanager
    async def get_connection(self):
        if not self.redis:
            await self.initialize()
        try:
            yield self.redis
        except (ConnectionError, TimeoutError) as e:
            memory_logger.error(f"Redis connection error: {str(e)}")
            memory_logger.error(f"Traceback: {traceback.format_exc()}")
            raise RedisConnectionError(f"Redis connection error: {str(e)}") from e
        except Exception as e:
            memory_logger.error(f"Unexpected error during Redis operation: {str(e)}")
            memory_logger.error(f"Traceback: {traceback.format_exc()}")
            raise RedisConnectionError(f"Unexpected error during Redis operation: {str(e)}") from e

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
            raise RedisConnectionError(f"Failed to ensure Redis connection: {str(e)}") from e
