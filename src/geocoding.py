from typing import Optional, Tuple
import googlemaps

# קואורדינטות ברירת מחדל גנריות של מרכז ישראל שגוגל מפות מחזיר כשאין דיוק
ISRAEL_CENTROID = (31.0461, 34.8516)
TOLERANCE = 0.005

def is_generic_centroid(lat: float, lng: float) -> bool:
    """בודק אם הקואורדינטות שנמצאו הן נקודת האמצע הגנרית של המדינה."""
    return (
        abs(lat - ISRAEL_CENTROID[0]) < TOLERANCE and 
        abs(lng - ISRAEL_CENTROID[1]) < TOLERANCE
    )

def safe_geocode(gmaps_client: googlemaps.Client, location_text: str) -> Tuple[Optional[float], Optional[float], str]:
    """מבצע גיאוקודינג עם מעקה בטיחות נגד נקודות גנריות."""
    if not location_text or location_text == 'לא מצוין':
        return None, None, "REQUIRES_MANUAL_REVIEW"
    
    results = gmaps_client.geocode(f"{location_text}, ישראל", language="iw")
    if not results:
        return None, None, "REQUIRES_MANUAL_REVIEW"
        
    loc = results[0]['geometry']['location']
    lat, lng = float(loc['lat']), float(loc['lng'])
    
    if is_generic_centroid(lat, lng):
        return None, None, "REQUIRES_MANUAL_REVIEW"
        
    return lat, lng, "VERIFIED"
