import pytest
import asyncio

@pytest.fixture(scope="session")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(autouse=True, scope="session")
async def cleanup_after_tests(event_loop):
    yield
    tasks = asyncio.all_tasks(event_loop)
    for task in tasks:
        if not task.done():
            task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)
    await event_loop.shutdown_asyncgens()

# Add this to pytest_plugins in the root conftest.py
# "tests.fixtures.async_fixtures",
