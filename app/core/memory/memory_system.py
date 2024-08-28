import asyncio
import uuid
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from app.core.models import MemoryConfig
from app.core.models import MemoryEntry
from app.api.models.memory import (
    MemoryType,
    AdvancedSearchQuery,
    MemoryOperation,
)
from app.utils.logging import memory_logger
from .redis_memory import RedisMemory, RedisMemoryError
from .vector_memory import VectorMemory, VectorMemoryError

class MemorySystemError(Exception):
    """Base exception for MemorySystem errors."""
    pass

class MemorySystem:
    def __init__(
        self,
        agent_id: uuid.UUID,
        config: MemoryConfig,
        short_term: Optional[RedisMemory] = None,
        long_term: Optional[VectorMemory] = None,
    ):
        self.agent_id = agent_id
        self.config = config
        self.short_term = short_term or RedisMemory(agent_id)
        self.long_term = long_term or VectorMemory(f"agent_{agent_id}")
        self.consolidation_queue: List[MemoryEntry] = []
        memory_logger.info(f"MemorySystem initialized for agent: {agent_id}")

    async def initialize(self) -> None:
        try:
            await asyncio.gather(
                self.short_term.initialize(),
                self.long_term.initialize()
            )
            memory_logger.info(f"MemorySystem fully initialized for agent: {self.agent_id}")
        except (RedisMemoryError, VectorMemoryError) as e:
            memory_logger.error(f"Failed to initialize MemorySystem for agent {self.agent_id}: {str(e)}")
            raise MemorySystemError("Failed to initialize MemorySystem") from e

    async def close(self) -> None:
        try:
            await asyncio.gather(
                self.short_term.close(),
                self.long_term.close()
            )
            memory_logger.info(f"MemorySystem closed for agent: {self.agent_id}")
        except (RedisMemoryError, VectorMemoryError) as e:
            memory_logger.error(f"Error closing MemorySystem for agent {self.agent_id}: {str(e)}")
            raise MemorySystemError("Failed to close MemorySystem") from e

    async def add(
        self, memory_type: Union[MemoryType, str], memory_entry: MemoryEntry
    ) -> str:
        try:
            if (
                memory_type == MemoryType.SHORT_TERM or memory_type == "SHORT_TERM"
            ) and self.config.use_redis_cache:
                memory_id = await self.short_term.add(memory_entry)
                self.consolidation_queue.append(memory_entry)
                memory_logger.info(
                    f"Short-term memory added for agent: {self.agent_id}"
                )
                return memory_id
            elif (
                memory_type == MemoryType.LONG_TERM or memory_type == "LONG_TERM"
            ) and self.config.use_long_term_memory:
                memory_id = await self.long_term.add(memory_entry)
                memory_logger.info(f"Long-term memory added for agent: {self.agent_id}")
                return memory_id
            else:
                raise MemorySystemError(f"Invalid memory type or configuration: {memory_type}")
        except (RedisMemoryError, VectorMemoryError) as e:
            memory_logger.error(
                f"Failed to add {memory_type} memory for agent: {self.agent_id}. Error: {str(e)}"
            )
            raise MemorySystemError(f"Failed to add {memory_type} memory") from e

    async def retrieve(
        self, memory_type: Union[MemoryType, str], memory_id: str
    ) -> Optional[MemoryEntry]:
        try:
            if (
                memory_type == MemoryType.SHORT_TERM or memory_type == "SHORT_TERM"
            ) and self.config.use_redis_cache:
                return await self.short_term.get(memory_id)
            elif (
                memory_type == MemoryType.LONG_TERM or memory_type == "LONG_TERM"
            ) and self.config.use_long_term_memory:
                return await self.long_term.get(memory_id)
            else:
                raise MemorySystemError(f"Invalid memory type or configuration: {memory_type}")
        except (RedisMemoryError, VectorMemoryError) as e:
            memory_logger.error(
                f"Failed to retrieve {memory_type} memory for agent: {self.agent_id}. Error: {str(e)}"
            )
            raise MemorySystemError(f"Failed to retrieve {memory_type} memory") from e

    async def search(self, query: AdvancedSearchQuery) -> List[Dict[str, Any]]:
        try:
            results = []
            search_tasks = []

            if (
                query.memory_type in (None, MemoryType.SHORT_TERM, "SHORT_TERM")
                and self.config.use_redis_cache
            ):
                search_tasks.append(self.short_term.search(query))
            if (
                query.memory_type in (None, MemoryType.LONG_TERM, "LONG_TERM")
                and self.config.use_long_term_memory
            ):
                search_tasks.append(self.long_term.search(query))

            search_results = await asyncio.gather(*search_tasks, return_exceptions=True)
            for result in search_results:
                if isinstance(result, Exception):
                    memory_logger.error(f"Error during search: {str(result)}")
                else:
                    results.extend(result)

            sorted_results = sorted(
                results, key=lambda x: x["relevance_score"], reverse=True
            )
            return sorted_results[: query.max_results]
        except Exception as e:
            memory_logger.error(
                f"Failed to search memories for agent: {self.agent_id}. Error: {str(e)}"
            )
            raise MemorySystemError("Failed to search memories") from e

    async def delete(self, memory_type: Union[MemoryType, str], memory_id: str):
        try:
            if (
                memory_type == MemoryType.SHORT_TERM or memory_type == "SHORT_TERM"
            ) and self.config.use_redis_cache:
                await self.short_term.delete(memory_id)
                memory_logger.info(
                    f"Short-term memory deleted for agent: {self.agent_id}"
                )
            elif (
                memory_type == MemoryType.LONG_TERM or memory_type == "LONG_TERM"
            ) and self.config.use_long_term_memory:
                await self.long_term.delete(memory_id)
                memory_logger.info(
                    f"Long-term memory deleted for agent: {self.agent_id}"
                )
            else:
                raise MemorySystemError(f"Invalid memory type or configuration: {memory_type}")
        except (RedisMemoryError, VectorMemoryError) as e:
            memory_logger.error(
                f"Failed to delete {memory_type} memory for agent: {self.agent_id}. Error: {str(e)}"
            )
            raise MemorySystemError(f"Failed to delete {memory_type} memory") from e

    async def perform_operation(
        self,
        operation: Union[MemoryOperation, str],
        memory_type: Union[MemoryType, str],
        data: Dict[str, Any],
    ) -> Any:
        try:
            if operation == MemoryOperation.ADD or operation == "ADD":
                return await self.add(memory_type, MemoryEntry(**data))
            elif operation == MemoryOperation.RETRIEVE or operation == "RETRIEVE":
                return await self.retrieve(memory_type, data["memory_id"])
            elif operation == MemoryOperation.SEARCH or operation == "SEARCH":
                return await self.search(AdvancedSearchQuery(**data))
            elif operation == MemoryOperation.DELETE or operation == "DELETE":
                await self.delete(memory_type, data["memory_id"])
                return {"message": "Memory deleted successfully"}
            else:
                raise MemorySystemError(f"Invalid memory operation: {operation}")
        except Exception as e:
            memory_logger.error(
                f"Failed to perform {operation} operation for agent: {self.agent_id}. Error: {str(e)}"
            )
            raise MemorySystemError(f"Failed to perform {operation} operation") from e

    async def consolidate_memories(self):
        try:
            threshold = datetime.now() - timedelta(hours=1)  # Consolidate memories older than 1 hour
            old_memories = await self.short_term.get_memories_older_than(threshold)

            for memory in old_memories:
                await self.long_term.add(memory)
                await self.short_term.delete(memory.id)

            memory_logger.info(
                f"Consolidated {len(old_memories)} memories for agent: {self.agent_id}"
            )
        except (RedisMemoryError, VectorMemoryError) as e:
            memory_logger.error(
                f"Failed to consolidate memories for agent: {self.agent_id}. Error: {str(e)}"
            )
            raise MemorySystemError("Failed to consolidate memories") from e

    async def forget_old_memories(self, age_limit: timedelta):
        try:
            threshold = datetime.now() - age_limit
            old_memories = await self.long_term.get_memories_older_than(threshold)

            for memory in old_memories:
                await self.long_term.delete(memory.id)

            memory_logger.info(
                f"Forgot {len(old_memories)} old memories for agent: {self.agent_id}"
            )
        except VectorMemoryError as e:
            memory_logger.error(
                f"Failed to forget old memories for agent: {self.agent_id}. Error: {str(e)}"
            )
            raise MemorySystemError("Failed to forget old memories") from e

    @classmethod
    async def initialize_memory_systems(cls):
        # This method is called during startup
        # Implement any global initialization logic here if needed
        pass
