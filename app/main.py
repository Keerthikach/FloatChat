from fastapi import FastAPI
from app.routers import router

app = FastAPI(
    title="ARGO MCP Server - MVP",
    description="Ultra-minimal PoC MCP server with in-memory session and mock RAG.",
    version="0.0.1",
)

app.include_router(router)

# Run: uvicorn app.main:app --reload --port 8000