import asyncio
from typing import Dict, Any, List
from chromadb import PersistentClient
from chromadb.config import Settings as ChromaDBSettings
from app.utils.logging import memory_logger

class VectorMemory:
    def __init__(self, collection_name: str, chroma_db_settings: ChromaDBSettings):
        self.client = PersistentClient(path=chroma_db_settings.persist_directory)
        self.collection = self.client.get_or_create_collection(collection_name)
        memory_logger.info(f"ChromaDB collection initialized: {collection_name}")

    async def add(self, id: str, content: str, metadata: Dict[str, Any] = {}):
        await asyncio.to_thread(self.collection.add,
                                documents=[content],
                                metadatas=[metadata],
                                ids=[id])
        memory_logger.debug(f"Added document to ChromaDB: {id}")

    async def search(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        results = await asyncio.to_thread(self.collection.query,
                                          query_texts=[query],
                                          n_results=n_results)
        memory_logger.debug(f"Searched ChromaDB: {query}")
        return [{"id": id, "content": doc, "metadata": meta}
                for id, doc, meta in zip(results['ids'][0], results['documents'][0], results['metadatas'][0])]
