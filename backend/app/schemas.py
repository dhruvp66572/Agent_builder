from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class DocumentUpload(BaseModel):
    filename: str
    content_type: str

class DocumentResponse(BaseModel):
    id: int
    filename: str
    original_filename: str
    file_size: int
    content_type: str
    embedding_status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class WorkflowCreate(BaseModel):
    name: str
    description: Optional[str] = None
    workflow_data: Dict[str, Any]

class WorkflowUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    workflow_data: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class WorkflowResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    workflow_data: Dict[str, Any]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ChatMessageCreate(BaseModel):
    session_id: int
    message: str

class ChatMessageResponse(BaseModel):
    id: int
    session_id: int
    message: str
    response: Optional[str] = None
    message_type: str
    execution_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class ChatSessionCreate(BaseModel):
    workflow_id: int
    session_name: Optional[str] = "New Chat"

class ChatSessionResponse(BaseModel):
    id: int
    workflow_id: int
    session_name: str
    created_at: datetime
    updated_at: datetime
    messages: List[ChatMessageResponse] = []
    
    class Config:
        from_attributes = True

class ComponentConfig(BaseModel):
    component_type: str
    config: Dict[str, Any]

class WorkflowExecutionRequest(BaseModel):
    workflow_id: int
    query: str
    session_id: Optional[int] = None