from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Depends
from typing import List, Optional
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.embeddings import EmbeddingService
from app.core.logging import get_logger
from app.api.v1.endpoints.auth import get_current_active_user
from app.models.models import User

router = APIRouter()
logger = get_logger(__name__)

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    collection: str = Form("documents"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Upload and embed a text document
    """
    if not file.filename.endswith('.txt') and not file.filename.endswith('.md'):
        raise HTTPException(status_code=400, detail="Only text and markdown files are supported")
        
    try:
        content = (await file.read()).decode("utf-8")
        
        service = EmbeddingService()
        doc_id = await service.store_document(
            db,
            content,
            {"filename": file.filename, "uploaded_by": current_user.username},
            collection
        )
        
        return {"message": "Document uploaded and embedded", "id": doc_id}
        
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/search")
async def search_documents(
    query: str,
    limit: int = 5,
    collection: str = "documents",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Semantic search for documents
    """
    try:
        service = EmbeddingService()
        results = await service.search_similar(db, query, limit, collection)
        return results
        
    except Exception as e:
        logger.error(f"Search failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
