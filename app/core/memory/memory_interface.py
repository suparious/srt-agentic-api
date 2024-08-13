from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
from uuid import UUID
from app.api.models.memory import MemoryEntry, AdvancedSearchQuery

class MemorySystemInterface(ABC):
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the memory system."""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close the memory system."""
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        """Perform cleanup operations on the memory system."""
        pass

    @abstractmethod
    async def add(self, memory_entry: MemoryEntry) -> str:
        """Add a memory entry to the system."""
        pass

    @abstractmethod
    async def get(self, memory_id: str) -> Optional[MemoryEntry]:
        """Retrieve a memory entry by its ID."""
        pass

    @abstractmethod
    async def search(self, query: AdvancedSearchQuery) -> List[Dict[str, Any]]:
        """Search for memory entries based on the given query."""
        pass

    @abstractmethod
    async def delete(self, memory_id: str) -> None:
        """Delete a memory entry by its ID."""
        pass

    @abstractmethod
    async def get_recent(self, limit: int) -> List[Dict[str, Any]]:
        """Get the most recent memory entries."""
        pass

    @abstractmethod
    async def get_memories_older_than(self, threshold: datetime) -> List[MemoryEntry]:
        """Get memory entries older than the given threshold."""
        pass
