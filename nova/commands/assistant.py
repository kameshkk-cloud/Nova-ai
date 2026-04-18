"""
NOVA Commands — Assistant Meta
===============================
Time, date, help, status, exit, reminders, notes, and other meta commands.
"""

from __future__ import annotations

import datetime
from typing import Optional

from nova.commands.registry import CommandResult, command
from nova.commands.system_info import check_alerts
from nova.config.settings import USER_NAME
from nova.utils import logger as log


@command(intents=["get_time", "current_time", "what_time"], description="Tell the current time", category="assistant")
def cmd_time(arg: Optional[str], memory) -> CommandResult:
    now = datetime.datetime.now().strftime("%I:%M %p")
    return CommandResult(response=f"It is {now}, {USER_NAME}.")


@command(intents=["get_date", "current_date", "today", "what_day"], description="Tell today's date", category="assistant")
def cmd_date(arg: Optional[str], memory) -> CommandResult:
    now = datetime.datetime.now()
    return CommandResult(response=f"Today is {now.strftime('%A')}, {now.strftime('%B %d, %Y')}.")


@command(intents=["help", "capabilities", "what_can_you_do"], description="List all capabilities", category="assistant")
def cmd_help(arg: Optional[str], memory) -> CommandResult:
    # The registry will inject full help via router; this is the fallback
    return CommandResult(
        response=(
            "I can help with: time and date, system stats like CPU and battery, "
            "opening and closing apps, browsing websites, organizing files, "
            "setting reminders and notes, shutting down the system, "
            "and general conversation. Just ask naturally!"
        ),
    )


@command(intents=["nova_status", "how_are_you", "are_you_ok"], description="Check NOVA's status", category="assistant")
def cmd_status(arg: Optional[str], memory) -> CommandResult:
    alerts = check_alerts()
    if alerts:
        return CommandResult(response=f"NOVA is running. Alerts: {'; '.join(alerts)}.")
    return CommandResult(response="NOVA is fully operational. All systems nominal.")


@command(intents=["exit", "stop", "quit", "goodbye", "offline"], description="Shut down NOVA", category="assistant")
def cmd_exit(arg: Optional[str], memory) -> CommandResult:
    return CommandResult(
        response=f"NOVA going offline. Stay productive, {USER_NAME}. Goodbye!",
        continue_running=False,
    )


@command(intents=["clear", "reset"], description="Reset session memory", category="assistant")
def cmd_clear(arg: Optional[str], memory) -> CommandResult:
    memory.stm.clear()
    return CommandResult(response="Session memory cleared. Ready for new commands.")


@command(intents=["add_reminder", "set_reminder", "remind_me"], description="Set a reminder", category="memory")
def cmd_add_reminder(arg: Optional[str], memory) -> CommandResult:
    if not arg:
        return CommandResult(response="What should I remind you about?")
    memory.add_reminder(arg)
    return CommandResult(response=f"Reminder set: {arg}")


@command(intents=["show_reminders", "my_reminders", "pending_reminders"], description="Show pending reminders", category="memory")
def cmd_reminders(arg: Optional[str], memory) -> CommandResult:
    pending = memory.get_pending_reminders()
    if not pending:
        return CommandResult(response="You have no pending reminders.")
    items = "; ".join(r["text"] for r in pending[:5])
    return CommandResult(response=f"Your reminders: {items}.")


@command(intents=["add_note", "save_note", "remember_this"], description="Save a note", category="memory")
def cmd_add_note(arg: Optional[str], memory) -> CommandResult:
    if not arg:
        return CommandResult(response="What would you like me to note?")
    memory.add_note(arg)
    return CommandResult(response=f"Note saved: {arg}")


@command(intents=["show_notes", "my_notes"], description="Show saved notes", category="memory")
def cmd_notes(arg: Optional[str], memory) -> CommandResult:
    notes = memory.get_notes(last_n=5)
    if not notes:
        return CommandResult(response="No notes saved yet.")
    items = "; ".join(n["text"] for n in notes)
    return CommandResult(response=f"Your recent notes: {items}.")
