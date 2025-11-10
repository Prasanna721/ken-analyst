from sqlalchemy.orm import Session
from models import ParsedDocument, ParsedDocumentCreate, ParsedDocumentUpdate
from typing import List, Optional

def get_all_parsed_documents(db: Session) -> List[ParsedDocument]:
    """Get all parsed documents"""
    return db.query(ParsedDocument).all()

def get_parsed_document_by_id(db: Session, parsed_document_id: str) -> Optional[ParsedDocument]:
    """Get parsed document by ID"""
    return db.query(ParsedDocument).filter(ParsedDocument.id == parsed_document_id).first()

def get_parsed_documents_by_workspace(db: Session, workspace_id: str) -> List[ParsedDocument]:
    """Get all parsed documents for a workspace"""
    return db.query(ParsedDocument).filter(ParsedDocument.workspace_id == workspace_id).all()

def get_parsed_documents_by_document(db: Session, document_id: str) -> List[ParsedDocument]:
    """Get all parsed documents for a document"""
    return db.query(ParsedDocument).filter(ParsedDocument.documents_id == document_id).all()

def create_parsed_document(db: Session, parsed_document_data: ParsedDocumentCreate) -> ParsedDocument:
    """Create a new parsed document"""
    parsed_document = ParsedDocument(
        workspace_id=parsed_document_data.workspace_id,
        documents_id=parsed_document_data.documents_id,
        filepath=parsed_document_data.filepath
    )
    db.add(parsed_document)
    db.commit()
    db.refresh(parsed_document)
    return parsed_document

def update_parsed_document(db: Session, parsed_document_id: str, parsed_document_data: ParsedDocumentUpdate) -> Optional[ParsedDocument]:
    """Update parsed document by ID"""
    parsed_document = get_parsed_document_by_id(db, parsed_document_id)
    if not parsed_document:
        return None

    # Update fields if provided
    if parsed_document_data.workspace_id is not None:
        parsed_document.workspace_id = parsed_document_data.workspace_id
    if parsed_document_data.documents_id is not None:
        parsed_document.documents_id = parsed_document_data.documents_id
    if parsed_document_data.filepath is not None:
        parsed_document.filepath = parsed_document_data.filepath

    db.commit()
    db.refresh(parsed_document)
    return parsed_document

def delete_parsed_document(db: Session, parsed_document_id: str) -> bool:
    """Delete parsed document by ID"""
    parsed_document = get_parsed_document_by_id(db, parsed_document_id)
    if not parsed_document:
        return False

    db.delete(parsed_document)
    db.commit()
    return True
