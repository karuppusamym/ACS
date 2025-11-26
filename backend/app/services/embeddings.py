from typing import List, Dict, Any, Optional
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from sqlalchemy.orm import Session
from sqlalchemy import text
import json
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

class EmbeddingService:
    """
    Service for generating and managing document embeddings using OpenAI and pgvector
    """
    
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            api_key=settings.OPENAI_API_KEY,
            model="text-embedding-3-small"
        )
        
    async def create_embeddings(self, text_content: str, metadata: Dict[str, Any]) -> List[float]:
        """
        Create embeddings for a text
        """
        try:
            return await self.embeddings.aembed_query(text_content)
        except Exception as e:
            logger.error(f"Error creating embeddings: {str(e)}")
            raise Exception(f"Failed to create embeddings: {str(e)}")
            
    async def store_document(self, db: Session, content: str, metadata: Dict[str, Any], collection_name: str = "documents"):
        """
        Store document and its embedding in the database
        Note: This assumes a table 'document_embeddings' exists with vector column
        """
        try:
            # Generate embedding
            vector = await self.create_embeddings(content, metadata)
            
            # Store in DB (using raw SQL for pgvector)
            # We need to ensure the table exists first
            self._ensure_table_exists(db)
            
            query = text("""
                INSERT INTO document_embeddings (content, metadata, embedding, collection)
                VALUES (:content, :metadata, :embedding, :collection)
                RETURNING id
            """)
            
            result = db.execute(query, {
                "content": content,
                "metadata": json.dumps(metadata),
                "embedding": str(vector),  # pgvector expects string representation
                "collection": collection_name
            })
            db.commit()
            
            return result.fetchone()[0]
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error storing document: {str(e)}")
            raise Exception(f"Failed to store document: {str(e)}")
            
    async def search_similar(self, db: Session, query_text: str, limit: int = 5, collection_name: str = "documents") -> List[Dict[str, Any]]:
        """
        Search for similar documents using cosine similarity
        """
        try:
            # Generate query embedding
            query_vector = await self.create_embeddings(query_text, {})
            
            # Search using pgvector cosine distance operator (<=>)
            # We want 1 - distance for similarity
            sql = text("""
                SELECT id, content, metadata, 1 - (embedding <=> :query_vector) as similarity
                FROM document_embeddings
                WHERE collection = :collection
                ORDER BY embedding <=> :query_vector
                LIMIT :limit
            """)
            
            results = db.execute(sql, {
                "query_vector": str(query_vector),
                "collection": collection_name,
                "limit": limit
            }).fetchall()
            
            return [
                {
                    "id": r.id,
                    "content": r.content,
                    "metadata": json.loads(r.metadata) if isinstance(r.metadata, str) else r.metadata,
                    "similarity": float(r.similarity)
                }
                for r in results
            ]
            
        except Exception as e:
            logger.error(f"Error searching documents: {str(e)}")
            raise Exception(f"Failed to search documents: {str(e)}")
            
    def _ensure_table_exists(self, db: Session):
        """Ensure the document_embeddings table exists with vector extension"""
        try:
            # Enable vector extension
            db.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            
            # Create table
            db.execute(text("""
                CREATE TABLE IF NOT EXISTS document_embeddings (
                    id SERIAL PRIMARY KEY,
                    content TEXT NOT NULL,
                    metadata JSONB DEFAULT '{}',
                    embedding vector(1536),
                    collection VARCHAR(50) DEFAULT 'documents',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Create index for faster search (IVFFlat)
            # Note: Requires some data to be effective, usually created later
            # db.execute(text("CREATE INDEX ON document_embeddings USING ivfflat (embedding vector_cosine_ops)"))
            
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Error ensuring table exists: {str(e)}")
            # Don't raise here, might be permission issue, try to proceed
