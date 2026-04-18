"""
NOVA Alert Manager
==================
Per-alert-type cooldown, severity levels, deduplication, and history.
Prevents alert spam while ensuring critical issues are surfaced.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List

from nova.config.settings import ALERT_COOLDOWN_SECONDS
from nova.utils import logger as log


class Severity(Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


@dataclass
class Alert:
    message: str
    severity: Severity
    timestamp: float = field(default_factory=time.time)


class AlertManager:
    """
    Manages alert state with per-type cooldowns and history.

    Once an alert fires, the same alert type is suppressed for
    ``cooldown_seconds`` (default 300 = 5 minutes).
    """

    def __init__(self, cooldown_seconds: int = ALERT_COOLDOWN_SECONDS) -> None:
        self._cooldown = cooldown_seconds
        self._last_fired: Dict[str, float] = {}
        self._history: List[Alert] = []

    def should_fire(self, alert_key: str) -> bool:
        """Return True if enough time has elapsed since the last alert of this type."""
        last = self._last_fired.get(alert_key, 0.0)
        return (time.time() - last) >= self._cooldown

    def fire(self, alert_key: str, message: str, severity: Severity = Severity.WARNING) -> bool:
        """
        Attempt to fire an alert. Returns True if it was actually emitted
        (i.e. not suppressed by cooldown).
        """
        if not self.should_fire(alert_key):
            return False
        self._last_fired[alert_key] = time.time()
        alert = Alert(message=message, severity=severity)
        self._history.append(alert)
        # Keep history bounded
        if len(self._history) > 200:
            self._history = self._history[-200:]
        log.warn(f"[Alert] [{severity.value}] {message}")
        return True

    def resolve(self, alert_key: str) -> None:
        """Mark an alert type as resolved (allows it to fire again immediately)."""
        self._last_fired.pop(alert_key, None)

    @property
    def recent(self) -> List[Alert]:
        return self._history[-10:]

    def clear(self) -> None:
        self._last_fired.clear()
        self._history.clear()
