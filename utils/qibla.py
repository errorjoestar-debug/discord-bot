import aiohttp
import os

ALADHAN_API = "https://api.aladhan.com/v1/qibla"

QIBLA_LOCATIONS = {
    "Cairo": {"lat": 30.0444, "lng": 31.2357, "direction": 135},
    "Riyadh": {"lat": 24.7136, "lng": 46.6753, "direction": 44},
    "Dubai": {"lat": 25.2048, "lng": 55.2708, "direction": 47},
    "Makkah": {"lat": 21.4225, "lng": 39.8262, "direction": 0},
    "Jeddah": {"lat": 21.5433, "lng": 39.1728, "direction": 19},
    "Kuwait": {"lat": 29.3759, "lng": 47.9774, "direction": 41},
    "Doha": {"lat": 25.2854, "lng": 51.5310, "direction": 46},
    "Abu Dhabi": {"lat": 24.4539, "lng": 54.3773, "direction": 47},
    "Amman": {"lat": 31.9539, "lng": 35.9106, "direction": 136},
    "Beirut": {"lat": 33.8938, "lng": 35.5019, "direction": 139},
    "Istanbul": {"lat": 41.0082, "lng": 28.9784, "direction": 146},
    "London": {"lat": 51.5074, "lng": -0.1278, "direction": 119},
    "New York": {"lat": 40.7128, "lng": -74.0060, "direction": 58},
    "Paris": {"lat": 48.8566, "lng": 2.3522, "direction": 115},
    "Berlin": {"lat": 52.5200, "lng": 13.4050, "direction": 124},
    "Tokyo": {"lat": 35.6762, "lng": 139.6503, "direction": 293},
}


async def get_qibla_direction(city: str) -> dict | None:
    """Get Qibla direction for a city."""
    # Check if city is in our predefined list
    city_key = city.title()
    if city_key in QIBLA_LOCATIONS:
        return {
            "city": city_key,
            "direction": QIBLA_LOCATIONS[city_key]["direction"],
            "latitude": QIBLA_LOCATIONS[city_key]["lat"],
            "longitude": QIBLA_LOCATIONS[city_key]["lng"],
        }
    
    # If not in list, try to get from API
    default_city = os.getenv("PRAYER_CITY", "Cairo")
    default_lat = QIBLA_LOCATIONS[default_city]["lat"]
    default_lng = QIBLA_LOCATIONS[default_city]["lng"]
    
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{ALADHAN_API}/{default_lat}/{default_lng}"
            async with session.get(url) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
                if data.get("code") != 200:
                    return None
                qibla = data["data"]
                return {
                    "city": city,
                    "direction": qibla.get("direction", 135),
                    "latitude": default_lat,
                    "longitude": default_lng,
                }
    except Exception:
        return None
