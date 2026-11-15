import json
from typing import List
import psycopg2
from psycopg2.extras import execute_values
from src.preprocessing import generate_report_hash


def upload_incidents_to_neon(database_url: str, enriched_list: List[dict]) -> int:
    """מזריק רשומות מאומתות לטבלת traffic_incidents ב-Neon ומחזיר את סך הרשומות בטבלה."""
    values = []
    for item in enriched_list:
        r_hash = generate_report_hash(item["source"], item["raw_text"])
        values.append((
            item["source"],
            json.dumps(item, ensure_ascii=False),
            r_hash,
            item["published_date"]
        ))

    if not values:
        return 0

    with psycopg2.connect(database_url) as conn:
        with conn.cursor() as cur:
            execute_values(
                cur,
                """
                INSERT INTO traffic_incidents (source, article_data, report_hash, published_date)
                VALUES %s
                ON CONFLICT (report_hash) DO NOTHING;
                """,
                values,
                template="(%s, %s::jsonb, %s, %s::timestamp)"
            )
            cur.execute("SELECT COUNT(*) FROM traffic_incidents;")
            total_db = cur.fetchone()[0]
        conn.commit()
    return total_db


def fetch_all_incidents(database_url: str) -> List[dict]:
    """שולף את כל התאונות המאומתות מ-Neon לשימוש במחברות הערכה או בדשבורד."""
    with psycopg2.connect(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, source, article_data, published_date
                FROM traffic_incidents
                ORDER BY published_date DESC;
            """)
            rows = cur.fetchall()
    return [
        {"id": r[0], "source": r[1], **r[2], "published_date": str(r[3])}
        for r in rows
    ]
