import pytest
import asyncio
import sys
from redis.asyncio import Redis
from redis.exceptions import ConnectionError

@pytest.fixture(scope="session")
def event_loop():
    if sys.platform.startswith("win"):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

async def close_redis_connections():
    # This function attempts to close all Redis connections
    for task in asyncio.all_tasks():
        if isinstance(task.get_coro().__self__, Redis):
            try:
                await task.get_coro().__self__.close()
            except ConnectionError:
                pass  # Connection might already be closed

@pytest.fixture(scope="session")
async def cleanup_after_tests(event_loop):
    yield
    await close_redis_connections()
    tasks = asyncio.all_tasks(event_loop)
    if tasks:
        for task in tasks:
            if not task.done():
                task.cancel()
        await asyncio.wait(tasks, timeout=5)
        for task in tasks:
            if not task.done():
                print(f"Force closing task: {task}")
                task.close()
    await event_loop.shutdown_asyncgens()

@pytest.fixture(autouse=True)
async def run_around_tests(cleanup_after_tests):
    yield
