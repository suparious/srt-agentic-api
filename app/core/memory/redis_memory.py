from uuid import UUID
from typing import List, Dict, Any, Optional
from datetime import datetime
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

    async def initialize(self) -> None:
        try:
            await self.connection.initialize()
            memory_logger.info(f"Redis memory initialized for agent: {self.agent_id}")
        except RedisConnectionError as e:
            memory_logger.error(f"Failed to initialize Redis memory for agent {self.agent_id}: {str(e)}")
            raise RedisMemoryError("Failed to initialize Redis memory") from e

    async def add(self, memory_entry: MemoryEntry) -> str:
        try:
            async with self.connection.get_connection() as conn:
                memory_id = str(UUID(int=0))  # Generate a new UUID
                await conn.set(f"agent:{self.agent_id}:{memory_id}", memory_entry.model_dump_json())
                memory_logger.debug(f"Added memory {memory_id} for agent {self.agent_id}")
                return memory_id
        except Exception as e:
            memory_logger.error(f"Error adding memory for agent {self.agent_id}: {str(e)}")
            raise RedisMemoryError("Failed to add memory") from e

    async def get(self, memory_id: str) -> Optional[MemoryEntry]:
        try:
            async with self.connection.get_connection() as conn:
                value = await conn.get(f"agent:{self.agent_id}:{memory_id}")
                if value:
                    memory_logger.debug(f"Retrieved memory {memory_id} for agent {self.agent_id}")
                    return MemoryEntry.model_validate_json(value)
                memory_logger.debug(f"Memory {memory_id} not found for agent {self.agent_id}")
                return None
        except Exception as e:
            memory_logger.error(f"Error retrieving memory for agent {self.agent_id}: {str(e)}")
            raise RedisMemoryError("Failed to retrieve memory") from e

    async def delete(self, memory_id: str) -> None:
        try:
            async with self.connection.get_connection() as conn:
                await conn.delete(f"agent:{self.agent_id}:{memory_id}")
                memory_logger.debug(f"Deleted memory {memory_id} for agent {self.agent_id}")
        except Exception as e:
            memory_logger.error(f"Error deleting memory for agent {self.agent_id}: {str(e)}")
            raise RedisMemoryError("Failed to delete memory") from e

    async def close(self) -> None:
        await self.connection.close()
        memory_logger.info(f"Redis memory closed for agent: {self.agent_id}")

    async def search(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        try:
            await self.connection.ensure_connection()
            return await self.search.search(query)
        except Exception as e:
            memory_logger.error(f"Error searching memories for agent {self.agent_id}: {str(e)}")
            raise RedisMemoryError("Failed to search memories") from e

    async def get_recent(self, limit: int) -> List[Dict[str, Any]]:
        try:
            await self.connection.ensure_connection()
            return await self.search.get_recent(limit)
        except Exception as e:
            memory_logger.error(f"Error retrieving recent memories for agent {self.agent_id}: {str(e)}")
            raise RedisMemoryError("Failed to retrieve recent memories") from e

    async def get_memories_older_than(self, threshold: datetime) -> List[MemoryEntry]:
        try:
            await self.connection.ensure_connection()
            return await self.search.get_memories_older_than(threshold)
        except Exception as e:
            memory_logger.error(f"Error retrieving old memories for agent {self.agent_id}: {str(e)}")
            raise RedisMemoryError("Failed to retrieve old memories") from e

    @classmethod
    async def cleanup(cls) -> None:
        try:
            await cls.cleanup.cleanup()
        except Exception as e:
            memory_logger.error(f"Error during Redis cleanup: {str(e)}")
            raise RedisMemoryError("Failed to perform Redis cleanup") from e
