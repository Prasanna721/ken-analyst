from typing import Any, Optional
from pydantic import BaseModel
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Enum
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

class Workspace(Base):
    __tablename__ = "workspaces"

    id = Column(String(8), primary_key=True, default=generate_workspace_id)
    name = Column(String, nullable=False)
    ticker = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships with cascade delete
    documents = relationship("Document", back_populates="workspace", cascade="all, delete-orphan")
    parsed_documents = relationship("ParsedDocument", back_populates="workspace", cascade="all, delete-orphan")

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

    # Relationships
    workspace = relationship("Workspace", back_populates="parsed_documents")
    document = relationship("Document", back_populates="parsed_documents")

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "workspace_id": self.workspace_id,
            "documents_id": self.documents_id,
            "filepath": self.filepath
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

class ParsedDocumentUpdate(BaseModel):
    workspace_id: Optional[str] = None
    documents_id: Optional[str] = None
    filepath: Optional[str] = None
