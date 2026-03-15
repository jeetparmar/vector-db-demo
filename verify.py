import os
import sys

# Add current directory to path
sys.path.append(os.getcwd())

from backend.document_loader import DocumentLoader
from backend.chunker import Chunker
from backend.embedding_service import EmbeddingService
from backend.vector_service import VectorService

def test_pipeline():
    print("--- Starting Pipeline Verification ---")
    
    # 1. Load sample doc
    sample_raw = "Artificial Intelligence is fascinating. Vector databases help AI remember things."
    print("1. Text loaded.")
    
    # 2. Chunking
    chunker = Chunker(chunk_size=50, chunk_overlap=10)
    chunks = chunker.chunk_text(sample_raw)
    print(f"2. Chunks created: {len(chunks)}")
    
    # 3. Embedding (Use Mock or local HF)
    print("3. Initializing Embedding Service (HF)...")
    embed_service = EmbeddingService()
    embeddings = embed_service.embed_documents(chunks)
    print(f"   Embeddings generated: {len(embeddings)} vectors of length {len(embeddings[0])}")
    
    # 4. Vector DB (Chroma)
    print("4. Testing ChromaDB Integration...")
    v_service = VectorService(db_type="chroma")
    v_service.add_documents(
        collection_name="test_col",
        ids=["id1", "id2"],
        embeddings=embeddings,
        metadatas=[{"source": "test"}, {"source": "test"}],
        documents=chunks
    )
    print("   Documents added to Chroma.")
    
    # 5. Search
    query = "What is fascinating?"
    query_emb = embed_service.embed_query(query)
    results = v_service.search("test_col", query_emb, n_results=1)
    print(f"5. Search Result: {results[0]['document']} (Score: {results[0]['score']})")
    
    print("--- Verification Complete ---")

if __name__ == "__main__":
    test_pipeline()
