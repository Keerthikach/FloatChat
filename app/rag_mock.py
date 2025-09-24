from random import random
from .models import MCPPayload, MockRAGResponse


def mock_complete_sql(payload: MCPPayload) -> MockRAGResponse:
    f = payload.filters
    where: list[str] = []

    if f.variables:
        var_list = ", ".join(repr(v) for v in f.variables)
        where.append(f"variable IN ({var_list})")

    if f.lat_range:
        lat_lo, lat_hi = f.lat_range
        where.append(f"lat BETWEEN {lat_lo} AND {lat_hi}")

    if f.lon_range:
        lon_lo, lon_hi = f.lon_range
        where.append(f"lon BETWEEN {lon_lo} AND {lon_hi}")

    if f.bbox:
        where.append(
            "(lat BETWEEN "
            f"{f.bbox.min_lat} AND {f.bbox.max_lat} "
            "AND lon BETWEEN "
            f"{f.bbox.min_lon} AND {f.bbox.max_lon})"
        )

    if f.time_range:
        where.append(
            f"time BETWEEN '{f.time_range.start}' AND '{f.time_range.end}'"
        )

    if f.depth_range:
        where.append(
            f"depth BETWEEN {f.depth_range.min_depth} "
            f"AND {f.depth_range.max_depth}"
        )

    sql = (
        "SELECT float_id, time, lat, lon, variable, value "
        "FROM argo_profiles"
    )
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " LIMIT 100;"

    rows = [
        {
            "float_id": "4901234",
            "time": "2023-03-12T05:00:00Z",
            "lat": 1.2,
            "lon": -46.7,
            "variable": (f.variables or ["salinity"])[0],
            "value": 35.1,
        },
        {
            "float_id": "4905678",
            "time": "2023-03-22T07:10:00Z",
            "lat": -0.8,
            "lon": -12.3,
            "variable": (f.variables or ["salinity"])[0],
            "value": 34.9,
        },
    ]

    return MockRAGResponse(
        sql_intent=sql,
        confidence=round(0.7 + 0.3 * random(), 2),
        simulated_rows=rows,
        echoed_payload=payload,
    )

