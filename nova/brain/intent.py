"""
NOVA Intent Classifier
======================
Maps raw user text to a structured Intent using fast pattern matching
as the primary path, with optional LLM-based classification for
ambiguous inputs.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from nova.utils import logger as log


@dataclass
class Intent:
    """Result of classifying a user utterance."""
    name: str
    confidence: float = 1.0
    entity: Optional[str] = None
    raw_text: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


# ─── Pattern table ───────────────────────────────────────────────────────────
# (compiled_regex, intent_name, entity_group_index_or_None)

_RAW_PATTERNS: List[Tuple[str, str, Optional[int]]] = [
    # Time / Date
    (r"\btime\b", "get_time", None),
    (r"\bdate\b|\bday\b|\btoday\b", "get_date", None),

    # System
    (r"cpu|processor", "cpu_status", None),
    (r"ram|memory usage", "ram_status", None),
    (r"battery", "battery_status", None),
    (r"disk|storage|space", "disk_status", None),
    (r"system (?:status|report|health)", "system_report", None),
    (r"network|internet|connection", "network_status", None),
    (r"top processes|running apps", "top_processes", None),

    # Apps
    (r"open (https?://\S+|www\.\S+)", "open_url", 1),
    (r"(?:open|launch) (.+)", "open_app", 1),
    (r"(?:close|kill) (.+)", "close_app", 1),
    (r"(?:search|google) (.+)", "search_web", 1),

    # Power
    (r"shutdown|shut down", "shutdown", None),
    (r"restart|reboot", "restart", None),
    (r"cancel shutdown|abort", "cancel_shutdown", None),
    (r"lock|screen saver", "lock_screen", None),

    # Volume
    (r"volume up|louder|increase volume", "volume_up", None),
    (r"volume down|quieter|lower volume", "volume_down", None),
    (r"mute|silence", "mute", None),
    (r"screenshot|capture screen", "screenshot", None),

    # Files
    (r"organis?e (.+)|sort (.+)", "organize_folder", 1),
    (r"summari[sz]e (.+)|analy[sz]e (.+)", "summarize_file", 1),
    (r"find (.+?) file|search for (.+)", "find_file", 1),

    # Memory
    (r"remind me (.+)|set reminder (.+)", "add_reminder", 1),
    (r"note (.+)|remember (.+)", "add_note", 1),
    (r"my reminders|pending reminders", "show_reminders", None),
    (r"my notes|show notes", "show_notes", None),
    (r"my stats|usage stats|interactions", "usage_stats", None),

    # Productivity
    (r"daily report|productivity", "daily_report", None),

    # NOVA control
    (r"stop|exit|goodbye|quit|offline", "exit", None),
    (r"help|what can you do|commands", "help", None),
    (r"status|how are you|are you ok", "nova_status", None),
    (r"clear|reset", "clear", None),
]

# Pre-compile patterns for speed
_PATTERNS = [
    (re.compile(pattern, re.IGNORECASE), intent, group)
    for pattern, intent, group in _RAW_PATTERNS
]


class IntentClassifier:
    """
    Classify user input into an Intent.

    Strategy:
    1. Fast regex pattern matching (< 1 ms)
    2. If no pattern matches → returns intent "general_conversation"
    """

    def classify(self, text: str) -> Intent:
        """Return the best-matching Intent for *text*."""
        cleaned = text.strip().lower()

        for regex, intent_name, group_idx in _PATTERNS:
            match = regex.search(cleaned)
            if match:
                entity = None
                if group_idx is not None:
                    # Try the specified group, then fallback groups
                    for g in range(group_idx, match.lastindex or group_idx):
                        entity = match.group(g)
                        if entity:
                            break
                    if not entity:
                        try:
                            entity = match.group(group_idx)
                        except IndexError:
                            entity = None

                log.debug(f"[Intent] Pattern match: '{intent_name}' (entity={entity!r})")
                return Intent(
                    name=intent_name,
                    confidence=1.0,
                    entity=entity.strip() if entity else None,
                    raw_text=text,
                )

        # No pattern matched → general conversation
        log.debug(f"[Intent] No pattern match for: '{cleaned[:60]}' → general_conversation")
        return Intent(
            name="general_conversation",
            confidence=0.5,
            raw_text=text,
        )
