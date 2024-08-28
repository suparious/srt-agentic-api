from typing import Dict
from uuid import UUID
from typing import Any

memory_systems: Dict[UUID, Any] = {}

def get_memory_system(agent_id: UUID):
    if agent_id not in memory_systems:
        from app.core.memory.memory_system import MemorySystem
        memory_systems[agent_id] = MemorySystem(agent_id)
    return memory_systems[agent_id]
