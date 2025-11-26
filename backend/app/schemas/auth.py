from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional
from app.core.validators import validate_password_strength, validate_username
from datetime import datetime

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)

    @validator('username')
    def validate_username_format(cls, v):
        return validate_username(v)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

    @validator('password')
    def validate_password_strength(cls, v):
        return validate_password_strength(v)

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    password: Optional[str] = Field(None, min_length=8)

    @validator('username')
    def validate_username_format(cls, v):
        if v is not None:
            return validate_username(v)
        return v

    @validator('password')
    def validate_password_strength(cls, v):
        if v is not None:
            return validate_password_strength(v)
        return v

class UserInDB(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class User(UserInDB):
    pass

# Auth schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int] = None
    username: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str
