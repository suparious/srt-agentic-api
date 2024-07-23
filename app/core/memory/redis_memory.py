import json
from uuid import UUID
from typing import Dict, Any, List
from redis import asyncio as aioredis
from app.utils.logging import memory_logger
from app.config import settings

class RedisMemory:
    def __init__(self, agent_id: UUID):
        try:
            self.redis = aioredis.from_url(settings.redis_url, encoding="utf-8", decode_responses=True)
            self.agent_id = agent_id
            memory_logger.info(f"Redis connection established: {settings.redis_url} for agent: {agent_id}")
        except Exception as e:
            memory_logger.error(f"Failed to connect to Redis: {str(e)}")
            raise

    async def add(self, key: str, value: str, expire: int = 3600):
        try:
            full_key = f"agent:{self.agent_id}:{key}"
            await self.redis.set(full_key, value, ex=expire)
            memory_logger.debug(f"Added key to Redis: {full_key}")
        except Exception as e:
            memory_logger.error(f"Failed to add key to Redis: {full_key}. Error: {str(e)}")
            raise

    async def get(self, key: str) -> str:
        try:
            full_key = f"agent:{self.agent_id}:{key}"
            value = await self.redis.get(full_key)
            memory_logger.debug(f"Retrieved key from Redis: {full_key}")
            return value
        except Exception as e:
            memory_logger.error(f"Failed to get key from Redis: {full_key}. Error: {str(e)}")
            raise

    async def delete(self, key: str):
        try:
            full_key = f"agent:{self.agent_id}:{key}"
            await self.redis.delete(full_key)
            memory_logger.debug(f"Deleted key from Redis: {full_key}")
        except Exception as e:
            memory_logger.error(f"Failed to delete key from Redis: {full_key}. Error: {str(e)}")
            raise

    async def get_recent(self, limit: int = 5) -> List[Dict[str, Any]]:
        try:
            pattern = f"agent:{self.agent_id}:*"
            keys = await self.redis.keys(pattern)
            recent_memories = []
            for key in keys[-limit:]:
                value = await self.redis.get(key)
                if value:
                    recent_memories.append(json.loads(value))
            return recent_memories
        except Exception as e:
            memory_logger.error(f"Failed to get recent memories from Redis for agent {self.agent_id}: {str(e)}")
            raise
