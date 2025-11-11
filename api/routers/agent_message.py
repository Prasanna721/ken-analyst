from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from database import get_db
from models import AgentMessageCreate, AgentMessageUpdate, APIResponse
from services import agent_message_service

router = APIRouter(prefix="/data/agent_message", tags=["agent_message"])

@router.get("", response_model=APIResponse)
def get_messages(
    agent_id: str = Query(None, description="Filter by agent ID"),
    db: Session = Depends(get_db)
):
    """Get all messages, optionally filtered by agent_id"""
    try:
        if agent_id:
            messages = agent_message_service.get_messages_by_agent(db, agent_id)
        else:
            messages = agent_message_service.get_all_messages(db)
        return APIResponse(
            status=200,
            response=[message.to_dict() for message in messages]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/{message_id}", response_model=APIResponse)
def get_message(message_id: str, db: Session = Depends(get_db)):
    """Get message by ID"""
    try:
        message = agent_message_service.get_message_by_id(db, message_id)
        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Message with ID '{message_id}' not found"
            )
        return APIResponse(
            status=200,
            response=message.to_dict()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
def create_message(
    message_data: AgentMessageCreate,
    db: Session = Depends(get_db)
):
    """Create a new message"""
    try:
        message = agent_message_service.create_message(db, message_data)
        return APIResponse(
            status=201,
            response=message.to_dict()
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

@router.put("/{message_id}", response_model=APIResponse)
def update_message(
    message_id: str,
    message_data: AgentMessageUpdate,
    db: Session = Depends(get_db)
):
    """Update message by ID"""
    try:
        message = agent_message_service.update_message(db, message_id, message_data)
        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Message with ID '{message_id}' not found"
            )
        return APIResponse(
            status=200,
            response=message.to_dict()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/{message_id}", response_model=APIResponse)
def delete_message(
    message_id: str,
    db: Session = Depends(get_db)
):
    """Delete message by ID"""
    try:
        success = agent_message_service.delete_message(db, message_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Message with ID '{message_id}' not found"
            )
        return APIResponse(
            status=200,
            response={"message": f"Message '{message_id}' deleted successfully"}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
