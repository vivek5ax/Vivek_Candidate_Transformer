import re
from typing import Optional
from dateutil import parser

def parse_to_yyyy_mm(date_str: Optional[str]) -> Optional[str]:
    """
    Normalizes a date string (e.g., 'May 2026', 'Feb 2026') to 'YYYY-MM'.
    If it's just a year (e.g., '2026'), returns 'YYYY'.
    """
    if not date_str:
        return None
    
    clean_str = date_str.strip().lower()
    if clean_str in ("present", "current", "now"):
        return "Present"
        
    # Check if it's just a year
    if re.fullmatch(r'\d{4}', clean_str):
        return clean_str

    try:
        # Default day to 1 so parsing 'May 2026' becomes 2026-05-01
        dt = parser.parse(clean_str, default=parser.parse("2000-01-01"))
        return dt.strftime("%Y-%m")
    except Exception:
        # Fallback regex if dateutil fails
        match = re.search(r'((?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*)\s*(\d{4})', clean_str, re.IGNORECASE)
        if match:
            month_str, year = match.groups()
            try:
                dt = parser.parse(f"{month_str} {year}")
                return dt.strftime("%Y-%m")
            except Exception:
                pass
        return date_str.strip()
