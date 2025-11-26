from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.schemas.chat import (
    ChatSessionCreate, ChatSessionUpdate, ChatSession,
    ChatMessageCreate, ChatMessage, ChatResponse
)
from app.models.models import (
    ChatSession as ChatSessionModel,
    ChatMessage as ChatMessageModel,
    DatabaseConnection,
    User as UserModel
)
from app.api.v1.endpoints.auth import get_current_active_user
from app.db.session import get_db
from app.services.llm_orchestrator import LLMOrchestrator
from app.services.sql_engine import SQLEngine
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()

@router.post("/sessions", response_model=ChatSession, status_code=status.HTTP_201_CREATED)
async def create_session(
    session_data: ChatSessionCreate,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new chat session"""
    # Validate connection ownership if connection_id provided
    if session_data.connection_id:
        connection = db.query(DatabaseConnection).filter(
            DatabaseConnection.id == session_data.connection_id
        ).first()

        if not connection:
            raise HTTPException(status_code=404, detail="Connection not found")

        # Check if user has access to this connection
        if not (current_user.is_superuser or current_user.role == "admin" or connection.owner_id == current_user.id):
            raise HTTPException(status_code=403, detail="Not authorized to use this connection")

    db_session = ChatSessionModel(
        name=session_data.name or "New Chat",
        user_id=current_user.id,
        connection_id=session_data.connection_id
    )

    db.add(db_session)
    db.commit()
    db.refresh(db_session)

    logger.info(f"Chat session created: {db_session.id} by user {current_user.username}")
    return db_session

@router.get("/sessions", response_model=List[ChatSession])
async def list_sessions(
    skip: int = 0,
    limit: int = 100,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List all chat sessions for current user"""
    sessions = db.query(ChatSessionModel).filter(
        ChatSessionModel.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    return sessions

@router.get("/sessions/{session_id}", response_model=ChatSession)
async def get_session(
    session_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific chat session"""
    session = db.query(ChatSessionModel).filter(ChatSessionModel.id == session_id).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return session

@router.get("/sessions/{session_id}/messages", response_model=List[ChatMessage])
async def get_messages(
    session_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all messages in a chat session"""
    session = db.query(ChatSessionModel).filter(ChatSessionModel.id == session_id).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    messages = db.query(ChatMessageModel).filter(
        ChatMessageModel.session_id == session_id
    ).order_by(ChatMessageModel.created_at).all()
    
    return messages

@router.post("/sessions/{session_id}/messages", response_model=ChatResponse)
async def send_message(
    session_id: int,
    message_data: ChatMessageCreate,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Send a message and get AI response"""
    session = db.query(ChatSessionModel).filter(ChatSessionModel.id == session_id).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Store user message
    user_message = ChatMessageModel(
        session_id=session_id,
        role="user",
        content=message_data.content
    )
    db.add(user_message)
    db.commit()
    
    # Generate response if user message
    if message_data.role == "user" and session.connection_id:
        try:
            # Get connection
            connection = db.query(DatabaseConnection).filter(
                DatabaseConnection.id == session.connection_id
            ).first()
            
            if not connection:
                raise HTTPException(status_code=404, detail="Connection not found")
            
            # Generate SQL
            llm = LLMOrchestrator()
            sql_result = llm.generate_sql(
                user_question=message_data.content,
                connection_id=connection.id,
                session_id=session_id,
                db=db
            )
            
            # Execute SQL
            sql_engine = SQLEngine()
            execution_result = sql_engine.execute_sql(sql_result["sql"], connection)
            
            # Suggest chart type
            chart_config = None
            if execution_result["success"] and execution_result["row_count"] > 0:
                chart_suggestion = llm.suggest_chart_type(
                    execution_result["columns"],
                    execution_result["row_count"]
                )
                chart_config = chart_suggestion
            
            # Build response content
            if execution_result["success"]:
                response_content = f"I found {execution_result['row_count']} results. {sql_result['explanation']}"
            else:
                response_content = f"I encountered an error: {execution_result['error']}"
            
            # Store assistant message
            assistant_message = ChatMessageModel(
                session_id=session_id,
                role="assistant",
                content=response_content,
                message_metadata={
                    "sql": sql_result["sql"],
                    "chart_config": chart_config,
                    "trace": sql_result["trace"]
                }
            )
            db.add(assistant_message)
            db.commit()
            db.refresh(assistant_message)
            
            logger.info(f"AI response generated for session {session_id}")
            
            return ChatResponse(
                message=assistant_message,
                sql=sql_result["sql"],
                chart_config=chart_config,
                data=execution_result["rows"] if execution_result["success"] else None,
                trace=sql_result["trace"]
            )
        
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            error_message = ChatMessageModel(
                session_id=session_id,
                role="assistant",
                content=f"I encountered an error: {str(e)}"
            )
            db.add(error_message)
            db.commit()
            db.refresh(error_message)
            
            return ChatResponse(
                message=error_message,
                trace=[{"step": "error", "message": str(e)}]
            )
    
    # Return user message if no AI response needed
    db.refresh(user_message)
    return ChatResponse(message=user_message)

@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a chat session"""
    session = db.query(ChatSessionModel).filter(ChatSessionModel.id == session_id).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db.delete(session)
    db.commit()
    
    logger.info(f"Chat session deleted: {session_id}")
    return None
