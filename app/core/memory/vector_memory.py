import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from uuid import UUID, uuid4
import uuid
from chromadb import PersistentClient
from chromadb.config import Settings as ChromaDBSettings
from chromadb.utils import embedding_functions

from app.utils.logging import memory_logger
from app.config import settings as app_settings
from app.api.models.memory import AdvancedSearchQuery, MemoryEntry, MemoryContext


class VectorMemory:
    """
    Handles long-term memory operations using ChromaDB for vector storage.
    """

    def __init__(self, collection_name: str):
        """
        Initialize VectorMemory with a ChromaDB collection.

        Args:
            collection_name (str): The name of the ChromaDB collection to use.
        """
        chroma_db_settings = ChromaDBSettings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=app_settings.CHROMA_PERSIST_DIRECTORY,
        )
        self.client = PersistentClient(path=chroma_db_settings.persist_directory)
        self.embedding_function = (
            embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2"
            )
        )
        self.collection = self.client.get_or_create_collection(
            name=collection_name, embedding_function=self.embedding_function
        )
        memory_logger.info(f"ChromaDB collection initialized: {collection_name}")

    async def add(self, memory_entry: MemoryEntry) -> str:
        """
        Add a memory entry to the vector store.

        Args:
            memory_entry (MemoryEntry): The memory entry to add.

        Returns:
            str: The ID of the added memory entry.

        Raises:
            Exception: If there's an error adding the memory entry.
        """
        try:
            memory_id = str(uuid.uuid4())
            metadata = {
                **memory_entry.metadata,
                "context_type": memory_entry.context.context_type,
                "context_timestamp": memory_entry.context.timestamp.isoformat(),
                **memory_entry.context.metadata,
            }
            await asyncio.to_thread(
                self.collection.add,
                documents=[memory_entry.content],
                metadatas=[metadata],
                ids=[memory_id],
            )
            memory_logger.debug(f"Added document to ChromaDB: {memory_id}")
            return memory_id
        except Exception as e:
            memory_logger.error(f"Error adding memory to ChromaDB: {str(e)}")
            raise

    async def get(self, memory_id: str) -> Optional[MemoryEntry]:
        """
        Retrieve a specific memory entry from the vector store.

        Args:
            memory_id (str): The ID of the memory entry to retrieve.

        Returns:
            Optional[MemoryEntry]: The retrieved memory entry, or None if not found.

        Raises:
            Exception: If there's an error retrieving the memory entry.
        """
        try:
            result = await asyncio.to_thread(self.collection.get, ids=[memory_id])
            if result["ids"]:
                metadata = result["metadatas"][0]
                context = MemoryContext(
                    context_type=metadata.pop("context_type"),
                    timestamp=datetime.fromisoformat(metadata.pop("context_timestamp")),
                    metadata={
                        k: v
                        for k, v in metadata.items()
                        if k not in result["metadatas"][0]
                    },
                )
                return MemoryEntry(
                    content=result["documents"][0],
                    metadata={
                        k: v for k, v in metadata.items() if k in result["metadatas"][0]
                    },
                    context=context,
                )
            return None
        except Exception as e:
            memory_logger.error(f"Error retrieving memory from ChromaDB: {str(e)}")
            raise

    async def search(self, query: AdvancedSearchQuery) -> List[Dict[str, Any]]:
        """
        Search for memories in the vector store based on the given query.

        Args:
            query (AdvancedSearchQuery): The search query parameters.

        Returns:
            List[Dict[str, Any]]: A list of search results.

        Raises:
            Exception: If there's an error searching for memories.
        """
        try:
            where_clause = {}
            if query.context_type:
                where_clause["context_type"] = query.context_type
            if query.time_range:
                where_clause["context_timestamp"] = {
                    "$gte": query.time_range["start"].isoformat(),
                    "$lte": query.time_range["end"].isoformat(),
                }
            if query.metadata_filters:
                where_clause.update(query.metadata_filters)

            results = await asyncio.to_thread(
                self.collection.query,
                query_texts=[query.query],
                n_results=query.max_results,
                where=where_clause if where_clause else None,
            )
            memory_logger.debug(f"Searched ChromaDB: {query.query}")

            processed_results = []
            for id, doc, meta, distance in zip(
                results["ids"][0],
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0],
            ):
                context = MemoryContext(
                    context_type=meta.pop("context_type"),
                    timestamp=datetime.fromisoformat(meta.pop("context_timestamp")),
                    metadata={k: v for k, v in meta.items() if k not in meta},
                )
                memory_entry = MemoryEntry(
                    content=doc,
                    metadata={k: v for k, v in meta.items() if k in meta},
                    context=context,
                )
                relevance_score = 1 - (
                    distance / max(results["distances"][0])
                )  # Normalize distance to a 0-1 score
                processed_results.append(
                    {
                        "id": id,
                        "memory_entry": memory_entry,
                        "relevance_score": relevance_score,
                    }
                )

            if query.relevance_threshold is not None:
                processed_results = [
                    r
                    for r in processed_results
                    if r["relevance_score"] >= query.relevance_threshold
                ]

            return processed_results
        except Exception as e:
            memory_logger.error(f"Error searching memories in ChromaDB: {str(e)}")
            raise

    async def delete(self, memory_id: str):
        """
        Delete a memory entry from the vector store.

        Args:
            memory_id (str): The ID of the memory entry to delete.

        Raises:
            Exception: If there's an error deleting the memory entry.
        """
        try:
            await asyncio.to_thread(self.collection.delete, ids=[memory_id])
            memory_logger.debug(f"Deleted document from ChromaDB: {memory_id}")
        except Exception as e:
            memory_logger.error(f"Error deleting memory from ChromaDB: {str(e)}")
            raise

    async def get_memories_older_than(self, threshold: datetime) -> List[MemoryEntry]:
        """
        Retrieve memory entries older than the given threshold.

        Args:
            threshold (datetime): The threshold datetime.

        Returns:
            List[MemoryEntry]: A list of memory entries older than the threshold.

        Raises:
            Exception: If there's an error retrieving old memories.
        """
        try:
            where_clause = {"context_timestamp": {"$lt": threshold.isoformat()}}
            results = await asyncio.to_thread(self.collection.get, where=where_clause)

            old_memories = []
            for doc, meta in zip(results["documents"], results["metadatas"]):
                context = MemoryContext(
                    context_type=meta.pop("context_type"),
                    timestamp=datetime.fromisoformat(meta.pop("context_timestamp")),
                    metadata={k: v for k, v in meta.items() if k not in meta},
                )
                memory_entry = MemoryEntry(
                    content=doc,
                    metadata={k: v for k, v in meta.items() if k in meta},
                    context=context,
                )
                old_memories.append(memory_entry)

            memory_logger.info(
                f"Retrieved {len(old_memories)} memories older than {threshold}"
            )
            return old_memories
        except Exception as e:
            memory_logger.error(f"Error getting old memories from ChromaDB: {str(e)}")
            raise

    async def close(self):
        """
        Close the ChromaDB client connection.

        Raises:
            Exception: If there's an error closing the connection.
        """
        try:
            await asyncio.to_thread(self.client.close)
            memory_logger.info("ChromaDB client connection closed")
        except Exception as e:
            memory_logger.error(f"Error closing ChromaDB client connection: {str(e)}")
            raise
