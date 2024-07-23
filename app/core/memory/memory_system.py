from uuid import UUID
from typing import Dict, Any, List, Optional
from app.api.models.memory import MemoryType, MemoryEntry, MemoryOperation
from app.api.models.agent import MemoryConfig
from app.utils.logging import memory_logger
from .redis_memory import RedisMemory
from .vector_memory import VectorMemory

class MemorySystem:
    def __init__(self, agent_id: UUID, config: MemoryConfig):
        self.agent_id = agent_id
        self.config = config
        self.short_term = RedisMemory(agent_id)
        self.long_term = VectorMemory(f"agent_{agent_id}")
        memory_logger.info(f"MemorySystem initialized for agent: {agent_id}")

    async def add(self, memory_type: MemoryType, content: str, metadata: Dict[str, Any] = {}) -> str:
        try:
            memory_id = str(UUID.uuid4())
            if memory_type == MemoryType.SHORT_TERM and self.config.use_redis_cache:
                await self.short_term.add(memory_id, content)
            elif memory_type == MemoryType.LONG_TERM and self.config.use_long_term_memory:
                await self.long_term.add(memory_id, content, metadata)
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
                content = await self.short_term.get(memory_id)
                return MemoryEntry(content=content) if content else None
            elif memory_type == MemoryType.LONG_TERM and self.config.use_long_term_memory:
                result = await self.long_term.search(f"id:{memory_id}", n_results=1)
                if result:
                    return MemoryEntry(content=result[0]['content'], metadata=result[0]['metadata'])
                return None
            else:
                raise ValueError(f"Invalid memory type or configuration: {memory_type}")
        except Exception as e:
            memory_logger.error(
                f"Failed to retrieve {memory_type.value} memory for agent: {self.agent_id}. Error: {str(e)}")
            raise

    async def search(self, memory_type: MemoryType, query: str, limit: int = 5) -> List[MemoryEntry]:
        try:
            if memory_type == MemoryType.LONG_TERM and self.config.use_long_term_memory:
                results = await self.long_term.search(query, n_results=limit)
                return [MemoryEntry(content=result['content'], metadata=result['metadata']) for result in results]
            else:
                raise ValueError(f"Search is only supported for long-term memory")
        except Exception as e:
            memory_logger.error(
                f"Failed to search {memory_type.value} memory for agent: {self.agent_id}. Error: {str(e)}")
            raise

    async def delete(self, memory_type: MemoryType, memory_id: str):
        try:
            if memory_type == MemoryType.SHORT_TERM and self.config.use_redis_cache:
                await self.short_term.delete(memory_id)
            elif memory_type == MemoryType.LONG_TERM and self.config.use_long_term_memory:
                # Implement deletion for long-term memory (ChromaDB doesn't have a direct delete method)
                # This might involve re-indexing or marking as deleted
                pass
            else:
                raise ValueError(f"Invalid memory type or configuration: {memory_type}")
            memory_logger.info(f"{memory_type.value} memory deleted for agent: {self.agent_id}")
        except Exception as e:
            memory_logger.error(
                f"Failed to delete {memory_type.value} memory for agent: {self.agent_id}. Error: {str(e)}")
            raise

    async def retrieve_relevant(self, context: str, limit: int = 5) -> List[Dict[str, Any]]:
        try:
            relevant_memories = []
            if self.config.use_redis_cache:
                # Retrieve recent memories from short-term memory
                recent_memories = await self.short_term.get_recent(limit)
                relevant_memories.extend(recent_memories)

            if self.config.use_long_term_memory:
                # Search long-term memory for relevant entries
                long_term_results = await self.long_term.search(context, n_results=limit)
                relevant_memories.extend(long_term_results)

            # Sort and limit the combined results
            relevant_memories.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
            return relevant_memories[:limit]
        except Exception as e:
            memory_logger.error(f"Error retrieving relevant memories for agent {self.agent_id}: {str(e)}")
            raise

# Global dictionary to store active memory systems
memory_systems: Dict[UUID, MemorySystem] = {}

async def get_memory_system(agent_id: UUID, config: MemoryConfig) -> MemorySystem:
    if agent_id not in memory_systems:
        memory_systems[agent_id] = MemorySystem(agent_id, config)
    return memory_systems[agent_id]

async def add_to_memory(agent_id: UUID, memory_type: MemoryType, entry: MemoryEntry, config: MemoryConfig) -> str:
    memory_system = await get_memory_system(agent_id, config)
    return await memory_system.add(memory_type, entry.content, entry.metadata)

async def retrieve_from_memory(agent_id: UUID, memory_type: MemoryType, memory_id: str, config: MemoryConfig) -> Optional[MemoryEntry]:
    memory_system = await get_memory_system(agent_id, config)
    return await memory_system.retrieve(memory_type, memory_id)

async def search_memory(agent_id: UUID, memory_type: MemoryType, query: str, limit: int, config: MemoryConfig) -> List[MemoryEntry]:
    memory_system = await get_memory_system(agent_id, config)
    return await memory_system.search(memory_type, query, limit)

async def delete_from_memory(agent_id: UUID, memory_type: MemoryType, memory_id: str, config: MemoryConfig):
    memory_system = await get_memory_system(agent_id, config)
    await memory_system.delete(memory_type, memory_id)

async def perform_memory_operation(agent_id: UUID, operation: MemoryOperation, memory_type: MemoryType, data: Dict[str, Any], config: MemoryConfig) -> Any:
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