"""
NOVA Memory Manager
===================
Unified facade over short-term (session) and long-term (persistent) memory.
All other modules interact with memory exclusively through this manager.

Usage::

    from nova.memory.manager import MemoryManager
    mem = MemoryManager()
    mem.record("what time is it", "It is 4:30 PM", intent="get_time")
    context = mem.get_context(n=5)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from nova.memory.short_term import ShortTermMemory
from nova.memory.long_term import LongTermMemory
from nova.utils import logger as log


class MemoryManager:
    """
    Unified interface that wraps both memory tiers.

    - **Short-term**: fast, in-memory ring buffer for the current session.
    - **Long-term**: persistent JSON files for profile, reminders, notes, history.
    """

    def __init__(self, stm_capacity: int = 20) -> None:
        self.stm = ShortTermMemory(capacity=stm_capacity)
        self.ltm = LongTermMemory()
        log.info("Memory manager initialised.")

    # ── Record ────────────────────────────────────────────────────────────
    def record(
        self,
        user_input: str,
        nova_response: str,
        intent: str = "",
        **metadata: Any,
    ) -> None:
        """Log an interaction in both memory tiers."""
        self.stm.add(user_input, nova_response, intent=intent, **metadata)
        self.ltm.record_interaction(user_input, nova_response, intent=intent)

    def update_last_response(self, response: str) -> None:
        """Fix-up the response in the most recent turn (both tiers)."""
        last = self.stm.last_turn()
        if last is not None:
            last.nova = response
        self.ltm.update_last_response(response)

    # ── Recall ────────────────────────────────────────────────────────────
    def get_context(self, n: int = 5) -> List[Dict[str, str]]:
        """Return the last *n* turns for LLM context injection."""
        return self.stm.recent(n)

    def recall(self, query: str, max_results: int = 10) -> List[Dict]:
        """Search long-term history for *query*."""
        return self.ltm.search_history(query, max_results)

    # ── Convenience passthroughs ─────────────────────────────────────────
    def add_reminder(self, text: str, due: Optional[str] = None) -> None:
        self.ltm.add_reminder(text, due)

    def get_pending_reminders(self) -> List[Dict]:
        return self.ltm.get_pending_reminders()

    def complete_reminder(self, index: int) -> bool:
        return self.ltm.complete_reminder(index)

    def add_note(self, text: str) -> None:
        self.ltm.add_note(text)

    def get_notes(self, last_n: int = 0) -> List[Dict]:
        return self.ltm.get_notes(last_n)

    def set_preference(self, key: str, value: Any) -> None:
        self.ltm.set_preference(key, value)

    def get_preference(self, key: str, default: Any = None) -> Any:
        return self.ltm.get_preference(key, default)

    def get_stats(self) -> Dict[str, Any]:
        stats = self.ltm.get_stats()
        stats["session_commands"] = self.stm.command_count
        stats["session_start"] = self.stm.session_start
        return stats

    def recent_conversations(self, n: int = 5) -> List[Dict]:
        return self.ltm.recent_conversations(n)

    # ── Lifecycle ─────────────────────────────────────────────────────────
    def end_session(self) -> None:
        """Clear short-term memory at session end."""
        log.info(f"Session ended — {self.stm.command_count} commands in this session.")
        self.stm.clear()
