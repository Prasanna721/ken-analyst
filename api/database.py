import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_DIR = os.path.join(os.path.dirname(__file__), "data")
DATABASE_URL = f"sqlite:///{os.path.join(DATABASE_DIR, 'ken-analyst.db')}"

# Ensure data directory exists
os.makedirs(DATABASE_DIR, exist_ok=True)

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    from models import Workspace, Document, ParsedDocument
    Base.metadata.create_all(bind=engine)
