import hashlib
from typing import List

KEYWORDS: List[str] = [
    "תאונה", "תאונת דרכים", "הולך רגל", "התנגשות", "אופנוע",
    "קורקינט", "התהפך", "התהפכות", "נפגע מרכב", "רוכב אופניים", "דריסה"
]


def has_traffic_keyword(text: str) -> bool:
    """בודק האם הטקסט מכיל לפחות אחת ממילות המפתח התחבורתיות."""
    if not text:
        return False
    return any(k in text for k in KEYWORDS)


def generate_report_hash(source: str, raw_text: str) -> str:
    """יוצר מזהה SHA-256 ייחודי זהה ללוגיקת ה-ON CONFLICT ב-Neon."""
    seed = f"{source}|{raw_text}"
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()
