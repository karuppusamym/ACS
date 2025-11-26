from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.schemas.models import ModelCreate, ModelUpdate, Model
from app.models.models import DatabaseConnection as ModelDB
from app.models.models import User as UserModel
from app.api.v1.endpoints.auth import get_current_active_user
from app.db.session import get_db
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()

@router.post("/", response_model=Model, status_code=status.HTTP_201_CREATED)
async def create_model(
    model_data: ModelCreate,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new data model"""
    db_model = ModelDB(
        name=model_data.name,
        type=model_data.type.value,
        description=model_data.description,
        owner_id=current_user.id,
        is_active=True,
        connection_string=""  # Will be set when connection is added
    )
    
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    
    logger.info(f"Model created: {db_model.name} by user {current_user.username}")
    return db_model

@router.get("/", response_model=List[Model])
async def list_models(
    skip: int = 0,
    limit: int = 100,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List all models accessible to the current user"""
    # For now, show all models owned by the user
    # TODO: Add shared models based on permissions
    models = db.query(ModelDB).filter(ModelDB.owner_id == current_user.id).offset(skip).limit(limit).all()
    return models

@router.get("/{model_id}", response_model=Model)
async def get_model(
    model_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific model"""
    model = db.query(ModelDB).filter(ModelDB.id == model_id).first()
    
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    # Check access (owner or has permission)
    if model.owner_id != current_user.id and not current_user.is_superuser:
        # TODO: Check permissions table
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return model

@router.put("/{model_id}", response_model=Model)
async def update_model(
    model_id: int,
    model_data: ModelUpdate,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a model"""
    model = db.query(ModelDB).filter(ModelDB.id == model_id).first()
    
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    if model.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Update fields
    if model_data.name is not None:
        model.name = model_data.name
    if model_data.type is not None:
        model.type = model_data.type.value
    if model_data.description is not None:
        model.description = model_data.description
    
    db.commit()
    db.refresh(model)
    
    logger.info(f"Model updated: {model.name}")
    return model

@router.delete("/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_model(
    model_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a model"""
    model = db.query(ModelDB).filter(ModelDB.id == model_id).first()
    
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    if model.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db.delete(model)
    db.commit()
    
    logger.info(f"Model deleted: {model.name}")
    return None

@router.post("/{model_id}/publish", response_model=Model)
async def publish_model(
    model_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Publish a model (make it available for use)"""
    model = db.query(ModelDB).filter(ModelDB.id == model_id).first()
    
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    if model.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    model.is_active = True
    db.commit()
    db.refresh(model)
    
    logger.info(f"Model published: {model.name}")
    return model

@router.post("/{model_id}/unpublish", response_model=Model)
async def unpublish_model(
    model_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Unpublish a model"""
    model = db.query(ModelDB).filter(ModelDB.id == model_id).first()
    
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    if model.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    model.is_active = False
    db.commit()
    db.refresh(model)
    
    logger.info(f"Model unpublished: {model.name}")
    return model
