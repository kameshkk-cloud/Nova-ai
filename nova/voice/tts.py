"""
NOVA Text-to-Speech Engine
===========================
Adaptive TTS that automatically adjusts voice profile based on
time-of-day, alert severity, or explicit request.

Voice profiles:
    calm      — slow (140 wpm), 75% volume, used late-night
    default   — balanced (175 wpm)
    energetic — fast (210 wpm), used for morning / excitement
    alert     — urgent (195 wpm), used for critical system alerts
"""

from __future__ import annotations

import datetime
import queue
import threading
from typing import Optional

from nova.config.settings import (
    ASSISTANT_NAME, VOICE_GENDER, VOICE_PROFILES,
    VOICE_RATE, VOICE_VOLUME,
)
from nova.utils import logger as log


class VoiceEngine:
    """Thread-safe, adaptive text-to-speech engine."""

    def __init__(self) -> None:
        self._engine = None
        self._available = False
        self._current_profile = "default"
        self._lock = threading.Lock()
        self._queue: queue.Queue = queue.Queue()
        self._worker: Optional[threading.Thread] = None
        self._running = False
        self._init_engine()

    # ── Initialisation ───────────────────────────────────────────────────
    def _init_engine(self) -> None:
        try:
            import pyttsx3
            self._engine = pyttsx3.init()
            voices = self._engine.getProperty("voices")
            if VOICE_GENDER == "female" and len(voices) > 1:
                self._engine.setProperty("voice", voices[1].id)
            else:
                self._engine.setProperty("voice", voices[0].id)
            self._engine.setProperty("rate", VOICE_RATE)
            self._engine.setProperty("volume", VOICE_VOLUME)
            self._available = True
            log.debug("pyttsx3 TTS engine ready.")
        except Exception as exc:
            self._available = False
            log.warn(f"pyttsx3 not available: {exc} — print-only mode.")

    # ── Public API ────────────────────────────────────────────────────────

    def speak(self, text: str, profile: Optional[str] = None, silent: bool = False) -> None:
        """
        Speak *text* aloud (or print if TTS unavailable).

        Parameters
        ----------
        profile : str, optional
            Force a voice profile ("calm", "energetic", "alert").
            If None, auto-selects based on time of day.
        silent : bool
            If True, print only — do not speak.
        """
        log.nova_say(ASSISTANT_NAME, text)

        if silent or not self._available:
            return

        chosen = profile or self._auto_profile()
        self._apply_profile(chosen)

        with self._lock:
            try:
                self._engine.say(text)
                self._engine.runAndWait()
            except RuntimeError:
                # pyttsx3 loop already running — stop and retry
                try:
                    self._engine.stop()
                    self._engine.say(text)
                    self._engine.runAndWait()
                except Exception as exc:
                    log.error(f"TTS retry failed: {exc}")

    def set_profile(self, name: str) -> None:
        """Explicitly switch voice profile."""
        if name in VOICE_PROFILES:
            self._current_profile = name
            self._apply_profile(name)
            log.info(f"Voice profile changed to '{name}'.")

    @property
    def available(self) -> bool:
        return self._available

    @property
    def current_profile(self) -> str:
        return self._current_profile

    # ── Adaptive profile selection ───────────────────────────────────────

    def _auto_profile(self) -> str:
        """Pick voice profile based on time of day."""
        hour = datetime.datetime.now().hour
        if hour < 6 or hour >= 23:
            return "calm"
        elif 6 <= hour < 10:
            return "energetic"
        else:
            return "default"

    def _apply_profile(self, name: str) -> None:
        """Apply the rate/volume settings of a profile."""
        if not self._available:
            return
        profile = VOICE_PROFILES.get(name, VOICE_PROFILES["default"])
        if name != self._current_profile:
            self._current_profile = name
        try:
            self._engine.setProperty("rate", profile["rate"])
            self._engine.setProperty("volume", profile["volume"])
        except Exception:
            pass  # Non-critical

    # ── Status ───────────────────────────────────────────────────────────

    def status(self) -> dict:
        return {
            "tts_available": self._available,
            "current_profile": self._current_profile,
            "profiles": list(VOICE_PROFILES.keys()),
        }
