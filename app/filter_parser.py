import re
from datetime import date, timedelta
from calendar import monthrange
from .models import ARGOFilters, TimeRange, BBox, DepthRange
from .settings import settings

GEO = {
    "equator": (-5.0, 5.0),
    "tropic of cancer": (23.0, 25.0),
    "tropic of capricorn": (-25.0, -23.0),
}

MONTHS = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}


def _vars(text: str) -> list[str] | None:
    t = text.lower()
    found = [v for v in settings.allowed_variables if v in t]
    return found or None


def _latlon_terms(text: str):
    t = text.lower()
    lat = None
    lon = None
    for k, rng in GEO.items():
        if k in t:
            lat = rng
    return lat, lon


def _month_year(text: str) -> TimeRange | None:
    t = text.lower()
    for name, num in MONTHS.items():
        m = re.search(rf"\b{name[:3]}[a-z]*\s+(\d{{4}})\b", t)
        if m:
            y = int(m.group(1))
            start = date(y, num, 1)
            end = date(y, num, monthrange(y, num)[1])
            return TimeRange(start=start, end=end)
    return None


def _last_n(text: str) -> TimeRange | None:
    m = re.search(r"last\s+(\d{1,2})\s+(month|months|year|years)\b", text.lower())
    if not m:
        return None

    n = int(m.group(1))
    unit = m.group(2)
    today = date.today()
    days = 30 * n if "month" in unit else int(365.25 * n)
    return TimeRange(start=today - timedelta(days=days), end=today)


def _depth(text: str) -> DepthRange | None:
    t = text.lower()

    r = re.search(r"(\d{1,4})\s*-\s*(\d{1,4})\s*m", t)
    if r:
        a = int(r.group(1))
        b = int(r.group(2))
        return DepthRange(min_depth=min(a, b), max_depth=max(a, b))

    r2 = re.search(r"to\s+(\d{1,4})\s*m", t)
    if r2:
        b = int(r2.group(1))
        return DepthRange(min_depth=0, max_depth=b)

    return None


def extract_filters(nlq: str) -> ARGOFilters:
    vars_ = _vars(nlq)
    lat_range, lon_range = _latlon_terms(nlq)
    time_range = _month_year(nlq) or _last_n(nlq)
    depth = _depth(nlq)
    bbox = None

    m = re.search(
        r"bbox\s+(-?\d+(\.\d+)?),\s*(-?\d+(\.\d+)?),\s*(-?\d+(\.\d+)?),\s*(-?\d+(\.\d+)?)",
        nlq.lower(),
    )
    if m:
        vals = [float(m.group(i)) for i in [1, 3, 5, 7]]
        bbox = BBox(min_lon=vals[0], min_lat=vals[1], max_lon=vals[2], max_lat=vals[3])

    return ARGOFilters(
        variables=vars_,
        bbox=bbox,
        time_range=time_range,
        depth_range=depth,
        lat_range=lat_range,
        lon_range=lon_range,
    )

