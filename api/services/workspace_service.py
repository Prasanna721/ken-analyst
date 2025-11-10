import os
import random
from sqlalchemy.orm import Session
from models import Workspace, WorkspaceCreate, WorkspaceUpdate, generate_workspace_id
from typing import List, Optional

# Word lists for generating random workspace names
ADJECTIVES = [
    "agile", "bright", "creative", "dynamic", "elegant", "fresh", "great", "happy",
    "innovative", "joyful", "keen", "lively", "modern", "noble", "optimal", "prime",
    "quick", "radiant", "smart", "trusted", "unique", "vital", "wise", "zesty"
]

NOUNS = [
    "space", "hub", "lab", "zone", "studio", "base", "center", "vault", "forge",
    "workshop", "arena", "chamber", "portal", "nest", "haven", "quarters", "realm"
]

def generate_random_name() -> str:
    """Generate a random workspace name from combination of words"""
    adj = random.choice(ADJECTIVES)
    noun = random.choice(NOUNS)
    return f"{adj.capitalize()} {noun.capitalize()}"

def create_workspace_folder(workspace_id: str) -> str:
    """Create workspace folder in data/{id}"""
    workspace_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "data",
        workspace_id
    )
    os.makedirs(workspace_dir, exist_ok=True)
    return workspace_dir

def get_all_workspaces(db: Session) -> List[Workspace]:
    """Get all workspaces"""
    return db.query(Workspace).all()

def get_workspace_by_id(db: Session, workspace_id: str) -> Optional[Workspace]:
    """Get workspace by ID"""
    return db.query(Workspace).filter(Workspace.id == workspace_id).first()

def create_workspace(db: Session, workspace_data: WorkspaceCreate) -> Workspace:
    """Create a new workspace"""
    # Generate ID if not provided
    workspace_id = workspace_data.id if workspace_data.id else generate_workspace_id()

    # Check if ID already exists
    if get_workspace_by_id(db, workspace_id):
        raise ValueError(f"Workspace with ID '{workspace_id}' already exists")

    # Generate name if not provided
    name = workspace_data.name if workspace_data.name else generate_random_name()

    # Create workspace in database
    workspace = Workspace(
        id=workspace_id,
        name=name,
        ticker=workspace_data.ticker
    )
    db.add(workspace)
    db.commit()
    db.refresh(workspace)

    # Create workspace folder
    create_workspace_folder(workspace_id)

    return workspace

def update_workspace(db: Session, workspace_id: str, workspace_data: WorkspaceUpdate) -> Optional[Workspace]:
    """Update workspace by ID"""
    workspace = get_workspace_by_id(db, workspace_id)
    if not workspace:
        return None

    # Update fields if provided
    if workspace_data.name is not None:
        workspace.name = workspace_data.name
    if workspace_data.ticker is not None:
        workspace.ticker = workspace_data.ticker

    db.commit()
    db.refresh(workspace)
    return workspace

def delete_workspace(db: Session, workspace_id: str) -> bool:
    """Delete workspace by ID"""
    workspace = get_workspace_by_id(db, workspace_id)
    if not workspace:
        return False

    # Delete workspace folder
    workspace_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "data",
        workspace_id
    )
    if os.path.exists(workspace_dir):
        import shutil
        shutil.rmtree(workspace_dir)

    db.delete(workspace)
    db.commit()
    return True
