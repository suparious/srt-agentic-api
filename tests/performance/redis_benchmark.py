import asyncio
import time
import psutil
import traceback
from uuid import UUID
from app.core.memory.redis_memory import RedisMemory
from app.api.models.memory import MemoryEntry, MemoryContext, AdvancedSearchQuery
from app.utils.logging import memory_logger
from app.config import settings


async def test_redis_connection():
    try:
        print("Testing basic Redis connection...")
        from redis.asyncio import Redis
        redis = Redis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
        await redis.ping()
        print("Successfully connected to Redis")
        info = await redis.info()
        print(f"Redis version: {info['redis_version']}")
        print(f"Connected clients: {info['connected_clients']}")
        print(f"Used memory: {info['used_memory_human']}")
        await redis.close()
    except Exception as e:
        print(f"Failed to connect to Redis: {str(e)}")
        raise


async def find_optimal_connection_limit(redis_memory, start=1, step=1, max_attempts=20):
    for i in range(max_attempts):
        connections = start + i * step
        redis_memory.connection.set_max_connections(connections)
        try:
            print(f"Testing {connections} concurrent connections...")
            await asyncio.wait_for(concurrent_access_benchmark(redis_memory, num_concurrent=connections), timeout=30)
            print(f"Successfully handled {connections} concurrent connections")
        except asyncio.TimeoutError:
            print(f"Timeout at {connections} connections")
            return connections - step
        except Exception as e:
            print(f"Failed at {connections} connections: {str(e)}")
            return connections - step
    return start + (max_attempts - 1) * step


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

            connection_start = time.time()
            async with redis_memory.connection.get_connection() as conn:
                connection_time = time.time() - connection_start
                memory_logger.debug(f"Connection acquired in {connection_time:.6f} seconds")

                add_start = time.time()
                memory_id = await asyncio.wait_for(redis_memory.add(memory_entry), timeout=5.0)
                add_time = time.time() - add_start
                memory_logger.debug(f"Memory added in {add_time:.6f} seconds")

                get_start = time.time()
                await asyncio.wait_for(redis_memory.get(memory_id), timeout=5.0)
                get_time = time.time() - get_start
                memory_logger.debug(f"Memory retrieved in {get_time:.6f} seconds")

                del_start = time.time()
                await asyncio.wait_for(redis_memory.delete(memory_id), timeout=5.0)
                del_time = time.time() - del_start
                memory_logger.debug(f"Memory deleted in {del_time:.6f} seconds")

            total_time = time.time() - start_time
            memory_logger.debug(f"Total operation time: {total_time:.6f} seconds")
        except asyncio.TimeoutError as e:
            memory_logger.error(f"Timeout in concurrent operation: {str(e)}")
            memory_logger.error(f"Traceback: {traceback.format_exc()}")
            raise
        except Exception as e:
            memory_logger.error(f"Error in concurrent operation: {str(e)}")
            memory_logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    start_time = time.time()
    tasks = [concurrent_operation() for _ in range(num_concurrent)]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    end_time = time.time()

    for result in results:
        if isinstance(result, Exception):
            memory_logger.error(f"Task failed with exception: {str(result)}")

    return end_time - start_time


async def measure_execution_time(func, *args, **kwargs):
    start_time = time.time()
    result = await func(*args, **kwargs)
    end_time = time.time()
    return end_time - start_time, result


async def basic_redis_operations_benchmark(redis_memory):
    results = {}
    try:
        async with redis_memory.connection.get_connection() as conn:
            memory_entry = MemoryEntry(
                content="Test content",
                metadata={},
                context=MemoryContext(context_type="test", timestamp=time.time(), metadata={})
            )

            start_time = time.time()
            memory_id = await redis_memory.add(memory_entry)
            results["SET"] = time.time() - start_time
            memory_logger.debug(f"SET operation completed in {results['SET']:.6f} seconds")

            start_time = time.time()
            await redis_memory.get(memory_id)
            results["GET"] = time.time() - start_time
            memory_logger.debug(f"GET operation completed in {results['GET']:.6f} seconds")

            start_time = time.time()
            await redis_memory.delete(memory_id)
            results["DEL"] = time.time() - start_time
            memory_logger.debug(f"DEL operation completed in {results['DEL']:.6f} seconds")

    except Exception as e:
        memory_logger.error(f"Error in basic Redis operations: {str(e)}")
        raise

    return results


async def advanced_search_benchmark(redis_memory, num_entries=100, num_searches=10):
    async with redis_memory.connection.get_connection() as conn:
        # Add test data
        for i in range(num_entries):
            memory_entry = MemoryEntry(
                content=f"Test content {i}",
                metadata={"index": i},
                context=MemoryContext(context_type="test", timestamp=time.time(), metadata={})
            )
            await redis_memory.add(memory_entry)

        # Perform searches
        total_time = 0
        for _ in range(num_searches):
            query = AdvancedSearchQuery(
                query="Test content",
                max_results=10
            )
            search_time, _ = await measure_execution_time(redis_memory.search, query)
            total_time += search_time

    return total_time / num_searches


def get_memory_usage():
    process = psutil.Process()
    memory_info = process.memory_info()
    return memory_info.rss / (1024 * 1024)  # Convert to MB


async def run_benchmarks():
    try:
        await test_redis_connection()
    except Exception as e:
        print(f"Redis connection test failed. Exiting benchmark.")
        return

    agent_id = UUID('12345678-1234-5678-1234-567812345678')
    redis_memory = RedisMemory(agent_id)

    try:
        await redis_memory.initialize()

        print("Finding optimal connection limit...")
        optimal_limit = await find_optimal_connection_limit(redis_memory)
        print(f"Optimal connection limit: {optimal_limit}")

        if optimal_limit > 0:
            redis_memory.connection.set_max_connections(optimal_limit)

            print("Running basic Redis operations benchmark...")
            basic_results = await basic_redis_operations_benchmark(redis_memory)
            print("Basic Redis operations results:")
            for operation, time_taken in basic_results.items():
                print(f"{operation}: {time_taken:.6f} seconds")

            print("\nRunning concurrent access benchmark...")
            concurrent_time = await concurrent_access_benchmark(redis_memory, num_concurrent=optimal_limit)
            print(f"Time taken for {optimal_limit} concurrent operations: {concurrent_time:.6f} seconds")

            print("\nRunning advanced search benchmark...")
            avg_search_time = await advanced_search_benchmark(redis_memory)
            print(f"Average time for advanced search: {avg_search_time:.6f} seconds")

            print("\nMeasuring memory usage...")
            memory_usage = get_memory_usage()
            print(f"Memory usage: {memory_usage:.2f} MB")
        else:
            print("Optimal connection limit is 0. Skipping benchmarks.")

    except Exception as e:
        print(f"An error occurred during benchmarking: {str(e)}")
    finally:
        await redis_memory.close()

if __name__ == "__main__":
    asyncio.run(run_benchmarks())
