from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from services.data_loader import load_data
from routers import search, filings, workspace, documents, parsed_documents, create_workspace, activity
from routers.documents import documents_router
from database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    load_data()
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search.router)
app.include_router(filings.router)
app.include_router(create_workspace.router)
app.include_router(workspace.router)
app.include_router(documents.router)
app.include_router(documents_router)
app.include_router(parsed_documents.router)
app.include_router(activity.router)
