# app/routers.py
from __future__ import annotations
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException

from .security import require_api_key
from .session_store import SimpleSessionStore
from .filter_parser import extract_filters
from .validators import validate_filters
from .rag_mock import mock_complete_sql
from .sql_executor import execute_select  # <-- NEW: your PG executor

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
    """
    Builds and returns the MCP payload only (no RAG, no DB). Useful for debugging.
    """
    # Resolve/create session on the fly for MVP
    ctx = _store.create_or_update(SessionUpsert(session_id=body.session_id))

    # Extract + validate filters
    filters = extract_filters(body.query)
    try:
        validate_filters(filters)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    payload = MCPPayload(
        session_id=ctx.session_id,
        query=body.query,
        filters=filters,
        metadata={"vector_schema_hint": ["float_id", "profile_time", "lat", "lon", "variables", "depth_range"]},
        sql_intent=None,
    )
    return QueryResponse(mcp_payload=payload)


@router.post("/admin/mock_rag", response_model=MockRAGResponse, dependencies=[Depends(require_api_key)])
def admin_mock_rag(body: MockRAGRequest):
    return mock_complete_sql(body.mcp_payload)


# ---------- NEW: one-shot end-to-end route (MCP -> RAG -> Postgres) ----------
@router.post("/query+execute", dependencies=[Depends(require_api_key)])
def query_and_execute(body: QueryRequest):
    """
    End-to-end flow in one call:
      1) Build MCP payload (session + filters)
      2) Call RAG to get SQL (uses real RAG if available, else mock)
      3) Execute SQL on Postgres (SELECT-only; LIMIT enforced)
      4) Return rows + SQL + sources

    Request body = QueryRequest (same as /query)
    """
    # 1) Build MCP payload (same as /query)
    ctx = _store.create_or_update(SessionUpsert(session_id=body.session_id))

    filters = extract_filters(body.query)
    try:
        validate_filters(filters)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    mcp_payload = MCPPayload(
        session_id=ctx.session_id,
        query=body.query,
        filters=filters,
        metadata={"vector_schema_hint": ["float_id", "profile_time", "lat", "lon", "variables", "depth_range"]},
        sql_intent=None,
    )

    # 2) RAG -> SQL (prefer real RAG if installed/importable; else mock)
    try:
        # Try the real RAG adapter you wired (rag/chain.py)
        from rag.chain import complete_from_mcp  # type: ignore
        rag_resp = complete_from_mcp(mcp_payload.model_dump(mode="json"))
        sql = rag_resp.get("sql_intent")
        if not sql:
            raise RuntimeError("RAG did not return sql_intent")
    except Exception:
        # Fallback to the existing mock for local dev
        mock = mock_complete_sql(mcp_payload)
        sql = mock.sql_intent
        rag_resp = {
            "sql_intent": sql,
            "confidence": getattr(mock, "confidence", None),
            "source_documents": [],
            "echoed_payload": mcp_payload.model_dump(mode="json"),
        }

    # 3) Execute SQL on Postgres
    try:
        rows = execute_select(sql)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"DB error: {e}")

    # 4) Respond to UI
    return {
        "sql": sql,
        "row_count": len(rows),
        "rows": rows,
        "source_documents": rag_resp.get("source_documents", []),
        "echoed_payload": rag_resp.get("echoed_payload", mcp_payload.model_dump(mode="json")),
    }
