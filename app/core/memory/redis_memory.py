import uuid
from typing import List, Dict, Any, Optional
import json
from datetime import datetime
from redis.asyncio import Redis, ConnectionPool
from contextlib import asynccontextmanager

from app.utils.logging import memory_logger
from app.config import settings
from app.api.models.memory import AdvancedSearchQuery, MemoryEntry, MemoryContext

class RedisMemory:
    """
    Handles short-term memory operations using Redis.
    """

    _connection_pool = None

    @classmethod
    async def get_connection_pool(cls):
        """
        Get or create a Redis connection pool.

        Returns:
            ConnectionPool: A Redis connection pool.
        """
        if cls._connection_pool is None:
            cls._connection_pool = ConnectionPool.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
        return cls._connection_pool

    def __init__(self, agent_id: uuid.UUID):
        """
        Initialize RedisMemory for an agent.

        Args:
            agent_id (uuid.UUID): The unique identifier for the agent.
        """
        self.agent_id = agent_id
        self.redis: Optional[Redis] = None
        memory_logger.info(f"Redis connection initialized for agent: {agent_id}")

    async def initialize(self):
        """
        Initialize the Redis connection if not already established.
        """
        if self.redis is None:
            pool = await self.get_connection_pool()
            self.redis = Redis(connection_pool=pool)
            memory_logger.info(f"Redis connection established for agent: {self.agent_id}")

    @asynccontextmanager
    async def get_connection(self):
        """
        Context manager for getting a Redis connection.

        Yields:
            Redis: A Redis connection.
        """
        await self.initialize()
        try:
            yield self.redis
        except Exception as e:
            memory_logger.error(f"Error in Redis connection: {str(e)}")
            raise

    async def add(self, memory_entry: MemoryEntry, expire: int = settings.SHORT_TERM_MEMORY_TTL) -> str:
        """
        Add a memory entry to Redis.

        Args:
            memory_entry (MemoryEntry): The memory entry to add.
            expire (int): The expiration time in seconds.

        Returns:
            str: The key of the added memory entry.

        Raises:
            Exception: If there's an error adding the memory entry.
        """
        try:
            memory_id = str(uuid.uuid4())
            full_key = f"agent:{self.agent_id}:{memory_id}"

            serialized_entry = json.dumps({
                "content": memory_entry.content,
                "metadata": memory_entry.metadata,
                "context": {
                    "context_type": memory_entry.context.context_type,
                    "timestamp": memory_entry.context.timestamp.isoformat(),
                    "metadata": memory_entry.context.metadata
                }
            })

            async with self.get_connection() as conn:
                await conn.set(full_key, serialized_entry, ex=expire)
            memory_logger.debug(f"Added key to Redis: {full_key}")
            return memory_id
        except Exception as e:
            memory_logger.error(f"Error adding memory for agent {self.agent_id}: {str(e)}")
            raise

    async def get(self, memory_id: str) -> Optional[MemoryEntry]:
        """
        Retrieve a memory entry from Redis.

        Args:
            memory_id (str): The ID of the memory entry to retrieve.

        Returns:
            Optional[MemoryEntry]: The retrieved memory entry, or None if not found.

        Raises:
            Exception: If there's an error retrieving the memory entry.
        """
        try:
            full_key = f"agent:{self.agent_id}:{memory_id}"
            async with self.get_connection() as conn:
                value = await conn.get(full_key)
            if value:
                deserialized_entry = json.loads(value)
                context = MemoryContext(
                    context_type=deserialized_entry["context"]["context_type"],
                    timestamp=datetime.fromisoformat(deserialized_entry["context"]["timestamp"]),
                    metadata=deserialized_entry["context"]["metadata"]
                )
                return MemoryEntry(
                    content=deserialized_entry["content"],
                    metadata=deserialized_entry["metadata"],
                    context=context
                )
            return None
        except Exception as e:
            memory_logger.error(f"Error retrieving memory for agent {self.agent_id}: {str(e)}")
            raise

    async def delete(self, memory_id: str):
        """
        Delete a memory entry from Redis.

        Args:
            memory_id (str): The ID of the memory entry to delete.

        Raises:
            Exception: If there's an error deleting the memory entry.
        """
        try:
            full_key = f"agent:{self.agent_id}:{memory_id}"
            async with self.get_connection() as conn:
                await conn.delete(full_key)
            memory_logger.debug(f"Deleted key from Redis: {full_key}")
        except Exception as e:
            memory_logger.error(f"Error deleting memory for agent {self.agent_id}: {str(e)}")
            raise

    async def search(self, query: AdvancedSearchQuery) -> List[Dict[str, Any]]:
        """
        Search for memories in Redis based on the given query.

        Args:
            query (AdvancedSearchQuery): The search query parameters.

        Returns:
            List[Dict[str, Any]]: A list of search results.

        Raises:
            Exception: If there's an error searching for memories.
        """
        try:
            pattern = f"agent:{self.agent_id}:*"
            cursor = 0
            results = []

            async with self.get_connection() as conn:
                while True:
                    cursor, keys = await conn.scan(cursor, match=pattern, count=100)
                    for key in keys:
                        value = await conn.get(key)
                        if value:
                            memory_entry = MemoryEntry.model_validate_json(value)
                            if self._matches_query(memory_entry, query):
                                relevance_score = self._calculate_relevance(memory_entry, query)
                                results.append({
                                    "id": key.split(":")[-1],
                                    "memory_entry": memory_entry,
                                    "relevance_score": relevance_score
                                })

                    if cursor == 0:
                        break

            results.sort(key=lambda x: x["relevance_score"], reverse=True)

            if query.relevance_threshold is not None:
                results = [r for r in results if r["relevance_score"] >= query.relevance_threshold]
            results = results[:query.max_results]

            return results
        except Exception as e:
            memory_logger.error(f"Error searching memories for agent {self.agent_id}: {str(e)}")
            raise

    def _matches_query(self, memory_entry: MemoryEntry, query: AdvancedSearchQuery) -> bool:
        """
        Check if a memory entry matches the given query.

        Args:
            memory_entry (MemoryEntry): The memory entry to check.
            query (AdvancedSearchQuery): The search query parameters.

        Returns:
            bool: True if the memory entry matches the query, False otherwise.
        """
        if query.context_type and memory_entry.context.context_type != query.context_type:
            return False
        if query.time_range:
            if (memory_entry.context.timestamp < query.time_range["start"] or
                    memory_entry.context.timestamp > query.time_range["end"]):
                return False
        if query.metadata_filters:
            for key, value in query.metadata_filters.items():
                if key not in memory_entry.metadata or memory_entry.metadata[key] != value:
                    return False
        return True

    def _calculate_relevance(self, memory_entry: MemoryEntry, query: AdvancedSearchQuery) -> float:
        """
        Calculate the relevance score of a memory entry for the given query.

        Args:
            memory_entry (MemoryEntry): The memory entry to calculate relevance for.
            query (AdvancedSearchQuery): The search query parameters.

        Returns:
            float: The relevance score (0 to 1).
        """
        relevance = 0
        keywords = query.query.lower().split()
        content_words = memory_entry.content.lower().split()
        for keyword in keywords:
            if keyword in content_words:
                relevance += 1
        return relevance / len(keywords) if keywords else 0

    async def get_recent(self, limit: int) -> List[Dict[str, Any]]:
        """
        Retrieve the most recent memory entries.

        Args:
            limit (int): The maximum number of entries to retrieve.

        Returns:
            List[Dict[str, Any]]: A list of recent memory entries.

        Raises:
            Exception: If there's an error retrieving recent memories.
        """
        try:
            pattern = f"agent:{self.agent_id}:*"
            cursor = 0
            results = []

            async with self.get_connection() as conn:
                while True:
                    cursor, keys = await conn.scan(cursor, match=pattern, count=100)
                    for key in keys:
                        value = await conn.get(key)
                        if value:
                            memory_entry = MemoryEntry.model_validate_json(value)
                            results.append({
                                "id": key.split(":")[-1],
                                "memory_entry": memory_entry,
                                "timestamp": memory_entry.context.timestamp
                            })

                    if cursor == 0:
                        break

            results.sort(key=lambda x: x["timestamp"], reverse=True)
            return results[:limit]
        except Exception as e:
            memory_logger.error(f"Error retrieving recent memories for agent {self.agent_id}: {str(e)}")
            raise

    async def get_memories_older_than(self, threshold: datetime) -> List[MemoryEntry]:
        """
        Retrieve memory entries older than the given threshold.

        Args:
            threshold (datetime): The threshold datetime.

        Returns:
            List[MemoryEntry]: A list of memory entries older than the threshold.

        Raises:
            Exception: If there's an error retrieving old memories.
        """
        try:
            pattern = f"agent:{self.agent_id}:*"
            cursor = 0
            old_memories = []

            async with self.get_connection() as conn:
                while True:
                    cursor, keys = await conn.scan(cursor, match=pattern, count=100)
                    for key in keys:
                        value = await conn.get(key)
                        if value:
                            memory_entry = MemoryEntry.model_validate_json(value)
                            if memory_entry.context.timestamp < threshold:
                                old_memories.append(memory_entry)

                    if cursor == 0:
                        break

            memory_logger.info(f"Retrieved {len(old_memories)} memories older than {threshold} for agent: {self.agent_id}")
            return old_memories
        except Exception as e:
            memory_logger.error(f"Error getting old memories for agent {self.agent_id}: {str(e)}")
            raise

    async def close(self):
        """
        Close the Redis connection.

        Raises:
            Exception: If there's an error closing the connection.
        """
        try:
            if self.redis:
                await self.redis.close()
                self.redis = None
                memory_logger.info(f"Redis connection closed for agent: {self.agent_id}")
        except Exception as e:
            memory_logger.error(f"Error closing Redis connection for agent {self.agent_id}: {str(e)}")
            raise

    @classmethod
    async def close_pool(cls):
        """
        Close the Redis connection pool.

        Raises:
            Exception: If there's an error closing the connection pool.
        """
        try:
            if cls._connection_pool:
                await cls._connection_pool.disconnect()
                cls._connection_pool = None
                memory_logger.info("Redis connection pool closed")
        except Exception as e:
            memory_logger.error(f"Error closing Redis connection pool: {str(e)}")
            raise
