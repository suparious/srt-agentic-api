from uuid import UUID
from app.core.memory import MemorySystem
from app.core.agent import Agent


async def get_memory_system(agent_id: UUID) -> MemorySystem:
    """
    Retrieve or create a MemorySystem for the given agent_id.

    Args:
        agent_id (UUID): The unique identifier of the agent.

    Returns:
        MemorySystem: The memory system associated with the agent.

    Raises:
        ValueError: If the agent is not found.
    """
    agent = await Agent.get(agent_id)
    if agent is None:
        raise ValueError(f"Agent with ID {agent_id} not found")
    return agent.memory
