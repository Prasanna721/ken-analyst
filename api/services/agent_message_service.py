from sqlalchemy.orm import Session
from models import AgentMessage, AgentMessageCreate, AgentMessageUpdate
from typing import List, Optional

def get_all_messages(db: Session) -> List[AgentMessage]:
    """Get all agent messages"""
    return db.query(AgentMessage).order_by(AgentMessage.timestamp.asc()).all()

def get_message_by_id(db: Session, message_id: str) -> Optional[AgentMessage]:
    """Get message by ID"""
    return db.query(AgentMessage).filter(AgentMessage.id == message_id).first()

def get_messages_by_agent(db: Session, agent_id: str) -> List[AgentMessage]:
    """Get all messages for an agent"""
    return db.query(AgentMessage).filter(AgentMessage.agent_id == agent_id).order_by(AgentMessage.timestamp.asc()).all()

def create_message(db: Session, message_data: AgentMessageCreate) -> AgentMessage:
    """Create a new agent message"""
    message = AgentMessage(
        agent_id=message_data.agent_id,
        role=message_data.role,
        message=message_data.message
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message

def update_message(db: Session, message_id: str, message_data: AgentMessageUpdate) -> Optional[AgentMessage]:
    """Update message by ID"""
    message = get_message_by_id(db, message_id)
    if not message:
        return None

    if message_data.role is not None:
        message.role = message_data.role
    if message_data.message is not None:
        message.message = message_data.message

    db.commit()
    db.refresh(message)
    return message

def delete_message(db: Session, message_id: str) -> bool:
    """Delete message by ID"""
    message = get_message_by_id(db, message_id)
    if not message:
        return False

    db.delete(message)
    db.commit()
    return True
