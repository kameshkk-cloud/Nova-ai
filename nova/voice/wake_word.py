"""
NOVA Wake Word Detector
========================
Dedicated module for detecting the wake word ("hey nova") from
continuous listening.  Supports debounce to avoid false triggers.
"""

from __future__ import annotations

import time

from nova.config.settings import WAKE_WORD, ACTIVATE_MODE
from nova.utils import logger as log


class WakeWordDetector:
    """
    Listens (via a SpeechListener instance) for the configured wake word.

    Parameters
    ----------
    listener : SpeechListener
        The STT engine to use for listening.
    debounce_seconds : float
        Minimum gap between two accepted wake word triggers.
    """

    def __init__(self, listener, debounce_seconds: float = 2.0) -> None:
        self._listener = listener
        self._debounce = debounce_seconds
        self._last_trigger: float = 0.0

    def check(self, text: str) -> bool:
        """
        Return True if *text* contains the wake word (respecting debounce).
        """
        if not text:
            return False
        lower = text.lower()
        if WAKE_WORD in lower or ACTIVATE_MODE in lower:
            now = time.time()
            if now - self._last_trigger >= self._debounce:
                self._last_trigger = now
                log.info("Wake word detected!")
                return True
            log.debug("Wake word ignored (debounce).")
        return False

    def is_direct_command(self, text: str) -> bool:
        """
        Heuristic: if the user said 3+ words and it's not just the wake word,
        treat it as a direct command (skip waiting for a second utterance).
        """
        if not text:
            return False
        words = text.strip().split()
        if len(words) >= 3 and WAKE_WORD not in text.lower():
            return True
        return False
