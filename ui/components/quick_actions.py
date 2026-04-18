"""
NOVA GUI — Quick Action Buttons
=================================
Grid of styled action buttons for common operations.
Each button fires a command string to the bridge.
"""

from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame, QGridLayout, QLabel, QPushButton, QSizePolicy, QVBoxLayout,
    QWidget,
)

from ui.styles.theme import Colors, Dimensions, Fonts, panel_style, section_title_style


class ActionButton(QPushButton):
    """Styled quick-action button with icon and label."""

    action_triggered = pyqtSignal(str)

    def __init__(
        self,
        icon: str,
        label: str,
        command: str,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._command = command
        self.setText(f"{icon}\n{label}")
        self.setToolTip(label)
        self.setFixedHeight(68)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.BG_PANEL_LIGHT};
                color: {Colors.TEXT_PRIMARY};
                border: 1px solid {Colors.BORDER};
                border-radius: {Dimensions.BORDER_RADIUS_SM}px;
                padding: 8px 4px;
                font-size: {Fonts.SIZE_SM}px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {Colors.BG_HOVER};
                border-color: {Colors.CYAN_DIM};
                color: {Colors.CYAN};
            }}
            QPushButton:pressed {{
                background-color: {Colors.CYAN_DIM};
                color: {Colors.TEXT_BRIGHT};
                border-color: {Colors.CYAN};
            }}
        """)

        self.clicked.connect(lambda: self.action_triggered.emit(self._command))


class QuickActions(QWidget):
    """
    Panel containing a grid of quick action buttons.
    Emits `action_requested(str)` with the command string.
    """

    action_requested = pyqtSignal(str)

    # ── Default actions ──────────────────────────────────────────────
    DEFAULT_ACTIONS = [
        ("🌐", "Chrome", "open chrome"),
        ("📂", "Explorer", "open explorer"),
        ("📸", "Screenshot", "screenshot"),
        ("📊", "Sys Stats", "system report"),
        ("🔊", "Vol Up", "volume up"),
        ("🔇", "Mute", "mute"),
        ("🔒", "Lock", "lock screen"),
        ("⏻", "Shutdown", "shutdown"),
    ]

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
        layout.setSpacing(8)

        # ── Title ────────────────────────────────────────────────────
        title = QLabel("⚡  QUICK ACTIONS")
        title.setStyleSheet(section_title_style())
        layout.addWidget(title)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"background-color: {Colors.BORDER}; max-height: 1px; border: none;")
        layout.addWidget(sep)

        # ── Button grid ──────────────────────────────────────────────
        grid = QGridLayout()
        grid.setSpacing(6)

        for i, (icon, label, cmd) in enumerate(self.DEFAULT_ACTIONS):
            btn = ActionButton(icon, label, cmd)
            btn.action_triggered.connect(self.action_requested.emit)
            row, col = divmod(i, 2)
            grid.addWidget(btn, row, col)

        layout.addLayout(grid)
        layout.addStretch()
