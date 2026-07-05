"""
Phone validation/normalization. Rejects date-like strings and PIN codes,
prefers Indian mobile formats.
"""

import re

_INDIAN_MOBILE = re.compile(r"(?:\+?91[\s\-]?)?([6-9]\d{4}[\s\-]?\d{5}|[6-9]\d{9})\b")
_DATE = re.compile(r"^\s*(\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4}|\d{4}[-/.]\d{1,2}[-/.]\d{1,2})\s*$")
_PIN = re.compile(r"^\d{6}$")


def _digits(value: str) -> str:
    return re.sub(r"\D", "", value)


def is_valid_phone(value: str | None) -> bool:
    if not value:
        return False
    raw = re.sub(r"[\n\r\t]+", "", str(value)).strip()
    if not raw or _DATE.match(raw):
        return False
    digits = _digits(raw)
    if len(digits) < 8 or len(digits) > 15 or _PIN.match(digits):
        return False
    if _INDIAN_MOBILE.search(raw):
        return True
    return len(digits) >= 10 and len(set(digits)) > 2


def clean_phone(value: str | None) -> str | None:
    """Return a normalized phone, or None if invalid."""
    if not is_valid_phone(value):
        return None
    raw = re.sub(r"[\n\r\t]+", "", str(value)).strip()
    m = _INDIAN_MOBILE.search(raw)
    if m:
        digits = _digits(m.group(0))
        if digits.startswith("91") and len(digits) == 12:
            return f"+91 {digits[2:7]} {digits[7:]}"
        if len(digits) == 10:
            return f"+91 {digits[:5]} {digits[5:]}"
    return raw
