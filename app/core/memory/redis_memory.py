from uuid import UUID
from typing import List, Dict, Any, Optional
from redis import asyncio as aioredis
from app.utils.logging import memory_logger
from app.config import settings as app_settings
from app.api.models.memory import AdvancedSearchQuery, MemoryEntry, MemoryContext
import json
from datetime import datetime

class RedisMemory:
    def __init__(self, agent_id: UUID):
        self.agent_id = agent_id
        self.redis = aioredis.from_url(app_settings.redis_url, encoding="utf-8", decode_responses=True)
        memory_logger.info(f"Redis connection established for agent: {agent_id}")

    async def add(self, key: str, memory_entry: MemoryEntry, expire: int = 3600):
        full_key = f"agent:{self.agent_id}:{key}"
        serialized_entry = json.dumps({
            "content": memory_entry.content,
            "metadata": memory_entry.metadata,
            "context": {
                "context_type": memory_entry.context.context_type,
                "timestamp": memory_entry.context.timestamp.isoformat(),
                "metadata": memory_entry.context.metadata
            }
        })
        await self.redis.set(full_key, serialized_entry, ex=expire)
        memory_logger.debug(f"Added key to Redis: {full_key}")

    async def get(self, key: str) -> Optional[MemoryEntry]:
        full_key = f"agent:{self.agent_id}:{key}"
        value = await self.redis.get(full_key)
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

    async def delete(self, key: str):
        full_key = f"agent:{self.agent_id}:{key}"
        await self.redis.delete(full_key)
        memory_logger.debug(f"Deleted key from Redis: {full_key}")

    async def search(self, query: AdvancedSearchQuery) -> List[Dict[str, Any]]:
        pattern = f"agent:{self.agent_id}:*"
        cursor = 0
        results = []

        while True:
            cursor, keys = await self.redis.scan(cursor, match=pattern, count=100)
            for key in keys:
                value = await self.redis.get(key)
                if value:
                    deserialized_entry = json.loads(value)
                    context = MemoryContext(
                        context_type=deserialized_entry["context"]["context_type"],
                        timestamp=datetime.fromisoformat(deserialized_entry["context"]["timestamp"]),
                        metadata=deserialized_entry["context"]["metadata"]
                    )
                    memory_entry = MemoryEntry(
                        content=deserialized_entry["content"],
                        metadata=deserialized_entry["metadata"],
                        context=context
                    )

                    # Apply filters
                    if self._matches_filters(memory_entry, query):
                        relevance_score = self._calculate_relevance(memory_entry, query)
                        results.append({
                            "id": key.split(":")[-1],
                            "memory_entry": memory_entry,
                            "relevance_score": relevance_score
                        })

            if cursor == 0:
                break

        # Sort results by relevance score
        results.sort(key=lambda x: x["relevance_score"], reverse=True)

        # Apply relevance threshold and limit results
        if query.relevance_threshold is not None:
            results = [r for r in results if r["relevance_score"] >= query.relevance_threshold]
        results = results[:query.max_results]

        return results

    def _matches_filters(self, memory_entry: MemoryEntry, query: AdvancedSearchQuery) -> bool:
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
        # Simple relevance calculation based on keyword matching
        # This can be improved with more sophisticated NLP techniques
        relevance = 0
        keywords = query.query.lower().split()
        content_words = memory_entry.content.lower().split()
        for keyword in keywords:
            if keyword in content_words:
                relevance += 1
        return relevance / len(keywords)
