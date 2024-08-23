import pytest
import os
from unittest.mock import AsyncMock, patch
from redis.exceptions import ConnectionError, TimeoutError
from app.core.memory.redis.connection import RedisConnection, RedisConnectionError


@pytest.fixture
def redis_url():
    return os.getenv("REDIS_URL", "redis://localhost:6379")


@pytest.mark.asyncio
async def test_redis_connection_initialization(redis_url):
    agent_id = '12345678-1234-5678-1234-567812345678'
    with patch('redis.asyncio.Redis.from_url') as mock_redis:
        mock_redis.return_value = AsyncMock()
        mock_redis.return_value.ping.return_value = True
        mock_redis.return_value.info.return_value = {
            'redis_version': '6.0.0',
            'connected_clients': '1',
            'used_memory_human': '1M'
        }

        connection = RedisConnection(agent_id)
        await connection.initialize()

        assert connection.redis is not None
        mock_redis.assert_called_once_with(redis_url, encoding="utf-8", decode_responses=True)
        mock_redis.return_value.ping.assert_called_once()


@pytest.mark.asyncio
async def test_redis_connection_initialization_retry(redis_url):
    agent_id = '12345678-1234-5678-1234-567812345678'
    with patch('redis.asyncio.Redis.from_url') as mock_redis, \
            patch('asyncio.sleep', return_value=None):
        mock_redis.return_value = AsyncMock()
        mock_redis.return_value.ping.side_effect = [TimeoutError, True]
        mock_redis.return_value.info.return_value = {
            'redis_version': '6.0.0',
            'connected_clients': '1',
            'used_memory_human': '1M'
        }

        connection = RedisConnection(agent_id)
        await connection.initialize()

        assert connection.redis is not None
        assert mock_redis.call_count == 2
        assert mock_redis.return_value.ping.call_count == 2


@pytest.mark.asyncio
async def test_redis_connection_initialization_failure(redis_url):
    agent_id = '12345678-1234-5678-1234-567812345678'
    with patch('redis.asyncio.Redis.from_url') as mock_redis, \
            patch('asyncio.sleep', return_value=None):
        mock_redis.return_value = AsyncMock()
        mock_redis.return_value.ping.side_effect = ConnectionError

        connection = RedisConnection(agent_id)
        with pytest.raises(RedisConnectionError):
            await connection.initialize()


@pytest.mark.asyncio
async def test_redis_connection_get_connection(redis_url):
    agent_id = '12345678-1234-5678-1234-567812345678'
    with patch('redis.asyncio.Redis.from_url') as mock_redis:
        mock_redis.return_value = AsyncMock()
        mock_redis.return_value.ping.return_value = True
        mock_redis.return_value.info.return_value = {
            'redis_version': '6.0.0',
            'connected_clients': '1',
            'used_memory_human': '1M'
        }

        connection = RedisConnection(agent_id)
        await connection.initialize()

        async with connection.get_connection() as conn:
            assert conn is not None
            assert conn is connection.redis


@pytest.mark.asyncio
async def test_redis_connection_ensure_connection(redis_url):
    agent_id = '12345678-1234-5678-1234-567812345678'
    with patch('redis.asyncio.Redis.from_url') as mock_redis:
        mock_redis.return_value = AsyncMock()
        mock_redis.return_value.ping.return_value = True
        mock_redis.return_value.info.return_value = {
            'redis_version': '6.0.0',
            'connected_clients': '1',
            'used_memory_human': '1M'
        }

        connection = RedisConnection(agent_id)

        # Test when redis is None
        await connection.ensure_connection()
        assert connection.redis is not None

        # Test when redis is already initialized
        await connection.ensure_connection()
        assert mock_redis.call_count == 1


@pytest.mark.asyncio
async def test_redis_connection_close(redis_url):
    agent_id = '12345678-1234-5678-1234-567812345678'
    with patch('redis.asyncio.Redis.from_url') as mock_redis:
        mock_redis.return_value = AsyncMock()
        mock_redis.return_value.ping.return_value = True
        mock_redis.return_value.info.return_value = {
            'redis_version': '6.0.0',
            'connected_clients': '1',
            'used_memory_human': '1M'
        }

        connection = RedisConnection(agent_id)
        await connection.initialize()

        await connection.close()
        assert connection.redis is None
        mock_redis.return_value.aclose.assert_called_once()


@pytest.mark.asyncio
async def test_redis_connection_too_many_connections(redis_url):
    agent_id = '12345678-1234-5678-1234-567812345678'
    with patch('redis.asyncio.Redis.from_url') as mock_redis, \
            patch('asyncio.sleep', return_value=None):
        mock_redis.return_value = AsyncMock()
        mock_redis.return_value.ping.side_effect = ConnectionError("too many connections")

        connection = RedisConnection(agent_id)
        with pytest.raises(RedisConnectionError) as excinfo:
            await connection.initialize()

        assert "too many connections" in str(excinfo.value)
        mock_redis.return_value.aclose.assert_called()
