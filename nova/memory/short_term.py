"""
NOVA Short-Term Memory
======================
Session-scoped ring buffer that holds the most recent conversation turns.
This is the "working memory" — it provides context for LLM calls and is
cleared when NOVA shuts down.
"""

from __future__ import annotations

import datetime
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Deque, Dict, List, Optional


@dataclass
class ConversationTurn:
    """One user ↔ NOVA exchange."""
    timestamp: str
    user: str
    nova: str
    intent: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class ShortTermMemory:
    """
    Fixed-size circular buffer of recent conversation turns.

    Parameters
    ----------
    capacity : int
        Maximum number of turns to retain (oldest are evicted).
    """

    def __init__(self, capacity: int = 20) -> None:
        self._buffer: Deque[ConversationTurn] = deque(maxlen=capacity)
        self._session_start: str = datetime.datetime.now().isoformat()
        self._command_count: int = 0

    # ── Write ─────────────────────────────────────────────────────────────
    def add(
        self,
        user_input: str,
        nova_response: str,
        intent: str = "",
        **metadata: Any,
    ) -> None:
        """Append a conversation turn."""
        self._buffer.append(ConversationTurn(
            timestamp=datetime.datetime.now().isoformat(),
            user=user_input,
            nova=nova_response,
            intent=intent,
            metadata=metadata,
        ))
        self._command_count += 1

    # ── Read ──────────────────────────────────────────────────────────────
    def recent(self, n: int = 5) -> List[Dict[str, str]]:
        """Return the last *n* turns as simple dicts (for LLM context)."""
        turns = list(self._buffer)[-n:]
        return [{"user": t.user, "nova": t.nova} for t in turns]

    def last_turn(self) -> Optional[ConversationTurn]:
        """Return the most recent turn, or None."""
        return self._buffer[-1] if self._buffer else None

    def all_turns(self) -> List[ConversationTurn]:
        """Return every turn in the buffer (oldest first)."""
        return list(self._buffer)

    # ── Session metadata ─────────────────────────────────────────────────
    @property
    def session_start(self) -> str:
        return self._session_start

    @property
    def command_count(self) -> int:
        return self._command_count

    @property
    def size(self) -> int:
        return len(self._buffer)

    # ── Lifecycle ─────────────────────────────────────────────────────────
    def clear(self) -> None:
        """Wipe the buffer (called on session end or explicit reset)."""
        self._buffer.clear()
        self._command_count = 0
