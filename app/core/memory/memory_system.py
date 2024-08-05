import uuid
import asyncio
from uuid import UUID
from typing import Dict, Any, List, Optional
from app.api.models.agent import MemoryConfig
from app.api.models.memory import MemoryType, MemoryEntry, AdvancedSearchQuery, MemoryOperation
from app.utils.logging import memory_logger
from .redis_memory import RedisMemory
from .vector_memory import VectorMemory


class MemorySystem:
    """
    Manages both short-term and long-term memory for an agent.

    This class coordinates between RedisMemory for short-term storage and
    VectorMemory for long-term storage based on the provided configuration.
    """

    def __init__(self, agent_id: UUID, config: MemoryConfig, short_term: Optional[RedisMemory] = None,
                 long_term: Optional[VectorMemory] = None):
        """
        Initialize the MemorySystem for an agent.

        Args:
            agent_id (UUID): The unique identifier for the agent.
            config (MemoryConfig): Configuration settings for the memory system.
            short_term (Optional[RedisMemory]): RedisMemory instance for short-term storage. If None, a new instance will be created.
            long_term (Optional[VectorMemory]): VectorMemory instance for long-term storage. If None, a new instance will be created.
        """
        self.agent_id = agent_id
        self.config = config
        self.short_term = short_term or RedisMemory(agent_id)
        self.long_term = long_term or VectorMemory(f"agent_{agent_id}")
        memory_logger.info(f"MemorySystem initialized for agent: {agent_id}")

    async def add(self, memory_type: MemoryType, memory_entry: MemoryEntry) -> str:
        """
        Add a memory entry to either short-term or long-term storage.

        Args:
            memory_type (MemoryType): The type of memory (SHORT_TERM or LONG_TERM).
            memory_entry (MemoryEntry): The memory entry to be added.

        Returns:
            str: The ID of the added memory entry.

        Raises:
            ValueError: If the memory type is invalid or not configured.
        """
        try:
            if memory_type == MemoryType.SHORT_TERM and self.config.use_redis_cache:
                memory_id = await self.short_term.add(memory_entry)
                memory_logger.info(f"Short-term memory added for agent: {self.agent_id}")
                return memory_id
            elif memory_type == MemoryType.LONG_TERM and self.config.use_long_term_memory:
                memory_id = await self.long_term.add(memory_entry)
                memory_logger.info(f"Long-term memory added for agent: {self.agent_id}")
                return memory_id
            else:
                raise ValueError(f"Invalid memory type or configuration: {memory_type}")
        except Exception as e:
            memory_logger.error(f"Failed to add {memory_type.value} memory for agent: {self.agent_id}. Error: {str(e)}")
            raise

    async def retrieve(self, memory_type: MemoryType, memory_id: str) -> Optional[MemoryEntry]:
        """
        Retrieve a memory entry from either short-term or long-term storage.

        Args:
            memory_type (MemoryType): The type of memory (SHORT_TERM or LONG_TERM).
            memory_id (str): The ID of the memory entry to retrieve.

        Returns:
            Optional[MemoryEntry]: The retrieved memory entry, or None if not found.

        Raises:
            ValueError: If the memory type is invalid or not configured.
        """
        try:
            if memory_type == MemoryType.SHORT_TERM and self.config.use_redis_cache:
                return await self.short_term.get(memory_id)
            elif memory_type == MemoryType.LONG_TERM and self.config.use_long_term_memory:
                results = await self.long_term.search(AdvancedSearchQuery(query=memory_id, max_results=1))
                return results[0]["memory_entry"] if results else None
            else:
                raise ValueError(f"Invalid memory type or configuration: {memory_type}")
        except Exception as e:
            memory_logger.error(
                f"Failed to retrieve {memory_type.value} memory for agent: {self.agent_id}. Error: {str(e)}")
            raise

    async def search(self, query: AdvancedSearchQuery) -> List[Dict[str, Any]]:
        """
        Search for memories across both short-term and long-term storage.

        Args:
            query (AdvancedSearchQuery): The search query parameters.

        Returns:
            List[Dict[str, Any]]: A list of search results, sorted by relevance.
        """
        try:
            results = []
            if query.memory_type in (None, MemoryType.SHORT_TERM) and self.config.use_redis_cache:
                results.extend(await self.short_term.search(query))
            if query.memory_type in (None, MemoryType.LONG_TERM) and self.config.use_long_term_memory:
                results.extend(await self.long_term.search(query))

            sorted_results = sorted(results, key=lambda x: x["relevance_score"], reverse=True)
            return sorted_results[:query.max_results]
        except Exception as e:
            memory_logger.error(f"Failed to search memories for agent: {self.agent_id}. Error: {str(e)}")
            raise

    async def delete(self, memory_type: MemoryType, memory_id: str):
        """
        Delete a memory entry from either short-term or long-term storage.

        Args:
            memory_type (MemoryType): The type of memory (SHORT_TERM or LONG_TERM).
            memory_id (str): The ID of the memory entry to delete.

        Raises:
            ValueError: If the memory type is invalid or not configured.
        """
        try:
            if memory_type == MemoryType.SHORT_TERM and self.config.use_redis_cache:
                await self.short_term.delete(memory_id)
                memory_logger.info(f"Short-term memory deleted for agent: {self.agent_id}")
            elif memory_type == MemoryType.LONG_TERM and self.config.use_long_term_memory:
                # Implement deletion for long-term memory if needed
                pass
            else:
                raise ValueError(f"Invalid memory type or configuration: {memory_type}")
        except Exception as e:
            memory_logger.error(
                f"Failed to delete {memory_type.value} memory for agent: {self.agent_id}. Error: {str(e)}")
            raise

    async def perform_operation(self, operation: MemoryOperation, memory_type: MemoryType, data: Dict[str, Any]) -> Any:
        """
        Perform a memory operation based on the given operation type.

        Args:
            operation (MemoryOperation): The type of operation to perform.
            memory_type (MemoryType): The type of memory (SHORT_TERM or LONG_TERM).
            data (Dict[str, Any]): The data required for the operation.

        Returns:
            Any: The result of the operation, which varies based on the operation type.

        Raises:
            ValueError: If the operation type is invalid.
        """
        try:
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
        except Exception as e:
            memory_logger.error(
                f"Failed to perform {operation.value} operation for agent: {self.agent_id}. Error: {str(e)}")
            raise

    async def retrieve_relevant(self, context: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve relevant memories based on the given context.

        Args:
            context (str): The context to use for retrieving relevant memories.
            limit (int): The maximum number of memories to retrieve.

        Returns:
            List[Dict[str, Any]]: A list of relevant memories.
        """
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

    async def advanced_search(self, query: AdvancedSearchQuery) -> List[Dict[str, Any]]:
        """
        Perform an advanced search across both short-term and long-term memory.

        Args:
            query (AdvancedSearchQuery): The advanced search query parameters.

        Returns:
            List[Dict[str, Any]]: A list of search results, sorted by relevance.
        """
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
            memory_logger.error(f"Failed to perform advanced search for agent: {self.agent_id}. Error: {str(e)}")
            raise

    async def close(self):
        """
        Close connections and perform cleanup for the memory system.
        """
        try:
            await self.short_term.close()
            # Implement close method for VectorMemory if needed
            memory_logger.info(f"MemorySystem closed for agent: {self.agent_id}")
        except Exception as e:
            memory_logger.error(f"Error closing MemorySystem for agent {self.agent_id}: {str(e)}")
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
