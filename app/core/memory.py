import asyncio
from uuid import UUID
from typing import Dict, Any, List
import aioredis
import chromadb
from chromadb.config import Settings
from app.api.models.agent import MemoryConfig
from app.utils.logging import memory_logger


class RedisMemory:
    def __init__(self, redis_url: str):
        try:
            self.redis = aioredis.from_url(redis_url, encoding="utf-8", decode_responses=True)
            memory_logger.info(f"Redis connection established: {redis_url}")
        except Exception as e:
            memory_logger.error(f"Failed to connect to Redis: {str(e)}")
            raise

    async def add(self, key: str, value: str, expire: int = 3600):
        try:
            await self.redis.set(key, value, ex=expire)
            memory_logger.debug(f"Added key to Redis: {key}")
        except Exception as e:
            memory_logger.error(f"Failed to add key to Redis: {key}. Error: {str(e)}")
            raise

    async def get(self, key: str) -> str:
        try:
            value = await self.redis.get(key)
            memory_logger.debug(f"Retrieved key from Redis: {key}")
            return value
        except Exception as e:
            memory_logger.error(f"Failed to get key from Redis: {key}. Error: {str(e)}")
            raise

    async def delete(self, key: str):
        try:
            await self.redis.delete(key)
            memory_logger.debug(f"Deleted key from Redis: {key}")
        except Exception as e:
            memory_logger.error(f"Failed to delete key from Redis: {key}. Error: {str(e)}")
            raise


class VectorMemory:
    def __init__(self, collection_name: str):
        try:
            self.client = chromadb.Client(Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory="/path/to/persist"
            ))
            self.collection = self.client.get_or_create_collection(collection_name)
            memory_logger.info(f"ChromaDB collection initialized: {collection_name}")
        except Exception as e:
            memory_logger.error(f"Failed to initialize ChromaDB: {str(e)}")
            raise

    async def add(self, id: str, content: str, metadata: Dict[str, Any] = {}):
        try:
            await asyncio.to_thread(self.collection.add,
                                    documents=[content],
                                    metadatas=[metadata],
                                    ids=[id])
            memory_logger.debug(f"Added document to ChromaDB: {id}")
        except Exception as e:
            memory_logger.error(f"Failed to add document to ChromaDB: {id}. Error: {str(e)}")
            raise

    async def search(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        try:
            results = await asyncio.to_thread(self.collection.query,
                                              query_texts=[query],
                                              n_results=n_results)
            memory_logger.debug(f"Searched ChromaDB: {query}")
            return [{"id": id, "content": doc, "metadata": meta}
                    for id, doc, meta in zip(results['ids'][0], results['documents'][0], results['metadatas'][0])]
        except Exception as e:
            memory_logger.error(f"Failed to search ChromaDB: {query}. Error: {str(e)}")
            raise


class MemorySystem:
    def __init__(self, agent_id: UUID, config: MemoryConfig):
        self.agent_id = agent_id
        self.config = config
        self.short_term = RedisMemory("redis://localhost:6379")
        self.long_term = VectorMemory(f"agent_{agent_id}")
        memory_logger.info(f"MemorySystem initialized for agent: {agent_id}")

    async def add(self, content: str, metadata: Dict[str, Any] = {}):
        try:
            if self.config.use_redis_cache:
                key = f"{self.agent_id}:{asyncio.get_event_loop().time()}"
                await self.short_term.add(key, content)

            if self.config.use_long_term_memory:
                await self.long_term.add(str(asyncio.get_event_loop().time()), content, metadata)

            memory_logger.info(f"Memory added for agent: {self.agent_id}")
        except Exception as e:
            memory_logger.error(f"Failed to add memory for agent: {self.agent_id}. Error: {str(e)}")
            raise

    async def retrieve_relevant(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        try:
            if not self.config.use_long_term_memory:
                return []
            results = await self.long_term.search(query, n_results)
            memory_logger.info(f"Retrieved relevant memories for agent: {self.agent_id}")
            return results
        except Exception as e:
            memory_logger.error(f"Failed to retrieve relevant memories for agent: {self.agent_id}. Error: {str(e)}")
            raise


async def add_to_memory(agent_id: UUID, data: Dict[str, Any]) -> str:
    try:
        # This function should be implemented to work with your agent storage system
        # For now, we'll just return a success message
        memory_logger.info(f"Data added to memory for agent {agent_id}")
        return f"Data added to memory for agent {agent_id}"
    except Exception as e:
        memory_logger.error(f"Failed to add data to memory for agent {agent_id}. Error: {str(e)}")
        raise


async def retrieve_from_memory(agent_id: UUID, query: str) -> List[Dict[str, Any]]:
    try:
        # This function should be implemented to work with your agent storage system
        # For now, we'll just return a dummy result
        memory_logger.info(f"Data retrieved from memory for agent {agent_id}")
        return [{"content": f"Retrieved data for query: {query}", "timestamp": "2023-06-15T10:00:00Z"}]
    except Exception as e:
        memory_logger.error(f"Failed to retrieve data from memory for agent {agent_id}. Error: {str(e)}")
        raise


async def search_memory(agent_id: UUID, query: str) -> List[Dict[str, Any]]:
    try:
        # This function should be implemented to work with your agent storage system
        # For now, we'll just return a dummy result
        memory_logger.info(f"Memory searched for agent {agent_id}")
        return [{"content": f"Search result for query: {query}", "relevance": 0.95}]
    except Exception as e:
        memory_logger.error(f"Failed to search memory for agent {agent_id}. Error: {str(e)}")
        raise
