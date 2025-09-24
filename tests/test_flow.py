from fastapi.testclient import TestClient
from app.main import app

API = {"X-API-Key": "dev-key"}

def test_context_query_mockrag_flow():
    c = TestClient(app)
    # upsert context
    r = c.post("/context", headers=API, json={"user_id":"u1"})
    assert r.status_code == 200
    sid = r.json()["session_id"]

    # query
    r2 = c.post("/query", headers=API, json={"session_id": sid, "query": "Show salinity near the equator in March 2023"})
    assert r2.status_code == 200
    payload = r2.json()["mcp_payload"]
    assert payload["session_id"] == sid
    assert "salinity" in (payload["filters"]["variables"] or [])
    assert payload["filters"]["lat_range"] == [-5.0, 5.0]
    assert payload["filters"]["time_range"]["start"] == "2023-03-01"

    # mock rag
    r3 = c.post("/admin/mock_rag", headers=API, json={"mcp_payload": payload})
    assert r3.status_code == 200
    assert "SELECT" in r3.json()["sql_intent"]
