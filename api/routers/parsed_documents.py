from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import ParsedDocumentCreate, ParsedDocumentUpdate, APIResponse
from services import parsed_documents_service

router = APIRouter(prefix="/data/parsed_documents", tags=["parsed_documents"])

@router.get("", response_model=APIResponse)
def get_parsed_documents(db: Session = Depends(get_db)):
    """Get all parsed documents"""
    try:
        parsed_documents = parsed_documents_service.get_all_parsed_documents(db)
        return APIResponse(
            status=200,
            response=[parsed_doc.to_dict() for parsed_doc in parsed_documents]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
def create_parsed_document(
    parsed_document_data: ParsedDocumentCreate,
    db: Session = Depends(get_db)
):
    """Create a new parsed document"""
    try:
        parsed_document = parsed_documents_service.create_parsed_document(db, parsed_document_data)
        return APIResponse(
            status=201,
            response=parsed_document.to_dict()
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

@router.put("/{parsed_document_id}", response_model=APIResponse)
def update_parsed_document(
    parsed_document_id: str,
    parsed_document_data: ParsedDocumentUpdate,
    db: Session = Depends(get_db)
):
    """Update parsed document by ID"""
    try:
        parsed_document = parsed_documents_service.update_parsed_document(db, parsed_document_id, parsed_document_data)
        if not parsed_document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Parsed document with ID '{parsed_document_id}' not found"
            )
        return APIResponse(
            status=200,
            response=parsed_document.to_dict()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/{parsed_document_id}", response_model=APIResponse)
def delete_parsed_document(
    parsed_document_id: str,
    db: Session = Depends(get_db)
):
    """Delete parsed document by ID"""
    try:
        success = parsed_documents_service.delete_parsed_document(db, parsed_document_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Parsed document with ID '{parsed_document_id}' not found"
            )
        return APIResponse(
            status=200,
            response={"message": f"Parsed document '{parsed_document_id}' deleted successfully"}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
