from typing import Dict
from uuid import UUID
from app.core.models import MemoryConfig
from app.core.memory import MemorySystem

# Global dictionary to store active memory systems
memory_systems: Dict[UUID, MemorySystem] = {}


async def get_memory_system(agent_id: UUID, config: MemoryConfig) -> MemorySystem:
    """
    Retrieve or create a MemorySystem for the given agent_id.

    Args:
        agent_id (UUID): The unique identifier of the agent.

    Returns:
        MemorySystem: The memory system associated with the agent.

    Raises:
        ValueError: If the agent is not found.
    """
    if agent_id not in memory_systems:
        memory_systems[agent_id] = MemorySystem(agent_id, config)
    return memory_systems[agent_id]
