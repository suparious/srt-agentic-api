import uuid
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from app.api.models.agent import MemoryConfig
from app.api.models.memory import (
    MemoryType,
    MemoryEntry,
    AdvancedSearchQuery,
    MemoryOperation,
)
from app.utils.logging import memory_logger
from .redis_memory import RedisMemory
from .vector_memory import VectorMemory
from .memory_utils import (
    DEFAULT_CONSOLIDATION_INTERVAL,
    DEFAULT_FORGET_AGE,
    serialize_memory_entry,
    deserialize_memory_entry,
    calculate_relevance_score,
    should_consolidate_memory,
    should_forget_memory,
)


class MemorySystem:
    """
    Manages both short-term and long-term memory for an agent.

    This class coordinates between RedisMemory for short-term storage and
    VectorMemory for long-term storage based on the provided configuration.
    """

    def __init__(
        self,
        agent_id: uuid.UUID,
        config: MemoryConfig,
        short_term: Optional[RedisMemory] = None,
        long_term: Optional[VectorMemory] = None,
    ):
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
        self.consolidation_queue: List[MemoryEntry] = []
        memory_logger.info(f"MemorySystem initialized for agent: {agent_id}")

    async def add(
        self, memory_type: Union[MemoryType, str], memory_entry: MemoryEntry
    ) -> str:
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
                raise ValueError(f"Invalid memory type or configuration: {memory_type}")
        except Exception as e:
            memory_logger.error(
                f"Failed to add {memory_type} memory for agent: {self.agent_id}. Error: {str(e)}"
            )
            raise

    async def retrieve(
        self, memory_type: Union[MemoryType, str], memory_id: str
    ) -> Optional[MemoryEntry]:
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
            if (
                memory_type == MemoryType.SHORT_TERM or memory_type == "SHORT_TERM"
            ) and self.config.use_redis_cache:
                return await self.short_term.get(memory_id)
            elif (
                memory_type == MemoryType.LONG_TERM or memory_type == "LONG_TERM"
            ) and self.config.use_long_term_memory:
                return await self.long_term.get(memory_id)
            else:
                raise ValueError(f"Invalid memory type or configuration: {memory_type}")
        except Exception as e:
            memory_logger.error(
                f"Failed to retrieve {memory_type} memory for agent: {self.agent_id}. Error: {str(e)}"
            )
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
            if (
                query.memory_type in (None, MemoryType.SHORT_TERM, "SHORT_TERM")
                and self.config.use_redis_cache
            ):
                results.extend(await self.short_term.search(query))
            if (
                query.memory_type in (None, MemoryType.LONG_TERM, "LONG_TERM")
                and self.config.use_long_term_memory
            ):
                results.extend(await self.long_term.search(query))

            sorted_results = sorted(
                results, key=lambda x: x["relevance_score"], reverse=True
            )
            return sorted_results[: query.max_results]
        except Exception as e:
            memory_logger.error(
                f"Failed to search memories for agent: {self.agent_id}. Error: {str(e)}"
            )
            raise

    async def delete(self, memory_type: Union[MemoryType, str], memory_id: str):
        """
        Delete a memory entry from either short-term or long-term storage.

        Args:
            memory_type (MemoryType): The type of memory (SHORT_TERM or LONG_TERM).
            memory_id (str): The ID of the memory entry to delete.

        Raises:
            ValueError: If the memory type is invalid or not configured.
        """
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
                raise ValueError(f"Invalid memory type or configuration: {memory_type}")
        except Exception as e:
            memory_logger.error(
                f"Failed to delete {memory_type} memory for agent: {self.agent_id}. Error: {str(e)}"
            )
            raise

    async def perform_operation(
        self,
        operation: Union[MemoryOperation, str],
        memory_type: Union[MemoryType, str],
        data: Dict[str, Any],
    ) -> Any:
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
                raise ValueError(f"Invalid memory operation: {operation}")
        except Exception as e:
            memory_logger.error(
                f"Failed to perform {operation} operation for agent: {self.agent_id}. Error: {str(e)}"
            )
            raise

    async def retrieve_relevant(
        self, context: str, limit: int = 5
    ) -> List[Dict[str, Any]]:
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
                long_term_results = await self.long_term.search(
                    AdvancedSearchQuery(query=context, max_results=limit)
                )
                relevant_memories.extend(long_term_results)

            relevant_memories.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
            return relevant_memories[:limit]
        except Exception as e:
            memory_logger.error(
                f"Error retrieving relevant memories for agent {self.agent_id}: {str(e)}"
            )
            raise

    async def consolidate_memories(self):
        """
        Consolidate short-term memories into long-term storage.
        """
        try:
            threshold = datetime.now() - timedelta(hours=1)  # Consolidate memories older than 1 hour
            old_memories = await self.short_term.get_memories_older_than(threshold)

            for memory in old_memories:
                await self.long_term.add(memory)
                await self.short_term.delete(memory.id)

            memory_logger.info(
                f"Consolidated {len(old_memories)} memories for agent: {self.agent_id}"
            )
        except Exception as e:
            memory_logger.error(
                f"Failed to consolidate memories for agent: {self.agent_id}. Error: {str(e)}"
            )

    async def forget_old_memories(self, age_limit: timedelta):
        """
        Forget (delete) old memories from long-term storage.

        Args:
            age_limit (timedelta): The age limit for memories to be forgotten.
        """
        try:
            threshold = datetime.now() - age_limit
            old_memories = await self.long_term.get_memories_older_than(threshold)

            for memory in old_memories:
                await self.long_term.delete(memory.id)

            memory_logger.info(
                f"Forgot {len(old_memories)} old memories for agent: {self.agent_id}"
            )
        except Exception as e:
            memory_logger.error(
                f"Failed to forget old memories for agent: {self.agent_id}. Error: {str(e)}"
            )

    async def close(self):
        """
        Close connections and perform cleanup for the memory system.
        """
        try:
            await self.short_term.close()
            await self.long_term.close()
            memory_logger.info(f"MemorySystem closed for agent: {self.agent_id}")
        except Exception as e:
            memory_logger.error(
                f"Error closing MemorySystem for agent {self.agent_id}: {str(e)}"
            )
            raise
