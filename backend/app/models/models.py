from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base
from pgvector.sqlalchemy import Vector

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user")  # admin, user, viewer
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    connections = relationship("DatabaseConnection", back_populates="owner")
    chat_sessions = relationship("ChatSession", back_populates="user")


class DatabaseConnection(Base):
    __tablename__ = "database_connections"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # postgresql, mysql, mssql, etc.
    connection_string = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    owner = relationship("User", back_populates="connections")
    semantic_models = relationship("SemanticModel", back_populates="connection")


class SemanticModel(Base):
    __tablename__ = "semantic_models"

    id = Column(Integer, primary_key=True, index=True)
    table_name = Column(String, nullable=False)
    business_description = Column(Text, nullable=True)
    column_descriptions = Column(JSON, nullable=True)
    relationships = Column(JSON, nullable=True)
    
    # RAG/CAG Enhancement Fields
    system_prompt = Column(Text, nullable=True)  # Custom system prompt for this model
    user_prompt_template = Column(Text, nullable=True)  # Template for user prompts
    business_glossary = Column(JSON, nullable=True)  # Business terms and definitions
    example_queries = Column(JSON, nullable=True)  # Sample queries for this table
    auto_generated_context = Column(JSON, nullable=True)  # LLM-generated suggestions
    prompt_version = Column(Integer, default=1)  # Version control for prompts
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    connection_id = Column(Integer, ForeignKey("database_connections.id"))
    
    # Relationships
    connection = relationship("DatabaseConnection", back_populates="semantic_models")


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id"))
    connection_id = Column(Integer, ForeignKey("database_connections.id"), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    role = Column(String, nullable=False)  # user or assistant
    content = Column(Text, nullable=False)
    message_metadata = Column(JSON, nullable=True)  # Store SQL queries, visualizations, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    session_id = Column(Integer, ForeignKey("chat_sessions.id"))
    
    # Relationships
    session = relationship("ChatSession", back_populates="messages")


class LLMConfiguration(Base):
    __tablename__ = "llm_configurations"

    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String, nullable=False)  # openai, anthropic, etc.
    model_name = Column(String, nullable=False)
    api_key = Column(String, nullable=False)  # Should be encrypted in production
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DocumentEmbedding(Base):
    __tablename__ = "document_embeddings"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(1536))  # OpenAI embedding size
    metadata_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
