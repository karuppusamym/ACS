from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.models.models import DatabaseConnection, SemanticModel, User as UserModel
from app.api.v1.endpoints.auth import get_current_active_user
from app.db.session import get_db
from app.services.metadata import MetadataService
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()

@router.post("/{model_id}/schema/sync")
async def sync_schema(
    model_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Sync schema from database for a model"""
    # Get the model
    model = db.query(DatabaseConnection).filter(DatabaseConnection.id == model_id).first()
    
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    if model.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    try:
        # Extract metadata
        metadata_service = MetadataService(model.connection_string)
        tables = metadata_service.get_tables()
        
        # Store in semantic models
        synced_tables = []
        for table in tables:
            # Check if semantic model exists
            semantic_model = db.query(SemanticModel).filter(
                SemanticModel.connection_id == model_id,
                SemanticModel.table_name == table["table_name"]
            ).first()
            
            if not semantic_model:
                # Create new semantic model
                semantic_model = SemanticModel(
                    connection_id=model_id,
                    table_name=table["table_name"],
                    business_description=f"Table: {table['table_name']}",
                    column_descriptions={col["column_name"]: col["data_type"] for col in table["columns"]},
                    relationships={}
                )
                db.add(semantic_model)
            
            synced_tables.append({
                "table_name": table["table_name"],
                "columns": table["columns"]
            })
        
        db.commit()
        
        logger.info(f"Schema synced for model {model_id}: {len(synced_tables)} tables")
        return {
            "model_id": model_id,
            "tables_synced": len(synced_tables),
            "tables": synced_tables
        }
    
    except Exception as e:
        logger.error(f"Schema sync failed for model {model_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Schema sync failed: {str(e)}")

@router.get("/{model_id}/tables")
async def get_model_tables(
    model_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Get all tables for a model"""
    model = db.query(DatabaseConnection).filter(DatabaseConnection.id == model_id).first()
    
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    if model.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Get semantic models
    semantic_models = db.query(SemanticModel).filter(SemanticModel.connection_id == model_id).all()
    
    return [
        {
            "id": sm.id,
            "table_name": sm.table_name,
            "business_description": sm.business_description,
            "column_descriptions": sm.column_descriptions,
            "relationships": sm.relationships
        }
        for sm in semantic_models
    ]

@router.put("/{model_id}/tables/{table_id}")
async def update_table_metadata(
    model_id: int,
    table_id: int,
    business_description: str = None,
    column_descriptions: Dict[str, str] = None,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update table metadata (business names, descriptions)"""
    semantic_model = db.query(SemanticModel).filter(
        SemanticModel.id == table_id,
        SemanticModel.connection_id == model_id
    ).first()
    
    if not semantic_model:
        raise HTTPException(status_code=404, detail="Table not found")
    
    # Check permissions
    model = db.query(DatabaseConnection).filter(DatabaseConnection.id == model_id).first()
    if model.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    if business_description:
        semantic_model.business_description = business_description
    if column_descriptions:
        semantic_model.column_descriptions = column_descriptions
    
    db.commit()
    db.refresh(semantic_model)
    
    logger.info(f"Table metadata updated: {semantic_model.table_name}")
    return semantic_model
