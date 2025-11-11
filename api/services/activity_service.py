from sqlalchemy.orm import Session
from models import Activity, ActivityCreate, ActivityUpdate
from typing import List, Optional

def get_all_activities(db: Session) -> List[Activity]:
    """Get all activities"""
    return db.query(Activity).order_by(Activity.created_at.desc()).all()

def get_activity_by_id(db: Session, activity_id: str) -> Optional[Activity]:
    """Get activity by ID"""
    return db.query(Activity).filter(Activity.id == activity_id).first()

def get_activities_by_workspace(db: Session, workspace_id: str) -> List[Activity]:
    """Get all activities for a workspace"""
    return db.query(Activity).filter(Activity.workspace_id == workspace_id).order_by(Activity.created_at.desc()).all()

def create_activity(db: Session, activity_data: ActivityCreate) -> Activity:
    """Create a new activity"""
    activity = Activity(
        workspace_id=activity_data.workspace_id,
        category=activity_data.category,
        status=activity_data.status,
        title=activity_data.title,
        message=activity_data.message
    )
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return activity

def update_activity(db: Session, activity_id: str, activity_data: ActivityUpdate) -> Optional[Activity]:
    """Update activity by ID"""
    activity = get_activity_by_id(db, activity_id)
    if not activity:
        return None

    if activity_data.workspace_id is not None:
        activity.workspace_id = activity_data.workspace_id
    if activity_data.category is not None:
        activity.category = activity_data.category
    if activity_data.status is not None:
        activity.status = activity_data.status
    if activity_data.title is not None:
        activity.title = activity_data.title
    if activity_data.message is not None:
        activity.message = activity_data.message

    db.commit()
    db.refresh(activity)
    return activity

def delete_activity(db: Session, activity_id: str) -> bool:
    """Delete activity by ID"""
    activity = get_activity_by_id(db, activity_id)
    if not activity:
        return False

    db.delete(activity)
    db.commit()
    return True
