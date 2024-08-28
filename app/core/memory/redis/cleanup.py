from app.core.memory.redis.connection import RedisConnection, RedisConnectionError
from app.utils.logging import memory_logger

class RedisCleanupError(Exception):
    """Custom exception for Redis cleanup errors."""
    pass

class RedisCleanup:
    @staticmethod
    async def cleanup(connection: RedisConnection) -> None:
        """
        Perform cleanup operations for the Redis connection.

        Args:
            connection (RedisConnection): The Redis connection to clean up.

        Raises:
            RedisCleanupError: If there's an error during the cleanup process.
        """
        try:
            await connection.close()
            memory_logger.info(f"Redis cleanup completed successfully for agent: {connection.agent_id}")
        except RedisConnectionError as e:
            error_message = f"Error during Redis cleanup for agent {connection.agent_id}: {str(e)}"
            memory_logger.error(error_message)
            raise RedisCleanupError(error_message) from e
        except Exception as e:
            error_message = f"Unexpected error during Redis cleanup for agent {connection.agent_id}: {str(e)}"
            memory_logger.error(error_message)
            raise RedisCleanupError(error_message) from e
