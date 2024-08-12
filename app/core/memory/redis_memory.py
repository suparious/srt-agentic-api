from uuid import UUID
from typing import List, Dict, Any
from app.core.memory.redis.connection import RedisConnection, RedisConnectionError
from app.core.memory.redis.memory_operations import RedisMemoryOperations
from app.core.memory.redis.search import RedisSearch
from app.core.memory.redis.cleanup import RedisCleanup
from app.api.models.memory import MemoryEntry, MemoryContext
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
        self.cleanup = RedisCleanup()

    async def initialize(self) -> None:
        try:
            await self.connection.initialize()
            memory_logger.info(f"Redis connection initialized for agent: {self.agent_id}")
        except RedisConnectionError as e:
            memory_logger.error(f"Failed to initialize Redis connection for agent {self.agent_id}: {str(e)}")
            raise

    async def close(self) -> None:
        try:
            await self.connection.close()
            memory_logger.info(f"Redis connection closed for agent: {self.agent_id}")
        except Exception as e:
            memory_logger.error(f"Error closing Redis connection for agent {self.agent_id}: {str(e)}")
            raise RedisConnectionError("Error closing Redis connection") from e

    async def get_connection(self):
        return self.connection.get_connection()

    # Delegate methods to appropriate components
    async def add(self, memory_entry, expire=None):
        return await self.operations.add(memory_entry, expire)

    async def get(self, memory_id):
        return await self.operations.get(memory_id)

    async def get_recent(self, limit: int) -> List[Dict[str, Any]]:
        """
        Retrieve the most recent memory entries.

        Args:
            limit (int): The maximum number of entries to retrieve.

        Returns:
            List[Dict[str, Any]]: A list of recent memory entries.

        Raises:
            RedisConnectionError: If there's an error retrieving recent memories.
        """
        try:
            pattern = f"agent:{self.agent_id}:*"
            results = []

            async with self.connection.get_connection() as conn:
                cursor = 0
                while True:
                    cursor, keys = await conn.scan(cursor, match=pattern, count=100)
                    pipeline = conn.pipeline()
                    for key in keys:
                        pipeline.get(key)
                    values = await pipeline.execute()

                    for key, value in zip(keys, values):
                        if value:
                            memory_entry = MemoryEntry.model_validate_json(value)
                            results.append({
                                "id": key.split(":")[-1],
                                "memory_entry": memory_entry,
                                "timestamp": memory_entry.context.timestamp,
                            })

                    if cursor == 0:
                        break

            results.sort(key=lambda x: x["timestamp"], reverse=True)
            return results[:limit]
        except Exception as e:
            memory_logger.error(f"Error retrieving recent memories for agent {self.agent_id}: {str(e)}")
            raise RedisConnectionError(f"Failed to retrieve recent memories for agent {self.agent_id}") from e

    async def delete(self, memory_id):
        await self.operations.delete(memory_id)

    async def search(self, query):
        return await self.search.search(query)

    async def get_memories_older_than(self, threshold):
        return await self.search.get_memories_older_than(threshold)

    async def cleanup(self):
        await self.cleanup.cleanup(self.connection)
