from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
from uuid import UUID
from app.api.models.memory import MemoryEntry, AdvancedSearchQuery

class MemorySystemInterface(ABC):
    @abstractmethod
    async def initialize(self) -> None:
        pass

    @abstractmethod
    async def close(self) -> None:
        pass

    @abstractmethod
    async def add(self, memory_entry: MemoryEntry) -> str:
        pass

    @abstractmethod
    async def get(self, memory_id: str) -> Optional[MemoryEntry]:
        pass

    @abstractmethod
    async def search(self, query: AdvancedSearchQuery) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def delete(self, memory_id: str) -> None:
        pass

    @abstractmethod
    async def get_recent(self, limit: int) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def get_memories_older_than(self, threshold: datetime) -> List[MemoryEntry]:
        pass
