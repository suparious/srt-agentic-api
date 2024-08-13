from uuid import UUID
import pytest
from unittest.mock import patch, AsyncMock
from redis.exceptions import ConnectionError, TimeoutError
from app.core.memory.redis.connection import RedisConnection, RedisConnectionError


@pytest.fixture
async def redis_connection():
    connection = RedisConnection(UUID('00000000-0000-0000-0000-000000000000'))
    yield connection
    await connection.close()


@pytest.mark.asyncio
async def test_redis_connection_initialization(redis_connection):
    with patch('redis.asyncio.Redis.from_url', new_callable=AsyncMock) as mock_redis:
        mock_redis.return_value.ping = AsyncMock()
        mock_redis.return_value.info = AsyncMock(
            return_value={'redis_version': '6.0.0', 'connected_clients': '1', 'used_memory_human': '1M'})

        await redis_connection.initialize()

        mock_redis.assert_called_once()
        mock_redis.return_value.ping.assert_called_once()
        mock_redis.return_value.info.assert_called_once()


@pytest.mark.asyncio
async def test_redis_connection_initialization_retry(redis_connection):
    with patch('redis.asyncio.Redis.from_url', new_callable=AsyncMock) as mock_redis:
        mock_redis.return_value.ping = AsyncMock(side_effect=[ConnectionError, TimeoutError, None])
        mock_redis.return_value.info = AsyncMock(
            return_value={'redis_version': '6.0.0', 'connected_clients': '1', 'used_memory_human': '1M'})

        await redis_connection.initialize()

        assert mock_redis.call_count == 3
        assert mock_redis.return_value.ping.call_count == 3


@pytest.mark.asyncio
async def test_redis_connection_initialization_failure(redis_connection):
    with patch('redis.asyncio.Redis.from_url', new_callable=AsyncMock) as mock_redis:
        mock_redis.return_value.ping = AsyncMock(side_effect=ConnectionError)

        with pytest.raises(RedisConnectionError):
            await redis_connection.initialize()

        assert mock_redis.call_count == 3


@pytest.mark.asyncio
async def test_redis_connection_get_connection(redis_connection):
    with patch('redis.asyncio.Redis.from_url', new_callable=AsyncMock) as mock_redis:
        mock_redis.return_value.ping = AsyncMock()
        mock_redis.return_value.info = AsyncMock(
            return_value={'redis_version': '6.0.0', 'connected_clients': '1', 'used_memory_human': '1M'})

        await redis_connection.initialize()

        async with redis_connection.get_connection() as conn:
            assert conn == mock_redis.return_value


@pytest.mark.asyncio
async def test_redis_connection_reconnect(redis_connection):
    with patch('redis.asyncio.Redis.from_url', new_callable=AsyncMock) as mock_redis:
        mock_redis.return_value.ping = AsyncMock(side_effect=[None, ConnectionError, None])
        mock_redis.return_value.info = AsyncMock(
            return_value={'redis_version': '6.0.0', 'connected_clients': '1', 'used_memory_human': '1M'})

        await redis_connection.initialize()

        with pytest.raises(RedisConnectionError):
            async with redis_connection.get_connection() as conn:
                raise ConnectionError()

        async with redis_connection.get_connection() as conn:
            assert conn == mock_redis.return_value

        assert mock_redis.call_count == 2


@pytest.mark.asyncio
async def test_redis_connection_ensure_connection(redis_connection):
    with patch('redis.asyncio.Redis.from_url', new_callable=AsyncMock) as mock_redis:
        mock_redis.return_value.ping = AsyncMock()
        mock_redis.return_value.info = AsyncMock(
            return_value={'redis_version': '6.0.0', 'connected_clients': '1', 'used_memory_human': '1M'})

        await redis_connection.ensure_connection()

        mock_redis.assert_called_once()
        mock_redis.return_value.ping.assert_called_once()

        # Test with existing connection
        await redis_connection.ensure_connection()
        assert mock_redis.call_count == 1
        assert mock_redis.return_value.ping.call_count == 2
