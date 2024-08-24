from uuid import UUID
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.api.models.memory import MemoryEntry, AdvancedSearchQuery
from app.core.memory.redis.connection import RedisConnection, RedisConnectionError
from app.core.memory.redis.memory_operations import RedisMemoryOperations
from app.core.memory.redis.search import RedisSearch
from app.core.memory.redis.cleanup import RedisCleanup
from app.utils.logging import memory_logger

class RedisMemoryError(Exception):
    """Custom exception for Redis memory operations."""
    pass

class RedisMemory:
    def __init__(self, agent_id: UUID):
        self.agent_id = agent_id
        self.connection = RedisConnection(agent_id)
        self.operations = RedisMemoryOperations(self.connection)
        self.search = RedisSearch(self.connection)

    async def initialize(self) -> None:
        try:
            await self.connection.initialize()
            memory_logger.info(f"Redis memory initialized for agent: {self.agent_id}")
        except RedisConnectionError as e:
            memory_logger.error(f"Failed to initialize Redis memory for agent {self.agent_id}: {str(e)}")
            raise RedisMemoryError("Failed to initialize Redis memory") from e

    async def close(self) -> None:
        try:
            await self.connection.close()
            memory_logger.info(f"Redis memory closed for agent: {self.agent_id}")
        except Exception as e:
            memory_logger.error(f"Error closing Redis memory for agent {self.agent_id}: {str(e)}")
            raise RedisMemoryError("Failed to close Redis memory") from e

    async def cleanup(self) -> None:
        try:
            await RedisCleanup.cleanup(self.connection)
            memory_logger.info(f"Redis memory cleanup completed for agent: {self.agent_id}")
        except Exception as e:
            memory_logger.error(f"Error during Redis memory cleanup for agent {self.agent_id}: {str(e)}")
            raise RedisMemoryError("Failed to cleanup Redis memory") from e

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

    async def search(self, query: AdvancedSearchQuery) -> List[Dict[str, Any]]:
        try:
            async with self.connection.get_connection() as conn:
                results = await self.search.search(conn, query)
                return results
        except Exception as e:
            memory_logger.error(f"Error searching memories for agent {self.agent_id}: {str(e)}")
            raise RedisMemoryError("Failed to search memories") from e

    async def delete(self, memory_id: str) -> None:
        try:
            async with self.connection.get_connection() as conn:
                await self.operations.delete(conn, memory_id)
                memory_logger.debug(f"Deleted memory {memory_id} for agent {self.agent_id}")
        except Exception as e:
            memory_logger.error(f"Error deleting memory for agent {self.agent_id}: {str(e)}")
            raise RedisMemoryError("Failed to delete memory") from e

    async def get_recent(self, limit: int) -> List[Dict[str, Any]]:
        try:
            async with self.connection.get_connection() as conn:
                results = await self.search.get_recent(conn, limit)
                return results
        except Exception as e:
            memory_logger.error(f"Error retrieving recent memories for agent {self.agent_id}: {str(e)}")
            raise RedisMemoryError("Failed to retrieve recent memories") from e

    async def get_memories_older_than(self, threshold: datetime) -> List[MemoryEntry]:
        try:
            async with self.connection.get_connection() as conn:
                results = await self.search.get_memories_older_than(conn, threshold)
                return results
        except Exception as e:
            memory_logger.error(f"Error retrieving old memories for agent {self.agent_id}: {str(e)}")
            raise RedisMemoryError("Failed to retrieve old memories") from e
