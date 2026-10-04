import re
from datetime import date, datetime

_NUM_RE = re.compile(r"[-+]?\d[\d,]*(?:\.\d+)?")


def parse_number(text: str | None) -> float | None:
    """Parse numbers like "1,121.25", "(-0.47%)", "+5.25". Returns None for "-", "" or None."""
    if not text:
        return None
    match = _NUM_RE.search(str(text).replace("−", "-"))
    if not match:
        return None
    return float(match.group().replace(",", ""))


def infer_year(month: int, day: int, today: date | None = None) -> date:
    """Turn a year-less "MM-DD" into a date, assuming it is not in the future
    (a December quote read in January belongs to the previous year)."""
    today = today or date.today()
    candidate = date(today.year, month, day)
    if candidate > today:
        candidate = date(today.year - 1, month, day)
    return candidate


def parse_date(text: str, formats: tuple[str, ...]) -> date:
    text = " ".join(text.split())
    for fmt in formats:
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Unrecognised date {text!r} (tried {formats})")
