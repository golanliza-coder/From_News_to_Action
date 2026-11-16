import os
import json
import time
import math
import hashlib
import asyncio
import feedparser
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from typing import List
from pydantic import BaseModel, Field
from telethon import TelegramClient
from telethon.sessions import StringSession
from google import genai
from google.genai import types
import googlemaps

DATABASE_URL = os.environ["DATABASE_URL"]
GEMINI_KEY = os.environ["GEMINI_API_KEY"]
MAPS_KEY = os.environ["GOOGLE_MAPS_API_KEY"]
TG_API_ID = int(os.environ["TELEGRAM_API_ID"])
TG_API_HASH = os.environ["TELEGRAM_API_HASH"]
TG_SESSION = os.environ["TELEGRAM_SESSION_STRING"]
RUN_TARGET = os.environ.get("RUN_TARGET", "yesterday")

KEYWORDS = [
    "תאונה", "תאונת דרכים", "הולך רגל", "התנגשות", "אופנוע",
    "קורקינט", "התהפך", "התהפכות", "נפגע מרכב", "רוכב אופניים", "דריסה"
]

IL_TZ = ZoneInfo("Asia/Jerusalem")
now_il = datetime.now(IL_TZ)
target_date = now_il.date() if RUN_TARGET == "today" else (now_il - timedelta(days=1)).date()
start_target = datetime.combine(target_date, datetime.min.time(), tzinfo=IL_TZ)
end_target = datetime.combine(target_date, datetime.max.time(), tzinfo=IL_TZ)


class TrafficAccidentExtract(BaseModel):
    is_traffic_accident: bool = Field(
        description="True אך ורק אם מדובר בתאונת דרכים הכוללת כלי רכב, אופנוע, קורקינט, אופניים או פגיעת רכב בהולך רגל. False עבור הפגנות, מחאות, פיגועים, אירועים ביטחוניים, קטטות, נפילות בבית או אירועים רפואיים שאינם תאונת דרכים."
    )
    accident_severity: str = Field(description="חומרת התאונה: light, moderate, severe, fatal, או 'not specified'")
    vehicle_types: List[str] = Field(description="רשימת רכבים באנגלית: car, bus, motorcycle, bicycle, electric scooter, truck")
    vulnerable_users_and_ages: str = Field(description="תיאור נפגעים פגיעים וגילאים (הולכי רגל, ילדים, קשישים) או 'none'")
    human_factor: str = Field(description="גורם אנושי או 'not specified'")
    verbal_location: str = Field(description="מיקום מדויק בישראל לחילוץ גיאוגרפי או 'not specified'")


def haversine_meters(lat1, lon1, lat2, lon2) -> float:
    """מחשב מרחק במטרים בין שתי נקודות GPS"""
    if None in (lat1, lon1, lat2, lon2):
        return float('inf')
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def merge_with_llm(gemini_client, existing_item: dict, new_item: dict) -> dict:
    """מאחד שני דיווחים על אותה תאונה לרשומה אחת עשירה"""
    prompt = (
        "לפניך שני דיווחים על אותה תאונת דרכים ממקורות שונים. "
        "אחד את המידע ביניהם כך שתישמר חומרת הפציעה המדויקת והמעודכנת ביותר, כלל כלי הרכב המעורבים, "
        "וכלל המידע על נפגעים פגיעים (VRU).\n\n"
        f"דיווח 1 ({existing_item['source']}): {existing_item['raw_text']}\n"
        f"חילוץ 1: {json.dumps(existing_item, ensure_ascii=False)}\n\n"
        f"דיווח 2 ({new_item['source']}): {new_item['raw_text']}\n"
        f"חילוץ 2: {json.dumps(new_item, ensure_ascii=False)}"
    )
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=TrafficAccidentExtract,
        temperature=0.0
    )
    resp = gemini_client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt,
        config=config
    )
    merged_extract = json.loads(resp.text)

    combined_sources = list(dict.fromkeys(existing_item["source"].split(", ") + [new_item["source"]]))
    existing_item.update(merged_extract)
    existing_item["source"] = ", ".join(combined_sources)
    existing_item["raw_text"] = f"{existing_item['raw_text']}\n---\n[{new_item['source']}]: {new_item['raw_text']}"
    existing_item["latitude"] = existing_item["latitude"] or new_item["latitude"]
    existing_item["longitude"] = existing_item["longitude"] or new_item["longitude"]
    existing_item["agent_status"] = "MERGED_VERIFIED"
    return existing_item


async def collect_telegram() -> List[dict]:
    records = []
    channels = ['mdaisrael', 'uh1221', 'hamalnews', 'fireisrael7777']
    async with TelegramClient(StringSession(TG_SESSION), TG_API_ID, TG_API_HASH) as client:
        for ch in channels:
            async for msg in client.iter_messages(ch, limit=800):
                if not msg.date:
                    continue
                msg_il = msg.date.astimezone(IL_TZ)
                if msg_il > end_target:
                    continue
                if msg_il < start_target:
                    break
                if msg.text and any(k in msg.text for k in KEYWORDS):
                    records.append({
                        "source": ch,
                        "raw_text": msg.text.strip(),
                        "published_date": msg_il.replace(tzinfo=None).isoformat()
                    })
    return records

def collect_rss() -> List[dict]:
    records = []
    rss_feeds = {
        "ynet": "http://ynet.co.il",
        "maariv": "https://maariv.co.il",
        "emess": "https://emess.co.il"
    }
    for src, url in rss_feeds.items():
        feed = feedparser.parse(url)
        for entry in feed.entries:
            title = entry.get("title", "")
            summary = entry.get("summary", "")
            full_text = f"{title}. {summary}".strip()
            if not any(k in full_text for k in KEYWORDS):
                continue
            pub_parsed = entry.get("published_parsed")
            if pub_parsed:
                dt_il = datetime(*pub_parsed[:6], tzinfo=timezone.utc).astimezone(IL_TZ)
                if dt_il.date() != target_date:
                    continue
                pub_str = dt_il.replace(tzinfo=None).isoformat()
            else:
                pub_str = start_target.replace(tzinfo=None).isoformat()
            records.append({"source": src, "raw_text": full_text, "published_date": pub_str})
    return records
def enrich_and_upload(raw_records: List[dict]):
    if not raw_records:
        print(f"ℹ️ לא נמצאו דיווחים חדשים עבור {target_date}.")
        return

    gemini_client = genai.Client(api_key=GEMINI_KEY)
    gmaps_client = googlemaps.Client(key=MAPS_KEY)
    raw_enriched_list = []

    print(f"🧠 מנתח {len(raw_records)} דיווחים מתאריך {target_date} באמצעות gemini-3.8-flash...")
    for rec in raw_records:
        try:
            prompt = (
                "בדוק תחילה האם הדיווח הבא מתאר תאונת דרכים אמיתית בישראל (is_traffic_accident=True). "
                "אם מדובר בהפגנה, אירוע ביטחוני, תקיפה או אירוע שאינו תאונת דרכים, סמן is_traffic_accident=False. "
                f"לאחר מכן חלץ את הנתונים במבנה המבוקש:\n{rec['raw_text']}"
            )
            config = types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=TrafficAccidentExtract,
                temperature=0.0
            )
            resp = gemini_client.models.generate_content(
                model="gemini-3.8-flash",
                contents=prompt,
                config=config
            )
            data = json.loads(resp.text)

            if not data.get("is_traffic_accident", False):
                print(f"🚫 סונן (אירוע שאינו תאונת דרכים): {rec['raw_text'][:55]}...")
                time.sleep(0.3)
                continue

            lat, lon = None, None
            loc = data.get("verbal_location", "")
            if loc and "not specified" not in loc.lower():
                geo = gmaps_client.geocode(f"{loc}, ישראל")
                if geo and isinstance(geo, list) and len(geo) > 0:
                    first_res = geo[0]
                    cand_lat = float(first_res["geometry"]["location"]["lat"])
                    cand_lon = float(first_res["geometry"]["location"]["lng"])
                    if not (round(cand_lat, 4) == 31.0461 and round(cand_lon, 4) == 34.8516):
                        lat, lon = cand_lat, cand_lon

            data.update({
                "source": rec["source"],
                "raw_text": rec["raw_text"],
                "published_date": rec["published_date"],
                "latitude": lat,
                "longitude": lon,
                "agent_status": "VERIFIED" if lat else "REQUIRES_MANUAL_REVIEW"
            })
            raw_enriched_list.append(data)
            time.sleep(0.4)
        except Exception as e:
            print(f"⚠️ דילוג על רשומה עקב שגיאה: {e}")

    deduplicated_list = []
    raw_enriched_list.sort(key=lambda x: x["published_date"])

    for item in raw_enriched_list:
        item_dt = datetime.fromisoformat(item["published_date"])
        matched_idx = None

        for idx, existing in enumerate(deduplicated_list):
            ex_dt = datetime.fromisoformat(existing["published_date"])
            time_diff_hours = abs((item_dt - ex_dt).total_seconds()) / 3600.0
            dist_meters = haversine_meters(
                item.get("latitude"), item.get("longitude"),
                existing.get("latitude"), existing.get("longitude")
            )

            if dist_meters <= 500 and time_diff_hours <= 3.0:
                matched_idx = idx
                break

        if matched_idx is not None:
            print(f"🔗 מאחד דיווח כפול ({item['source']}) לתוך אירוע קיים ב-{deduplicated_list[matched_idx]['verbal_location']}...")
            deduplicated_list[matched_idx] = merge_with_llm(gemini_client, deduplicated_list[matched_idx], item)
            time.sleep(0.4)
        else:
            deduplicated_list.append(item)

    json_filename = f"accidents_{target_date}.json"
    with open(json_filename, "w", encoding="utf-8") as f:
        json.dump(deduplicated_list, f, ensure_ascii=False, indent=2)

    values = []
    for item in deduplicated_list:
        seed = f"{item['source']}|{item['raw_text']}"
        r_hash = hashlib.sha256(seed.encode("utf-8")).hexdigest()
        values.append((item["source"], json.dumps(item, ensure_ascii=False), r_hash, item["published_date"]))

    if values:
        with psycopg2.connect(DATABASE_URL) as conn:
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
        print(f"🚀 הצלחה! עובדו ואוחדו {len(values)} תאונות ייחודיות מתאריך {target_date}. סה\"כ בטבלה ב-Neon כעת: {total_db} רשומות!")
    else:
        print(f"ℹ️ לאחר סינון סמנטי, לא נמצאו תאונות דרכים להוספה עבור {target_date}.")


async def main():
    tg_data = await collect_telegram()
    rss_data = collect_rss()
    all_records = tg_data + rss_data
    enrich_and_upload(all_records)


if __name__ == "__main__":
    asyncio.run(main())
