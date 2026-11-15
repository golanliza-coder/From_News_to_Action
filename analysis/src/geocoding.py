from typing import Optional, Tuple
import googlemaps


def geocode_israel_location(
    gmaps_client: googlemaps.Client,
    verbal_location: str
) -> Tuple[Optional[float], Optional[float], str]:
    """
    מבצע גיאוקודינג מול Google Maps עם מעקה בטיחות לפסילת נקודת האמצע הגנרית של ישראל.
    מחזיר: (latitude, longitude, agent_status)
    """
    lat, lon = None, None
    if verbal_location and "not specified" not in verbal_location.lower():
        geo = gmaps_client.geocode(f"{verbal_location}, ישראל")
        if geo and isinstance(geo, list) and len(geo) > 0:
            first_res = geo[0]
            cand_lat = float(first_res["geometry"]["location"]["lat"])
            cand_lon = float(first_res["geometry"]["location"]["lng"])
            # Guardrail: פסילת נקודת מרכז ישראל הגנרית (31.0461, 34.8516)
            if not (round(cand_lat, 4) == 31.0461 and round(cand_lon, 4) == 34.8516):
                lat, lon = cand_lat, cand_lon

    agent_status = "VERIFIED" if lat else "REQUIRES_MANUAL_REVIEW"
    return lat, lon, agent_status
