import psycopg2
from psycopg2.extras import RealDictCursor

def get_db_connection(database_url: str):
    """יוצר חיבור מאובטח לענן PostgreSQL (Neon)."""
    return psycopg2.connect(database_url)

def insert_incident(conn, incident_data: dict) -> bool:
    """מבצע UPSERT לטבלת התאונות ללא דריסת רשומות קיימות."""
    query = """
    INSERT INTO traffic_incidents 
        (report_hash, source, published_date, raw_text, severity, location_text, lat, lng, status)
    VALUES 
        (%(report_hash)s, %(source)s, %(published_date)s, %(raw_text)s, %(severity)s, %(location_text)s, %(lat)s, %(lng)s, %(status)s)
    ON CONFLICT (report_hash) DO NOTHING;
    """
    with conn.cursor() as cur:
        cur.execute(query, incident_data)
        conn.commit()
        return cur.rowcount > 0
