from typing import List
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings
from utils.config import settings
from utils.logger import app_logger

class EmbeddingService:
    def __init__(self, model_name: str = None, use_openai: bool = False):
        self.model_name = model_name or settings.DEFAULT_EMBEDDING_MODEL
        self.use_openai = use_openai
        
        if self.use_openai:
            if not settings.OPENAI_API_KEY:
                app_logger.error("OpenAI API Key not found in settings.")
                raise ValueError("OpenAI API Key is required for OpenAI embeddings.")
            self.embeddings = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)
        else:
            app_logger.info(f"Loading HuggingFace model: {self.model_name}")
            self.embeddings = HuggingFaceEmbeddings(model_name=self.model_name)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self.embeddings.embed_documents(texts)

    def embed_query(self, text: str) -> List[float]:
        return self.embeddings.embed_query(text)
