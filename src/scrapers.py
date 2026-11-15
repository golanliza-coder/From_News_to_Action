from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from typing import List, Dict
import feedparser
from telethon import TelegramClient
from telethon.sessions import StringSession
from src.preprocessing import has_traffic_keyword

IL_TZ = ZoneInfo("Asia/Jerusalem")
TELEGRAM_CHANNELS = ['mdaisrael', 'uh1221', 'hamalnews', 'fireisrael7777']
RSS_FEEDS: Dict[str, str] = {
    "ynet": "http://ynet.co.il",
    "maariv": "https://maariv.co.il",
    "emess": "https://emess.co.il"
}


async def fetch_telegram_window(
    session_str: str,
    api_id: int,
    api_hash: str,
    start_dt: datetime,
    end_dt: datetime
) -> List[dict]:
    """אוסף דיווחים רלוונטיים מערוצי החירום בטלגרם בטווח תאריכים מוגדר."""
    records = []
    async with TelegramClient(StringSession(session_str), api_id, api_hash) as client:
        for ch in TELEGRAM_CHANNELS:
            async for msg in client.iter_messages(ch, limit=800):
                if not msg.date:
                    continue
                msg_il = msg.date.astimezone(IL_TZ)
                if msg_il > end_dt:
                    continue
                if msg_il < start_dt:
                    break
                if msg.text and has_traffic_keyword(msg.text):
                    records.append({
                        "source": ch,
                        "raw_text": msg.text.strip(),
                        "published_date": msg_il.replace(tzinfo=None).isoformat()
                    })
    return records


def fetch_rss_by_date(target_date, fallback_start: datetime) -> List[dict]:
    """אוסף דיווחי תאונות מערוצי החדשות עבור תאריך מטרה ספציפי."""
    records = []
    for src, url in RSS_FEEDS.items():
        feed = feedparser.parse(url)
        for entry in feed.entries:
            title = entry.get("title", "")
            summary = entry.get("summary", "")
            full_text = f"{title}. {summary}".strip()
            if not has_traffic_keyword(full_text):
                continue
            pub_parsed = entry.get("published_parsed")
            if pub_parsed:
                dt_il = datetime(*pub_parsed[:6], tzinfo=timezone.utc).astimezone(IL_TZ)
                if dt_il.date() != target_date:
                    continue
                pub_str = dt_il.replace(tzinfo=None).isoformat()
            else:
                pub_str = fallback_start.replace(tzinfo=None).isoformat()
            records.append({"source": src, "raw_text": full_text, "published_date": pub_str})
    return records
