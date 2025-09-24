from fastapi import APIRouter, Depends, HTTPException
from .security import require_api_key
from .session_store import SimpleSessionStore
from .filter_parser import extract_filters
from .validators import validate_filters
from .rag_mock import mock_complete_sql
from .models import (
    SessionUpsert, SessionContext, QueryRequest, QueryResponse,
    MCPPayload, MockRAGRequest, MockRAGResponse
)

router = APIRouter()

# Single, simple in-memory store for the whole app
_store = SimpleSessionStore()

@router.get("/health")
def health():
    return {"status": "ok"}

@router.post("/context", response_model=SessionContext, dependencies=[Depends(require_api_key)])
def upsert_context(upsert: SessionUpsert):
    return _store.create_or_update(upsert)

@router.get("/session/{session_id}", response_model=SessionContext, dependencies=[Depends(require_api_key)])
def get_session(session_id: str):
    ctx = _store.get(session_id)
    if not ctx:
        raise HTTPException(status_code=404, detail="Session not found")
    return ctx

@router.post("/query", response_model=QueryResponse, dependencies=[Depends(require_api_key)])
def query(body: QueryRequest):
    # Resolve/create session on the fly for MVP
    ctx = _store.create_or_update(SessionUpsert(session_id=body.session_id))
    filters = extract_filters(body.query)
    try:
        validate_filters(filters)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    payload = MCPPayload(
        session_id=ctx.session_id,
        query=body.query,
        filters=filters,
        metadata={"vector_schema_hint": ["float_id","profile_time","lat","lon","variables","depth_range"]},
        sql_intent=None
    )
    return QueryResponse(mcp_payload=payload)

@router.post("/admin/mock_rag", response_model=MockRAGResponse, dependencies=[Depends(require_api_key)])
def admin_mock_rag(body: MockRAGRequest):
    return mock_complete_sql(body.mcp_payload)
