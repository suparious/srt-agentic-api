import uuid
from typing import Dict, Any, List, Optional
from datetime import timedelta
from app.api.models.agent import MemoryConfig
from app.api.models.memory import (
    MemoryType,
    MemoryEntry,
    AdvancedSearchQuery,
    MemoryOperation,
)
from .memory_system import MemorySystem
from .memory_utils import DEFAULT_FORGET_AGE

# Global dictionary to store active memory systems
memory_systems: Dict[uuid.UUID, MemorySystem] = {}


async def get_memory_system(agent_id: uuid.UUID, config: MemoryConfig) -> MemorySystem:
    """
    Get or create a MemorySystem for the given agent_id.

    Args:
        agent_id (uuid.UUID): The unique identifier for the agent.
        config (MemoryConfig): Configuration settings for the memory system.

    Returns:
        MemorySystem: The memory system for the agent.
    """
    if agent_id not in memory_systems:
        memory_systems[agent_id] = MemorySystem(agent_id, config)
    return memory_systems[agent_id]


async def add_to_memory(
    agent_id: uuid.UUID,
    memory_type: MemoryType,
    entry: MemoryEntry,
    config: MemoryConfig,
) -> str:
    """
    Add a memory entry to the specified memory type for an agent.

    Args:
        agent_id (uuid.UUID): The unique identifier for the agent.
        memory_type (MemoryType): The type of memory (SHORT_TERM or LONG_TERM).
        entry (MemoryEntry): The memory entry to add.
        config (MemoryConfig): Configuration settings for the memory system.

    Returns:
        str: The ID of the added memory entry.
    """
    memory_system = await get_memory_system(agent_id, config)
    return await memory_system.add(memory_type, entry)


async def retrieve_from_memory(
    agent_id: uuid.UUID, memory_type: MemoryType, memory_id: str, config: MemoryConfig
) -> Optional[MemoryEntry]:
    """
    Retrieve a memory entry from the specified memory type for an agent.

    Args:
        agent_id (uuid.UUID): The unique identifier for the agent.
        memory_type (MemoryType): The type of memory (SHORT_TERM or LONG_TERM).
        memory_id (str): The ID of the memory entry to retrieve.
        config (MemoryConfig): Configuration settings for the memory system.

    Returns:
        Optional[MemoryEntry]: The retrieved memory entry, or None if not found.
    """
    memory_system = await get_memory_system(agent_id, config)
    return await memory_system.retrieve(memory_type, memory_id)


async def search_memory(
    agent_id: uuid.UUID, query: AdvancedSearchQuery, config: MemoryConfig
) -> List[Dict[str, Any]]:
    """
    Search for memories across both short-term and long-term storage for an agent.

    Args:
        agent_id (uuid.UUID): The unique identifier for the agent.
        query (AdvancedSearchQuery): The search query parameters.
        config (MemoryConfig): Configuration settings for the memory system.

    Returns:
        List[Dict[str, Any]]: A list of search results, sorted by relevance.
    """
    memory_system = await get_memory_system(agent_id, config)
    return await memory_system.search(query)


async def delete_from_memory(
    agent_id: uuid.UUID, memory_type: MemoryType, memory_id: str, config: MemoryConfig
):
    """
    Delete a memory entry from the specified memory type for an agent.

    Args:
        agent_id (uuid.UUID): The unique identifier for the agent.
        memory_type (MemoryType): The type of memory (SHORT_TERM or LONG_TERM).
        memory_id (str): The ID of the memory entry to delete.
        config (MemoryConfig): Configuration settings for the memory system.
    """
    memory_system = await get_memory_system(agent_id, config)
    await memory_system.delete(memory_type, memory_id)


async def perform_memory_operation(
    agent_id: uuid.UUID,
    operation: MemoryOperation,
    memory_type: MemoryType,
    data: Dict[str, Any],
    config: MemoryConfig,
) -> Any:
    """
    Perform a memory operation for an agent.

    Args:
        agent_id (uuid.UUID): The unique identifier for the agent.
        operation (MemoryOperation): The type of operation to perform.
        memory_type (MemoryType): The type of memory (SHORT_TERM or LONG_TERM).
        data (Dict[str, Any]): The data required for the operation.
        config (MemoryConfig): Configuration settings for the memory system.

    Returns:
        Any: The result of the operation, which varies based on the operation type.

    Raises:
        ValueError: If the operation type is invalid.
    """
    memory_system = await get_memory_system(agent_id, config)
    if operation == MemoryOperation.ADD:
        return await memory_system.add(
            memory_type, data["content"], data.get("metadata", {})
        )
    elif operation == MemoryOperation.RETRIEVE:
        return await memory_system.retrieve(memory_type, data["memory_id"])
    elif operation == MemoryOperation.SEARCH:
        return await memory_system.search(
            memory_type, data["query"], data.get("limit", 5)
        )
    elif operation == MemoryOperation.DELETE:
        await memory_system.delete(memory_type, data["memory_id"])
        return {"message": "Memory deleted successfully"}
    else:
        raise ValueError(f"Invalid memory operation: {operation}")


async def consolidate_agent_memories(agent_id: uuid.UUID, config: MemoryConfig):
    """
    Consolidate short-term memories into long-term storage for an agent.

    Args:
        agent_id (uuid.UUID): The unique identifier for the agent.
        config (MemoryConfig): Configuration settings for the memory system.
    """
    memory_system = await get_memory_system(agent_id, config)
    await memory_system.consolidate_memories()


async def forget_agent_old_memories(
    agent_id: uuid.UUID, config: MemoryConfig, age_limit: timedelta = DEFAULT_FORGET_AGE
):
    """
    Forget (delete) old memories from long-term storage for an agent.

    Args:
        agent_id (uuid.UUID): The unique identifier for the agent.
        age_limit (timedelta): The age limit for memories to be forgotten.
        config (MemoryConfig): Configuration settings for the memory system.
    """
    memory_system = await get_memory_system(agent_id, config)
    await memory_system.forget_old_memories(age_limit)


async def initialize_memory_systems():
    for agent_id, memory_system in memory_systems.items():
        asyncio.create_task(memory_system.close())


async def close_memory_systems():
    """
    Close all active memory systems.
    """
    for agent_id, memory_system in memory_systems.items():
        await memory_system.close()
    memory_systems.clear()
