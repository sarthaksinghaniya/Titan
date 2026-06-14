import os
from typing import List, Dict, Any, Optional

import structlog
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_qdrant import QdrantVectorStore
from langchain_pinecone import PineconeVectorStore
from qdrant_client import QdrantClient
from pinecone import Pinecone

from app.core.config import settings

logger = structlog.get_logger(__name__)

class VectorStoreManager:
    """
    Manages connections to Vector Databases (Chroma, Qdrant, Pinecone).
    Handles long-term memory insertion and semantic retrieval.
    """
    
    def __init__(self, collection_name: str = "titan_memory"):
        self.collection_name = collection_name
        self.provider = settings.VECTOR_STORE_PROVIDER.lower()
        self.embeddings = self._get_embeddings()
        self.vector_store = self._init_vector_store()
        
    def _get_embeddings(self) -> Embeddings:
        """Fallback embedding logic: Try OpenAI, else Gemini."""
        if settings.OPENAI_API_KEY:
            try:
                return OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY)
            except Exception as e:
                logger.warning("OpenAI Embeddings failed, falling back to Gemini", error=str(e))
                
        return GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=settings.GEMINI_API_KEY
        )

    def _init_vector_store(self) -> Any:
        """Initializes the configured vector store."""
        try:
            if self.provider == "qdrant" and settings.QDRANT_URL and settings.QDRANT_API_KEY:
                client = QdrantClient(
                    url=settings.QDRANT_URL,
                    api_key=settings.QDRANT_API_KEY
                )
                return QdrantVectorStore(
                    client=client,
                    collection_name=self.collection_name,
                    embedding=self.embeddings
                )
                
            elif self.provider == "pinecone" and settings.PINECONE_API_KEY:
                pc = Pinecone(api_key=settings.PINECONE_API_KEY)
                return PineconeVectorStore(
                    index_name=settings.PINECONE_INDEX_NAME,
                    embedding=self.embeddings,
                    namespace=self.collection_name
                )
                
            else:
                # Default to Chroma (local SQLite)
                os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)
                return Chroma(
                    collection_name=self.collection_name,
                    embedding_function=self.embeddings,
                    persist_directory=settings.CHROMA_PERSIST_DIR
                )
        except Exception as e:
            logger.error("Failed to initialize requested vector store, falling back to Chroma", provider=self.provider, error=str(e))
            os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)
            return Chroma(
                collection_name=self.collection_name,
                embedding_function=self.embeddings,
                persist_directory=settings.CHROMA_PERSIST_DIR
            )

    def add_memory(self, problem: str, resolution: str, metadata: Dict[str, Any]):
        """Adds a finalized policy or session outcome to long-term memory."""
        doc = Document(
            page_content=f"PROBLEM: {problem}\n\nRESOLUTION: {resolution}",
            metadata=metadata
        )
        try:
            self.vector_store.add_documents([doc])
            logger.info("Memory archived", metadata=metadata)
        except Exception as e:
            logger.error("Failed to archive memory", error=str(e))

    def search_precedents(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Searches past sessions for precedents matching the current problem."""
        try:
            results = self.vector_store.similarity_search_with_score(query, k=top_k)
            precedents = []
            for doc, score in results:
                precedents.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "relevance_score": score
                })
            return precedents
        except Exception as e:
            logger.error("Semantic search failed", error=str(e))
            return []

# Singleton instance
vector_store_manager = VectorStoreManager()
