"""
NOVA Commands — Power Management
=================================
Shutdown, restart, cancel-shutdown, and lock-screen.
"""

from __future__ import annotations

import os
import platform
import subprocess
from typing import Optional

from nova.commands.registry import CommandResult, command
from nova.config.settings import USER_NAME
from nova.utils import logger as log

_SYSTEM = platform.system()


@command(
    intents=["shutdown", "shut_down", "power_off"],
    description="Shut down the computer",
    category="power",
)
def cmd_shutdown(arg: Optional[str], memory) -> CommandResult:
    delay = 10
    log.warn(f"Shutdown scheduled in {delay}s")
    if _SYSTEM == "Windows":
        os.system(f"shutdown /s /t {delay}")
    else:
        os.system(f"shutdown -h +{delay // 60 or 1}")
    return CommandResult(
        response=f"System will shut down in {delay} seconds, {USER_NAME}.",
    )


@command(
    intents=["restart", "reboot"],
    description="Restart the computer",
    category="power",
)
def cmd_restart(arg: Optional[str], memory) -> CommandResult:
    delay = 10
    log.warn(f"Restart scheduled in {delay}s")
    if _SYSTEM == "Windows":
        os.system(f"shutdown /r /t {delay}")
    else:
        os.system("reboot")
    return CommandResult(
        response=f"System will restart in {delay} seconds.",
    )


@command(
    intents=["cancel_shutdown", "abort_shutdown"],
    description="Cancel a pending shutdown",
    category="power",
)
def cmd_cancel_shutdown(arg: Optional[str], memory) -> CommandResult:
    if _SYSTEM == "Windows":
        os.system("shutdown /a")
    else:
        os.system("shutdown -c")
    return CommandResult(response="Shutdown cancelled.")


@command(
    intents=["lock_screen", "lock"],
    description="Lock the workstation",
    category="power",
)
def cmd_lock(arg: Optional[str], memory) -> CommandResult:
    if _SYSTEM == "Windows":
        subprocess.run(["rundll32", "user32.dll,LockWorkStation"])
    else:
        subprocess.run(["gnome-screensaver-command", "-l"])
    return CommandResult(response="Screen locked.")
