"""Patient identity primitives: phone normalisation and identity resolution.

Phone numbers are the anchor for patient identity, so the same logical number
must normalise identically no matter how the caller formats it (spaces, dashes,
parentheses, or a leading ``whatsapp:``). Every patient-identity lookup goes
through :func:`normalize_phone` so two spellings can never resolve to two
different patients.
"""

from __future__ import annotations

import re

_NON_DIGIT = re.compile(r"\D+")


def normalize_phone(value: str | None) -> str:
    """Reduce a user-supplied phone string to bare E.164-ish digits.

    Strips a ``whatsapp:`` prefix, drops every non-digit character, and
    removes a single leading ``00`` international access code. Raises
    ``ValueError`` when nothing digit-like survives, so callers never build a
    Redis key from garbage.
    """
    if not value:
        raise ValueError("Phone number is required.")

    candidate = value.strip().lower()
    if candidate.startswith("whatsapp:"):
        candidate = candidate[len("whatsapp:"):]

    digits = _NON_DIGIT.sub("", candidate)
    if not digits:
        raise ValueError("Phone number must contain digits.")

    if digits.startswith("00"):
        digits = digits[2:]

    if len(digits) < 7 or len(digits) > 15:
        raise ValueError("Phone number length is out of range.")

    return digits


__all__ = ["normalize_phone"]