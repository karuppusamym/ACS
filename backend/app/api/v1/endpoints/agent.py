from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, Any
from app.db.session import get_db
from app.models.models import DatabaseConnection, ChatSession, ChatMessage
from app.services.rag_engine import RAGEngine
from app.services.agent import SQLAgent
from datetime import datetime

router = APIRouter()


class ChatRequest(BaseModel):
    """Request to chat with the agent"""
    query: str
    connection_id: int
    session_id: Optional[int] = None
    execute_sql: bool = True


class ChatResponse(BaseModel):
    """Response from the agent"""
    session_id: int
    message_id: int
    user_query: str
    sql: Optional[str]
    explanation: Optional[str]
    tables_used: list
    execution: Optional[Dict[str, Any]]


@router.post("/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Chat with the RAG/CAG-enhanced SQL agent
    """
    # Get or create session
    if request.session_id:
        session = db.query(ChatSession).filter(ChatSession.id == request.session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
    else:
        # Create new session
        session = ChatSession(
            name=f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            connection_id=request.connection_id,
            user_id=None  # TODO: Add auth
        )
        db.add(session)
        db.commit()
        db.refresh(session)
    
    # Get connection
    connection = db.query(DatabaseConnection).filter(
        DatabaseConnection.id == request.connection_id
    ).first()
    
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")
    
    # Initialize RAG engine
    rag_engine = RAGEngine(db)
    
    # Get LLM config
    llm_config = rag_engine.get_active_llm_config()
    if not llm_config:
        raise HTTPException(
            status_code=400,
            detail="No active LLM configuration. Please configure an LLM provider in settings."
        )
    
    # Get semantic context
    rag_context = rag_engine.get_connection_context(request.connection_id)
    
    # Initialize agent
    try:
        agent = SQLAgent(
            connection_string=connection.connection_string,
            llm_config=llm_config,
            rag_context=rag_context
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize agent: {str(e)}")
    
    # Process query
    try:
        result = agent.chat(request.query, execute=request.execute_sql)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")
    
    # Save user message
    user_message = ChatMessage(
        session_id=session.id,
        role="user",
        content=request.query
    )
    db.add(user_message)
    
    # Save assistant message
    assistant_content = {
        "sql": result.get("sql"),
        "explanation": result.get("explanation"),
        "tables_used": result.get("tables_used", []),
        "execution": result.get("execution")
    }
    
    assistant_message = ChatMessage(
        session_id=session.id,
        role="assistant",
        content=result.get("explanation", ""),
        message_metadata=assistant_content
    )
    db.add(assistant_message)
    db.commit()
    db.refresh(assistant_message)
    
    return {
        "session_id": session.id,
        "message_id": assistant_message.id,
        "user_query": request.query,
        "sql": result.get("sql"),
        "explanation": result.get("explanation"),
        "tables_used": result.get("tables_used", []),
        "execution": result.get("execution")
    }


@router.get("/context/{connection_id}")
async def get_agent_context(connection_id: int, db: Session = Depends(get_db)):
    """
    Get the semantic context that will be used by the agent
    """
    rag_engine = RAGEngine(db)
    context = rag_engine.get_connection_context(connection_id)
    
    return {
        "connection_id": connection_id,
        "context": context,
        "has_semantic_models": len(context.get("tables", {})) > 0
    }
