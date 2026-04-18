"""
NOVA Event Bus
==============
Lightweight publish-subscribe event system that decouples components.
The monitor can emit alerts without knowing about the voice engine;
the orchestrator can react to shutdown events from anywhere.

Usage::

    from nova.core.events import bus

    # Subscribe
    bus.on("alert_triggered", my_handler)

    # Emit
    bus.emit("alert_triggered", message="CPU is high")
"""

from __future__ import annotations

import threading
from collections import defaultdict
from typing import Any, Callable, Dict, List

from nova.utils import logger as log


class EventBus:
    """Thread-safe publish-subscribe event bus."""

    def __init__(self) -> None:
        self._subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self._lock = threading.Lock()

    # ── Subscribe ─────────────────────────────────────────────────────────
    def on(self, event: str, callback: Callable) -> None:
        """Register *callback* to be called when *event* is emitted."""
        with self._lock:
            if callback not in self._subscribers[event]:
                self._subscribers[event].append(callback)
                log.debug(f"[EventBus] Subscribed {callback.__name__} → '{event}'")

    def off(self, event: str, callback: Callable) -> None:
        """Unsubscribe *callback* from *event*."""
        with self._lock:
            try:
                self._subscribers[event].remove(callback)
            except ValueError:
                pass

    # ── Emit ──────────────────────────────────────────────────────────────
    def emit(self, event: str, **kwargs: Any) -> None:
        """
        Fire *event*, calling all registered handlers with **kwargs.
        Exceptions in individual handlers are caught so that one broken
        handler does not prevent others from running.
        """
        with self._lock:
            handlers = list(self._subscribers.get(event, []))

        for handler in handlers:
            try:
                handler(**kwargs)
            except Exception as exc:
                log.error(
                    f"[EventBus] Handler {handler.__name__} "
                    f"failed on '{event}': {exc!r}"
                )

    # ── Utility ───────────────────────────────────────────────────────────
    def clear(self) -> None:
        """Remove all subscriptions (used in tests / shutdown)."""
        with self._lock:
            self._subscribers.clear()

    @property
    def events(self) -> List[str]:
        """Return a list of events that have at least one subscriber."""
        with self._lock:
            return [e for e, subs in self._subscribers.items() if subs]


# ─── Global singleton ────────────────────────────────────────────────────────
bus = EventBus()
