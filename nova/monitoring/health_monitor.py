"""
NOVA Background Health Monitor
===============================
Runs in a daemon thread, periodically checks system health, and
emits alerts through the event bus (no direct voice coupling).
"""

from __future__ import annotations

import threading
import time

from nova.commands.system_info import check_alerts
from nova.config.settings import MONITOR_INTERVAL_SECONDS, USER_NAME
from nova.core.events import bus
from nova.monitoring.alerts import AlertManager, Severity
from nova.utils import logger as log


class HealthMonitor:
    """
    Daemon thread that polls system health and fires cooldown-managed alerts
    via the event bus.
    """

    def __init__(self, interval: int = MONITOR_INTERVAL_SECONDS) -> None:
        self._interval = interval
        self._alert_mgr = AlertManager()
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            log.warn("Health monitor already running.")
            return
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._loop,
            daemon=True,
            name="NOVA-HealthMonitor",
        )
        self._thread.start()
        log.info("Background health monitor started.")

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5)
        log.info("Health monitor stopped.")

    def _loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                alerts = check_alerts()
                current_keys = set()
                for msg in alerts:
                    key = msg.split(":")[0].strip()
                    current_keys.add(key)
                    severity = Severity.CRITICAL if "CRITICAL" in msg else Severity.WARNING
                    if self._alert_mgr.should_fire(key):
                        self._alert_mgr.fire(key, msg, severity)
                        bus.emit(
                            "alert_triggered",
                            message=f"Alert, {USER_NAME}. {msg}",
                            severity=severity.value,
                        )

                # Resolve alerts that are no longer active
                for prev_key in list(self._alert_mgr._last_fired.keys()):
                    if prev_key not in current_keys:
                        self._alert_mgr.resolve(prev_key)

            except Exception as exc:
                log.error(f"Health monitor error: {exc}")

            self._stop_event.wait(self._interval)
