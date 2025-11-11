from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from database import get_db
from models import AgentCreate, AgentUpdate, APIResponse
from services import agent_service

router = APIRouter(prefix="/data/agent", tags=["agent"])

@router.get("", response_model=APIResponse)
def get_agents(
    workspace_id: str = Query(None, description="Filter by workspace ID"),
    active_only: bool = Query(False, description="Get only active agents"),
    db: Session = Depends(get_db)
):
    """Get all agents, optionally filtered by workspace_id and status"""
    try:
        if workspace_id:
            if active_only:
                agents = agent_service.get_active_agents_by_workspace(db, workspace_id)
            else:
                agents = agent_service.get_agents_by_workspace(db, workspace_id)
        else:
            agents = agent_service.get_all_agents(db)
        return APIResponse(
            status=200,
            response=[agent.to_dict() for agent in agents]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/{agent_id}", response_model=APIResponse)
def get_agent(agent_id: str, db: Session = Depends(get_db)):
    """Get agent by ID"""
    try:
        agent = agent_service.get_agent_by_id(db, agent_id)
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent with ID '{agent_id}' not found"
            )
        return APIResponse(
            status=200,
            response=agent.to_dict()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
def create_agent(
    agent_data: AgentCreate,
    db: Session = Depends(get_db)
):
    """Create a new agent"""
    try:
        agent = agent_service.create_agent(db, agent_data)
        return APIResponse(
            status=201,
            response=agent.to_dict()
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

@router.put("/{agent_id}", response_model=APIResponse)
def update_agent(
    agent_id: str,
    agent_data: AgentUpdate,
    db: Session = Depends(get_db)
):
    """Update agent by ID"""
    try:
        agent = agent_service.update_agent(db, agent_id, agent_data)
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent with ID '{agent_id}' not found"
            )
        return APIResponse(
            status=200,
            response=agent.to_dict()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/{agent_id}", response_model=APIResponse)
def delete_agent(
    agent_id: str,
    db: Session = Depends(get_db)
):
    """Delete agent by ID"""
    try:
        success = agent_service.delete_agent(db, agent_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent with ID '{agent_id}' not found"
            )
        return APIResponse(
            status=200,
            response={"message": f"Agent '{agent_id}' deleted successfully"}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
