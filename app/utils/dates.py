# app/utils/dates.py
from datetime import datetime


def parse_date(date_str: str) -> datetime:
    """
    Accepts 'YYYY-MM-DD' or ISO datetime strings.
    Returns a naive datetime.
    """
    if not date_str or not isinstance(date_str, str):
        raise ValueError("Date is required")

    s = date_str.strip()

    # Try YYYY-MM-DD
    try:
        return datetime.strptime(s, "%Y-%m-%d")
    except ValueError:
        pass

    # Try ISO datetime (e.g., 2026-02-06T00:00:00)
    try:
        return datetime.fromisoformat(s)
    except ValueError:
        raise ValueError("Invalid date format. Use YYYY-MM-DD")
