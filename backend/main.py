from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from typing import List, Optional
import os
import shutil
import time
import uuid

from backend.document_loader import DocumentLoader
from backend.chunker import Chunker
from backend.embedding_service import EmbeddingService
from backend.vector_service import VectorService
from utils.logger import app_logger
from utils.config import settings

app = FastAPI(title=settings.APP_NAME)

@app.post("/process-document")
async def process_document(
    file: UploadFile = File(...),
    db_type: str = Form("chroma"),
    embedding_model: str = Form("sentence-transformers/all-MiniLM-L6-v2"),
    chunk_size: int = Form(500),
    chunk_overlap: int = Form(100),
    collection_name: str = Form("default_collection")
):
    start_time = time.time()
    
    # Create temp directory
    temp_dir = "temp"
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, file.filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 1. Load Document
        app_logger.info(f"Loading document: {file.filename}")
        text = DocumentLoader.load_document(file_path)
        if not text:
            raise HTTPException(status_code=400, detail="Could not extract text from document.")
        
        # 2. Chunk Text
        app_logger.info("Chunking text")
        chunker = Chunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        chunks = chunker.chunk_text(text)
        
        # 3. Generate Embeddings
        app_logger.info(f"Generating embeddings using {embedding_model}")
        use_openai = "openai" in embedding_model.lower()
        embed_service = EmbeddingService(model_name=embedding_model, use_openai=use_openai)
        embeddings = embed_service.embed_documents(chunks)
        
        # 4. Store in Vector DB
        app_logger.info(f"Storing in {db_type}")
        vector_service = VectorService(db_type=db_type)
        
        ids = [str(uuid.uuid4()) for _ in range(len(chunks))]
        metadatas = [{"source": file.filename, "chunk_index": i, "timestamp": time.time()} for i in range(len(chunks))]
        
        vector_service.add_documents(
            collection_name=collection_name,
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=chunks
        )
        
        processing_time = time.time() - start_time
        
        return {
            "status": "success",
            "document_name": file.filename,
            "chunks_created": len(chunks),
            "processing_time": f"{processing_time:.2f}s",
            "db_type": db_type
        }
    
    except Exception as e:
        app_logger.error(f"Error processing document: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

@app.get("/search")
async def search(
    query: str,
    db_type: str = "chroma",
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
    collection_name: str = "default_collection",
    top_k: int = 5
):
    try:
        use_openai = "openai" in embedding_model.lower()
        embed_service = EmbeddingService(model_name=embedding_model, use_openai=use_openai)
        query_embedding = embed_service.embed_query(query)
        
        vector_service = VectorService(db_type=db_type)
        results = vector_service.search(collection_name, query_embedding, n_results=top_k)
        
        return results
    except Exception as e:
        app_logger.error(f"Error searching: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/list-collections")
async def list_collections(db_type: str = "chroma"):
    vector_service = VectorService(db_type=db_type)
    # This varies by DB, simplified here
    return {"collections": ["default_collection"]}

@app.get("/collection-data")
async def get_collection_data(db_type: str = "chroma", collection_name: str = "default_collection"):
    vector_service = VectorService(db_type=db_type)
    return vector_service.list_documents(collection_name)

@app.delete("/document")
async def delete_document(db_type: str, collection_name: str, doc_name: str):
    vector_service = VectorService(db_type=db_type)
    vector_service.delete_document(collection_name, doc_name)
    return {"status": "deleted", "document": doc_name}

@app.delete("/collection")
async def delete_collection(db_type: str, collection_name: str):
    vector_service = VectorService(db_type=db_type)
    vector_service.delete_collection(collection_name)
    return {"status": "deleted", "collection": collection_name}

def start():
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=False)

if __name__ == "__main__":
    start()
