"""
NOVA Text-to-Speech Engine — JARVIS Edition
=============================================
Thread-safe, JARVIS-style TTS using pyttsx3 with SAPI5 backend.

The engine runs on a **dedicated background thread** with a command queue,
which eliminates the pyttsx3 "run loop already active" crashes that caused
the broken/stuttering voice.

Voice profiles:
    jarvis    — The default. Smooth, authoritative (165 wpm)
    calm      — Slow and gentle, late-night mode (150 wpm)
    energetic — Upbeat morning voice (180 wpm)
    alert     — Urgent but clear (175 wpm)
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
    """Thread-safe, JARVIS-style text-to-speech engine.

    All pyttsx3 calls happen on a single dedicated thread to avoid the
    infamous 'run loop already active' RuntimeError.  The public ``speak()``
    method just drops text onto a queue and returns immediately (or blocks
    until spoken if ``block=True``).
    """

    def __init__(self) -> None:
        self._engine = None
        self._available = False
        self._current_profile = "jarvis"
        self._queue: queue.Queue = queue.Queue()
        self._lock = threading.Lock()
        self._worker: Optional[threading.Thread] = None
        self._running = False
        self._speaking = threading.Event()

        # Boot the engine on its dedicated thread
        self._init_engine()
        if self._available:
            self._start_worker()

    # ── Initialisation ───────────────────────────────────────────────────

    def _init_engine(self) -> None:
        try:
            import platform
            import pyttsx3

            _system = platform.system()

            # Auto-select TTS driver based on OS
            if _system == "Windows":
                self._engine = pyttsx3.init("sapi5")
            elif _system == "Darwin":  # macOS
                self._engine = pyttsx3.init("nsss")
            else:  # Linux
                self._engine = pyttsx3.init("espeak")

            voices = self._engine.getProperty("voices")

            # ── Select the best voice for JARVIS ─────────────────────
            selected_voice = None
            for v in voices:
                name_lower = v.name.lower()
                if _system == "Windows":
                    # Microsoft David = deep, authoritative male
                    if "david" in name_lower:
                        selected_voice = v
                        break
                else:
                    # On Linux/Mac, prefer English male voices
                    if "english" in name_lower and "male" in str(getattr(v, 'gender', '')).lower():
                        selected_voice = v
                        break
                    if "en" in name_lower or "english" in name_lower:
                        selected_voice = v
                        # Don't break — keep looking for a male one

            # Fallback: pick first male, or just the first voice
            if selected_voice is None:
                if VOICE_GENDER == "female" and len(voices) > 1:
                    selected_voice = voices[1]
                elif voices:
                    selected_voice = voices[0]

            if selected_voice:
                self._engine.setProperty("voice", selected_voice.id)
                log.info(f"TTS voice selected: {selected_voice.name}")

            # ── JARVIS tuning ────────────────────────────────────────
            # Rate 165 = smooth, deliberate delivery (not robotic-fast)
            self._engine.setProperty("rate", VOICE_RATE)
            # Full volume for confident delivery
            self._engine.setProperty("volume", VOICE_VOLUME)

            self._available = True
            log.debug("pyttsx3 SAPI5 TTS engine ready (JARVIS mode).")

        except Exception as exc:
            self._available = False
            log.warn(f"pyttsx3 not available: {exc} — print-only mode.")

    # ── Background Worker ────────────────────────────────────────────────

    def _start_worker(self) -> None:
        """Start the dedicated TTS thread."""
        self._running = True
        self._worker = threading.Thread(
            target=self._worker_loop, daemon=True, name="NOVA-TTS",
        )
        self._worker.start()

    def _worker_loop(self) -> None:
        """Process speak requests from the queue on this single thread.

        Only this thread ever touches self._engine, which prevents
        the pyttsx3 threading issues that caused the broken voice.
        """
        while self._running:
            try:
                item = self._queue.get(timeout=0.5)
            except queue.Empty:
                continue

            if item is None:
                # Poison pill — shutdown signal
                break

            text, profile, done_event = item

            try:
                self._speaking.set()
                self._apply_profile(profile)
                self._engine.say(text)
                self._engine.runAndWait()
            except RuntimeError:
                # Engine loop stuck — force stop and retry once
                try:
                    self._engine.stop()
                    self._engine.say(text)
                    self._engine.runAndWait()
                except Exception as exc:
                    log.error(f"TTS retry failed: {exc}")
            except Exception as exc:
                log.error(f"TTS error: {exc}")
            finally:
                self._speaking.clear()
                if done_event:
                    done_event.set()
                self._queue.task_done()

    # ── Public API ────────────────────────────────────────────────────────

    def speak(
        self,
        text: str,
        profile: Optional[str] = None,
        silent: bool = False,
        block: bool = False,
    ) -> None:
        """
        Speak *text* aloud (or print if TTS unavailable).

        Parameters
        ----------
        profile : str, optional
            Force a voice profile ("calm", "energetic", "alert", "jarvis").
            If None, auto-selects based on time of day.
        silent : bool
            If True, print only — do not speak.
        block : bool
            If True, wait until speech finishes before returning.
        """
        log.nova_say(ASSISTANT_NAME, text)

        if silent or not self._available:
            return

        chosen = profile or self._auto_profile()
        done_event = threading.Event() if block else None

        self._queue.put((text, chosen, done_event))

        if block and done_event:
            done_event.wait(timeout=30)

    def stop(self) -> None:
        """Stop any current speech immediately."""
        if self._available and self._engine:
            try:
                self._engine.stop()
            except Exception:
                pass

    def is_speaking(self) -> bool:
        """Return True if the engine is currently speaking."""
        return self._speaking.is_set()

    def set_profile(self, name: str) -> None:
        """Explicitly switch voice profile."""
        if name in VOICE_PROFILES:
            self._current_profile = name
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
            return "jarvis"

    def _apply_profile(self, name: str) -> None:
        """Apply the rate/volume settings of a profile.

        Called ONLY from the worker thread, so no locking needed.
        """
        if not self._available:
            return
        profile = VOICE_PROFILES.get(name, VOICE_PROFILES["jarvis"])
        self._current_profile = name
        try:
            self._engine.setProperty("rate", profile["rate"])
            self._engine.setProperty("volume", profile["volume"])
        except Exception:
            pass  # Non-critical

    # ── Shutdown ─────────────────────────────────────────────────────────

    def shutdown(self) -> None:
        """Cleanly shut down the TTS worker thread."""
        self._running = False
        self._queue.put(None)  # Poison pill
        if self._worker and self._worker.is_alive():
            self._worker.join(timeout=3)
        if self._engine:
            try:
                self._engine.stop()
            except Exception:
                pass

    # ── Status ───────────────────────────────────────────────────────────

    def status(self) -> dict:
        return {
            "tts_available": self._available,
            "current_profile": self._current_profile,
            "profiles": list(VOICE_PROFILES.keys()),
            "is_speaking": self.is_speaking(),
        }
