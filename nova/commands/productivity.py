"""
NOVA Commands — Productivity Tracking
======================================
Activity logging, session stats, and daily reports.
"""

from __future__ import annotations

import json
import os
from collections import Counter
from datetime import datetime, date
from typing import Optional

from nova.commands.registry import CommandResult, command
from nova.config.settings import ACTIVITY_FILE, USER_NAME
from nova.utils import logger as log


class ActivityTracker:
    """Tracks per-session commands and generates productivity reports."""

    def __init__(self) -> None:
        self._data = self._load()
        self._session = {
            "date": str(date.today()),
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "commands": [],
            "categories": Counter(),
        }

    def _load(self) -> dict:
        os.makedirs(os.path.dirname(ACTIVITY_FILE), exist_ok=True)
        if os.path.exists(ACTIVITY_FILE):
            try:
                with open(ACTIVITY_FILE, "r", encoding="utf-8") as fh:
                    return json.load(fh)
            except Exception:
                pass
        return {"sessions": []}

    def _save(self) -> None:
        with open(ACTIVITY_FILE, "w", encoding="utf-8") as fh:
            json.dump(self._data, fh, indent=2)

    def log_command(self, command_text: str, category: str = "general") -> None:
        self._session["commands"].append({
            "time": datetime.now().isoformat(),
            "command": command_text[:100],
            "category": category,
        })
        self._session["categories"][category] += 1

    def end_session(self) -> None:
        self._session["end_time"] = datetime.now().isoformat()
        self._session["categories"] = dict(self._session["categories"])
        try:
            start = datetime.fromisoformat(self._session["start_time"])
            end = datetime.fromisoformat(self._session["end_time"])
            self._session["duration_minutes"] = round((end - start).seconds / 60, 1)
        except Exception:
            self._session["duration_minutes"] = 0
        self._data["sessions"].append(self._session)
        self._save()
        log.info(f"Session saved: {len(self._session['commands'])} commands logged.")

    def daily_report(self) -> str:
        today_str = str(date.today())
        today_sessions = [s for s in self._data["sessions"] if s.get("date") == today_str]
        all_commands = []
        total_minutes = 0
        all_categories = Counter()
        for s in today_sessions:
            all_commands.extend(s.get("commands", []))
            total_minutes += s.get("duration_minutes", 0)
            all_categories.update(s.get("categories", {}))
        all_commands.extend(self._session["commands"])
        all_categories.update(self._session["categories"])
        total = len(all_commands)
        top = all_categories.most_common(1)
        top_label = top[0][0] if top else "general"
        report = (
            f"Today's report, {USER_NAME}. "
            f"You've given {total} commands across {total_minutes} minutes. "
            f"Most used: {top_label}. "
        )
        if total > 20:
            report += "Excellent productivity!"
        elif total > 10:
            report += "Good session!"
        else:
            report += "Just getting started. Let's be productive!"
        return report


# Singleton tracker
_tracker = ActivityTracker()


def get_tracker() -> ActivityTracker:
    return _tracker


# ─── Registered commands ─────────────────────────────────────────────────────

@command(intents=["daily_report", "productivity_report"], description="Show today's productivity report", category="productivity")
def cmd_daily_report(arg: Optional[str], memory) -> CommandResult:
    return CommandResult(response=_tracker.daily_report())


@command(intents=["usage_stats", "my_stats"], description="Show usage statistics", category="productivity")
def cmd_usage_stats(arg: Optional[str], memory) -> CommandResult:
    stats = memory.get_stats()
    return CommandResult(
        response=f"You've had {stats['total_interactions']} interactions. "
                 f"Session commands: {stats['session_commands']}. "
                 f"Last seen: {stats.get('last_seen', 'N/A')}.",
        data=stats,
    )
