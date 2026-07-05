"""
ResQAI – Geospatial Utilities
Geohash encoding, distance calculation, and coordinate validation.
"""
import math
from typing import Optional, Tuple

try:
    import pygeohash as _geohash   # pygeohash — pure Python, no C compiler needed
    _GEOHASH_AVAILABLE = True
    _GEOHASH_LIB = "pygeohash"
except ImportError:
    try:
        import geohash as _geohash  # python-geohash fallback
        _GEOHASH_AVAILABLE = True
        _GEOHASH_LIB = "python-geohash"
    except ImportError:
        _GEOHASH_AVAILABLE = False
        _GEOHASH_LIB = None


def encode_geohash(latitude: float, longitude: float, precision: int = 6) -> str:
    """
    Encode lat/lng to geohash string.
    Precision 6 ≈ 1.2 km radius — used for duplicate detection.
    """
    if _GEOHASH_AVAILABLE:
        try:
            if _GEOHASH_LIB == "pygeohash":
                return _geohash.encode(latitude, longitude, precision)
            else:
                return _geohash.encode(latitude, longitude, precision)
        except Exception:
            pass
    # Simple fallback: quantized coordinate string
    lat_q = round(latitude, 2)
    lng_q = round(longitude, 2)
    return f"{lat_q:.2f}_{lng_q:.2f}"


def haversine_distance(
    lat1: float, lon1: float, lat2: float, lon2: float
) -> float:
    """
    Calculate the great-circle distance between two points in kilometers.
    Uses the Haversine formula.
    """
    R = 6371.0  # Earth radius in km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def estimated_arrival_minutes(distance_km: float, speed_kmh: float = 40.0) -> int:
    """
    Estimate travel time in minutes given distance and average speed.
    Default 40 km/h accounts for urban/semi-urban Indian road conditions.
    """
    if distance_km <= 0:
        return 0
    return max(1, round((distance_km / speed_kmh) * 60))


def validate_coordinates(latitude: float, longitude: float) -> Tuple[bool, Optional[str]]:
    """Return (is_valid, error_message)."""
    if not (-90.0 <= latitude <= 90.0):
        return False, f"Latitude {latitude} is out of range [-90, 90]"
    if not (-180.0 <= longitude <= 180.0):
        return False, f"Longitude {longitude} is out of range [-180, 180]"
    # Rough India bounding box check
    if not (6.0 <= latitude <= 37.5 and 68.0 <= longitude <= 97.5):
        return False, "Coordinates appear to be outside India"
    return True, None


def geohash_neighbors(geohash_str: str) -> list:
    """Get the 8 neighboring geohash cells for proximity search."""
    if _GEOHASH_AVAILABLE:
        try:
            if _GEOHASH_LIB == "pygeohash":
                return list(_geohash.neighbors(geohash_str).values())
            else:
                return list(_geohash.neighbors(geohash_str))
        except Exception:
            pass
    return []
