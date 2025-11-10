from fastapi import FastAPI
from contextlib import asynccontextmanager
from services.data_loader import load_data
from routers import search, filings, workspace, documents, parsed_documents, create_workspace
from database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database
    init_db()
    # Load CSV data
    load_data()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(search.router)
app.include_router(filings.router)
app.include_router(create_workspace.router)
app.include_router(workspace.router)
app.include_router(documents.router)
app.include_router(parsed_documents.router)
