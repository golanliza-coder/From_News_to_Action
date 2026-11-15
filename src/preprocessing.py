import hashlib
import re

# ביטויים מרובי מילים למניעת פסילת תאונות אמיתיות (כמו המילה "צירים")
EXCLUDED_PHRASES = ["אירוע ירי", "פיגוע ירי", "ירי רקטות", "הפגנה", "מחאה"]

def generate_report_hash(source: str, raw_text: str) -> str:
    """יוצר מזהה SHA-256 ייחודי למניעת הזרקת כפילויות למסד הנתונים."""
    clean_str = f"{source.strip()}|{raw_text.strip()}"
    return hashlib.sha256(clean_str.encode('utf-8')).hexdigest()

def is_valid_accident_text(text: str) -> bool:
    """מסנן דיווחים שאינם תאונות דרכים על בסיס ביטויים מדויקים."""
    if not text or len(text.strip()) < 15:
        return False
    for phrase in EXCLUDED_PHRASES:
        if phrase in text:
            return False
    return True

def clean_hebrew_location(location_str: str) -> str:
    """מנקה מילות יחס מבלבלות לפני שליחה ל-Geocoding."""
    cleaned = re.sub(r'\b(לכיוון|סמוך ל|ליד|באזור)\b', '', location_str)
    return " ".join(cleaned.split())
