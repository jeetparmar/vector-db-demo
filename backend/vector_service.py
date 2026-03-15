from typing import List, Dict, Any, Union
from vector_db.chroma_db import ChromaDBClient
from vector_db.qdrant_db import QdrantDBClient
from utils.logger import app_logger

class VectorService:
    def __init__(self, db_type: str = "chroma"):
        self.db_type = db_type.lower()
        if self.db_type == "chroma":
            self.client = ChromaDBClient()
        elif self.db_type == "qdrant":
            self.client = QdrantDBClient()
        else:
            raise ValueError(f"Unsupported database type: {db_type}")

    def add_documents(self, collection_name: str, ids: List[str], embeddings: List[List[float]], metadatas: List[Dict[str, Any]], documents: List[str]):
        self.client.add_documents(collection_name, ids, embeddings, metadatas, documents)

    def search(self, collection_name: str, query_embedding: List[float], n_results: int = 5):
        if self.db_type == "chroma":
            results = self.client.query(collection_name, [query_embedding], n_results)
            # Standardize output
            standardized = []
            for i in range(len(results["ids"][0])):
                standardized.append({
                    "id": results["ids"][0][i],
                    "score": results["distances"][0][i] if "distances" in results else 0,
                    "metadata": results["metadatas"][0][i],
                    "document": results["documents"][0][i]
                })
            return standardized
        elif self.db_type == "qdrant":
            results = self.client.query(collection_name, query_embedding, n_results)
            standardized = []
            for r in results:
                standardized.append({
                    "id": str(r.id),
                    "score": r.score,
                    "metadata": r.payload,
                    "document": r.payload.get("page_content", "")
                })
            return standardized

    def list_documents(self, collection_name: str):
        data = self.client.get_all_data(collection_name)
        # Groups by original document if possible, or just return chunks
        return data

    def delete_document(self, collection_name: str, doc_name: str):
        if self.db_type == "chroma":
            self.client.delete_by_metadata(collection_name, {"source": doc_name})
        elif self.db_type == "qdrant":
            self.client.delete_by_metadata(collection_name, "source", doc_name)

    def delete_collection(self, collection_name: str):
        self.client.delete_collection(collection_name)

    def get_stats(self, collection_name: str):
        return {
            "count": self.client.get_collection_count(collection_name),
            "db_type": self.db_type
        }
