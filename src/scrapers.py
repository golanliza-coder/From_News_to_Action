import feedparser
from datetime import datetime, timedelta, timezone

def fetch_rss_yesterday(rss_urls: dict) -> list:
    """מושך כתבות מערוצי RSS שפורסמו ב-24 השעות האחרונות."""
    articles = []
    cutoff_time = datetime.now(timezone.utc) - timedelta(days=1)
    
    for source_name, url in rss_urls.items():
        feed = feedparser.parse(url)
        for entry in feed.entries:
            articles.append({
                "source": source_name,
                "raw_text": f"{entry.get('title', '')} - {entry.get('summary', '')}",
                "url": entry.get('link', '')
            })
    return articles
