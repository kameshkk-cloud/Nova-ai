"""
NOVA Orchestrator
=================
Central lifecycle manager that boots all subsystems, runs the main
interaction loop, and handles graceful shutdown.

This is the single "God object" — intentionally — because it is the only
place where all subsystems are wired together.
"""

from __future__ import annotations

import datetime
import sys

from nova.brain.llm import LLMClient
from nova.brain.router import Router
from nova.commands.productivity import get_tracker
from nova.commands.registry import CommandRegistry
from nova.config.settings import (
    ACTIVATE_MODE, ASSISTANT_NAME, USER_NAME, WAKE_WORD,
)
from nova.core.events import bus
from nova.memory.manager import MemoryManager
from nova.monitoring.health_monitor import HealthMonitor
from nova.plugins.loader import load_plugins
from nova.utils import logger as log
from nova.voice.stt import SpeechListener
from nova.voice.tts import VoiceEngine
from nova.voice.wake_word import WakeWordDetector


class Orchestrator:
    """Boots NOVA, runs the main loop, and tears everything down cleanly."""

    def __init__(self) -> None:
        self._running = False

        # Subsystems (initialised in boot())
        self._tts: VoiceEngine | None = None
        self._stt: SpeechListener | None = None
        self._wake: WakeWordDetector | None = None
        self._memory: MemoryManager | None = None
        self._registry: CommandRegistry | None = None
        self._router: Router | None = None
        self._monitor: HealthMonitor | None = None
        self._tracker = get_tracker()

    # ══════════════════════════════════════════════════════════════════════
    #  BOOT
    # ══════════════════════════════════════════════════════════════════════

    def boot(self) -> None:
        """Initialise every subsystem in dependency order."""
        self._print_banner()
        log.info("NOVA boot sequence initiated...")

        # 1. Voice
        self._tts = VoiceEngine()
        self._stt = SpeechListener()
        self._wake = WakeWordDetector(self._stt)
        self._log_voice_status()

        # 2. Memory
        self._memory = MemoryManager()

        # 3. Commands
        self._registry = CommandRegistry()
        load_plugins()                          # import plugin @commands
        self._registry.load_builtin_commands()  # import builtin @commands + drain

        # 4. Brain
        llm = LLMClient()
        self._router = Router(self._registry, self._memory, llm)

        # 5. Monitoring — subscribe to alerts via event bus
        bus.on("alert_triggered", self._on_alert)
        self._monitor = HealthMonitor()
        self._monitor.start()

        # 6. Greet
        self._greet()
        self._proactive_check()

        log.info("Boot complete. NOVA is online.")

    # ══════════════════════════════════════════════════════════════════════
    #  MAIN LOOP
    # ══════════════════════════════════════════════════════════════════════

    def run(self) -> None:
        """Main interaction loop — runs until 'exit' or Ctrl+C."""
        self._running = True
        log.info(f"Waiting for wake word: '{WAKE_WORD}'")
        print(f"\n  [Wake word: '{WAKE_WORD}' | Type commands directly | 'exit' to quit]\n")

        while self._running:
            try:
                command = self._get_command()
                if not command:
                    continue

                log.info(f"Command received: '{command}'")
                self._tracker.log_command(command)

                # Process through brain
                response, keep_running = self._router.process(command)

                # Record in memory
                self._memory.record(command, response)

                # Speak
                self._tts.speak(response)

                if not keep_running:
                    self._running = False

            except KeyboardInterrupt:
                log.info("KeyboardInterrupt — shutting down.")
                self._tts.speak(f"Emergency shutdown, {USER_NAME}. NOVA offline.")
                self._running = False

            except Exception as exc:
                log.exception(f"Main loop error: {exc}")
                self._tts.speak(f"I encountered an error, {USER_NAME}. Recovering...")

        self._shutdown()

    # ══════════════════════════════════════════════════════════════════════
    #  INPUT HANDLING
    # ══════════════════════════════════════════════════════════════════════

    def _get_command(self) -> str:
        """Get next command via voice or keyboard."""
        if self._stt.available:
            return self._voice_input()
        return self._keyboard_input()

    def _voice_input(self) -> str:
        """Listen for wake word, then capture the actual command."""
        text = self._stt.listen(timeout=8)
        if not text:
            return ""

        # Check for wake word
        if self._wake.check(text):
            self._tts.speak(f"Yes, {USER_NAME}?")
            command = self._stt.listen(timeout=8)
            return command or ""

        # Direct command (3+ words, no wake word required)
        if self._wake.is_direct_command(text):
            return text

        return ""

    def _keyboard_input(self) -> str:
        """Read from stdin."""
        try:
            return input(f"\n  [{USER_NAME}] > ").strip()
        except (KeyboardInterrupt, EOFError):
            return "exit"

    # ══════════════════════════════════════════════════════════════════════
    #  LIFECYCLE
    # ══════════════════════════════════════════════════════════════════════

    def _shutdown(self) -> None:
        """Clean shutdown of all subsystems."""
        log.info("Shutting down NOVA...")
        if self._monitor:
            self._monitor.stop()
        self._tracker.end_session()
        if self._memory:
            self._memory.end_session()
        bus.clear()
        log.info("NOVA offline. Goodbye.")

    # ══════════════════════════════════════════════════════════════════════
    #  HELPERS
    # ══════════════════════════════════════════════════════════════════════

    def _on_alert(self, message: str = "", severity: str = "", **kw) -> None:
        """Event handler for health monitor alerts."""
        profile = "alert" if severity == "CRITICAL" else "energetic"
        self._tts.speak(message, profile=profile)

    def _greet(self) -> None:
        hour = datetime.datetime.now().hour
        if hour < 5:
            period = "Good night"
        elif hour < 12:
            period = "Good morning"
        elif hour < 17:
            period = "Good afternoon"
        else:
            period = "Good evening"
        self._tts.speak(
            f"{period}, {USER_NAME}. I am {ASSISTANT_NAME}, your personal AI assistant. "
            f"Systems are online. Say '{WAKE_WORD}' to activate me, "
            f"or type your command directly."
        )

    def _proactive_check(self) -> None:
        reminders = self._memory.get_pending_reminders()
        if reminders:
            count = len(reminders)
            self._tts.speak(
                f"By the way, {USER_NAME}, you have {count} pending "
                f"reminder{'s' if count > 1 else ''}. "
                f"Say 'my reminders' to hear them."
            )

    def _log_voice_status(self) -> None:
        if not self._tts.available:
            log.warn("TTS not available. pip install pyttsx3")
        if not self._stt.available:
            log.warn("STT not available. pip install SpeechRecognition pyaudio")
            log.info("Falling back to KEYBOARD INPUT mode.")

    @staticmethod
    def _print_banner() -> None:
        banner = f"""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   ███╗   ██╗ ██████╗ ██╗   ██╗ █████╗                       ║
║   ████╗  ██║██╔═══██╗██║   ██║██╔══██╗                      ║
║   ██╔██╗ ██║██║   ██║██║   ██║███████║                      ║
║   ██║╚██╗██║██║   ██║╚██╗ ██╔╝██╔══██║                      ║
║   ██║ ╚████║╚██████╔╝ ╚████╔╝ ██║  ██║                      ║
║   ╚═╝  ╚═══╝ ╚═════╝   ╚═══╝  ╚═╝  ╚═╝                      ║
║                                                              ║
║   Neural Operative Virtual Assistant                         ║
║   Version 2.0 — Production Build                             ║
║   Built for: {USER_NAME:<44}║
╚══════════════════════════════════════════════════════════════╝
"""
        print(banner)
