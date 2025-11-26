from fastapi import APIRouter, HTTPException, Depends
from app.core.deps import require_admin
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from app.db.session import get_db
from app.models.models import LLMConfiguration
from app.core.encryption import encryption_service
from openai import OpenAI
from anthropic import Anthropic

router = APIRouter()


class LLMConfigCreate(BaseModel):
    """Schema for creating LLM configuration"""
    provider: str  # openai, anthropic, google, azure
    model_name: str
    api_key: str
    is_active: bool = False


class LLMConfigUpdate(BaseModel):
    """Schema for updating LLM configuration"""
    model_name: Optional[str] = None
    api_key: Optional[str] = None
    is_active: Optional[bool] = None


class LLMConfigResponse(BaseModel):
    """Schema for LLM configuration response"""
    id: int
    provider: str
    model_name: str
    is_active: bool
    
    class Config:
        from_attributes = True


@router.post("/llm-config", response_model=LLMConfigResponse)
async def create_llm_config(config: LLMConfigCreate, db: Session = Depends(get_db)):
    """Create a new LLM configuration with encrypted API key"""
    
    # Encrypt the API key
    encrypted_key = encryption_service.encrypt(config.api_key)
    
    # If setting as active, deactivate all others
    if config.is_active:
        db.query(LLMConfiguration).update({"is_active": False})
    
    # Create new configuration
    db_config = LLMConfiguration(
        provider=config.provider,
        model_name=config.model_name,
        api_key=encrypted_key,
        is_active=config.is_active
    )
    
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    
    return db_config


@router.get("/llm-configs", response_model=List[LLMConfigResponse])
async def get_llm_configs(db: Session = Depends(get_db)):
    """Get all LLM configurations (without API keys)"""
    configs = db.query(LLMConfiguration).all()
    return configs


@router.get("/llm-config/{config_id}", response_model=LLMConfigResponse)
async def get_llm_config(config_id: int, db: Session = Depends(get_db)):
    """Get a specific LLM configuration"""
    config = db.query(LLMConfiguration).filter(LLMConfiguration.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="LLM configuration not found")
    return config


@router.put("/llm-config/{config_id}", response_model=LLMConfigResponse)
async def update_llm_config(
    config_id: int,
    config_update: LLMConfigUpdate,
    db: Session = Depends(get_db)
):
    """Update an LLM configuration"""
    config = db.query(LLMConfiguration).filter(LLMConfiguration.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="LLM configuration not found")
    
    # Update fields
    if config_update.model_name is not None:
        config.model_name = config_update.model_name
    
    if config_update.api_key is not None:
        config.api_key = encryption_service.encrypt(config_update.api_key)
    
    if config_update.is_active is not None:
        if config_update.is_active:
            # Deactivate all others
            db.query(LLMConfiguration).update({"is_active": False})
        config.is_active = config_update.is_active
    
    db.commit()
    db.refresh(config)
    
    return config


@router.delete("/llm-config/{config_id}")
async def delete_llm_config(config_id: int, db: Session = Depends(get_db)):
    """Delete an LLM configuration"""
    config = db.query(LLMConfiguration).filter(LLMConfiguration.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="LLM configuration not found")
    
    db.delete(config)
    db.commit()
    
    return {"message": "LLM configuration deleted successfully"}


@router.post("/llm-config/{config_id}/test")
async def test_llm_config(config_id: int, db: Session = Depends(get_db)):
    """Test an LLM configuration by making a simple API call"""
    config = db.query(LLMConfiguration).filter(LLMConfiguration.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="LLM configuration not found")
    
    # Decrypt API key
    try:
        api_key = encryption_service.decrypt(config.api_key)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to decrypt API key: {str(e)}")
    
    # Test based on provider
    try:
        if config.provider.lower() == "openai":
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model=config.model_name,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            return {
                "status": "success",
                "message": "OpenAI connection successful",
                "model": config.model_name
            }
        
        elif config.provider.lower() == "anthropic":
            client = Anthropic(api_key=api_key)
            response = client.messages.create(
                model=config.model_name,
                max_tokens=5,
                messages=[{"role": "user", "content": "Hello"}]
            )
            return {
                "status": "success",
                "message": "Anthropic connection successful",
                "model": config.model_name
            }
        
        else:
            return {
                "status": "warning",
                "message": f"Test not implemented for provider: {config.provider}"
            }
    
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"LLM connection test failed: {str(e)}"
        )


@router.post("/llm-config/{config_id}/activate")
async def activate_llm_config(config_id: int, db: Session = Depends(get_db)):
    """Set an LLM configuration as active"""
    config = db.query(LLMConfiguration).filter(LLMConfiguration.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="LLM configuration not found")
    
    # Deactivate all others
    db.query(LLMConfiguration).update({"is_active": False})
    
    # Activate this one
    config.is_active = True
    db.commit()
    db.refresh(config)
    

# -----------------------------------------------------------------------------
# User Management Endpoints
# -----------------------------------------------------------------------------

from app.models.models import User
from app.core.security import get_password_hash
from app.core.deps import require_admin

class UserCreate(BaseModel):
    email: str
    username: str
    password: str
    role: str = "user"
    is_active: bool = True

class UserUpdate(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    role: str
    is_active: bool
    is_superuser: bool
    
    class Config:
        from_attributes = True

@router.post("/users", response_model=UserResponse)
async def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Create a new user (Admin only)"""
    # Check if user exists
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = db.query(User).filter(User.username == user_in.username).first()
    if user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    db_user = User(
        email=user_in.email,
        username=user_in.username,
        hashed_password=get_password_hash(user_in.password),
        role=user_in.role,
        is_active=user_in.is_active,
        is_superuser=(user_in.role == "admin")
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/users", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """List all users (Admin only)"""
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Update a user (Admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user_in.email is not None:
        user.email = user_in.email
    if user_in.role is not None:
        user.role = user_in.role
        if user_in.role == "admin":
            user.is_superuser = True
        else:
            user.is_superuser = False
    if user_in.is_active is not None:
        user.is_active = user_in.is_active
    if user_in.password is not None:
        user.hashed_password = get_password_hash(user_in.password)
        
    db.commit()
    db.refresh(user)
    return user

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete a user (Admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}

