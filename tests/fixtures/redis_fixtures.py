import pytest
import asyncio
from uuid import UUID
from app.core.memory.redis_memory import RedisMemory
from app.core.memory.redis.connection import RedisConnection

@pytest.fixture(scope="session")
async def redis_connection(test_settings):
    connection = RedisConnection(UUID('00000000-0000-0000-0000-000000000000'))
    await connection.initialize()
    yield connection
    await connection.close()

@pytest.fixture
async def redis_memory():
    agent_id = UUID('12345678-1234-5678-1234-567812345678')
    redis_mem = RedisMemory(agent_id)
    await redis_mem.initialize()
    yield redis_mem
    await redis_mem.close()

@pytest.fixture(autouse=True)
async def redis_isolation(request, redis_connection):
    if "redis" in request.keywords:
        async with redis_connection.get_connection() as conn:
            await conn.flushdb()
        yield
        async with redis_connection.get_connection() as conn:
            await conn.flushdb()
    else:
        yield
