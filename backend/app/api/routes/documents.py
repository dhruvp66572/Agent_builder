from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import os
import uuid
import shutil
from datetime import datetime

from app.database import get_db
from app.models import Document
from app.schemas import DocumentResponse
from app.services.document_service import DocumentService

router = APIRouter()

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload and process a document"""
    
    # Validate file type
    if not file.content_type.startswith('application/pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join("uploads", unique_filename)
    
    # Ensure uploads directory exists
    os.makedirs("uploads", exist_ok=True)
    
    # Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Create document record
    document = Document(
        filename=unique_filename,
        original_filename=file.filename,
        file_path=file_path,
        file_size=os.path.getsize(file_path),
        content_type=file.content_type,
        embedding_status="pending"
    )
    
    db.add(document)
    db.commit()
    db.refresh(document)
    
    # Process document asynchronously
    document_service = DocumentService()
    try:
        await document_service.process_document(document.id, db)
    except Exception as e:
        # Log error but don't fail the upload
        print(f"Document processing error: {str(e)}")
    
    return document

@router.get("/", response_model=List[DocumentResponse])
def list_documents(db: Session = Depends(get_db)):
    """Get all documents"""
    documents = db.query(Document).all()
    return documents

@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(document_id: int, db: Session = Depends(get_db)):
    """Get a specific document"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document

@router.delete("/{document_id}")
def delete_document(document_id: int, db: Session = Depends(get_db)):
    """Delete a document"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Delete file from filesystem
    if os.path.exists(document.file_path):
        os.remove(document.file_path)
    
    # Delete from database
    db.delete(document)
    db.commit()
    
    return {"message": "Document deleted successfully"}

@router.post("/{document_id}/reprocess")
async def reprocess_document(document_id: int, db: Session = Depends(get_db)):
    """Reprocess a document for embeddings"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    document.embedding_status = "pending"
    db.commit()
    
    # Process document
    document_service = DocumentService()
    try:
        await document_service.process_document(document.id, db)
        return {"message": "Document reprocessing started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reprocess document: {str(e)}")