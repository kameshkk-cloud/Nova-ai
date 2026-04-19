"""
NOVA Commands — System Information
===================================
CPU, RAM, battery, disk, network, and process queries.
"""

from __future__ import annotations

import platform
import socket
from typing import Optional

import psutil

from nova.commands.registry import CommandResult, command
from nova.config.settings import (
    CPU_ALERT_THRESHOLD,
    RAM_ALERT_THRESHOLD,
    BATTERY_LOW_THRESHOLD,
    BATTERY_CRIT_THRESHOLD,
    DISK_ALERT_THRESHOLD,
    USER_NAME,
)
from nova.utils import logger as log


# ─── Internal helpers ────────────────────────────────────────────────────────

def _cpu_info() -> dict:
    usage = psutil.cpu_percent(interval=1)
    freq = psutil.cpu_freq()
    return {
        "usage_percent": usage,
        "cores": psutil.cpu_count(logical=True),
        "freq_mhz": round(freq.current, 0) if freq else "N/A",
        "alert": usage >= CPU_ALERT_THRESHOLD,
    }


def _ram_info() -> dict:
    mem = psutil.virtual_memory()
    return {
        "total_gb": round(mem.total / (1024 ** 3), 2),
        "used_gb": round(mem.used / (1024 ** 3), 2),
        "usage_percent": mem.percent,
        "available_gb": round(mem.available / (1024 ** 3), 2),
        "alert": mem.percent >= RAM_ALERT_THRESHOLD,
    }


def _battery_info() -> dict:
    bat = psutil.sensors_battery()
    if bat is None:
        return {"available": False}
    mins_left = None
    if bat.secsleft not in (psutil.POWER_TIME_UNLIMITED, psutil.POWER_TIME_UNKNOWN):
        mins_left = round(bat.secsleft / 60, 0)
    alert_level = None
    if not bat.power_plugged:
        if bat.percent <= BATTERY_CRIT_THRESHOLD:
            alert_level = "CRITICAL"
        elif bat.percent <= BATTERY_LOW_THRESHOLD:
            alert_level = "LOW"
    return {
        "available": True,
        "percent": bat.percent,
        "plugged": bat.power_plugged,
        "mins_remaining": mins_left,
        "alert_level": alert_level,
    }


def _disk_info(path: str = "C:\\" if platform.system() == "Windows" else "/") -> dict:
    try:
        d = psutil.disk_usage(path)
        return {
            "total_gb": round(d.total / (1024 ** 3), 2),
            "used_gb": round(d.used / (1024 ** 3), 2),
            "free_gb": round(d.free / (1024 ** 3), 2),
            "usage_percent": d.percent,
            "alert": d.percent >= DISK_ALERT_THRESHOLD,
        }
    except Exception as exc:
        return {"error": str(exc)}


def _network_info() -> dict:
    net = psutil.net_io_counters()
    return {
        "bytes_sent_mb": round(net.bytes_sent / (1024 ** 2), 2),
        "bytes_recv_mb": round(net.bytes_recv / (1024 ** 2), 2),
        "packets_sent": net.packets_sent,
        "packets_recv": net.packets_recv,
    }


def _internet_available() -> bool:
    try:
        socket.setdefaulttimeout(3)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("8.8.8.8", 53))
        s.close()
        return True
    except OSError:
        return False


def _top_processes(n: int = 5) -> list:
    procs = []
    for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
        try:
            procs.append(p.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    procs.sort(key=lambda x: x.get("cpu_percent", 0), reverse=True)
    return procs[:n]


def _full_snapshot() -> dict:
    return {
        "cpu": _cpu_info(),
        "ram": _ram_info(),
        "disk": _disk_info(),
        "battery": _battery_info(),
        "network": _network_info(),
        "internet": _internet_available(),
        "os": f"{platform.system()} {platform.release()}",
    }


def check_alerts() -> list[str]:
    """Return a list of alert messages (used by health monitor)."""
    alerts: list[str] = []
    snap = _full_snapshot()
    if snap["cpu"]["alert"]:
        alerts.append(f"High CPU usage: {snap['cpu']['usage_percent']}%")
    if snap["ram"]["alert"]:
        alerts.append(f"High RAM usage: {snap['ram']['usage_percent']}%")
    if snap["disk"].get("alert"):
        alerts.append(f"Low disk space: {snap['disk']['free_gb']} GB remaining")
    bat = snap["battery"]
    if bat.get("alert_level"):
        alerts.append(f"Battery {bat['alert_level']}: {bat['percent']}%")
    if not snap["internet"]:
        alerts.append("Internet connection lost")
    return alerts


# ─── Registered commands ─────────────────────────────────────────────────────

@command(
    intents=["cpu_status", "check_cpu", "processor"],
    description="Check CPU usage",
    category="system",
)
def cmd_cpu(arg: Optional[str], memory) -> CommandResult:
    cpu = _cpu_info()
    resp = f"CPU usage is {cpu['usage_percent']}%."
    if cpu["alert"]:
        resp += f" That's quite high, {USER_NAME}. Consider closing heavy applications."
    return CommandResult(response=resp, data=cpu)


@command(
    intents=["ram_status", "check_ram", "memory_usage"],
    description="Check RAM usage",
    category="system",
)
def cmd_ram(arg: Optional[str], memory) -> CommandResult:
    ram = _ram_info()
    return CommandResult(
        response=f"RAM usage is {ram['usage_percent']}%, "
                 f"using {ram['used_gb']} GB of {ram['total_gb']} GB.",
        data=ram,
    )


@command(
    intents=["battery_status", "check_battery"],
    description="Check battery level",
    category="system",
)
def cmd_battery(arg: Optional[str], memory) -> CommandResult:
    bat = _battery_info()
    if not bat.get("available"):
        return CommandResult(response="No battery detected. You appear to be on a desktop system.")
    status = "plugged in" if bat["plugged"] else "on battery"
    resp = f"Battery is at {bat['percent']}%, {status}."
    if bat.get("mins_remaining"):
        resp += f" Approximately {int(bat['mins_remaining'])} minutes remaining."
    if bat.get("alert_level"):
        resp += f" Warning: battery is {bat['alert_level']}!"
    return CommandResult(response=resp, data=bat)


@command(
    intents=["disk_status", "check_disk", "storage", "disk_space"],
    description="Check disk space",
    category="system",
)
def cmd_disk(arg: Optional[str], memory) -> CommandResult:
    disk = _disk_info()
    if "error" in disk:
        return CommandResult(response=f"Disk check error: {disk['error']}")
    return CommandResult(
        response=f"Disk usage is {disk['usage_percent']}%. "
                 f"{disk['free_gb']} GB free of {disk['total_gb']} GB total.",
        data=disk,
    )


@command(
    intents=["system_report", "system_health", "full_report"],
    description="Full system health report",
    category="system",
)
def cmd_system_report(arg: Optional[str], memory) -> CommandResult:
    snap = _full_snapshot()
    cpu, ram, bat = snap["cpu"], snap["ram"], snap["battery"]
    lines = [
        f"CPU is at {cpu['usage_percent']} percent.",
        f"RAM usage is {ram['usage_percent']} percent, {ram['used_gb']} GB used.",
    ]
    if bat.get("available"):
        status = "charging" if bat["plugged"] else "on battery"
        lines.append(f"Battery at {bat['percent']} percent, {status}.")
        if bat.get("alert_level"):
            lines.append(f"Warning: battery is {bat['alert_level']}!")
    else:
        lines.append("No battery detected — likely a desktop machine.")
    if not snap["internet"]:
        lines.append("No internet connection detected.")
    return CommandResult(response=" ".join(lines), data=snap)


@command(
    intents=["network_status", "check_network", "internet_status"],
    description="Check network and internet status",
    category="system",
)
def cmd_network(arg: Optional[str], memory) -> CommandResult:
    net = _network_info()
    online = _internet_available()
    status = "connected" if online else "NOT connected"
    return CommandResult(
        response=f"Internet is {status}. Sent {net['bytes_sent_mb']} MB, "
                 f"received {net['bytes_recv_mb']} MB this session.",
        data={**net, "online": online},
    )


@command(
    intents=["top_processes", "running_apps", "what_is_running"],
    description="List top running processes",
    category="system",
)
def cmd_top_processes(arg: Optional[str], memory) -> CommandResult:
    procs = _top_processes(5)
    names = ", ".join(p["name"] for p in procs if p.get("name"))
    return CommandResult(
        response=f"Top running processes: {names}.",
        data={"processes": procs},
    )
