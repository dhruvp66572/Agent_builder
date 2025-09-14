from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import Workflow, WorkflowDocument
from app.schemas import WorkflowCreate, WorkflowUpdate, WorkflowResponse

router = APIRouter()

@router.post("/", response_model=WorkflowResponse)
def create_workflow(workflow: WorkflowCreate, db: Session = Depends(get_db)):
    """Create a new workflow"""
    db_workflow = Workflow(
        name=workflow.name,
        description=workflow.description,
        workflow_data=workflow.workflow_data
    )
    db.add(db_workflow)
    db.commit()
    db.refresh(db_workflow)
    return db_workflow

@router.get("/", response_model=List[WorkflowResponse])
def list_workflows(db: Session = Depends(get_db)):
    """Get all workflows"""
    workflows = db.query(Workflow).all()
    return workflows

@router.get("/{workflow_id}", response_model=WorkflowResponse)
def get_workflow(workflow_id: int, db: Session = Depends(get_db)):
    """Get a specific workflow"""
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow

@router.put("/{workflow_id}", response_model=WorkflowResponse)
def update_workflow(
    workflow_id: int, 
    workflow_update: WorkflowUpdate, 
    db: Session = Depends(get_db)
):
    """Update a workflow"""
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    if workflow_update.name is not None:
        workflow.name = workflow_update.name
    if workflow_update.description is not None:
        workflow.description = workflow_update.description
    if workflow_update.workflow_data is not None:
        workflow.workflow_data = workflow_update.workflow_data
    if workflow_update.is_active is not None:
        workflow.is_active = workflow_update.is_active
    
    db.commit()
    db.refresh(workflow)
    return workflow

@router.delete("/{workflow_id}")
def delete_workflow(workflow_id: int, db: Session = Depends(get_db)):
    """Delete a workflow"""
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    db.delete(workflow)
    db.commit()
    return {"message": "Workflow deleted successfully"}

@router.post("/{workflow_id}/validate")
def validate_workflow(workflow_id: int, db: Session = Depends(get_db)):
    """Validate a workflow configuration"""
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    # Basic validation logic
    workflow_data = workflow.workflow_data
    nodes = workflow_data.get('nodes', [])
    edges = workflow_data.get('edges', [])
    
    # Check if workflow has required components
    component_types = [node.get('type') for node in nodes]
    required_types = ['user-query', 'output']
    
    missing_types = [t for t in required_types if t not in component_types]
    if missing_types:
        return {
            "valid": False,
            "errors": [f"Missing required component: {t}" for t in missing_types]
        }
    
    # Check if components are connected
    if len(nodes) > 1 and len(edges) == 0:
        return {
            "valid": False,
            "errors": ["Components are not connected"]
        }
    
    return {"valid": True, "errors": []}

@router.post("/{workflow_id}/documents/{document_id}")
def link_document_to_workflow(
    workflow_id: int, 
    document_id: int, 
    db: Session = Depends(get_db)
):
    """Link a document to a workflow"""
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    # Check if link already exists
    existing_link = db.query(WorkflowDocument).filter(
        WorkflowDocument.workflow_id == workflow_id,
        WorkflowDocument.document_id == document_id
    ).first()
    
    if existing_link:
        raise HTTPException(status_code=400, detail="Document already linked to workflow")
    
    workflow_doc = WorkflowDocument(
        workflow_id=workflow_id,
        document_id=document_id
    )
    db.add(workflow_doc)
    db.commit()
    
    return {"message": "Document linked to workflow successfully"}

@router.delete("/{workflow_id}/documents/{document_id}")
def unlink_document_from_workflow(
    workflow_id: int, 
    document_id: int, 
    db: Session = Depends(get_db)
):
    """Unlink a document from a workflow"""
    workflow_doc = db.query(WorkflowDocument).filter(
        WorkflowDocument.workflow_id == workflow_id,
        WorkflowDocument.document_id == document_id
    ).first()
    
    if not workflow_doc:
        raise HTTPException(status_code=404, detail="Document not linked to workflow")
    
    db.delete(workflow_doc)
    db.commit()
    
    return {"message": "Document unlinked from workflow successfully"}