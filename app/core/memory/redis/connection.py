import asyncio
from redis.asyncio import Redis, ConnectionPool
from redis.exceptions import ConnectionError, TimeoutError
from contextlib import asynccontextmanager
import traceback
from typing import Optional
from uuid import UUID
from app.config import settings
from .logger import get_memory_logger

class RedisConnectionError(Exception):
    """Custom exception for Redis connection errors."""
    pass

class RedisConnection:
    def __init__(self, agent_id: UUID):
        self.agent_id = agent_id
        self.pool: Optional[ConnectionPool] = None
        self.max_retries = 3
        self.retry_delay = 1  # Initial delay in seconds
        self._lock = asyncio.Lock()
        self._initialized = asyncio.Event()

    async def initialize(self) -> None:
        """Initialize the Redis connection pool."""
        async with self._lock:
            if self._initialized.is_set():
                return

            last_error = None
            for attempt in range(self.max_retries):
                try:
                    get_memory_logger().debug(f"Attempting to initialize Redis connection pool for agent: {self.agent_id} (Attempt {attempt + 1})")
                    self.pool = ConnectionPool.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
                    # Test the connection
                    async with Redis(connection_pool=self.pool) as redis:
                        await redis.ping()
                        info = await redis.info()
                    get_memory_logger().info(f"Redis connection pool established for agent: {self.agent_id}")
                    get_memory_logger().debug(f"Redis version: {info['redis_version']}")
                    get_memory_logger().debug(f"Connected clients: {info['connected_clients']}")
                    get_memory_logger().debug(f"Used memory: {info['used_memory_human']}")
                    self._initialized.set()
                    return
                except (ConnectionError, TimeoutError) as e:
                    last_error = e
                    get_memory_logger().warning(f"Failed to initialize Redis connection pool (Attempt {attempt + 1}): {str(e)}")
                    if attempt == self.max_retries - 1:
                        break
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff

            get_memory_logger().error(f"Failed to initialize Redis connection pool after {self.max_retries} attempts")
            raise RedisConnectionError(f"Failed to initialize Redis connection pool: {str(last_error)}")

    async def close(self) -> None:
        """Close the Redis connection pool."""
        async with self._lock:
            if self.pool:
                try:
                    await self.pool.disconnect(inuse_connections=True)
                except Exception as e:
                    get_memory_logger().error(f"Error while closing Redis connection pool: {str(e)}")
                finally:
                    self.pool = None
                    self._initialized.clear()
                    get_memory_logger().info(f"Redis connection pool closed for agent: {self.agent_id}")

    @asynccontextmanager
    async def get_connection(self):
        if not self._initialized.is_set():
            await self.initialize()
        try:
            async with Redis(connection_pool=self.pool) as redis:
                yield redis
        except (ConnectionError, TimeoutError) as e:
            get_memory_logger().error(f"Redis connection error: {str(e)}")
            get_memory_logger().error(f"Traceback: {traceback.format_exc()}")
            raise RedisConnectionError(f"Redis connection error: {str(e)}") from e
        except Exception as e:
            get_memory_logger().error(f"Unexpected error during Redis operation: {str(e)}")
            get_memory_logger().error(f"Traceback: {traceback.format_exc()}")
            raise RedisConnectionError(f"Unexpected error during Redis operation: {str(e)}") from e

    async def ensure_connection(self) -> None:
        """
        Ensure that the Redis connection pool is initialized and working.

        Raises:
            RedisConnectionError: If the connection pool cannot be established or is not working.
        """
        if not self._initialized.is_set():
            await self.initialize()
        else:
            try:
                async with Redis(connection_pool=self.pool) as redis:
                    await redis.ping()
            except Exception as e:
                get_memory_logger().error(f"Error ensuring Redis connection: {str(e)}")
                self._initialized.clear()
                await self.initialize()

    def __del__(self):
        if self.pool:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(self.close())
            else:
                get_memory_logger().warning(f"Unable to close Redis connection pool for agent: {self.agent_id} (no running event loop)")
