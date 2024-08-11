import pytest
import asyncio
from uuid import UUID
from app.core.memory.redis_memory import RedisMemory
from app.core.memory.vector_memory import VectorMemory

@pytest.mark.asyncio
async def test_redis_memory_async_setup():
    agent_id = UUID('12345678-1234-5678-1234-567812345678')
    redis_mem = RedisMemory(agent_id)
    await redis_mem.initialize()
    assert redis_mem.redis is not None
    await redis_mem.close()

@pytest.mark.asyncio
async def test_vector_memory_async_setup():
    agent_id = UUID('12345678-1234-5678-1234-567812345678')
    vector_mem = VectorMemory(f"agent_{agent_id}")
    assert vector_mem.collection is not None
    # VectorMemory doesn't have an explicit close method yet, but we should ensure
    # that any async operations are properly handled
    await asyncio.sleep(0)  # Allow any pending tasks to complete
