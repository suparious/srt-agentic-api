from uuid import UUID
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.core.memory.memory_interface import MemorySystemInterface
from app.core.memory.redis.connection import RedisConnection, RedisConnectionError
from app.api.models.memory import MemoryEntry, AdvancedSearchQuery
from app.utils.logging import memory_logger

class RedisMemoryError(Exception):
    """Custom exception for Redis memory operations."""
    pass

class RedisMemory(MemorySystemInterface):
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

    async def close(self) -> None:
        try:
            await self.connection.close()
            memory_logger.info(f"Redis memory closed for agent: {self.agent_id}")
        except Exception as e:
            memory_logger.error(f"Error closing Redis memory for agent {self.agent_id}: {str(e)}")
            raise RedisMemoryError("Failed to close Redis memory") from e

    async def cleanup(self) -> None:
        try:
            async with self.connection.get_connection() as conn:
                keys = await conn.keys(f"agent:{self.agent_id}:*")
                if keys:
                    await conn.delete(*keys)
            memory_logger.info(f"Redis memory cleanup completed for agent: {self.agent_id}")
        except Exception as e:
            memory_logger.error(f"Error during Redis memory cleanup for agent {self.agent_id}: {str(e)}")
            raise RedisMemoryError("Failed to cleanup Redis memory") from e

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
                    return MemoryEntry.model_validate_json(value)
                return None
        except Exception as e:
            memory_logger.error(f"Error retrieving memory for agent {self.agent_id}: {str(e)}")
            raise RedisMemoryError("Failed to retrieve memory") from e

    async def search(self, query: AdvancedSearchQuery) -> List[Dict[str, Any]]:
        try:
            results = []
            async with self.connection.get_connection() as conn:
                cursor = 0
                while True:
                    cursor, keys = await conn.scan(cursor, match=f"agent:{self.agent_id}:*", count=100)
                    pipeline = conn.pipeline()
                    for key in keys:
                        pipeline.get(key)
                    values = await pipeline.execute()

                    for key, value in zip(keys, values):
                        if value:
                            memory_entry = MemoryEntry.model_validate_json(value)
                            if self._matches_query(memory_entry, query):
                                relevance_score = self._calculate_relevance(memory_entry, query)
                                results.append({
                                    "id": key.split(":")[-1],
                                    "memory_entry": memory_entry,
                                    "relevance_score": relevance_score,
                                })

                    if cursor == 0:
                        break

            results.sort(key=lambda x: x["relevance_score"], reverse=True)
            return results[:query.max_results]
        except Exception as e:
            memory_logger.error(f"Error searching memories for agent {self.agent_id}: {str(e)}")
            raise RedisMemoryError("Failed to search memories") from e

    def _matches_query(self, memory_entry: MemoryEntry, query: AdvancedSearchQuery) -> bool:
        if query.query.lower() not in memory_entry.content.lower():
            return False
        if query.context_type and memory_entry.context.context_type != query.context_type:
            return False
        if query.time_range:
            if memory_entry.context.timestamp < query.time_range["start"] or memory_entry.context.timestamp > \
                    query.time_range["end"]:
                return False
        if query.metadata_filters:
            for key, value in query.metadata_filters.items():
                if key not in memory_entry.metadata or memory_entry.metadata[key] != value:
                    return False
        return True

    def _calculate_relevance(self, memory_entry: MemoryEntry, query: AdvancedSearchQuery) -> float:
        relevance = 0.0
        query_words = set(query.query.lower().split())
        content_words = set(memory_entry.content.lower().split())
        common_words = query_words.intersection(content_words)
        relevance = len(common_words) / len(query_words) if query_words else 0.0
        return relevance

    async def delete(self, memory_id: str) -> None:
        try:
            async with self.connection.get_connection() as conn:
                await conn.delete(f"agent:{self.agent_id}:{memory_id}")
                memory_logger.debug(f"Deleted memory {memory_id} for agent {self.agent_id}")
        except Exception as e:
            memory_logger.error(f"Error deleting memory for agent {self.agent_id}: {str(e)}")
            raise RedisMemoryError("Failed to delete memory") from e

    async def get_recent(self, limit: int) -> List[Dict[str, Any]]:
        try:
            results = []
            async with self.connection.get_connection() as conn:
                keys = await conn.keys(f"agent:{self.agent_id}:*")
                for key in sorted(keys, reverse=True)[:limit]:
                    value = await conn.get(key)
                    if value:
                        memory_entry = MemoryEntry.model_validate_json(value)
                        results.append({
                            "id": key.split(":")[-1],
                            "memory_entry": memory_entry
                        })
            return results
        except Exception as e:
            memory_logger.error(f"Error retrieving recent memories for agent {self.agent_id}: {str(e)}")
            raise RedisMemoryError("Failed to retrieve recent memories") from e

    async def get_memories_older_than(self, threshold: datetime) -> List[MemoryEntry]:
        try:
            results = []
            async with self.connection.get_connection() as conn:
                keys = await conn.keys(f"agent:{self.agent_id}:*")
                for key in keys:
                    value = await conn.get(key)
                    if value:
                        memory_entry = MemoryEntry.model_validate_json(value)
                        if memory_entry.context.timestamp < threshold:
                            results.append(memory_entry)
            return results
        except Exception as e:
            memory_logger.error(f"Error retrieving old memories for agent {self.agent_id}: {str(e)}")
            raise RedisMemoryError("Failed to retrieve old memories") from e