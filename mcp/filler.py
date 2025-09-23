from .contract import MCPExample
import random
from datetime import datetime, timedelta

def generate_mcp(user_query: str):
    """
    Generates mock MCP payload with fake rows and SQL intent.
    """
    mcp_payload = MCPExample.copy()
    mcp_payload["query"] = user_query
    mcp_payload["sql_intent"] = f"SELECT * FROM argo_profiles WHERE query LIKE '%{user_query}%' LIMIT 5;"
    
    # Simulate some rows
    simulated_rows = []
    for i in range(3):
        row = {
            "float_id": f"{random.randint(1000000, 9999999)}",
            "profile_time": (datetime.utcnow() - timedelta(days=random.randint(0, 365))).isoformat() + "Z",
            "lat": round(random.uniform(-5, 5), 2),
            "lon": round(random.uniform(-180, 180), 2),
            "variables": "temperature,salinity",
            "depth_range": "0.0,2000.0",
            "value": round(random.uniform(0, 35), 2)
        }
        simulated_rows.append(row)
    
    mcp_payload["simulated_rows"] = simulated_rows
    return mcp_payload
