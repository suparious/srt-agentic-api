from typing import Optional
from uuid import UUID
from app.api.models.memory import MemoryEntry
from app.core.memory.redis.connection import RedisConnection
from app.utils.logging import memory_logger

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
            RedisConnectionError: If there's an error with the Redis connection.
        """
        memory_id = str(UUID(int=0))  # Generate a new UUID
        full_key = f"agent:{self.connection.agent_id}:{memory_id}"

        async with self.connection.get_connection() as conn:
            await conn.set(full_key, memory_entry.model_dump_json())
            if expire:
                await conn.expire(full_key, expire)

        memory_logger.debug(f"Added memory to Redis: {full_key}")
        return memory_id

    async def get(self, memory_id: str) -> Optional[MemoryEntry]:
        """
        Retrieve a memory entry from Redis.

        Args:
            memory_id (str): The ID of the memory entry to retrieve.

        Returns:
            Optional[MemoryEntry]: The retrieved memory entry, or None if not found.

        Raises:
            RedisConnectionError: If there's an error with the Redis connection.
        """
        full_key = f"agent:{self.connection.agent_id}:{memory_id}"

        async with self.connection.get_connection() as conn:
            value = await conn.get(full_key)

        if value:
            return MemoryEntry.model_validate_json(value)
        return None

    async def delete(self, memory_id: str) -> None:
        """
        Delete a memory entry from Redis.

        Args:
            memory_id (str): The ID of the memory entry to delete.

        Raises:
            RedisConnectionError: If there's an error with the Redis connection.
        """
        full_key = f"agent:{self.connection.agent_id}:{memory_id}"

        async with self.connection.get_connection() as conn:
            await conn.delete(full_key)

        memory_logger.debug(f"Deleted memory from Redis: {full_key}")
