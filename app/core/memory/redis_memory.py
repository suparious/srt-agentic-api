from uuid import UUID
from app.core.memory.redis.connection import RedisConnection
from app.core.memory.redis.memory_operations import RedisMemoryOperations
from app.core.memory.redis.search import RedisSearch
from app.core.memory.redis.cleanup import RedisCleanup

class RedisMemoryError(Exception):
    """Custom exception for Redis memory operations."""
    pass

class RedisMemory:
    def __init__(self, agent_id: UUID):
        self.connection = RedisConnection(agent_id)
        self.operations = RedisMemoryOperations(self.connection)
        self.search = RedisSearch(self.connection)
        self.cleanup = RedisCleanup()

    async def initialize(self) -> None:
        await self.connection.initialize()

    async def close(self) -> None:
        await self.connection.close()

    # Delegate methods to appropriate components
    async def add(self, memory_entry, expire=None):
        return await self.operations.add(memory_entry, expire)

    async def get(self, memory_id):
        return await self.operations.get(memory_id)

    async def delete(self, memory_id):
        await self.operations.delete(memory_id)

    async def search(self, query):
        return await self.search.search(query)

    async def get_memories_older_than(self, threshold):
        return await self.search.get_memories_older_than(threshold)

    async def cleanup(self):
        await self.cleanup.cleanup(self.connection)
