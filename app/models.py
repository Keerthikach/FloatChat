from pydantic import BaseModel, Field, field_validator
from typing import Any, Literal
from datetime import datetime, date

# -------- Core filter shapes --------
class BBox(BaseModel):
    min_lon: float = Field(..., ge=-180, le=180)
    min_lat: float = Field(..., ge=-90,  le=90)
    max_lon: float = Field(..., ge=-180, le=180)
    max_lat: float = Field(..., ge=-90,  le=90)

    @field_validator("max_lon")
    @classmethod
    def check_lon(cls, v, info):
        if info.data.get("min_lon") is not None and v < info.data["min_lon"]:
            raise ValueError("max_lon must be >= min_lon")
        return v

    @field_validator("max_lat")
    @classmethod
    def check_lat(cls, v, info):
        if info.data.get("min_lat") is not None and v < info.data["min_lat"]:
            raise ValueError("max_lat must be >= min_lat")
        return v

class TimeRange(BaseModel):
    start: date
    end: date
    @field_validator("end")
    @classmethod
    def order(cls, v, info):
        if info.data.get("start") and v < info.data["start"]:
            raise ValueError("end must be >= start")
        return v

class DepthRange(BaseModel):
    min_depth: float = Field(..., ge=0)
    max_depth: float = Field(..., ge=0)
    @field_validator("max_depth")
    @classmethod
    def dorder(cls, v, info):
        if info.data.get("min_depth") and v < info.data["min_depth"]:
            raise ValueError("max_depth must be >= min_depth")
        return v

class ARGOFilters(BaseModel):
    variables: list[str] | None = None
    bbox: BBox | None = None
    time_range: TimeRange | None = None
    depth_range: DepthRange | None = None
    float_ids: list[str] | None = None
    qc_flags: list[int] | None = None
    lat_range: tuple[float, float] | None = None
    lon_range: tuple[float, float] | None = None

# -------- Session --------
class SessionContext(BaseModel):
    session_id: str
    user_id: str | None = None
    preferred_units: Literal["metric","imperial"] = "metric"
    notes: str | None = None
    created_at: datetime
    updated_at: datetime

class SessionUpsert(BaseModel):
    session_id: str | None = None
    user_id: str | None = None
    preferred_units: Literal["metric","imperial"] | None = None
    notes: str | None = None

# -------- Query/MCP payload --------
class QueryRequest(BaseModel):
    session_id: str | None = None
    query: str

class MCPPayload(BaseModel):
    session_id: str
    query: str
    filters: ARGOFilters
    metadata: dict[str, Any] = Field(default_factory=dict)
    sql_intent: str | None = None

class QueryResponse(BaseModel):
    mcp_payload: MCPPayload

# -------- Mock RAG --------
class MockRAGRequest(BaseModel):
    mcp_payload: MCPPayload

class MockRAGResponse(BaseModel):
    sql_intent: str
    confidence: float
    simulated_rows: list[dict[str, Any]]
    echoed_payload: MCPPayload
