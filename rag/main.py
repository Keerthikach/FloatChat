# main.py
from __future__ import annotations
from typing import Any, Dict
from .chain import build_chain, complete_from_mcp


def run_chat() -> None:
    """
    Simple CLI to test: model returns ONLY SQL based on your question + retrieved context.
    """
    qa = build_chain()

    while True:
        try:
            query = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not query:
            continue
        if query.lower() in {"exit", "quit"}:
            break

        # For CLI we don't add filters; MCP path uses complete_from_mcp
        out = qa.invoke({"query": query})
        print("\nSQL:")
        print(out["result"])

        print("\n--- Sources (metadata) ---")
        for doc in out.get("source_documents", []):
            print(doc.metadata)
        print()


def complete(mcp_payload: Dict[str, Any]) -> Dict[str, Any]:
    """Callable from your MCP server if you import this module."""
    return complete_from_mcp(mcp_payload)


if __name__ == "__main__":
    run_chat()
