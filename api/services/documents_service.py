from sqlalchemy.orm import Session
from models import Document, DocumentCreate, DocumentUpdate
from typing import List, Optional

def get_all_documents(db: Session) -> List[Document]:
    """Get all documents"""
    return db.query(Document).all()

def get_document_by_id(db: Session, document_id: str) -> Optional[Document]:
    """Get document by ID"""
    return db.query(Document).filter(Document.id == document_id).first()

def get_documents_by_workspace(db: Session, workspace_id: str) -> List[Document]:
    """Get all documents for a workspace"""
    return db.query(Document).filter(Document.workspace_id == workspace_id).all()

def create_document(db: Session, document_data: DocumentCreate) -> Document:
    """Create a new document"""
    document = Document(
        workspace_id=document_data.workspace_id,
        doc_type=document_data.doc_type,
        file_path=document_data.file_path,
        filing_date=document_data.filing_date,
        reporting_date=document_data.reporting_date,
        doc_id=document_data.doc_id
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document

def update_document(db: Session, document_id: str, document_data: DocumentUpdate) -> Optional[Document]:
    """Update document by ID"""
    document = get_document_by_id(db, document_id)
    if not document:
        return None

    # Update fields if provided
    if document_data.workspace_id is not None:
        document.workspace_id = document_data.workspace_id
    if document_data.doc_type is not None:
        document.doc_type = document_data.doc_type
    if document_data.file_path is not None:
        document.file_path = document_data.file_path
    if document_data.filing_date is not None:
        document.filing_date = document_data.filing_date
    if document_data.reporting_date is not None:
        document.reporting_date = document_data.reporting_date
    if document_data.doc_id is not None:
        document.doc_id = document_data.doc_id

    db.commit()
    db.refresh(document)
    return document

def delete_document(db: Session, document_id: str) -> bool:
    """Delete document by ID (cascade deletes parsed_documents)"""
    document = get_document_by_id(db, document_id)
    if not document:
        return False

    db.delete(document)
    db.commit()
    return True
