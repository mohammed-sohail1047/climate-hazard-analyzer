
from datetime import datetime, timezone

import httpx

from app.config import OPEN_METEO_ARCHIVE_URL
from app.database import get_weather_collection


async def fetch_historical_weather(
    latitude: float,
    longitude: float,
    start_date: str,
    end_date: str,
) -> dict:
    """Fetch historical weather, reusing cached results when available."""

    collection = get_weather_collection()

    cache_key = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
    }

    cached_record = collection.find_one(cache_key)

    if cached_record:
        print("Weather data loaded from MongoDB cache.")
        return cached_record["weather_data"]

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "daily": "temperature_2m_max",
        "timezone": "auto",
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(OPEN_METEO_ARCHIVE_URL, params=params)
        response.raise_for_status()
        weather_data = response.json()

    collection.insert_one({
        **cache_key,
        "weather_data": weather_data,
        "cached_at": datetime.now(timezone.utc),
    })

    print("Weather data fetched from Open-Meteo and cached in MongoDB.")
    return weather_data



async def fetch_baseline_weather(
    latitude: float,
    longitude: float,
) -> dict:
    """Fetch a separate 10-year reference period for climate analysis."""

    return await fetch_historical_weather(
        latitude=latitude,
        longitude=longitude,
        start_date="2004-01-01",
        end_date="2013-12-31",
    )

