import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio

from app.api.models.memory import MemoryType, MemoryEntry, MemoryOperation, AdvancedSearchQuery
from app.api.models.agent import MemoryConfig
from app.utils.logging import memory_logger
from .redis_memory import RedisMemory
from .vector_memory import VectorMemory
from app.config import settings as app_settings

class MemorySystem:
    def __init__(self, agent_id: uuid.UUID, config: MemoryConfig):
        self.agent_id = agent_id
        self.config = config
        self.short_term = RedisMemory(agent_id)
        self.long_term = VectorMemory(f"agent_{agent_id}")
        memory_logger.info(f"MemorySystem initialized for agent: {agent_id}")

    async def add(self, memory_type: MemoryType, memory_entry: MemoryEntry) -> str:
        try:
            memory_id = str(uuid.uuid4())
            if memory_type == MemoryType.SHORT_TERM and self.config.use_redis_cache:
                await self.short_term.add(memory_id, memory_entry)
            elif memory_type == MemoryType.LONG_TERM and self.config.use_long_term_memory:
                await self.long_term.add(memory_id, memory_entry)
            else:
                raise ValueError(f"Invalid memory type or configuration: {memory_type}")

            memory_logger.info(f"{memory_type.value} memory added for agent: {self.agent_id}")
            return memory_id
        except Exception as e:
            memory_logger.error(f"Failed to add {memory_type.value} memory for agent: {self.agent_id}. Error: {str(e)}")
            raise

    async def retrieve(self, memory_type: MemoryType, memory_id: str) -> Optional[MemoryEntry]:
        try:
            if memory_type == MemoryType.SHORT_TERM and self.config.use_redis_cache:
                return await self.short_term.get(memory_id)
            elif memory_type == MemoryType.LONG_TERM and self.config.use_long_term_memory:
                results = await self.long_term.search(AdvancedSearchQuery(query=memory_id, max_results=1))
                return results[0]["memory_entry"] if results else None
            else:
                raise ValueError(f"Invalid memory type or configuration: {memory_type}")
        except Exception as e:
            memory_logger.error(f"Failed to retrieve {memory_type.value} memory for agent: {self.agent_id}. Error: {str(e)}")
            raise

    async def search(self, query: AdvancedSearchQuery) -> List[Dict[str, Any]]:
        try:
            results = []
            if query.memory_type in (None, MemoryType.SHORT_TERM) and self.config.use_redis_cache:
                short_term_results = await self.short_term.search(query)
                results.extend(short_term_results)
            if query.memory_type in (None, MemoryType.LONG_TERM) and self.config.use_long_term_memory:
                long_term_results = await self.long_term.search(query)
                results.extend(long_term_results)

            results.sort(key=lambda x: x["relevance_score"], reverse=True)

            if query.relevance_threshold is not None:
                results = [r for r in results if r["relevance_score"] >= query.relevance_threshold]

            return results[:query.max_results]
        except Exception as e:
            memory_logger.error(f"Failed to search memory for agent: {self.agent_id}. Error: {str(e)}")
            raise

    async def delete(self, memory_type: MemoryType, memory_id: str):
        try:
            if memory_type == MemoryType.SHORT_TERM and self.config.use_redis_cache:
                await self.short_term.delete(memory_id)
            elif memory_type == MemoryType.LONG_TERM and self.config.use_long_term_memory:
                # TODO: Implement deletion for long-term memory
                pass
            else:
                raise ValueError(f"Invalid memory type or configuration: {memory_type}")
            memory_logger.info(f"{memory_type.value} memory deleted for agent: {self.agent_id}")
        except Exception as e:
            memory_logger.error(f"Failed to delete {memory_type.value} memory for agent: {self.agent_id}. Error: {str(e)}")
            raise

    async def perform_operation(self, operation: MemoryOperation, memory_type: MemoryType, data: Dict[str, Any]) -> Any:
        if operation == MemoryOperation.ADD:
            return await self.add(memory_type, MemoryEntry(**data))
        elif operation == MemoryOperation.RETRIEVE:
            return await self.retrieve(memory_type, data["memory_id"])
        elif operation == MemoryOperation.SEARCH:
            return await self.search(AdvancedSearchQuery(**data))
        elif operation == MemoryOperation.DELETE:
            await self.delete(memory_type, data["memory_id"])
            return {"message": "Memory deleted successfully"}
        else:
            raise ValueError(f"Invalid memory operation: {operation}")

    async def retrieve_relevant(self, context: str, limit: int = 5) -> List[Dict[str, Any]]:
        try:
            relevant_memories = []
            if self.config.use_redis_cache:
                recent_memories = await self.short_term.get_recent(limit)
                relevant_memories.extend(recent_memories)

            if self.config.use_long_term_memory:
                long_term_results = await self.long_term.search(AdvancedSearchQuery(query=context, max_results=limit))
                relevant_memories.extend(long_term_results)

            relevant_memories.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
            return relevant_memories[:limit]
        except Exception as e:
            memory_logger.error(f"Error retrieving relevant memories for agent {self.agent_id}: {str(e)}")
            raise

    async def close(self):
        await self.short_term.close()

    async def advanced_search(self, query: AdvancedSearchQuery) -> List[Dict[str, Any]]:
        try:
            results = []
            if query.memory_type in (None, MemoryType.SHORT_TERM) and self.config.use_redis_cache:
                short_term_results = await self.short_term.search(query)
                results.extend(short_term_results)
            if query.memory_type in (None, MemoryType.LONG_TERM) and self.config.use_long_term_memory:
                long_term_results = await self.long_term.search(query)
                results.extend(long_term_results)

            # Merge and rank results
            results.sort(key=lambda x: x["relevance_score"], reverse=True)
            return results[:query.max_results]
        except Exception as e:
            memory_logger.error(
                f"Failed to perform advanced search for agent: {self.agent_id}. Error: {str(e)}")
            raise

# Global dictionary to store active memory systems
memory_systems: Dict[uuid.UUID, MemorySystem] = {}

async def get_memory_system(agent_id: uuid.UUID, config: MemoryConfig) -> MemorySystem:
    if agent_id not in memory_systems:
        memory_systems[agent_id] = MemorySystem(agent_id, config)
    return memory_systems[agent_id]

async def add_to_memory(agent_id: uuid.UUID, memory_type: MemoryType, entry: MemoryEntry, config: MemoryConfig) -> str:
    memory_system = await get_memory_system(agent_id, config)
    return await memory_system.add(memory_type, entry)

async def retrieve_from_memory(agent_id: uuid.UUID, memory_type: MemoryType, memory_id: str, config: MemoryConfig) -> Optional[MemoryEntry]:
    memory_system = await get_memory_system(agent_id, config)
    return await memory_system.retrieve(memory_type, memory_id)

async def search_memory(agent_id: uuid.UUID, query: AdvancedSearchQuery, config: MemoryConfig) -> List[Dict[str, Any]]:
    memory_system = await get_memory_system(agent_id, config)
    return await memory_system.search(query)

async def delete_from_memory(agent_id: uuid.UUID, memory_type: MemoryType, memory_id: str, config: MemoryConfig):
    memory_system = await get_memory_system(agent_id, config)
    await memory_system.delete(memory_type, memory_id)

async def perform_memory_operation(agent_id: uuid.UUID, operation: MemoryOperation, memory_type: MemoryType, data: Dict[str, Any], config: MemoryConfig) -> Any:
    memory_system = await get_memory_system(agent_id, config)
    if operation == MemoryOperation.ADD:
        return await memory_system.add(memory_type, data['content'], data.get('metadata', {}))
    elif operation == MemoryOperation.RETRIEVE:
        return await memory_system.retrieve(memory_type, data['memory_id'])
    elif operation == MemoryOperation.SEARCH:
        return await memory_system.search(memory_type, data['query'], data.get('limit', 5))
    elif operation == MemoryOperation.DELETE:
        await memory_system.delete(memory_type, data['memory_id'])
        return {"message": "Memory deleted successfully"}
    else:
        raise ValueError(f"Invalid memory operation: {operation}")

async def initialize_memory_systems():
    for agent_id, memory_system in memory_systems.items():
        asyncio.create_task(memory_system.close())

# Call this function when your application starts
# asyncio.create_task(initialize_memory_systems())
