import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

async def test_read_main(async_client: AsyncClient):
    response = await async_client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to SolidRusT Agentic API"}