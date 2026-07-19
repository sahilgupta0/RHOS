"""
RHOS Google Maps Service.

Provides distance calculations and location-based helpers.
"""

from __future__ import annotations

import logging
from typing import Any

from app.config import get_settings

logger = logging.getLogger(__name__)


def calculate_distance_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    Calculate the great-circle distance between two points on the Earth's surface
    using the Haversine formula.
    """
    import math

    # Convert latitude and longitude to radians
    rlat1, rlng1, rlat2, rlng2 = map(math.radians, [lat1, lng1, lat2, lng2])

    # Haversine formula
    dlat = rlat2 - rlat1
    dlng = rlng2 - rlng1
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(rlat1) * math.cos(rlat2) * math.sin(dlng / 2) ** 2
    )
    c = 2 * math.asin(math.sqrt(a))
    r = 6371.0  # Radius of earth in kilometers
    return round(c * r, 2)


async def get_nearest_hospitals(
    lat: float, lng: float, limit: int = 3
) -> list[dict[str, Any]]:
    """
    Find the nearest hospitals/PHCs to a given coordinate.
    Uses mock spatial search over seeded hospital data.
    """
    settings = get_settings()
    # In a full production app, you might use the googlemaps client to find nearby places.
    # We will search the database or return mock data.
    try:
        from app.core.mongodb import get_mongodb_db

        db = get_mongodb_db()
        if db is not None:
            cursor = db["hospitals"].find()
            hospitals = []
            async for doc in cursor:
                doc["id"] = str(doc.pop("_id"))
                h_lat = doc.get("lat", 0.0)
                h_lng = doc.get("lng", 0.0)
                if h_lat and h_lng:
                    doc["distance_km"] = calculate_distance_km(lat, lng, h_lat, h_lng)
                    hospitals.append(doc)

            # Sort by distance
            hospitals.sort(key=lambda x: x.get("distance_km", 999.0))
            return hospitals[:limit]
    except Exception as e:
        logger.error("Error finding nearest hospitals: %s", e)

    # Mock fallback
    return [
        {
            "id": "H001",
            "name": "Khandela Community Health Center",
            "type": "CHC",
            "district": "Sikar",
            "distance_km": 4.2,
            "phone": "+91-1575-220011",
        },
        {
            "id": "H002",
            "name": "Ringus Primary Health Center",
            "type": "PHC",
            "district": "Sikar",
            "distance_km": 12.8,
            "phone": "+91-1575-224422",
        },
    ]
