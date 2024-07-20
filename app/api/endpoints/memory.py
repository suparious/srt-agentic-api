import asyncio
from uuid import UUID
from typing import Dict, Any, List, Optional
from redis import asyncio as aioredis
import chromadb
from chromadb.config import Settings
from app.api.models.memory import MemoryEntry, MemoryType
from app.config import settings
from app.utils.logging import memory_logger
from fastapi import APIRouter

router = APIRouter()

class RedisMemory:
    def __init__(self, redis_url: str):
        self.redis = aioredis.from_url(redis_url, encoding="utf-8", decode_responses=True)
        memory_logger.info(f"Redis connection established: {redis_url}")

    async def add(self, key: str, value: str, expire: int = 3600):
        try:
            await self.redis.set(key, value, ex=expire)
            memory_logger.debug(f"Added key to Redis: {key}")
        except Exception as e:
            memory_logger.error(f"Failed to add key to Redis: {key}. Error: {str(e)}")
            raise

    async def get(self, key: str) -> Optional[str]:
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
        self.client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=settings.CHROMA_PERSIST_DIRECTORY
        ))
        self.collection = self.client.get_or_create_collection(collection_name)
        memory_logger.info(f"ChromaDB collection initialized: {collection_name}")

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

    async def get(self, id: str) -> Optional[Dict[str, Any]]:
        try:
            result = await asyncio.to_thread(self.collection.get, ids=[id])
            if result['documents']:
                memory_logger.debug(f"Retrieved document from ChromaDB: {id}")
                return {
                    "content": result['documents'][0],
                    "metadata": result['metadatas'][0]
                }
            return None
        except Exception as e:
            memory_logger.error(f"Failed to get document from ChromaDB: {id}. Error: {str(e)}")
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
    def __init__(self, agent_id: UUID):
        self.agent_id = agent_id
        self.short_term = RedisMemory(settings.REDIS_URL)
        self.long_term = VectorMemory(f"agent_{agent_id}")
        memory_logger.info(f"MemorySystem initialized for agent: {agent_id}")

    async def add(self, memory_type: MemoryType, content: str, metadata: Dict[str, Any] = {}) -> str:
        memory_id = str(UUID.uuid4())
        try:
            if memory_type == MemoryType.SHORT_TERM:
                await self.short_term.add(memory_id, content)
            elif memory_type == MemoryType.LONG_TERM:
                await self.long_term.add(memory_id, content, metadata)
            else:
                raise ValueError(f"Invalid memory type: {memory_type}")

            memory_logger.info(f"{memory_type.value} memory added for agent: {self.agent_id}")
            return memory_id
        except Exception as e:
            memory_logger.error(f"Failed to add {memory_type.value} memory for agent: {self.agent_id}. Error: {str(e)}")
            raise

    async def retrieve(self, memory_type: MemoryType, memory_id: str) -> Optional[MemoryEntry]:
        try:
            if memory_type == MemoryType.SHORT_TERM:
                content = await self.short_term.get(memory_id)
                return MemoryEntry(content=content) if content else None
            elif memory_type == MemoryType.LONG_TERM:
                result = await self.long_term.get(memory_id)
                return MemoryEntry(content=result['content'], metadata=result['metadata']) if result else None
            else:
                raise ValueError(f"Invalid memory type: {memory_type}")
        except Exception as e:
            memory_logger.error(
                f"Failed to retrieve {memory_type.value} memory for agent: {self.agent_id}. Error: {str(e)}")
            raise

    async def search(self, memory_type: MemoryType, query: str, limit: int = 5) -> List[MemoryEntry]:
        try:
            if memory_type == MemoryType.LONG_TERM:
                results = await self.long_term.search(query, limit)
                return [MemoryEntry(content=result['content'], metadata=result['metadata']) for result in results]
            else:
                raise ValueError(f"Search is only supported for long-term memory")
        except Exception as e:
            memory_logger.error(
                f"Failed to search {memory_type.value} memory for agent: {self.agent_id}. Error: {str(e)}")
            raise


# Global dictionary to store active memory systems
memory_systems: Dict[UUID, MemorySystem] = {}


async def get_memory_system(agent_id: UUID) -> MemorySystem:
    if agent_id not in memory_systems:
        memory_systems[agent_id] = MemorySystem(agent_id)
    return memory_systems[agent_id]


async def add_to_memory(agent_id: UUID, memory_type: MemoryType, entry: MemoryEntry) -> str:
    memory_system = await get_memory_system(agent_id)
    return await memory_system.add(memory_type, entry.content, entry.metadata)


async def retrieve_from_memory(agent_id: UUID, memory_type: MemoryType, memory_id: str) -> Optional[MemoryEntry]:
    memory_system = await get_memory_system(agent_id)
    return await memory_system.retrieve(memory_type, memory_id)


async def search_memory(agent_id: UUID, memory_type: MemoryType, query: str, limit: int = 5) -> List[MemoryEntry]:
    memory_system = await get_memory_system(agent_id)
    return await memory_system.search(memory_type, query, limit)

@router.post("/add")
async def add_memory_endpoint(agent_id: UUID, memory_type: MemoryType, entry: MemoryEntry):
    return await add_to_memory(agent_id, memory_type, entry)

@router.get("/retrieve")
async def retrieve_memory_endpoint(agent_id: UUID, memory_type: MemoryType, memory_id: str):
    return await retrieve_from_memory(agent_id, memory_type, memory_id)

@router.post("/search")
async def search_memory_endpoint(agent_id: UUID, memory_type: MemoryType, query: str, limit: int = 5):
    return await search_memory(agent_id, memory_type, query, limit)
