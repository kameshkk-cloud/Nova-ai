"""
NOVA Text Utilities
===================
Helper functions for sanitising, truncating, and extracting information
from raw user input.
"""

from __future__ import annotations

import re
from typing import List, Optional


def sanitize(text: str) -> str:
    """
    Clean raw user input:
    - Strip leading/trailing whitespace
    - Collapse multiple spaces
    - Lowercase
    """
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    return text.lower()


def truncate(text: str, max_len: int = 200, suffix: str = "…") -> str:
    """Safely truncate a string, appending *suffix* if it was shortened."""
    if len(text) <= max_len:
        return text
    return text[: max_len - len(suffix)] + suffix


def extract_path(text: str) -> Optional[str]:
    """
    Try to pull a Windows or Unix file/folder path from *text*.

    Examples that match:
        C:\\Users\\KK\\file.txt
        /home/kk/file.txt
        ~/Downloads
    """
    # Windows path
    m = re.search(r'[A-Za-z]:\\[\w\\.\- ]+', text)
    if m:
        return m.group(0).rstrip()
    # Unix path
    m = re.search(r'(?:~|/[\w.\-]+)(?:/[\w.\- ]+)+', text)
    if m:
        return m.group(0).rstrip()
    return None


def extract_url(text: str) -> Optional[str]:
    """Pull the first URL from *text*."""
    m = re.search(r'https?://\S+|www\.\S+', text)
    if m:
        return m.group(0)
    return None


def extract_number(text: str) -> Optional[float]:
    """Return the first number found in *text*, or None."""
    m = re.search(r'[\d]+(?:\.[\d]+)?', text)
    if m:
        return float(m.group(0))
    return None


def extract_quoted(text: str) -> Optional[str]:
    """Return the first quoted substring, or None."""
    m = re.search(r'["\'](.+?)["\']', text)
    if m:
        return m.group(1)
    return None


def keyword_match(text: str, keywords: List[str]) -> bool:
    """Return True if any keyword appears as a whole word in *text*."""
    lower = text.lower()
    for kw in keywords:
        if re.search(rf"\b{re.escape(kw)}\b", lower):
            return True
    return False
