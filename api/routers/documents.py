from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import DocumentCreate, DocumentUpdate, APIResponse
from services import documents_service

router = APIRouter(prefix="/data/documents", tags=["documents"])

@router.get("", response_model=APIResponse)
def get_documents(db: Session = Depends(get_db)):
    """Get all documents"""
    try:
        documents = documents_service.get_all_documents(db)
        return APIResponse(
            status=200,
            response=[document.to_dict() for document in documents]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
def create_document(
    document_data: DocumentCreate,
    db: Session = Depends(get_db)
):
    """Create a new document"""
    try:
        document = documents_service.create_document(db, document_data)
        return APIResponse(
            status=201,
            response=document.to_dict()
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/{document_id}", response_model=APIResponse)
def update_document(
    document_id: str,
    document_data: DocumentUpdate,
    db: Session = Depends(get_db)
):
    """Update document by ID"""
    try:
        document = documents_service.update_document(db, document_id, document_data)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with ID '{document_id}' not found"
            )
        return APIResponse(
            status=200,
            response=document.to_dict()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/{document_id}", response_model=APIResponse)
def delete_document(
    document_id: str,
    db: Session = Depends(get_db)
):
    """Delete document by ID (cascade deletes parsed_documents)"""
    try:
        success = documents_service.delete_document(db, document_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with ID '{document_id}' not found"
            )
        return APIResponse(
            status=200,
            response={"message": f"Document '{document_id}' deleted successfully"}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
