"""
NOVA Long-Term Memory
=====================
Persistent JSON-backed storage for user profile, reminders, notes,
command frequency, and full conversation archive.

Survives across sessions — this is NOVA's "hard drive".
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from nova.config.settings import MEMORY_FILE, CONVO_FILE
from nova.utils import logger as log


# ─── Safe JSON I/O ───────────────────────────────────────────────────────────

def _load_json(filepath: str, default: Any) -> Any:
    """Load a JSON file, returning *default* if missing or corrupt."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except (json.JSONDecodeError, IOError) as exc:
            log.warn(f"Could not read {filepath} ({exc!r}); starting fresh.")
    return default


def _save_json(filepath: str, data: Any) -> None:
    """Atomically write *data* to a JSON file."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    tmp_path = filepath + ".tmp"
    try:
        with open(tmp_path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False)
        # Atomic rename (same filesystem)
        if os.path.exists(filepath):
            os.replace(tmp_path, filepath)
        else:
            os.rename(tmp_path, filepath)
    except Exception:
        # Fallback: direct write
        with open(filepath, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False)


# ─── Long-Term Memory ────────────────────────────────────────────────────────

_DEFAULT_PROFILE: Dict[str, Any] = {
    "user_name": "KK Sir",
    "created_at": "",
    "interactions": 0,
    "last_seen": None,
    "preferences": {},
    "reminders": [],
    "notes": [],
    "favorite_commands": {},
}


class LongTermMemory:
    """
    Persistent profile + conversation archive backed by JSON files.

    Files used:
        - ``MEMORY_FILE``  →  user profile, reminders, notes, stats
        - ``CONVO_FILE``   →  full conversation history (capped at 500)
    """

    MAX_HISTORY = 500

    def __init__(self) -> None:
        self._profile: Dict[str, Any] = _load_json(
            MEMORY_FILE, {**_DEFAULT_PROFILE, "created_at": str(datetime.now().date())}
        )
        self._conversations: Dict[str, list] = _load_json(
            CONVO_FILE, {"history": []}
        )
        log.debug("Long-term memory loaded.")

    # ── Interactions ──────────────────────────────────────────────────────
    def record_interaction(
        self,
        user_input: str,
        nova_response: str,
        intent: str = "",
    ) -> None:
        """Persist a single conversation turn."""
        self._profile["interactions"] += 1
        self._profile["last_seen"] = datetime.now().isoformat()

        # Track command frequency
        key = user_input.strip().lower()[:60]
        freq = self._profile.setdefault("favorite_commands", {})
        freq[key] = freq.get(key, 0) + 1

        # Append to history
        self._conversations["history"].append({
            "time": datetime.now().isoformat(),
            "user": user_input,
            "nova": nova_response,
            "intent": intent,
        })

        # Cap history size
        hist = self._conversations["history"]
        if len(hist) > self.MAX_HISTORY:
            self._conversations["history"] = hist[-self.MAX_HISTORY:]

        self._flush()
        log.debug(f"LTM: interaction #{self._profile['interactions']} recorded.")

    def update_last_response(self, response: str) -> None:
        """Overwrite the nova response of the most recent history entry."""
        hist = self._conversations["history"]
        if hist:
            hist[-1]["nova"] = response
            self._flush()

    # ── Preferences ──────────────────────────────────────────────────────
    def set_preference(self, key: str, value: Any) -> None:
        self._profile["preferences"][key] = value
        self._flush()

    def get_preference(self, key: str, default: Any = None) -> Any:
        return self._profile["preferences"].get(key, default)

    # ── Reminders ────────────────────────────────────────────────────────
    def add_reminder(self, text: str, due: Optional[str] = None) -> None:
        self._profile["reminders"].append({
            "text": text,
            "due": due,
            "done": False,
            "created": datetime.now().isoformat(),
        })
        self._flush()
        log.info(f"Reminder added: {text}")

    def get_pending_reminders(self) -> List[Dict]:
        return [r for r in self._profile["reminders"] if not r["done"]]

    def complete_reminder(self, index: int) -> bool:
        pending = self.get_pending_reminders()
        if 0 <= index < len(pending):
            pending[index]["done"] = True
            self._flush()
            return True
        return False

    # ── Notes ────────────────────────────────────────────────────────────
    def add_note(self, text: str) -> None:
        self._profile["notes"].append({
            "text": text,
            "created": datetime.now().isoformat(),
        })
        self._flush()

    def get_notes(self, last_n: int = 0) -> List[Dict]:
        notes = self._profile["notes"]
        return notes[-last_n:] if last_n else notes

    # ── Stats ────────────────────────────────────────────────────────────
    def get_stats(self) -> Dict[str, Any]:
        return {
            "total_interactions": self._profile["interactions"],
            "last_seen": self._profile["last_seen"],
            "reminders_pending": len(self.get_pending_reminders()),
            "notes_count": len(self._profile["notes"]),
            "history_size": len(self._conversations["history"]),
        }

    # ── History queries ──────────────────────────────────────────────────
    def recent_conversations(self, n: int = 5) -> List[Dict]:
        return self._conversations["history"][-n:]

    def search_history(self, query: str, max_results: int = 10) -> List[Dict]:
        """Search past interactions by keyword."""
        q = query.lower()
        results = []
        for turn in reversed(self._conversations["history"]):
            if q in turn.get("user", "").lower() or q in turn.get("nova", "").lower():
                results.append(turn)
                if len(results) >= max_results:
                    break
        return results

    # ── Internal ─────────────────────────────────────────────────────────
    def _flush(self) -> None:
        _save_json(MEMORY_FILE, self._profile)
        _save_json(CONVO_FILE, self._conversations)
