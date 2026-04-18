"""
NOVA GUI — Backend Bridge
===========================
Decouples the GUI from the NOVA backend by running all backend operations
in QThread workers and communicating results back via Qt signals.

No business logic lives here — this is pure plumbing.
"""

from __future__ import annotations

import sys
import os
import traceback

from PyQt6.QtCore import QObject, QThread, QTimer, pyqtSignal

# Ensure project root is importable
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)


# ─── Worker: Boot NOVA ──────────────────────────────────────────────────────

class BootWorker(QThread):
    """Boots the NOVA orchestrator in a background thread."""

    boot_complete = pyqtSignal(object)   # emits the Orchestrator instance
    boot_error = pyqtSignal(str)

    def run(self) -> None:
        try:
            from nova.core.orchestrator import Orchestrator
            orch = Orchestrator()
            orch.boot()
            self.boot_complete.emit(orch)
        except Exception as exc:
            self.boot_error.emit(f"{exc}\n{traceback.format_exc()}")


# ─── Worker: Process a command ──────────────────────────────────────────────

class CommandWorker(QThread):
    """Runs Router.process() off the main thread."""

    result_ready = pyqtSignal(str, str, bool)  # user_input, response, keep_running
    error = pyqtSignal(str)

    def __init__(self, router, memory, user_input: str, parent=None) -> None:
        super().__init__(parent)
        self._router = router
        self._memory = memory
        self._user_input = user_input

    def run(self) -> None:
        try:
            response, keep_running = self._router.process(self._user_input)
            self._memory.record(self._user_input, response)
            self.result_ready.emit(self._user_input, response, keep_running)
        except Exception as exc:
            self.error.emit(str(exc))


# ─── Worker: TTS speak ─────────────────────────────────────────────────────

class SpeakWorker(QThread):
    """Runs VoiceEngine.speak() off the main thread."""

    started = pyqtSignal()
    finished_speaking = pyqtSignal()

    def __init__(self, tts, text: str, profile: str | None = None, parent=None) -> None:
        super().__init__(parent)
        self._tts = tts
        self._text = text
        self._profile = profile

    def run(self) -> None:
        self.started.emit()
        try:
            self._tts.speak(self._text, profile=self._profile, silent=False)
        except Exception:
            pass
        self.finished_speaking.emit()


# ─── Worker: STT listen ────────────────────────────────────────────────────

class ListenWorker(QThread):
    """Runs a single listen cycle off the main thread."""

    text_heard = pyqtSignal(str)
    listen_error = pyqtSignal(str)

    def __init__(self, stt, timeout: int = 8, parent=None) -> None:
        super().__init__(parent)
        self._stt = stt
        self._timeout = timeout

    def run(self) -> None:
        try:
            text = self._stt.listen(timeout=self._timeout)
            self.text_heard.emit(text or "")
        except Exception as exc:
            self.listen_error.emit(str(exc))


# ─── Main Bridge ────────────────────────────────────────────────────────────

class NovaBridge(QObject):
    """
    Central bridge between the GUI and NOVA backend.

    Signals
    -------
    state_changed(str)      — "idle" / "listening" / "processing" / "speaking"
    response_ready(str, str)— (user_input, nova_response)
    system_stats(dict)      — periodic system stats snapshot
    alert_fired(str, str)   — (message, severity)
    boot_complete()
    boot_error(str)
    activity(str, str)      — (message, type) for the activity log
    """

    state_changed = pyqtSignal(str)
    response_ready = pyqtSignal(str, str)
    system_stats = pyqtSignal(dict)
    alert_fired = pyqtSignal(str, str)
    boot_complete = pyqtSignal()
    boot_error = pyqtSignal(str)
    activity = pyqtSignal(str, str)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)

        self._orchestrator = None
        self._booted = False

        # Active workers (prevent GC)
        self._active_workers: list[QThread] = []

        # Stats polling timer
        self._stats_timer = QTimer(self)
        self._stats_timer.setInterval(2500)  # 2.5 seconds
        self._stats_timer.timeout.connect(self._poll_stats)

    # ── Boot ─────────────────────────────────────────────────────────

    def start_boot(self) -> None:
        """Kick off the NOVA boot sequence in a background thread."""
        self.activity.emit("Boot sequence initiated…", "system")
        worker = BootWorker()
        worker.boot_complete.connect(self._on_boot_complete)
        worker.boot_error.connect(self._on_boot_error)
        worker.finished.connect(lambda: self._cleanup_worker(worker))
        self._active_workers.append(worker)
        worker.start()

    def _on_boot_complete(self, orch) -> None:
        self._orchestrator = orch
        self._booted = True

        # Subscribe to event bus for alerts
        from nova.core.events import bus
        bus.on("alert_triggered", self._on_backend_alert)

        # Start stats polling
        self._stats_timer.start()

        self.boot_complete.emit()
        self.activity.emit("NOVA online — all systems operational", "success")
        self.state_changed.emit("idle")

    def _on_boot_error(self, error_msg: str) -> None:
        self.boot_error.emit(error_msg)
        self.activity.emit(f"Boot failed: {error_msg[:80]}", "alert")

    # ── Commands ─────────────────────────────────────────────────────

    def send_command(self, text: str) -> None:
        """Process a user command in a background thread."""
        if not self._booted or not self._orchestrator:
            self.response_ready.emit(text, "NOVA is still booting. Please wait…")
            return

        self.state_changed.emit("processing")
        self.activity.emit(f"CMD: {text}", "command")

        # Track the command
        try:
            self._orchestrator._tracker.log_command(text)
        except Exception:
            pass

        worker = CommandWorker(
            self._orchestrator._router,
            self._orchestrator._memory,
            text,
        )
        worker.result_ready.connect(self._on_command_result)
        worker.error.connect(self._on_command_error)
        worker.finished.connect(lambda: self._cleanup_worker(worker))
        self._active_workers.append(worker)
        worker.start()

    def _on_command_result(self, user_input: str, response: str, keep_running: bool) -> None:
        self.response_ready.emit(user_input, response)
        self.activity.emit(f"RSP: {response[:60]}…" if len(response) > 60 else f"RSP: {response}", "response")

        # Speak the response
        self._speak(response)

        if not keep_running:
            self.activity.emit("Shutdown requested", "warning")

    def _on_command_error(self, error_msg: str) -> None:
        self.response_ready.emit("", f"Error: {error_msg}")
        self.state_changed.emit("idle")
        self.activity.emit(f"Error: {error_msg[:60]}", "alert")

    # ── Voice ────────────────────────────────────────────────────────

    def start_listening(self) -> None:
        """Begin a single listening cycle."""
        if not self._booted or not self._orchestrator:
            return
        if not self._orchestrator._stt.available:
            self.activity.emit("Microphone not available", "warning")
            return

        self.state_changed.emit("listening")
        self.activity.emit("Listening…", "system")

        worker = ListenWorker(self._orchestrator._stt, timeout=8)
        worker.text_heard.connect(self._on_text_heard)
        worker.listen_error.connect(self._on_listen_error)
        worker.finished.connect(lambda: self._cleanup_worker(worker))
        self._active_workers.append(worker)
        worker.start()

    def _on_text_heard(self, text: str) -> None:
        if text:
            self.activity.emit(f"Heard: \"{text}\"", "success")
            self.send_command(text)
        else:
            self.state_changed.emit("idle")
            self.activity.emit("No speech detected", "system")

    def _on_listen_error(self, error_msg: str) -> None:
        self.state_changed.emit("idle")
        self.activity.emit(f"Listen error: {error_msg[:60]}", "alert")

    def stop_listening(self) -> None:
        """Cancel listening (sets state back to idle)."""
        self.state_changed.emit("idle")

    def _speak(self, text: str) -> None:
        """Speak text off the main thread."""
        if not self._booted or not self._orchestrator:
            return
        if not self._orchestrator._tts.available:
            self.state_changed.emit("idle")
            return

        self.state_changed.emit("speaking")

        worker = SpeakWorker(self._orchestrator._tts, text)
        worker.finished_speaking.connect(lambda: self.state_changed.emit("idle"))
        worker.finished.connect(lambda: self._cleanup_worker(worker))
        self._active_workers.append(worker)
        worker.start()

    # ── Voice mode ───────────────────────────────────────────────────

    def set_voice_mode(self, mode: str) -> None:
        """Change the TTS voice profile."""
        if self._booted and self._orchestrator and self._orchestrator._tts:
            self._orchestrator._tts.set_profile(mode)
            self.activity.emit(f"Voice mode: {mode}", "system")

    # ── Stats polling ────────────────────────────────────────────────

    def _poll_stats(self) -> None:
        """Poll system stats (runs in main thread — psutil calls are fast)."""
        try:
            from nova.commands.system_info import _full_snapshot
            stats = _full_snapshot()
            self.system_stats.emit(stats)
        except Exception:
            pass

    # ── Alert handler ────────────────────────────────────────────────

    def _on_backend_alert(self, message: str = "", severity: str = "", **kw) -> None:
        """Called from the event bus (may be on a different thread)."""
        self.alert_fired.emit(message, severity)
        self.activity.emit(f"ALERT: {message}", "alert")

    # ── Lifecycle ────────────────────────────────────────────────────

    def shutdown(self) -> None:
        """Clean shutdown."""
        self._stats_timer.stop()
        if self._orchestrator:
            try:
                self._orchestrator._shutdown()
            except Exception:
                pass
        # Wait for workers
        for w in self._active_workers:
            if w.isRunning():
                w.quit()
                w.wait(2000)
        self._active_workers.clear()

    def _cleanup_worker(self, worker: QThread) -> None:
        if worker in self._active_workers:
            self._active_workers.remove(worker)

    # ── Properties ───────────────────────────────────────────────────

    @property
    def is_booted(self) -> bool:
        return self._booted

    @property
    def mic_available(self) -> bool:
        if self._orchestrator and self._orchestrator._stt:
            return self._orchestrator._stt.available
        return False

    def get_config(self) -> dict:
        """Return config values for the settings panel."""
        try:
            from nova.config.settings import USER_NAME, LLM_PROVIDER
            return {"user_name": USER_NAME, "llm_provider": LLM_PROVIDER}
        except Exception:
            return {"user_name": "Unknown", "llm_provider": "Unknown"}
