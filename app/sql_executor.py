# app/sql_executor.py
from __future__ import annotations
import os
import re
from typing import List, Dict, Any
import psycopg2
from psycopg2.extras import RealDictCursor 
from dotenv import load_dotenv

load_dotenv(dotenv_pat="C:\\Users\keert\mcp_mvp\.env") 

DATABASE_URL = os.getenv("DATABASE_URL")
_SELECT_RE = re.compile(r"^\s*select\b", re.IGNORECASE)

def _conn():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL env var is not set")
    # accept both postgresql+psycopg2:// and postgresql://
    url = DATABASE_URL.replace("postgresql+psycopg2://", "postgresql://")
    return psycopg2.connect(url)

def _enforce_safe_select(sql: str, default_limit: int = 200) -> str:
    if not _SELECT_RE.match(sql):
        raise ValueError("Only SELECT queries are allowed.")
    s = sql.strip().rstrip(";")
    if " limit " not in s.lower():
        s += f" LIMIT {default_limit}"
    return s + ";"

def execute_select(sql: str) -> List[Dict[str, Any]]:
    safe = _enforce_safe_select(sql)
    with _conn() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(safe)
        rows = cur.fetchall()
    return [dict(r) for r in rows]
