from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.db.session import get_db
from app.services.semantic_service import (
    SemanticModelService,
    SemanticModelCreate,
    SemanticModelUpdate,
    SemanticModelResponse
)
from app.services.context_generator import ContextGenerator
from app.services.metadata import MetadataService
from app.models.models import DatabaseConnection, LLMConfiguration
from pydantic import BaseModel
import os

router = APIRouter()


class ContextGenerationRequest(BaseModel):
    """Request to generate context for a table"""
    table_name: str


class PromptUpdateRequest(BaseModel):
    """Request to update prompts"""
    system_prompt: str
    user_prompt_template: str


@router.post("/model", response_model=SemanticModelResponse)
async def create_semantic_model(
    model_data: SemanticModelCreate,
    db: Session = Depends(get_db)
):
    """Create a new semantic model"""
    # Check if connection exists
    connection = db.query(DatabaseConnection).filter(
        DatabaseConnection.id == model_data.connection_id
    ).first()
    
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")
    
    # Check if model already exists for this table
    existing = SemanticModelService.get_model_by_table(
        db, model_data.connection_id, model_data.table_name
    )
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Semantic model already exists for table {model_data.table_name}"
        )
    
    model = SemanticModelService.create_model(db, model_data)
    return model


@router.get("/models/{connection_id}", response_model=List[SemanticModelResponse])
async def get_semantic_models(
    connection_id: int,
    db: Session = Depends(get_db)
):
    """Get all semantic models for a connection"""
    models = SemanticModelService.get_models_by_connection(db, connection_id)
    return models


@router.get("/model/{model_id}", response_model=SemanticModelResponse)
async def get_semantic_model(
    model_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific semantic model"""
    model = SemanticModelService.get_model(db, model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Semantic model not found")
    return model


@router.put("/model/{model_id}", response_model=SemanticModelResponse)
async def update_semantic_model(
    model_id: int,
    model_data: SemanticModelUpdate,
    db: Session = Depends(get_db)
):
    """Update a semantic model"""
    model = SemanticModelService.update_model(db, model_id, model_data)
    if not model:
        raise HTTPException(status_code=404, detail="Semantic model not found")
    return model


@router.delete("/model/{model_id}")
async def delete_semantic_model(
    model_id: int,
    db: Session = Depends(get_db)
):
    """Delete a semantic model"""
    success = SemanticModelService.delete_model(db, model_id)
    if not success:
        raise HTTPException(status_code=404, detail="Semantic model not found")
    return {"message": "Semantic model deleted successfully"}


@router.post("/model/{model_id}/generate-context")
async def generate_context(
    model_id: int,
    request: ContextGenerationRequest,
    db: Session = Depends(get_db)
):
    """
    Generate business context for a table using LLM (RAG/CAG)
    """
    # Get semantic model
    model = SemanticModelService.get_model(db, model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Semantic model not found")
    
    # Get connection
    connection = db.query(DatabaseConnection).filter(
        DatabaseConnection.id == model.connection_id
    ).first()
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")
    
    # Get active LLM configuration
    llm_config = db.query(LLMConfiguration).filter(
        LLMConfiguration.is_active == True
    ).first()
    
    if not llm_config:
        raise HTTPException(
            status_code=400,
            detail="No active LLM configuration found. Please configure an LLM provider first."
        )
    
    try:
        # Get table metadata
        metadata_service = MetadataService(connection.connection_string)
        table_metadata = metadata_service._get_table_metadata(request.table_name)
        
        # Generate context using LLM
        context_gen = ContextGenerator(
            api_key=llm_config.api_key,
            model=llm_config.model_name
        )
        
        generated_context = await context_gen.generate_table_context(table_metadata)
        
        # Store generated context
        model = SemanticModelService.update_auto_generated_context(
            db, model_id, generated_context
        )
        
        return {
            "message": "Context generated successfully",
            "context": generated_context
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate context: {str(e)}"
        )


@router.put("/model/{model_id}/prompt")
async def update_prompt(
    model_id: int,
    request: PromptUpdateRequest,
    db: Session = Depends(get_db)
):
    """Update custom prompts for a semantic model"""
    update_data = SemanticModelUpdate(
        system_prompt=request.system_prompt,
        user_prompt_template=request.user_prompt_template
    )
    
    model = SemanticModelService.update_model(db, model_id, update_data)
    if not model:
        raise HTTPException(status_code=404, detail="Semantic model not found")
    
    return {
        "message": "Prompts updated successfully",
        "prompt_version": model.prompt_version
    }


@router.get("/model/{model_id}/context")
async def get_full_context(
    model_id: int,
    db: Session = Depends(get_db)
):
    """
    Get complete context for a semantic model
    This is used by the agent to load all relevant context
    """
    model = SemanticModelService.get_model(db, model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Semantic model not found")
    
    return {
        "table_name": model.table_name,
        "business_description": model.business_description,
        "column_descriptions": model.column_descriptions,
        "relationships": model.relationships,
        "system_prompt": model.system_prompt,
        "user_prompt_template": model.user_prompt_template,
        "business_glossary": model.business_glossary,
        "example_queries": model.example_queries,
        "auto_generated_context": model.auto_generated_context,
        "prompt_version": model.prompt_version
    }


@router.post("/model/{model_id}/generate-prompt")
async def generate_system_prompt(
    model_id: int,
    db: Session = Depends(get_db)
):
    """
    Generate a custom system prompt based on table metadata and business context
    """
    # Get semantic model
    model = SemanticModelService.get_model(db, model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Semantic model not found")
    
    # Get connection
    connection = db.query(DatabaseConnection).filter(
        DatabaseConnection.id == model.connection_id
    ).first()
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")
    
    # Get active LLM configuration
    llm_config = db.query(LLMConfiguration).filter(
        LLMConfiguration.is_active == True
    ).first()
    
    if not llm_config:
        raise HTTPException(
            status_code=400,
            detail="No active LLM configuration found"
        )
    
    try:
        # Get table metadata
        metadata_service = MetadataService(connection.connection_string)
        table_metadata = metadata_service._get_table_metadata(model.table_name)
        
        # Prepare business context
        business_context = {
            "business_description": model.business_description,
            "column_descriptions": model.column_descriptions,
            "business_glossary": model.business_glossary,
            "example_queries": model.example_queries
        }
        
        # Generate system prompt
        context_gen = ContextGenerator(
            api_key=llm_config.api_key,
            model=llm_config.model_name
        )
        
        system_prompt = await context_gen.generate_system_prompt(
            table_metadata, business_context
        )
        
        # Update model with generated prompt
        update_data = SemanticModelUpdate(system_prompt=system_prompt)
        model = SemanticModelService.update_model(db, model_id, update_data)
        
        return {
            "message": "System prompt generated successfully",
            "system_prompt": system_prompt
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate system prompt: {str(e)}"
        )
