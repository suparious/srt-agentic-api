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
from app.core.memory.memory_interface import MemorySystemInterface


class VectorMemoryError(Exception):
    """Custom exception for Vector memory operations."""
    pass


class VectorMemory(MemorySystemInterface):
    def __init__(self, collection_name: str):
        self.collection_name = collection_name
        self.client = None
        self.collection = None
        self.embedding_function = None

    async def initialize(self) -> None:
        try:
            chroma_db_settings = ChromaDBSettings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=app_settings.CHROMA_PERSIST_DIRECTORY,
            )
            self.client = PersistentClient(path=chroma_db_settings.persist_directory)
            self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
            self.collection = self.client.get_or_create_collection(name=self.collection_name, embedding_function=self.embedding_function)
            memory_logger.info(f"ChromaDB collection initialized: {self.collection_name}")
        except Exception as e:
            memory_logger.error(f"Failed to initialize VectorMemory: {str(e)}")
            raise VectorMemoryError("Failed to initialize VectorMemory") from e

    async def close(self) -> None:
        try:
            await asyncio.to_thread(self.client.close)
            memory_logger.info("ChromaDB client connection closed")
        except Exception as e:
            memory_logger.error(f"Error closing ChromaDB client connection: {str(e)}")
            raise VectorMemoryError("Failed to close VectorMemory") from e

    async def cleanup(self) -> None:
        try:
            await asyncio.to_thread(self.collection.delete)
            self.collection = self.client.get_or_create_collection(name=self.collection_name, embedding_function=self.embedding_function)
            memory_logger.info(f"VectorMemory cleanup completed for collection: {self.collection_name}")
        except Exception as e:
            memory_logger.error(f"Error during VectorMemory cleanup: {str(e)}")
            raise VectorMemoryError("Failed to cleanup VectorMemory") from e

    async def add(self, memory_entry: MemoryEntry) -> str:
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
            raise VectorMemoryError("Failed to add memory") from e

    async def get(self, memory_id: str) -> Optional[MemoryEntry]:
        try:
            result = await asyncio.to_thread(self.collection.get, ids=[memory_id])
            if result["ids"]:
                metadata = result["metadatas"][0]
                context = MemoryContext(
                    context_type=metadata.pop("context_type"),
                    timestamp=datetime.fromisoformat(metadata.pop("context_timestamp")),
                    metadata={k: v for k, v in metadata.items() if k not in result["metadatas"][0]}
                )
                return MemoryEntry(
                    content=result["documents"][0],
                    metadata={k: v for k, v in metadata.items() if k in result["metadatas"][0]},
                    context=context
                )
            return None
        except Exception as e:
            memory_logger.error(f"Error retrieving memory from ChromaDB: {str(e)}")
            raise VectorMemoryError("Failed to retrieve memory") from e

    async def search(self, query: AdvancedSearchQuery) -> List[Dict[str, Any]]:
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
                relevance_score = 1 - (distance / max(results["distances"][0]))  # Normalize distance to a 0-1 score
                processed_results.append(
                    {
                        "id": id,
                        "memory_entry": memory_entry,
                        "relevance_score": relevance_score,
                    }
                )

            if query.relevance_threshold is not None:
                processed_results = [r for r in processed_results if r["relevance_score"] >= query.relevance_threshold]

            return processed_results
        except Exception as e:
            memory_logger.error(f"Error searching memories in ChromaDB: {str(e)}")
            raise VectorMemoryError("Failed to search memories") from e

    async def delete(self, memory_id: str) -> None:
        try:
            await asyncio.to_thread(self.collection.delete, ids=[memory_id])
            memory_logger.debug(f"Deleted document from ChromaDB: {memory_id}")
        except Exception as e:
            memory_logger.error(f"Error deleting memory from ChromaDB: {str(e)}")
            raise VectorMemoryError("Failed to delete memory") from e

    async def get_recent(self, limit: int) -> List[Dict[str, Any]]:
        try:
            results = await asyncio.to_thread(
                self.collection.query,
                query_texts=[""],
                n_results=limit,
                where={},
            )
            memory_logger.debug(f"Retrieved {len(results['ids'][0])} recent memories from ChromaDB")

            processed_results = []
            for id, doc, meta in zip(results["ids"][0], results["documents"][0], results["metadatas"][0]):
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
                processed_results.append({
                    "id": id,
                    "memory_entry": memory_entry,
                })

            return sorted(processed_results, key=lambda x: x["memory_entry"].context.timestamp, reverse=True)
        except Exception as e:
            memory_logger.error(f"Error retrieving recent memories from ChromaDB: {str(e)}")
            raise VectorMemoryError("Failed to retrieve recent memories") from e

    async def get_memories_older_than(self, threshold: datetime) -> List[MemoryEntry]:
        try:
            results = await asyncio.to_thread(
                self.collection.query,
                query_texts=[""],
                n_results=None,  # Retrieve all matching results
                where={"context_timestamp": {"$lt": threshold.isoformat()}},
            )
            memory_logger.debug(f"Retrieved {len(results['ids'][0])} old memories from ChromaDB")

            old_memories = []
            for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
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

            return old_memories
        except Exception as e:
            memory_logger.error(f"Error retrieving old memories from ChromaDB: {str(e)}")
            raise VectorMemoryError("Failed to retrieve old memories") from e
