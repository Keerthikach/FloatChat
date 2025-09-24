# chain.py
from __future__ import annotations
from typing import Any, Dict, Optional
import json

from langchain.chains import RetrievalQA
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from .retriever import get_retriever


def filters_to_chroma_where(filters: Dict[str, Any]) -> Dict[str, Any]:
    """Convert MCP ARGOFilters to a Chroma 'where' filter."""
    where: Dict[str, Any] = {}

    lat_range = filters.get("lat_range")
    if lat_range and len(lat_range) == 2:
        lo, hi = float(lat_range[0]), float(lat_range[1])
        where["lat"] = {"$gte": lo, "$lte": hi}

    lon_range = filters.get("lon_range")
    if lon_range and len(lon_range) == 2:
        lo, hi = float(lon_range[0]), float(lon_range[1])
        where["lon"] = {"$gte": lo, "$lte": hi}

    time_range = filters.get("time_range")
    if isinstance(time_range, dict) and "start" in time_range and "end" in time_range:
        where["profile_time"] = {"$gte": str(time_range["start"]), "$lte": str(time_range["end"])}

    # If your metadata stores variables as a LIST, you could add:
    # if filters.get("variables"):
    #     where["variables"] = {"$in": filters["variables"]}

    return where


# IMPORTANT: RetrievalQA expects {question} and injects {context}. Do NOT use {query} or {filters} here.
SQL_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an expert ocean data assistant. "
            "Given a user question and context snippets, output ONE valid PostgreSQL SQL statement "
            "for table argo_profiles with columns: latitude, longitude, depth, time, variable, value, float_id. "
            "Rules:\n"
            "• Apply any constraints present in the question (lat/lon ranges, time_range, variables, depth_range).\n"
            "• Use BETWEEN for numeric/date ranges.\n"
            "• Return ONLY the SQL. No commentary.\n"
            "• LIMIT 200 rows."
        ),
        (
            "human",
            "Question:\n{question}\n\nContext:\n{context}\n\nSQL:",
        ),
    ]
)


def build_chain(
    where: Optional[Dict[str, Any]] = None,
    k: int = 5,
    model: str = "llama3.1",
    temperature: float = 0.0,
) -> RetrievalQA:
    """
    Build a RetrievalQA chain using:
      - Chroma retriever with metadata filter (where)
      - Ollama LLM
      - SQL-only prompt
    """
    retriever = get_retriever(where=where, k=k)
    llm = OllamaLLM(model=model, temperature=temperature)

    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": SQL_PROMPT},  # RetrievalQA will supply {question} and {context}
    )
    return chain


def _question_with_filters(query: str, filters: Dict[str, Any]) -> str:
    """
    Embed the MCP filters into the natural-language question so the LLM can honor them.
    RetrievalQA won't pass extra variables to the prompt, so we put them inside the question text.
    """
    if not filters:
        return query
    return f"{query}\n\nFilters (JSON): {json.dumps(filters, ensure_ascii=False)}"


def complete_from_mcp(mcp_payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    For MCP:
      - Build Chroma 'where' from MCP filters
      - Build RetrievalQA
      - Invoke with a 'question' that includes the filters in JSON
      - Return ONLY the SQL produced by the LLM
    """
    query = mcp_payload.get("query", "")
    filters = mcp_payload.get("filters", {}) or {}

    where = filters_to_chroma_where(filters)
    qa = build_chain(where=where, k=5, model="llama3.1", temperature=0.0)

    # RetrievalQA expects key 'query' OR 'question' depending on version; .invoke({"query": ...}) maps to 'question'
    question = _question_with_filters(query, filters)
    result = qa.invoke({"query": question})

    # SQL-only output lives in result["result"] by design of our prompt
    sql_text = result["result"]
    return {
        "sql_intent": sql_text,
        "source_documents": result.get("source_documents", []),
        "echoed_payload": mcp_payload,
    }


#$env:OLLAMA_HOST="http://localhost:11434"
