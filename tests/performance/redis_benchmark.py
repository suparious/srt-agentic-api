import asyncio
import time
import psutil
import traceback
from uuid import UUID
from app.core.memory.redis_memory import RedisMemory
from app.api.models.memory import MemoryEntry, MemoryContext, AdvancedSearchQuery
from app.utils.logging import memory_logger
from app.config import settings


async def concurrent_access_benchmark(redis_memory, num_concurrent=10):
    async def concurrent_operation():
        memory_entry = MemoryEntry(
            content="Concurrent test",
            metadata={},
            context=MemoryContext(context_type="test", timestamp=time.time(), metadata={})
        )
        try:
            start_time = time.time()
            memory_logger.debug("Starting concurrent operation")

            add_start = time.time()
            memory_id = await redis_memory.add(memory_entry)
            add_time = time.time() - add_start
            memory_logger.debug(f"Memory added in {add_time:.6f} seconds")

            get_start = time.time()
            retrieved_entry = await redis_memory.get(memory_id)
            get_time = time.time() - get_start
            memory_logger.debug(f"Memory retrieved in {get_time:.6f} seconds")

            del_start = time.time()
            await redis_memory.delete(memory_id)
            del_time = time.time() - del_start
            memory_logger.debug(f"Memory deleted in {del_time:.6f} seconds")

            total_time = time.time() - start_time
            memory_logger.debug(f"Total operation time: {total_time:.6f} seconds")
        except Exception as e:
            memory_logger.error(f"Error in concurrent operation: {str(e)}")
            memory_logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    tasks = [concurrent_operation() for _ in range(num_concurrent)]
    start_time = time.time()
    results = await asyncio.gather(*tasks, return_exceptions=True)
    end_time = time.time()

    success_count = sum(1 for r in results if not isinstance(r, Exception))
    memory_logger.info(f"Successful operations: {success_count}/{num_concurrent}")

    for result in results:
        if isinstance(result, Exception):
            memory_logger.error(f"Task failed with exception: {str(result)}")

    return end_time - start_time


async def run_benchmarks():
    agent_id = UUID('12345678-1234-5678-1234-567812345678')
    redis_memory = RedisMemory(agent_id)

    try:
        await redis_memory.initialize()

        for num_connections in [1, 2, 5, 10]:
            print(f"\nTesting {num_connections} concurrent connections...")
            total_time = await concurrent_access_benchmark(redis_memory, num_concurrent=num_connections)
            print(f"Time taken for {num_connections} concurrent operations: {total_time:.6f} seconds")

    except Exception as e:
        print(f"An error occurred during benchmarking: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
    finally:
        await redis_memory.close()


if __name__ == "__main__":
    asyncio.run(run_benchmarks())
