from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import ActivityCreate, ActivityUpdate, APIResponse
from services import activity_service

router = APIRouter(prefix="/data/activity", tags=["activity"])

@router.get("", response_model=APIResponse)
def get_activities(db: Session = Depends(get_db)):
    """Get all activities"""
    try:
        activities = activity_service.get_all_activities(db)
        return APIResponse(
            status=200,
            response=[activity.to_dict() for activity in activities]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/{activity_id}", response_model=APIResponse)
def get_activity(activity_id: str, db: Session = Depends(get_db)):
    """Get activity by ID"""
    try:
        activity = activity_service.get_activity_by_id(db, activity_id)
        if not activity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Activity with ID '{activity_id}' not found"
            )
        return APIResponse(
            status=200,
            response=activity.to_dict()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
def create_activity(
    activity_data: ActivityCreate,
    db: Session = Depends(get_db)
):
    """Create a new activity"""
    try:
        activity = activity_service.create_activity(db, activity_data)
        return APIResponse(
            status=201,
            response=activity.to_dict()
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

@router.put("/{activity_id}", response_model=APIResponse)
def update_activity(
    activity_id: str,
    activity_data: ActivityUpdate,
    db: Session = Depends(get_db)
):
    """Update activity by ID"""
    try:
        activity = activity_service.update_activity(db, activity_id, activity_data)
        if not activity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Activity with ID '{activity_id}' not found"
            )
        return APIResponse(
            status=200,
            response=activity.to_dict()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/{activity_id}", response_model=APIResponse)
def delete_activity(
    activity_id: str,
    db: Session = Depends(get_db)
):
    """Delete activity by ID"""
    try:
        success = activity_service.delete_activity(db, activity_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Activity with ID '{activity_id}' not found"
            )
        return APIResponse(
            status=200,
            response={"message": f"Activity '{activity_id}' deleted successfully"}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
