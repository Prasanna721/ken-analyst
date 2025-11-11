from sqlalchemy.orm import Session
from models import Agent, AgentCreate, AgentUpdate
from typing import List, Optional

def get_all_agents(db: Session) -> List[Agent]:
    """Get all agents"""
    return db.query(Agent).order_by(Agent.created_at.desc()).all()

def get_agent_by_id(db: Session, agent_id: str) -> Optional[Agent]:
    """Get agent by ID"""
    return db.query(Agent).filter(Agent.id == agent_id).first()

def get_agents_by_workspace(db: Session, workspace_id: str) -> List[Agent]:
    """Get all agents for a workspace"""
    return db.query(Agent).filter(Agent.workspace_id == workspace_id).order_by(Agent.created_at.desc()).all()

def get_active_agents_by_workspace(db: Session, workspace_id: str) -> List[Agent]:
    """Get all active agents for a workspace"""
    return db.query(Agent).filter(
        Agent.workspace_id == workspace_id,
        Agent.status == "active"
    ).order_by(Agent.created_at.desc()).all()

def create_agent(db: Session, agent_data: AgentCreate) -> Agent:
    """Create a new agent"""
    agent = Agent(
        workspace_id=agent_data.workspace_id,
        name=agent_data.name,
        status=agent_data.status if agent_data.status else "active"
    )
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return agent

def update_agent(db: Session, agent_id: str, agent_data: AgentUpdate) -> Optional[Agent]:
    """Update agent by ID"""
    agent = get_agent_by_id(db, agent_id)
    if not agent:
        return None

    if agent_data.name is not None:
        agent.name = agent_data.name
    if agent_data.status is not None:
        agent.status = agent_data.status

    db.commit()
    db.refresh(agent)
    return agent

def delete_agent(db: Session, agent_id: str) -> bool:
    """Delete agent by ID"""
    agent = get_agent_by_id(db, agent_id)
    if not agent:
        return False

    db.delete(agent)
    db.commit()
    return True
