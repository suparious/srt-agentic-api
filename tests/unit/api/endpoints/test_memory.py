import pytest
from app.api.endpoints import memory

def test_memory_router_export():
    assert hasattr(memory, 'router'), "memory module should export 'router'"
    from app.api.endpoints.memory import router as internal_router
    assert memory.router == internal_router, "Exported router should be the same as the internal router"

# Add more tests for the actual endpoints here once we've addressed the router export