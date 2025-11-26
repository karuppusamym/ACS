from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

class ChatSessionBase(BaseModel):
    name: Optional[str] = None

class ChatSessionCreate(ChatSessionBase):
    connection_id: Optional[int] = None

class ChatSessionUpdate(BaseModel):
    name: Optional[str] = None

class ChatSessionInDB(ChatSessionBase):
    id: int
    user_id: int
    connection_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ChatSession(ChatSessionInDB):
    pass

# Message schemas
class MessageRole(str):
    USER = "user"
    ASSISTANT = "assistant"

class ChatMessageBase(BaseModel):
    role: str
    content: str

class ChatMessageCreate(ChatMessageBase):
    pass

class ChatMessageInDB(ChatMessageBase):
    id: int
    session_id: int
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class ChatMessage(ChatMessageInDB):
    pass

class ChatResponse(BaseModel):
    message: ChatMessage
    sql: Optional[str] = None
    chart_config: Optional[Dict[str, Any]] = None
    data: Optional[List[Dict[str, Any]]] = None
    trace: Optional[List[Dict[str, Any]]] = None
