import asyncio
from typing import Dict, Any, List
from datetime import datetime
from chromadb import PersistentClient
from chromadb.config import Settings as ChromaDBSettings
from app.utils.logging import memory_logger
from app.api.models.memory import AdvancedSearchQuery, MemoryEntry, MemoryContext
from app.config import settings as app_settings

class VectorMemory:
    def __init__(self, collection_name: str):
        chroma_db_settings = ChromaDBSettings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=app_settings.CHROMA_PERSIST_DIRECTORY
        )
        self.client = PersistentClient(path=chroma_db_settings.persist_directory)
        self.collection = self.client.get_or_create_collection(collection_name)
        memory_logger.info(f"ChromaDB collection initialized: {collection_name}")

    async def add(self, id: str, memory_entry: MemoryEntry):
        metadata = {
            **memory_entry.metadata,
            "context_type": memory_entry.context.context_type,
            "context_timestamp": memory_entry.context.timestamp.isoformat(),
            **memory_entry.context.metadata
        }
        await asyncio.to_thread(
            self.collection.add,
            documents=[memory_entry.content],
            metadatas=[metadata],
            ids=[id]
        )
        memory_logger.debug(f"Added document to ChromaDB: {id}")

    async def search(self, query: AdvancedSearchQuery) -> List[Dict[str, Any]]:
        where_clause = {}
        if query.context_type:
            where_clause["context_type"] = query.context_type
        if query.time_range:
            where_clause["context_timestamp"] = {
                "$gte": query.time_range['start'].isoformat(),
                "$lte": query.time_range['end'].isoformat()
            }
        if query.metadata_filters:
            where_clause.update(query.metadata_filters)

        results = await asyncio.to_thread(
            self.collection.query,
            query_texts=[query.query],
            n_results=query.max_results,
            where=where_clause
        )
        memory_logger.debug(f"Searched ChromaDB: {query.query}")

        processed_results = []
        for id, doc, meta, distance in zip(
            results['ids'][0],
            results['documents'][0],
            results['metadatas'][0],
            results['distances'][0]
        ):
            context = MemoryContext(
                context_type=meta.pop('context_type'),
                timestamp=datetime.fromisoformat(meta.pop('context_timestamp')),
                metadata={k: v for k, v in meta.items() if k not in memory_entry.metadata}
            )
            memory_entry = MemoryEntry(
                content=doc,
                metadata={k: v for k, v in meta.items() if k in memory_entry.metadata},
                context=context
            )
            relevance_score = 1 - (distance / max(results['distances'][0]))  # Normalize distance to a 0-1 score
            processed_results.append({
                "id": id,
                "memory_entry": memory_entry,
                "relevance_score": relevance_score
            })

        if query.relevance_threshold is not None:
            processed_results = [r for r in processed_results if r['relevance_score'] >= query.relevance_threshold]

        return processed_results
