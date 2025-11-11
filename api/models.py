from typing import Any, Optional
from pydantic import BaseModel
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Enum, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
import random
import string
import enum

class APIResponse(BaseModel):
    status: int
    response: Any

def generate_workspace_id():
    """Generate a unique 8 character alphanumeric ID (case sensitive)"""
    chars = string.ascii_letters + string.digits  # a-z, A-Z, 0-9
    return ''.join(random.choice(chars) for _ in range(8))

def generate_id():
    """Generate a unique ID"""
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(12))

class DocTypeEnum(str, enum.Enum):
    TEN_Q = "10_Q"
    TEN_K = "10_K"
    OTHER = "other"

class ActivityCategory(str, enum.Enum):
    MAIN = "main"
    SUB = "sub"

class Workspace(Base):
    __tablename__ = "workspaces"

    id = Column(String(8), primary_key=True, default=generate_workspace_id)
    name = Column(String, nullable=False)
    ticker = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships with cascade delete
    documents = relationship("Document", back_populates="workspace", cascade="all, delete-orphan")
    parsed_documents = relationship("ParsedDocument", back_populates="workspace", cascade="all, delete-orphan")
    activities = relationship("Activity", back_populates="workspace", cascade="all, delete-orphan")
    agents = relationship("Agent", back_populates="workspace", cascade="all, delete-orphan")

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "ticker": self.ticker,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class Document(Base):
    __tablename__ = "documents"

    id = Column(String(12), primary_key=True, default=generate_id)
    workspace_id = Column(String(8), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    doc_type = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    filing_date = Column(String, nullable=True)  # YYYY/MM/DD format
    reporting_date = Column(String, nullable=True)  # YYYY/MM/DD format
    doc_id = Column(String, nullable=True)

    # Relationships
    workspace = relationship("Workspace", back_populates="documents")
    parsed_documents = relationship("ParsedDocument", back_populates="document", cascade="all, delete-orphan")

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "workspace_id": self.workspace_id,
            "doc_type": self.doc_type,
            "file_path": self.file_path,
            "filing_date": self.filing_date,
            "reporting_date": self.reporting_date,
            "doc_id": self.doc_id
        }

class ParsedDocument(Base):
    __tablename__ = "parsed_documents"

    id = Column(String(12), primary_key=True, default=generate_id)
    workspace_id = Column(String(8), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    documents_id = Column(String(12), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    filepath = Column(String, nullable=False)
    status = Column(Boolean, default=False, nullable=False)

    # Relationships
    workspace = relationship("Workspace", back_populates="parsed_documents")
    document = relationship("Document", back_populates="parsed_documents")

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "workspace_id": self.workspace_id,
            "documents_id": self.documents_id,
            "filepath": self.filepath,
            "status": self.status
        }

class Activity(Base):
    __tablename__ = "activity"

    id = Column(String(12), primary_key=True, default=generate_id)
    workspace_id = Column(String(8), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    category = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    status = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)

    # Relationships
    workspace = relationship("Workspace", back_populates="activities")

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "workspace_id": self.workspace_id,
            "category": self.category,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "status": self.status,
            "title": self.title,
            "message": self.message
        }

class Agent(Base):
    __tablename__ = "agents"

    id = Column(String(12), primary_key=True, default=generate_id)
    workspace_id = Column(String(8), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    status = Column(String, nullable=False, default="active")  # active, inactive, completed
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    workspace = relationship("Workspace", back_populates="agents")
    messages = relationship("AgentMessage", back_populates="agent", cascade="all, delete-orphan")

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "workspace_id": self.workspace_id,
            "name": self.name,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class AgentMessage(Base):
    __tablename__ = "agent_messages"

    id = Column(String(12), primary_key=True, default=generate_id)
    agent_id = Column(String(12), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    role = Column(String, nullable=False)  # user, assistant, system
    message = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    agent = relationship("Agent", back_populates="messages")

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "role": self.role,
            "message": self.message,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }

# Pydantic models for API
class WorkspaceCreate(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    ticker: str

class WorkspaceUpdate(BaseModel):
    name: Optional[str] = None
    ticker: Optional[str] = None

class DocumentCreate(BaseModel):
    workspace_id: str
    doc_type: str
    file_path: str
    filing_date: Optional[str] = None
    reporting_date: Optional[str] = None
    doc_id: Optional[str] = None

class DocumentUpdate(BaseModel):
    workspace_id: Optional[str] = None
    doc_type: Optional[str] = None
    file_path: Optional[str] = None
    filing_date: Optional[str] = None
    reporting_date: Optional[str] = None
    doc_id: Optional[str] = None

class ParsedDocumentCreate(BaseModel):
    workspace_id: str
    documents_id: str
    filepath: str
    status: Optional[bool] = False

class ParsedDocumentUpdate(BaseModel):
    workspace_id: Optional[str] = None
    documents_id: Optional[str] = None
    filepath: Optional[str] = None
    status: Optional[bool] = None

class ActivityCreate(BaseModel):
    workspace_id: str
    category: str
    status: int
    title: str
    message: str

class ActivityUpdate(BaseModel):
    workspace_id: Optional[str] = None
    category: Optional[str] = None
    status: Optional[int] = None
    title: Optional[str] = None
    message: Optional[str] = None

class AgentCreate(BaseModel):
    workspace_id: str
    name: str
    status: Optional[str] = "active"

class AgentUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None

class AgentMessageCreate(BaseModel):
    agent_id: str
    role: str
    message: str

class AgentMessageUpdate(BaseModel):
    role: Optional[str] = None
    message: Optional[str] = None
