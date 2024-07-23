import asyncio
from typing import Dict, Any, List
import chromadb
from chromadb.config import Settings
from app.utils.logging import memory_logger
from app.config import settings as app_settings

class VectorMemory:
    def __init__(self, collection_name: str):
        try:
            self.client = chromadb.Client(Settings(persist_directory=app_settings.chroma_persist_directory))
            self.collection = self.client.get_or_create_collection(collection_name)
            memory_logger.info(f"ChromaDB collection initialized: {collection_name}")
        except Exception as e:
            memory_logger.error(f"Failed to initialize ChromaDB: {str(e)}")
            raise

    async def add(self, id: str, content: str, metadata: Dict[str, Any] = {}):
        try:
            await asyncio.to_thread(self.collection.add,
                                    documents=[content],
                                    metadatas=[metadata],
                                    ids=[id])
            memory_logger.debug(f"Added document to ChromaDB: {id}")
        except Exception as e:
            memory_logger.error(f"Failed to add document to ChromaDB: {id}. Error: {str(e)}")
            raise

    async def search(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        try:
            results = await asyncio.to_thread(self.collection.query,
                                              query_texts=[query],
                                              n_results=n_results)
            memory_logger.debug(f"Searched ChromaDB: {query}")
            return [{"id": id, "content": doc, "metadata": meta}
                    for id, doc, meta in zip(results['ids'][0], results['documents'][0], results['metadatas'][0])]
        except Exception as e:
            memory_logger.error(f"Failed to search ChromaDB: {query}. Error: {str(e)}")
            raise