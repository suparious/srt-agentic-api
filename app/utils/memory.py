from typing import Dict
from uuid import UUID
from app.core.memory.memory_system import MemorySystem

memory_systems: Dict[UUID, MemorySystem] = {}

def get_memory_system(agent_id: UUID) -> MemorySystem:
    if agent_id not in memory_systems:
        memory_systems[agent_id] = MemorySystem(agent_id)
    return memory_systems[agent_id]
