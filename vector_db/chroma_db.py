import chromadb
from chromadb.config import Settings
from utils.config import settings
from utils.logger import app_logger
from typing import List, Dict, Any

class ChromaDBClient:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIRECTORY)
        app_logger.info(f"ChromaDB initialized at {settings.CHROMA_PERSIST_DIRECTORY}")

    def get_or_create_collection(self, name: str):
        return self.client.get_or_create_collection(name=name)

    def add_documents(self, collection_name: str, ids: List[str], embeddings: List[List[float]], metadatas: List[Dict[str, Any]], documents: List[str]):
        collection = self.get_or_create_collection(collection_name)
        collection.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=documents
        )

    def query(self, collection_name: str, query_embeddings: List[List[float]], n_results: int = 5):
        collection = self.get_or_create_collection(collection_name)
        return collection.query(
            query_embeddings=query_embeddings,
            n_results=n_results
        )

    def delete_collection(self, name: str):
        self.client.delete_collection(name=name)

    def list_collections(self):
        return self.client.list_collections()

    def get_collection_count(self, name: str):
        collection = self.get_or_create_collection(name)
        return collection.count()
    
    def get_all_data(self, collection_name: str):
        collection = self.get_or_create_collection(collection_name)
        return collection.get()

    def delete_by_metadata(self, collection_name: str, where: Dict[str, Any]):
        collection = self.get_or_create_collection(collection_name)
        collection.delete(where=where)
