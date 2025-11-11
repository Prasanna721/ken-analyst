from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import WorkspaceCreate, WorkspaceUpdate, APIResponse
from services import workspace_service

router = APIRouter(prefix="/data/workspace", tags=["workspace"])

@router.get("", response_model=APIResponse)
def get_workspaces(db: Session = Depends(get_db)):
    """Get all workspaces"""
    try:
        workspaces = workspace_service.get_all_workspaces(db)
        return APIResponse(
            status=200,
            response=[workspace.to_dict() for workspace in workspaces]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/{workspace_id}", response_model=APIResponse)
def get_workspace(workspace_id: str, db: Session = Depends(get_db)):
    """Get workspace by ID"""
    try:
        workspace = workspace_service.get_workspace_by_id(db, workspace_id)
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workspace with ID '{workspace_id}' not found"
            )
        return APIResponse(
            status=200,
            response=workspace.to_dict()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
def create_workspace(
    workspace_data: WorkspaceCreate,
    db: Session = Depends(get_db)
):
    """Create a new workspace"""
    try:
        workspace = workspace_service.create_workspace(db, workspace_data)
        return APIResponse(
            status=201,
            response=workspace.to_dict()
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

@router.put("/{workspace_id}", response_model=APIResponse)
def update_workspace(
    workspace_id: str,
    workspace_data: WorkspaceUpdate,
    db: Session = Depends(get_db)
):
    """Update workspace by ID"""
    try:
        workspace = workspace_service.update_workspace(db, workspace_id, workspace_data)
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workspace with ID '{workspace_id}' not found"
            )
        return APIResponse(
            status=200,
            response=workspace.to_dict()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/{workspace_id}", response_model=APIResponse)
def delete_workspace(
    workspace_id: str,
    db: Session = Depends(get_db)
):
    """Delete workspace by ID"""
    try:
        success = workspace_service.delete_workspace(db, workspace_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workspace with ID '{workspace_id}' not found"
            )
        return APIResponse(
            status=200,
            response={"message": f"Workspace '{workspace_id}' deleted successfully"}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
