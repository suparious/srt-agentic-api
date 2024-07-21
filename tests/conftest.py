import pytest
from httpx import AsyncClient
from app.main import app
from app.config import settings

@pytest.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
def auth_headers():
    return {"X-API-Key": settings.API_KEY}