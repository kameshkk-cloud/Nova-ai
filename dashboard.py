#!/usr/bin/env python3
"""
NOVA Dashboard — Live Terminal UI
===================================
Displays real-time system health panels using Rich.

Usage:
    python dashboard.py
"""

import sys
import os
import time
import datetime

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

try:
    from rich.console import Console
    from rich.layout import Layout
    from rich.live import Live
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
except ImportError:
    print("Install rich: pip install rich")
    sys.exit(1)

from nova.commands.system_info import _cpu_info, _ram_info, _battery_info, _disk_info, _network_info, _internet_available
from nova.config.settings import USER_NAME, ASSISTANT_NAME

console = Console()


def build_dashboard() -> Layout:
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="body", size=12),
        Layout(name="footer", size=3),
    )

    now = datetime.datetime.now().strftime("%A, %B %d  |  %I:%M:%S %p")
    layout["header"].update(Panel(
        Text(f"⬡  {ASSISTANT_NAME} SYSTEM DASHBOARD  |  {USER_NAME}  |  {now}", justify="center", style="bold cyan"),
        border_style="cyan",
    ))

    cpu = _cpu_info()
    ram = _ram_info()
    bat = _battery_info()
    disk = _disk_info()
    net = _network_info()
    inet = _internet_available()

    cpu_c = "red" if cpu["alert"] else "green" if cpu["usage_percent"] < 60 else "yellow"
    ram_c = "red" if ram["alert"] else "green" if ram["usage_percent"] < 70 else "yellow"
    disk_c = "red" if disk.get("alert") else "green"
    net_c = "green" if inet else "red"

    cpu_panel = Panel(
        f"[bold {cpu_c}]{cpu['usage_percent']}%[/]\nCores: {cpu['cores']}\nFreq: {cpu['freq_mhz']} MHz",
        title="🖥  CPU", border_style=cpu_c,
    )
    ram_panel = Panel(
        f"[bold {ram_c}]{ram['usage_percent']}%[/]\nUsed: {ram['used_gb']} GB\nFree: {ram['available_gb']} GB",
        title="💾 RAM", border_style=ram_c,
    )

    if bat.get("available"):
        bat_c = "red" if bat.get("alert_level") == "CRITICAL" else "yellow" if bat.get("alert_level") == "LOW" else "green"
        plug = "🔌 Charging" if bat["plugged"] else "🔋 Discharging"
        bat_panel = Panel(
            f"[bold {bat_c}]{bat['percent']}%[/]\n{plug}\nETA: {int(bat.get('mins_remaining') or 0)} min",
            title="🔋 Battery", border_style=bat_c,
        )
    else:
        bat_panel = Panel("Desktop PC\nNo battery", title="🔋 Battery")

    disk_panel = Panel(
        f"[bold {disk_c}]{disk.get('usage_percent', '?')}%[/]\nUsed: {disk.get('used_gb', '?')} GB\nFree: {disk.get('free_gb', '?')} GB",
        title="💽 Disk", border_style=disk_c,
    )
    net_panel = Panel(
        f"Internet: [bold {net_c}]{'✓ Online' if inet else '✗ Offline'}[/]\n↑ {net['bytes_sent_mb']} MB\n↓ {net['bytes_recv_mb']} MB",
        title="🌐 Network", border_style=net_c,
    )

    body = Layout()
    body.split_row(
        Layout(cpu_panel), Layout(ram_panel), Layout(bat_panel),
        Layout(disk_panel), Layout(net_panel),
    )
    layout["body"].update(body)

    layout["footer"].update(Panel(
        "[dim]Press Ctrl+C to exit  |  NOVA is monitoring your system[/]",
        border_style="bright_black",
    ))
    return layout


def main():
    console.print("\n[bold cyan]Starting NOVA Dashboard...[/]\n")
    try:
        with Live(build_dashboard(), console=console, refresh_per_second=0.5, screen=True) as live:
            while True:
                live.update(build_dashboard())
                time.sleep(2)
    except KeyboardInterrupt:
        console.print("\n[cyan]Dashboard closed.[/]")


if __name__ == "__main__":
    main()
