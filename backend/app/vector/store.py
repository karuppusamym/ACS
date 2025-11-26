from sqlalchemy.orm import Session
from app.vector.models import DocumentEmbedding
from typing import List, Dict, Any
import json

class VectorStore:
    def __init__(self, db: Session):
        self.db = db

    def add_documents(self, documents: List[Dict[str, Any]], embeddings: List[List[float]]):
        for doc, embedding in zip(documents, embeddings):
            db_doc = DocumentEmbedding(
                content=doc["content"],
                embedding=embedding,
                metadata_json=json.dumps(doc.get("metadata", {}))
            )
            self.db.add(db_doc)
        self.db.commit()

    def search(self, query_embedding: List[float], limit: int = 5):
        return self.db.query(DocumentEmbedding).order_by(
            DocumentEmbedding.embedding.l2_distance(query_embedding)
        ).limit(limit).all()
