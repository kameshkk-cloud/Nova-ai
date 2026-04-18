#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║         NOVA AI — Futuristic GUI Entry Point                  ║
║         Neural Operative Virtual Assistant v2.0               ║
╚══════════════════════════════════════════════════════════════╝

Usage:
    python nova_gui.py

Launches the PyQt6-based GUI that connects to all NOVA backend
subsystems (voice, brain, commands, monitoring).
"""

import sys
import os

# ─── Force UTF-8 on Windows ─────────────────────────────────────────────────
if sys.stdout and sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# ─── Ensure project root is importable ───────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def main() -> None:
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt

    # ── High-DPI support ─────────────────────────────────────────────
    os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")

    app = QApplication(sys.argv)
    app.setApplicationName("NOVA AI")
    app.setApplicationVersion("2.0")

    # ── Apply global stylesheet ──────────────────────────────────────
    from ui.styles.theme import global_stylesheet
    app.setStyleSheet(global_stylesheet())

    # ── Launch main window ───────────────────────────────────────────
    from ui.main_window import MainWindow
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
