import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "Vector DB Demo"
    DEBUG: bool = True
    
    # Vector DB Settings
    CHROMA_PERSIST_DIRECTORY: str = "data/chroma"
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_PATH: str = "data/qdrant" # For local storage
    
    # Embedding Settings
    DEFAULT_EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Document Settings
    DEFAULT_CHUNK_SIZE: int = 500
    DEFAULT_CHUNK_OVERLAP: int = 100

    class Config:
        env_file = ".env"

settings = Settings()
