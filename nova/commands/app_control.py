"""
NOVA Commands — Application & Browser Control
==============================================
Open/close applications, control volume, take screenshots, browse the web.
"""

from __future__ import annotations

import datetime
import os
import platform
import subprocess
import webbrowser
from typing import Optional

from nova.commands.registry import CommandResult, command
from nova.utils import logger as log

_SYSTEM = platform.system()

# ─── App maps ────────────────────────────────────────────────────────────────

_APP_MAP_WINDOWS = {
    "chrome": "chrome", "firefox": "firefox", "notepad": "notepad",
    "calculator": "calc", "explorer": "explorer", "cmd": "cmd",
    "task manager": "taskmgr", "paint": "mspaint", "word": "winword",
    "excel": "excel", "powerpoint": "powerpnt", "vs code": "code",
    "discord": "discord", "spotify": "spotify", "vlc": "vlc",
    "zoom": "zoom", "edge": "msedge", "terminal": "wt",
}

_APP_MAP_LINUX = {
    "chrome": "google-chrome", "firefox": "firefox", "gedit": "gedit",
    "terminal": "gnome-terminal", "calculator": "gnome-calculator",
    "vlc": "vlc", "vs code": "code", "discord": "discord",
}


def _open(app_name: str) -> str:
    name = app_name.lower().strip()
    app_map = _APP_MAP_WINDOWS if _SYSTEM == "Windows" else _APP_MAP_LINUX
    cmd = app_map.get(name, name)
    try:
        if _SYSTEM == "Windows":
            subprocess.Popen(["start", cmd], shell=True)
        else:
            subprocess.Popen([cmd])
        log.info(f"Opened app: {cmd}")
        return f"Opening {app_name} for you."
    except Exception as exc:
        log.error(f"Failed to open {app_name}: {exc}")
        return f"I couldn't open {app_name}. Make sure it is installed."


def _close(app_name: str) -> str:
    try:
        if _SYSTEM == "Windows":
            subprocess.run(
                ["taskkill", "/F", "/IM", f"{app_name}.exe"],
                capture_output=True,
            )
        else:
            subprocess.run(["pkill", "-f", app_name], capture_output=True)
        log.info(f"Closed app: {app_name}")
        return f"{app_name} has been closed."
    except Exception as exc:
        log.error(f"Failed to close {app_name}: {exc}")
        return f"Could not close {app_name}."


def _ps_volume_change(delta: int) -> None:
    """Change Windows volume via PowerShell SendKeys."""
    steps = abs(delta) // 2 or 1
    vk_key = "[char]175" if delta > 0 else "[char]174"
    script = (
        f"$obj = New-Object -ComObject WScript.Shell; "
        f"for($i=0; $i -lt {steps}; $i++) "
        f"{{$obj.SendKeys({vk_key})}}"
    )
    subprocess.run(["powershell", "-Command", script], capture_output=True)


# ─── Registered commands ─────────────────────────────────────────────────────

@command(
    intents=["open_app"],
    description="Open an application",
    category="apps",
)
def cmd_open_app(arg: Optional[str], memory) -> CommandResult:
    if not arg:
        return CommandResult(response="Please specify which app to open.")
    return CommandResult(response=_open(arg))


@command(
    intents=["close_app", "kill_app"],
    description="Close a running application",
    category="apps",
)
def cmd_close_app(arg: Optional[str], memory) -> CommandResult:
    if not arg:
        return CommandResult(response="Please specify which app to close.")
    return CommandResult(response=_close(arg))


@command(
    intents=["open_url", "open_website"],
    description="Open a URL in the browser",
    category="apps",
)
def cmd_open_url(arg: Optional[str], memory) -> CommandResult:
    if not arg:
        return CommandResult(response="Please provide a URL.")
    url = arg if arg.startswith("http") else f"https://{arg}"
    webbrowser.open(url)
    log.info(f"Opened URL: {url}")
    return CommandResult(response=f"Opened {url} in your browser.")


@command(
    intents=["search_web", "google_search"],
    description="Search the web via Google",
    category="apps",
)
def cmd_search_web(arg: Optional[str], memory) -> CommandResult:
    if not arg:
        return CommandResult(response="What would you like to search for?")
    url = f"https://www.google.com/search?q={arg.replace(' ', '+')}"
    webbrowser.open(url)
    return CommandResult(response=f"Searching Google for '{arg}'.")


@command(
    intents=["volume_up", "louder"],
    description="Increase system volume",
    category="apps",
)
def cmd_volume_up(arg: Optional[str], memory) -> CommandResult:
    try:
        if _SYSTEM == "Windows":
            _ps_volume_change(10)
        return CommandResult(response="Volume increased.")
    except Exception as exc:
        return CommandResult(response=f"Volume control error: {exc}")


@command(
    intents=["volume_down", "quieter"],
    description="Decrease system volume",
    category="apps",
)
def cmd_volume_down(arg: Optional[str], memory) -> CommandResult:
    try:
        if _SYSTEM == "Windows":
            _ps_volume_change(-10)
        return CommandResult(response="Volume decreased.")
    except Exception as exc:
        return CommandResult(response=f"Volume control error: {exc}")


@command(
    intents=["mute", "silence"],
    description="Mute system audio",
    category="apps",
)
def cmd_mute(arg: Optional[str], memory) -> CommandResult:
    try:
        if _SYSTEM == "Windows":
            subprocess.run([
                "powershell", "-Command",
                "$obj = New-Object -ComObject WScript.Shell; $obj.SendKeys([char]173)"
            ], capture_output=True)
        return CommandResult(response="System muted.")
    except Exception as exc:
        return CommandResult(response=f"Mute error: {exc}")


@command(
    intents=["screenshot", "capture_screen"],
    description="Take a screenshot",
    category="apps",
)
def cmd_screenshot(arg: Optional[str], memory) -> CommandResult:
    try:
        import pyautogui
        save_dir = os.path.join(os.path.expanduser("~"), "Desktop")
        filename = f"nova_screenshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(save_dir, filename)
        pyautogui.screenshot(filepath)
        return CommandResult(response=f"Screenshot saved to {filepath}")
    except ImportError:
        return CommandResult(response="pyautogui is not installed. Run: pip install pyautogui")
    except Exception as exc:
        return CommandResult(response=f"Screenshot error: {exc}")
