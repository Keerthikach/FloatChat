MCPExample = {
    "session_id": "demo-session",
    "query": "user query here",
    "filters": {
        "variables": ["temperature", "salinity"],
        "time_range": {"start": "2023-01-01", "end": "2023-01-31"},
        "depth_range": {"min_depth": 0.0, "max_depth": 2000.0},
        "lat_range": [-90.0, 90.0],
        "lon_range": [-180.0, 180.0]
    },
    "metadata": {
        "vector_schema_hint": ["float_id","profile_time","lat","lon","variables","depth_range"]
    },
    "sql_intent": None  # to be filled by MCP layer
}
