from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import ChatSession, ChatMessage, Workflow
from app.schemas import (
    ChatSessionCreate, 
    ChatSessionResponse, 
    ChatMessageCreate, 
    ChatMessageResponse,
    WorkflowExecutionRequest
)
from app.services.workflow_execution_service import WorkflowExecutionService

router = APIRouter()

@router.post("/sessions", response_model=ChatSessionResponse)
def create_chat_session(session: ChatSessionCreate, db: Session = Depends(get_db)):
    """Create a new chat session"""
    # Verify workflow exists
    workflow = db.query(Workflow).filter(Workflow.id == session.workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    db_session = ChatSession(
        workflow_id=session.workflow_id,
        session_name=session.session_name
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

@router.get("/sessions", response_model=List[ChatSessionResponse])
def list_chat_sessions(workflow_id: int = None, db: Session = Depends(get_db)):
    """Get all chat sessions, optionally filtered by workflow"""
    query = db.query(ChatSession)
    if workflow_id:
        query = query.filter(ChatSession.workflow_id == workflow_id)
    sessions = query.all()
    return sessions

@router.get("/sessions/{session_id}", response_model=ChatSessionResponse)
def get_chat_session(session_id: int, db: Session = Depends(get_db)):
    """Get a specific chat session with messages"""
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    return session

@router.delete("/sessions/{session_id}")
def delete_chat_session(session_id: int, db: Session = Depends(get_db)):
    """Delete a chat session"""
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    db.delete(session)
    db.commit()
    return {"message": "Chat session deleted successfully"}

@router.post("/execute", response_model=ChatMessageResponse)
async def execute_workflow(
    request: WorkflowExecutionRequest, 
    db: Session = Depends(get_db)
):
    """Execute a workflow with a user query"""
    # Get or create session
    if request.session_id:
        session = db.query(ChatSession).filter(ChatSession.id == request.session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")
    else:
        # Create new session
        session = ChatSession(
            workflow_id=request.workflow_id,
            session_name=f"Chat {request.query[:20]}..."
        )
        db.add(session)
        db.commit()
        db.refresh(session)
    
    # Create user message
    user_message = ChatMessage(
        session_id=session.id,
        message=request.query,
        message_type="user"
    )
    db.add(user_message)
    db.commit()
    db.refresh(user_message)
    
    # Execute workflow
    execution_service = WorkflowExecutionService()
    try:
        result = await execution_service.execute_workflow(
            workflow_id=request.workflow_id,
            query=request.query,
            db=db
        )
        
        # Create assistant message
        assistant_message = ChatMessage(
            session_id=session.id,
            message="",
            response=result.get("response", ""),
            message_type="assistant",
            execution_data=result
        )
        db.add(assistant_message)
        db.commit()
        db.refresh(assistant_message)
        
        return assistant_message
        
    except Exception as e:
        # Create error message
        error_message = ChatMessage(
            session_id=session.id,
            message="",
            response=f"Error executing workflow: {str(e)}",
            message_type="assistant",
            execution_data={"error": str(e)}
        )
        db.add(error_message)
        db.commit()
        db.refresh(error_message)
        
        return error_message

@router.get("/sessions/{session_id}/messages", response_model=List[ChatMessageResponse])
def get_session_messages(session_id: int, db: Session = Depends(get_db)):
    """Get all messages for a chat session"""
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.created_at).all()
    
    return messages