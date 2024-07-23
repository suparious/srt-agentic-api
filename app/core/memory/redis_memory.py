from uuid import UUID
from typing import List, Dict, Any
from redis import asyncio as aioredis
from app.utils.logging import memory_logger
from app.config import settings as app_settings

class RedisMemory:
    def __init__(self, agent_id: UUID):
        self.agent_id = agent_id
        self.redis = aioredis.from_url(app_settings.redis_url, encoding="utf-8", decode_responses=True)
        memory_logger.info(f"Redis connection established for agent: {agent_id}")

    async def add(self, key: str, value: str, expire: int = 3600):
        full_key = f"agent:{self.agent_id}:{key}"
        await self.redis.set(full_key, value, ex=expire)
        memory_logger.debug(f"Added key to Redis: {full_key}")

    async def get(self, key: str) -> str:
        full_key = f"agent:{self.agent_id}:{key}"
        value = await self.redis.get(full_key)
        memory_logger.debug(f"Retrieved key from Redis: {full_key}")
        return value

    async def delete(self, key: str):
        full_key = f"agent:{self.agent_id}:{key}"
        await self.redis.delete(full_key)
        memory_logger.debug(f"Deleted key from Redis: {full_key}")

    async def get_recent(self, limit: int = 5) -> List[Dict[str, Any]]:
        pattern = f"agent:{self.agent_id}:*"
        keys = await self.redis.keys(pattern)
        recent_memories = []
        for key in keys[-limit:]:
            value = await self.redis.get(key)
            if value:
                recent_memories.append({"content": value})
        return recent_memories
