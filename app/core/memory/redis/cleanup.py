from app.core.memory.redis.connection import RedisConnection
from app.utils.logging import memory_logger

class RedisCleanup:
    @staticmethod
    async def cleanup(connection: RedisConnection) -> None:
        """
        Perform cleanup operations for the Redis connection.

        Args:
            connection (RedisConnection): The Redis connection to clean up.
        """
        await connection.close()
        memory_logger.info(f"Redis cleanup completed for agent: {connection.agent_id}")
