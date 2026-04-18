"""
NOVA GUI — Activity Log Panel
===============================
Scrollable, color-coded event log showing timestamped activity.
"""

from __future__ import annotations

import datetime

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame, QLabel, QScrollArea, QSizePolicy, QVBoxLayout, QWidget,
)

from ui.styles.theme import Colors, Dimensions, Fonts, panel_style, section_title_style


class ActivityLog(QWidget):
    """
    Scrollable activity log panel. Each entry is timestamped and color-coded.

    Types:
        command  — cyan
        response — text_secondary
        alert    — red/yellow
        system   — muted
    """

    MAX_ENTRIES = 200

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setStyleSheet(f"""
            QWidget {{
                {panel_style()}
                padding: 0;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 16, 12, 12)
        layout.setSpacing(6)

        # ── Title ────────────────────────────────────────────────────
        title = QLabel("📋  ACTIVITY LOG")
        title.setStyleSheet(section_title_style())
        layout.addWidget(title)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"background-color: {Colors.BORDER}; max-height: 1px; border: none;")
        layout.addWidget(sep)

        # ── Scroll area ──────────────────────────────────────────────
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self._scroll.setStyleSheet(f"""
            QScrollArea {{
                background-color: {Colors.BG_DARKEST};
                border: 1px solid {Colors.BORDER};
                border-radius: {Dimensions.BORDER_RADIUS_SM}px;
            }}
        """)

        self._container = QWidget()
        self._container.setStyleSheet(f"background-color: {Colors.BG_DARKEST}; border: none;")
        self._log_layout = QVBoxLayout(self._container)
        self._log_layout.setContentsMargins(8, 8, 8, 8)
        self._log_layout.setSpacing(2)
        self._log_layout.addStretch()

        self._scroll.setWidget(self._container)
        layout.addWidget(self._scroll, 1)

        self._count = 0

    def add_entry(self, text: str, entry_type: str = "system") -> None:
        """Add a timestamped log entry."""
        color_map = {
            "command": Colors.CYAN,
            "response": Colors.TEXT_SECONDARY,
            "alert": Colors.RED,
            "warning": Colors.YELLOW,
            "system": Colors.TEXT_MUTED,
            "success": Colors.GREEN,
        }
        color = color_map.get(entry_type, Colors.TEXT_MUTED)
        icon_map = {
            "command": "▶",
            "response": "◀",
            "alert": "⚠",
            "warning": "⚡",
            "system": "●",
            "success": "✓",
        }
        icon = icon_map.get(entry_type, "●")

        now = datetime.datetime.now().strftime("%H:%M:%S")
        label = QLabel(f"{now}  {icon}  {text}")
        label.setWordWrap(True)
        label.setStyleSheet(f"""
            color: {color};
            font-family: {Fonts.FAMILY_MONO};
            font-size: {Fonts.SIZE_XS}px;
            padding: 2px 4px;
            background: transparent;
            border: none;
        """)

        self._log_layout.insertWidget(self._log_layout.count() - 1, label)
        self._count += 1

        # Prune old entries
        if self._count > self.MAX_ENTRIES:
            item = self._log_layout.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()
            self._count -= 1

        # Auto-scroll
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(50, lambda: self._scroll.verticalScrollBar().setValue(
            self._scroll.verticalScrollBar().maximum()
        ))

    def clear_log(self) -> None:
        while self._log_layout.count() > 1:
            item = self._log_layout.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()
        self._count = 0
