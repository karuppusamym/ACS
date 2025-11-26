from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.models import SemanticModel
from pydantic import BaseModel


class SemanticModelCreate(BaseModel):
    """Schema for creating a semantic model"""
    table_name: str
    connection_id: int
    business_description: Optional[str] = None
    column_descriptions: Optional[Dict[str, str]] = None
    relationships: Optional[List[Dict[str, Any]]] = None
    system_prompt: Optional[str] = None
    user_prompt_template: Optional[str] = None
    business_glossary: Optional[Dict[str, str]] = None
    example_queries: Optional[List[str]] = None


class SemanticModelUpdate(BaseModel):
    """Schema for updating a semantic model"""
    business_description: Optional[str] = None
    column_descriptions: Optional[Dict[str, str]] = None
    relationships: Optional[List[Dict[str, Any]]] = None
    system_prompt: Optional[str] = None
    user_prompt_template: Optional[str] = None
    business_glossary: Optional[Dict[str, str]] = None
    example_queries: Optional[List[str]] = None


class SemanticModelResponse(BaseModel):
    """Schema for semantic model response"""
    id: int
    table_name: str
    connection_id: int
    business_description: Optional[str]
    column_descriptions: Optional[Dict[str, str]]
    relationships: Optional[List[Dict[str, Any]]]
    system_prompt: Optional[str]
    user_prompt_template: Optional[str]
    business_glossary: Optional[Dict[str, str]]
    example_queries: Optional[List[str]]
    auto_generated_context: Optional[Dict[str, Any]]
    prompt_version: int
    
    class Config:
        from_attributes = True


class SemanticModelService:
    """Service for managing semantic models"""
    
    @staticmethod
    def create_model(db: Session, model_data: SemanticModelCreate) -> SemanticModel:
        """Create a new semantic model"""
        db_model = SemanticModel(
            table_name=model_data.table_name,
            connection_id=model_data.connection_id,
            business_description=model_data.business_description,
            column_descriptions=model_data.column_descriptions,
            relationships=model_data.relationships,
            system_prompt=model_data.system_prompt,
            user_prompt_template=model_data.user_prompt_template,
            business_glossary=model_data.business_glossary,
            example_queries=model_data.example_queries,
        )
        db.add(db_model)
        db.commit()
        db.refresh(db_model)
        return db_model
    
    @staticmethod
    def get_model(db: Session, model_id: int) -> Optional[SemanticModel]:
        """Get a semantic model by ID"""
        return db.query(SemanticModel).filter(SemanticModel.id == model_id).first()
    
    @staticmethod
    def get_models_by_connection(db: Session, connection_id: int) -> List[SemanticModel]:
        """Get all semantic models for a connection"""
        return db.query(SemanticModel).filter(
            SemanticModel.connection_id == connection_id
        ).all()
    
    @staticmethod
    def get_model_by_table(db: Session, connection_id: int, table_name: str) -> Optional[SemanticModel]:
        """Get semantic model for a specific table"""
        return db.query(SemanticModel).filter(
            SemanticModel.connection_id == connection_id,
            SemanticModel.table_name == table_name
        ).first()
    
    @staticmethod
    def update_model(db: Session, model_id: int, model_data: SemanticModelUpdate) -> Optional[SemanticModel]:
        """Update a semantic model"""
        db_model = db.query(SemanticModel).filter(SemanticModel.id == model_id).first()
        if not db_model:
            return None
        
        update_data = model_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_model, field, value)
        
        # Increment version if prompts changed
        if 'system_prompt' in update_data or 'user_prompt_template' in update_data:
            db_model.prompt_version += 1
        
        db.commit()
        db.refresh(db_model)
        return db_model
    
    @staticmethod
    def delete_model(db: Session, model_id: int) -> bool:
        """Delete a semantic model"""
        db_model = db.query(SemanticModel).filter(SemanticModel.id == model_id).first()
        if not db_model:
            return False
        
        db.delete(db_model)
        db.commit()
        return True
    
    @staticmethod
    def update_auto_generated_context(db: Session, model_id: int, context: Dict[str, Any]) -> Optional[SemanticModel]:
        """Update auto-generated context for a model"""
        db_model = db.query(SemanticModel).filter(SemanticModel.id == model_id).first()
        if not db_model:
            return None
        
        db_model.auto_generated_context = context
        db.commit()
        db.refresh(db_model)
        return db_model
