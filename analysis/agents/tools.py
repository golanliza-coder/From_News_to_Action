import os
from typing import Optional
import psycopg2
from langchain_core.tools import tool
import googlemaps
from src.geocoding import geocode_israel_location


@tool
def advanced_geocoding_tool(cleaned_location: str) -> dict:
    """
    Geocodes a cleaned Hebrew location string in Israel using Google Maps API
    with built-in protection against generic country-center fallbacks.
    """
    api_key = os.environ.get("GOOGLE_MAPS_API_KEY", "")
    gmaps_client = googlemaps.Client(key=api_key)
    lat, lon, status = geocode_israel_location(gmaps_client, cleaned_location)
    return {
        "latitude": lat,
        "longitude": lon,
        "status": status
    }


@tool
def cross_source_news_search(location_keyword: str, target_date: str) -> list:
    """
    Searches the Neon PostgreSQL database for follow-up news reports matching
    the same date and location keyword to enrich missing medical severity.
    """
    db_url = os.environ.get("DATABASE_URL")
    if not db_url or not location_keyword:
        return []

    with psycopg2.connect(db_url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT source, article_data->>'raw_text', article_data->>'accident_severity'
                FROM traffic_incidents
                WHERE DATE(published_date) = %s::date
                  AND article_data->>'raw_text' ILIKE %s
                LIMIT 5;
                """,
                (target_date, f"%{location_keyword}%")
            )
            rows = cur.fetchall()

    return [
        {"source": r[0], "raw_text": r[1], "severity": r[2]}
        for r in rows
    ]


@tool
def spatial_density_analyzer(lat: Optional[float], lon: Optional[float], published_date: str) -> dict:
    """
    Checks historical accidents within a 500-meter radius over the preceding 90 days
    (preventing temporal leakage) to compute the Traffic Light risk level.
    """
    if lat is None or lon is None:
        return {"cluster_count": 0, "risk_level": "UNKNOWN", "suspected_infrastructure_hazard": False}

    db_url = os.environ.get("DATABASE_URL")
    with psycopg2.connect(db_url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT COUNT(*)
                FROM traffic_incidents
                WHERE (article_data->>'latitude') IS NOT NULL
                  AND published_date <= %s::timestamp
                  AND published_date >= (%s::timestamp - INTERVAL '90 days')
                  AND ST_DWithin(
                        ST_SetSRID(ST_MakePoint((article_data->>'longitude')::float, (article_data->>'latitude')::float), 4326)::geography,
                        ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography,
                        500
                  );
                """,
                (published_date, published_date, lon, lat)
            )
            count = cur.fetchone()[0] + 1  # כולל האירוע הנוכחי

    if count >= 3:
        risk = "RED"
    elif count == 2:
        risk = "ORANGE"
    else:
        risk = "GREEN"

    return {
        "cluster_count": count,
        "risk_level": risk,
        "suspected_infrastructure_hazard": count >= 3
    }
