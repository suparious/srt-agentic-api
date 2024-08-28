from functools import lru_cache

@lru_cache(maxsize=None)
def get_memory_logger():
    from app.utils.logging import memory_logger
    return memory_logger
