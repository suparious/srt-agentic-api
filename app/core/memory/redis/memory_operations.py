from typing import Optional
from uuid import UUID
from app.api.models.memory import MemoryEntry
from app.core.memory.redis.connection import RedisConnection, RedisConnectionError
from app.utils.logging import memory_logger

class RedisMemoryOperationsError(Exception):
    """Custom exception for Redis memory operations errors."""
    pass

class RedisMemoryOperations:
    def __init__(self, connection: RedisConnection):
        self.connection = connection

    async def add(self, memory_entry: MemoryEntry, expire: Optional[int] = None) -> str:
        """
        Add a memory entry to Redis.

        Args:
            memory_entry (MemoryEntry): The memory entry to add.
            expire (Optional[int]): The expiration time in seconds.

        Returns:
            str: The key of the added memory entry.

        Raises:
            RedisMemoryOperationsError: If there's an error adding the memory entry.
        """
        memory_id = str(UUID(int=0))  # Generate a new UUID
        full_key = f"agent:{self.connection.agent_id}:{memory_id}"

        try:
            async with self.connection.get_connection() as conn:
                await conn.set(full_key, memory_entry.model_dump_json())
                if expire:
                    await conn.expire(full_key, expire)

            memory_logger.debug(f"Added memory to Redis: {full_key}")
            return memory_id
        except RedisConnectionError as e:
            memory_logger.error(f"Failed to add memory to Redis: {full_key}. Error: {str(e)}")
            raise RedisMemoryOperationsError(f"Failed to add memory: {str(e)}") from e

    async def get(self, memory_id: str) -> Optional[MemoryEntry]:
        """
        Retrieve a memory entry from Redis.

        Args:
            memory_id (str): The ID of the memory entry to retrieve.

        Returns:
            Optional[MemoryEntry]: The retrieved memory entry, or None if not found.

        Raises:
            RedisMemoryOperationsError: If there's an error retrieving the memory entry.
        """
        full_key = f"agent:{self.connection.agent_id}:{memory_id}"

        try:
            async with self.connection.get_connection() as conn:
                value = await conn.get(full_key)

            if value:
                return MemoryEntry.model_validate_json(value)
            return None
        except RedisConnectionError as e:
            memory_logger.error(f"Failed to retrieve memory from Redis: {full_key}. Error: {str(e)}")
            raise RedisMemoryOperationsError(f"Failed to retrieve memory: {str(e)}") from e
        except ValueError as e:
            memory_logger.error(f"Failed to parse memory data from Redis: {full_key}. Error: {str(e)}")
            raise RedisMemoryOperationsError(f"Failed to parse memory data: {str(e)}") from e

    async def delete(self, memory_id: str) -> None:
        """
        Delete a memory entry from Redis.

        Args:
            memory_id (str): The ID of the memory entry to delete.

        Raises:
            RedisMemoryOperationsError: If there's an error deleting the memory entry.
        """
        full_key = f"agent:{self.connection.agent_id}:{memory_id}"

        try:
            async with self.connection.get_connection() as conn:
                await conn.delete(full_key)

            memory_logger.debug(f"Deleted memory from Redis: {full_key}")
        except RedisConnectionError as e:
            memory_logger.error(f"Failed to delete memory from Redis: {full_key}. Error: {str(e)}")
            raise RedisMemoryOperationsError(f"Failed to delete memory: {str(e)}") from e
