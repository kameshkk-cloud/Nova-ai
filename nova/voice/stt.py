"""
NOVA Speech-to-Text Engine
===========================
Listens via microphone (SpeechRecognition + PyAudio) with automatic
fallback to keyboard input if hardware is unavailable.

Includes retry logic for transient recognition failures.
"""

from __future__ import annotations

from typing import Optional

from nova.config.settings import USER_NAME
from nova.utils import logger as log


class SpeechListener:
    """Microphone-based speech recognition with keyboard fallback."""

    def __init__(self) -> None:
        self._recognizer = None
        self._available = False
        self._init_stt()

    def _init_stt(self) -> None:
        try:
            import speech_recognition as sr
            self._recognizer = sr.Recognizer()
            self._recognizer.energy_threshold = 300
            self._recognizer.dynamic_energy_threshold = True
            # Smoke-test PyAudio
            try:
                import pyaudio
                pyaudio.PyAudio().terminate()
                self._available = True
                log.debug("SpeechRecognition + PyAudio ready.")
            except Exception as exc:
                self._available = False
                log.warn(f"PyAudio not available: {exc} — keyboard fallback.")
        except ImportError:
            self._available = False
            log.warn("speech_recognition not installed — keyboard fallback.")

    @property
    def available(self) -> bool:
        return self._available

    def listen(self, timeout: int = 6, phrase_limit: int = 10) -> str:
        """
        Listen for speech and return recognised text (lowercased).
        Falls back to keyboard if mic is unavailable.
        Returns empty string on silence/timeout.
        """
        if not self._available:
            return self._keyboard_fallback()
        return self._mic_listen(timeout, phrase_limit)

    def _mic_listen(self, timeout: int, phrase_limit: int) -> str:
        import speech_recognition as sr
        max_attempts = 2
        for attempt in range(1, max_attempts + 1):
            try:
                with sr.Microphone() as source:
                    self._recognizer.adjust_for_ambient_noise(source, duration=0.4)
                    log.info("🎙  Listening...")
                    audio = self._recognizer.listen(
                        source, timeout=timeout, phrase_time_limit=phrase_limit,
                    )
                text = self._recognizer.recognize_google(audio).lower()
                log.info(f"Heard: '{text}'")
                return text

            except sr.WaitTimeoutError:
                log.debug("Mic timeout — no speech detected.")
                return ""
            except sr.UnknownValueError:
                log.debug("Could not understand audio.")
                if attempt < max_attempts:
                    continue
                return ""
            except sr.RequestError as exc:
                log.warn(f"Google STT error: {exc}")
                return ""
            except OSError as exc:
                log.warn(f"Mic access error: {exc}")
                return self._keyboard_fallback()
            except Exception as exc:
                log.warn(f"STT error: {exc}")
                return self._keyboard_fallback()
        return ""

    @staticmethod
    def _keyboard_fallback() -> str:
        try:
            text = input(f"  [{USER_NAME}] > ").strip().lower()
            return text
        except (EOFError, KeyboardInterrupt):
            return "exit"

    def status(self) -> dict:
        return {"stt_available": self._available}
