# retriever.py
from __future__ import annotations
from typing import Any, Dict, Optional

from langchain_chroma import Chroma   # <— NEW import
from langchain_community.embeddings import HuggingFaceEmbeddings

CHROMA_DB_DIR = "chroma_db"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def get_retriever(where: Optional[Dict[str, Any]] = None, k: int = 5):
    """
    Build a LangChain Chroma retriever with optional metadata filtering.

    Pass MCP filters (converted to Chroma 'where') as `where`.
    Example:
      {"lat": {"$gte": -5, "$lte": 5}, "profile_time": {"$gte": "2023-03-01", "$lte": "2023-03-31"}}
    """
    embedding = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
    vectordb = Chroma(persist_directory=CHROMA_DB_DIR, embedding_function=embedding)

    search_kwargs: Dict[str, Any] = {"k": k}
    if where:
        # LangChain forwards this to Chroma as the 'where' filter
        search_kwargs["filter"] = where

    retriever = vectordb.as_retriever(search_type="similarity", search_kwargs=search_kwargs)
    return retriever
