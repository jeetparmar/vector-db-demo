from qdrant_client import QdrantClient
from qdrant_client.http import models
from utils.config import settings
from utils.logger import app_logger
from typing import List, Dict, Any
import uuid

class QdrantDBClient:
    def __init__(self):
        # Prefer remote connection if host is set, otherwise use local path
        if os.getenv("QDRANT_HOST"):
            self.client = QdrantClient(
                host=os.getenv("QDRANT_HOST", "localhost"),
                port=int(os.getenv("QDRANT_PORT", 6333))
            )
            app_logger.info(f"QdrantDB initialized (Remote) at {os.getenv('QDRANT_HOST')}")
        else:
            self.client = QdrantClient(path=settings.QDRANT_PATH)
            app_logger.info(f"QdrantDB initialized (Local) at {settings.QDRANT_PATH}")

    def create_collection(self, name: str, vector_size: int):
        if not self.client.collection_exists(name):
            self.client.create_collection(
                collection_name=name,
                vectors_config=models.VectorParams(size=vector_size, distance=models.Distance.COSINE),
            )

    def add_documents(self, collection_name: str, ids: List[str], embeddings: List[List[float]], metadatas: List[Dict[str, Any]], documents: List[str]):
        # Ensure collection exists (assume vector size from first embedding)
        if embeddings:
            self.create_collection(collection_name, len(embeddings[0]))
        
        points = [
            models.PointStruct(
                id=str(uuid.uuid4()), # Qdrant prefers UUIDs or ints
                vector=emb,
                payload={**meta, "page_content": doc}
            )
            for emb, meta, doc in zip(embeddings, metadatas, documents)
        ]
        
        self.client.upsert(
            collection_name=collection_name,
            points=points
        )

    def query(self, collection_name: str, query_embedding: List[float], n_results: int = 5):
        return self.client.search(
            collection_name=collection_name,
            query_vector=query_embedding,
            limit=n_results
        )

    def delete_collection(self, name: str):
        self.client.delete_collection(name=name)

    def get_collection_count(self, name: str):
        if not self.client.collection_exists(name):
            return 0
        return self.client.get_collection(name).points_count

    def get_all_data(self, collection_name: str):
        if not self.client.collection_exists(collection_name):
            return {"ids": [], "metadatas": [], "documents": []}
        
        # Scroll through all points
        results, _ = self.client.scroll(
            collection_name=collection_name,
            with_payload=True,
            with_vectors=True,
            limit=10000
        )
        
        return {
            "ids": [str(r.id) for r in results],
            "metadatas": [r.payload for r in results],
            "documents": [r.payload.get("page_content", "") for r in results],
            "vectors": [r.vector for r in results]
        }

    def delete_by_metadata(self, collection_name: str, key: str, value: Any):
        self.client.delete(
            collection_name=collection_name,
            points_selector=models.FilterSelector(
                filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key=key,
                            match=models.MatchValue(value=value),
                        )
                    ]
                )
            ),
        )
