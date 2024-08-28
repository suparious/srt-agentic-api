from typing import List, Dict, Any
from datetime import datetime
from app.api.models.memory import AdvancedSearchQuery
from app.core.models import MemoryEntry
from app.core.memory.redis.connection import RedisConnection, RedisConnectionError
from app.utils.logging import memory_logger

class RedisSearchError(Exception):
    """Custom exception for Redis search operations errors."""
    pass

class RedisSearch:
    def __init__(self, connection: RedisConnection):
        self.connection = connection

    async def search(self, query: AdvancedSearchQuery) -> List[Dict[str, Any]]:
        """
        Search for memories in Redis based on the given query.

        Args:
            query (AdvancedSearchQuery): The search query parameters.

        Returns:
            List[Dict[str, Any]]: A list of search results.

        Raises:
            RedisSearchError: If there's an error during the search operation.
        """
        pattern = f"agent:{self.connection.agent_id}:*"
        results = []

        try:
            async with self.connection.get_connection() as conn:
                cursor = 0
                while True:
                    cursor, keys = await conn.scan(cursor, match=pattern, count=100)
                    if not keys:
                        break
                    
                    pipeline = conn.pipeline()
                    for key in keys:
                        pipeline.get(key)
                    values = await pipeline.execute()

                    for key, value in zip(keys, values):
                        if value:
                            try:
                                memory_entry = MemoryEntry.model_validate_json(value)
                                if self._matches_query(memory_entry, query):
                                    relevance_score = self._calculate_relevance(memory_entry, query)
                                    results.append({
                                        "id": key.split(":")[-1],
                                        "memory_entry": memory_entry,
                                        "relevance_score": relevance_score,
                                    })
                            except ValueError as e:
                                memory_logger.warning(f"Failed to parse memory entry: {key}. Error: {str(e)}")

                    if cursor == 0:
                        break

            results.sort(key=lambda x: x["relevance_score"], reverse=True)
            return results[:query.max_results]
        except RedisConnectionError as e:
            memory_logger.error(f"Redis connection error during search: {str(e)}")
            raise RedisSearchError(f"Failed to perform search: {str(e)}") from e
        except Exception as e:
            memory_logger.error(f"Unexpected error during search: {str(e)}")
            raise RedisSearchError(f"Unexpected error during search: {str(e)}") from e

    async def get_memories_older_than(self, threshold: datetime) -> List[MemoryEntry]:
        """
        Retrieve memory entries older than the given threshold.

        Args:
            threshold (datetime): The threshold datetime.

        Returns:
            List[MemoryEntry]: A list of memory entries older than the threshold.

        Raises:
            RedisSearchError: If there's an error retrieving old memories.
        """
        pattern = f"agent:{self.connection.agent_id}:*"
        old_memories = []

        try:
            async with self.connection.get_connection() as conn:
                cursor = 0
                while True:
                    cursor, keys = await conn.scan(cursor, match=pattern, count=100)
                    if not keys:
                        break

                    pipeline = conn.pipeline()
                    for key in keys:
                        pipeline.get(key)
                    values = await pipeline.execute()

                    for value in values:
                        if value:
                            try:
                                memory_entry = MemoryEntry.model_validate_json(value)
                                if memory_entry.context.timestamp < threshold:
                                    old_memories.append(memory_entry)
                                    memory_logger.debug(f"Added old memory: {memory_entry.content}")
                                else:
                                    memory_logger.debug(f"Skipped memory: {memory_entry.content} (not old enough)")
                            except ValueError as e:
                                memory_logger.warning(f"Failed to parse memory entry. Error: {str(e)}")

                    if cursor == 0:
                        break

            memory_logger.info(f"Retrieved {len(old_memories)} memories older than {threshold} for agent: {self.connection.agent_id}")
            return old_memories
        except RedisConnectionError as e:
            memory_logger.error(f"Redis connection error while retrieving old memories: {str(e)}")
            raise RedisSearchError(f"Failed to retrieve old memories: {str(e)}") from e
        except Exception as e:
            memory_logger.error(f"Unexpected error while retrieving old memories: {str(e)}")
            raise RedisSearchError(f"Unexpected error while retrieving old memories: {str(e)}") from e

    async def get_recent(self, limit: int) -> List[Dict[str, Any]]:
        """
        Retrieve the most recent memory entries.

        Args:
            limit (int): The maximum number of entries to retrieve.

        Returns:
            List[Dict[str, Any]]: A list of recent memory entries.

        Raises:
            RedisSearchError: If there's an error retrieving recent memories.
        """
        pattern = f"agent:{self.connection.agent_id}:*"
        results = []

        try:
            async with self.connection.get_connection() as conn:
                cursor = 0
                while True:
                    cursor, keys = await conn.scan(cursor, match=pattern, count=100)
                    if not keys:
                        break

                    pipeline = conn.pipeline()
                    for key in keys:
                        pipeline.get(key)
                    values = await pipeline.execute()

                    for key, value in zip(keys, values):
                        if value:
                            try:
                                memory_entry = MemoryEntry.model_validate_json(value)
                                results.append({
                                    "id": key.split(":")[-1],
                                    "memory_entry": memory_entry,
                                    "timestamp": memory_entry.context.timestamp,
                                })
                            except ValueError as e:
                                memory_logger.warning(f"Failed to parse memory entry: {key}. Error: {str(e)}")

                    if cursor == 0:
                        break

            results.sort(key=lambda x: x["timestamp"], reverse=True)
            return results[:limit]
        except RedisConnectionError as e:
            memory_logger.error(f"Redis connection error while retrieving recent memories: {str(e)}")
            raise RedisSearchError(f"Failed to retrieve recent memories: {str(e)}") from e
        except Exception as e:
            memory_logger.error(f"Unexpected error while retrieving recent memories: {str(e)}")
            raise RedisSearchError(f"Unexpected error while retrieving recent memories: {str(e)}") from e


    def _matches_query(
            self, memory_entry: MemoryEntry, query: AdvancedSearchQuery
    ) -> bool:
        """
        Check if a memory entry matches the given query.

        Args:
            memory_entry (MemoryEntry): The memory entry to check.
            query (AdvancedSearchQuery): The search query parameters.

        Returns:
            bool: True if the memory entry matches the query, False otherwise.
        """
        if (
                query.context_type
                and memory_entry.context.context_type != query.context_type
        ):
            return False
        if query.time_range:
            if (
                    memory_entry.context.timestamp < query.time_range["start"]
                    or memory_entry.context.timestamp > query.time_range["end"]
            ):
                return False
        if query.metadata_filters:
            for key, value in query.metadata_filters.items():
                if (
                        key not in memory_entry.metadata
                        or memory_entry.metadata[key] != value
                ):
                    return False
        return True

    def _calculate_relevance(
            self, memory_entry: MemoryEntry, query: AdvancedSearchQuery
    ) -> float:
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
