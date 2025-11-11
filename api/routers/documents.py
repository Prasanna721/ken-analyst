from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import FileResponse, Response
from sqlalchemy.orm import Session
from database import get_db
from models import DocumentCreate, DocumentUpdate, APIResponse
from services import documents_service
from typing import Optional
import os
import mimetypes

router = APIRouter(prefix="/data/documents", tags=["documents"])

documents_router = APIRouter(prefix="/documents", tags=["documents"])

@documents_router.get("", response_model=APIResponse)
def get_documents_by_workspace_id(
    workspace_id: str = Query(..., description="Workspace ID to filter documents"),
    db: Session = Depends(get_db)
):
    """Get all documents for a specific workspace"""
    try:
        documents = documents_service.get_documents_by_workspace(db, workspace_id)
        return APIResponse(
            status=200,
            response=[document.to_dict() for document in documents]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@documents_router.get("/{document_id}/download")
def download_document(
    document_id: str,
    db: Session = Depends(get_db)
):
    """Serve document file for viewing (not downloading)"""
    try:
        from services import parsed_documents_service
        import json

        document = documents_service.get_document_by_id(db, document_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with ID '{document_id}' not found"
            )

        # Check if there's a parsed document
        parsed_docs = parsed_documents_service.get_parsed_documents_by_document(db, document_id)
        if parsed_docs and len(parsed_docs) > 0:
            parsed_doc = parsed_docs[0]
            if parsed_doc.status and os.path.exists(parsed_doc.filepath):
                # Return parsed JSON content
                with open(parsed_doc.filepath, 'r') as f:
                    json_content = json.load(f)

                return Response(
                    content=json.dumps(json_content),
                    media_type='application/json',
                    headers={
                        'Content-Disposition': 'inline',
                        'Cache-Control': 'no-cache'
                    }
                )

        # Fall back to original document
        file_path = document.file_path
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File not found at path: {file_path}"
            )

        # Read file content
        with open(file_path, 'rb') as f:
            content = f.read()

        # Determine content type
        filename = os.path.basename(file_path)
        ext = os.path.splitext(filename)[1].lower()

        if ext == '.pdf':
            media_type = 'application/pdf'
        elif ext == '.txt':
            media_type = 'text/plain; charset=utf-8'
        else:
            # Try to guess from mimetypes
            guessed_type = mimetypes.guess_type(filename)[0]
            media_type = guessed_type if guessed_type else 'text/plain'

        # Return file content with proper headers for inline display
        return Response(
            content=content,
            media_type=media_type,
            headers={
                'Content-Disposition': f'inline; filename="{filename}"',
                'Cache-Control': 'no-cache'
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

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
