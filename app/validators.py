from .models import ARGOFilters, BBox
from .settings import settings

def validate_filters(f: ARGOFilters) -> None:
    if f.variables:
        bad = [v for v in f.variables if v not in settings.allowed_variables]
        if bad:
            raise ValueError(f"Variables not allowed: {bad}. Allowed: {settings.allowed_variables}")

    if f.bbox:
        b: BBox = f.bbox
        area = (b.max_lat - b.min_lat) * (b.max_lon - b.min_lon)
        if area > settings.max_bbox_area_deg2:
            raise ValueError(f"BBox area too large (> {settings.max_bbox_area_deg2})")

    if f.time_range:
        days = (f.time_range.end - f.time_range.start).days
        if days / 365.25 > settings.max_date_years:
            raise ValueError(f"Date range too long (> {settings.max_date_years} years)")

    if f.lat_range:
        a,b = f.lat_range
        if not (-90 <= a <= 90 and -90 <= b <= 90) or b < a:
            raise ValueError("Invalid lat_range")
    if f.lon_range:
        a,b = f.lon_range
        if not (-180 <= a <= 180 and -180 <= b <= 180) or b < a:
            raise ValueError("Invalid lon_range")
