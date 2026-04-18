"""
NOVA GUI — Notification Bar (Toast System)
============================================
Toast-style popup notifications that slide in from the top-right
and auto-dismiss with a fade-out animation.
"""

from __future__ import annotations

from PyQt6.QtCore import (
    QEasingCurve, QPoint, QPropertyAnimation, QSequentialAnimationGroup,
    QTimer, Qt, pyqtProperty,
)
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QGraphicsOpacityEffect, QLabel, QVBoxLayout, QWidget

from ui.styles.theme import Colors, Dimensions, Fonts


class Toast(QWidget):
    """Single toast notification that fades in, stays, then fades out."""

    def __init__(
        self,
        message: str,
        severity: str = "info",
        duration_ms: int = 5000,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setFixedWidth(320)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)

        # ── Color by severity ────────────────────────────────────────
        color_map = {
            "info": (Colors.CYAN, Colors.CYAN_DIM),
            "warning": (Colors.YELLOW, Colors.YELLOW_DIM),
            "critical": (Colors.RED, Colors.RED_DIM),
            "success": (Colors.GREEN, Colors.GREEN_DIM),
        }
        text_color, border_color = color_map.get(severity, color_map["info"])

        # ── Icon ─────────────────────────────────────────────────────
        icon_map = {
            "info": "ℹ",
            "warning": "⚠",
            "critical": "🔴",
            "success": "✓",
        }
        icon = icon_map.get(severity, "ℹ")

        # ── Layout ───────────────────────────────────────────────────
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._label = QLabel(f"  {icon}  {message}")
        self._label.setWordWrap(True)
        self._label.setStyleSheet(f"""
            QLabel {{
                background-color: {Colors.BG_PANEL};
                color: {text_color};
                border: 1px solid {border_color};
                border-left: 4px solid {text_color};
                border-radius: {Dimensions.BORDER_RADIUS_SM}px;
                padding: 14px 16px;
                font-size: {Fonts.SIZE_SM}px;
                font-weight: 500;
            }}
        """)
        layout.addWidget(self._label)

        # ── Opacity effect for fade ──────────────────────────────────
        self._opacity = QGraphicsOpacityEffect(self)
        self._opacity.setOpacity(1.0)
        self.setGraphicsEffect(self._opacity)

        # ── Auto-dismiss timer ───────────────────────────────────────
        QTimer.singleShot(duration_ms, self._fade_out)

    def _fade_out(self) -> None:
        anim = QPropertyAnimation(self._opacity, b"opacity")
        anim.setDuration(400)
        anim.setStartValue(1.0)
        anim.setEndValue(0.0)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.finished.connect(self._remove)
        anim.start()
        self._fade_anim = anim  # prevent GC

    def _remove(self) -> None:
        self.setParent(None)
        self.deleteLater()


class NotificationBar(QWidget):
    """
    Manages a stack of toast notifications in the top-right corner.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setStyleSheet("background: transparent; border: none;")
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)

        self._toasts: list[Toast] = []
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 8, 8, 0)
        self._layout.setSpacing(8)
        self._layout.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight
        )

    def show_notification(
        self, message: str, severity: str = "info", duration_ms: int = 5000,
    ) -> None:
        """Display a toast notification."""
        toast = Toast(message, severity, duration_ms, parent=self)
        self._layout.addWidget(toast)
        self._toasts.append(toast)

        # Clean up reference when removed
        def _cleanup():
            if toast in self._toasts:
                self._toasts.remove(toast)

        QTimer.singleShot(duration_ms + 600, _cleanup)

    def clear_all(self) -> None:
        for toast in list(self._toasts):
            toast._remove()
        self._toasts.clear()
