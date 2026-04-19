"""
NOVA GUI — Voice Control Widget
=================================
Large circular mic button with glow effect and pulsing animation.
Displays current voice state: Ready / Listening / Processing / Speaking.
"""

from __future__ import annotations

import math

from PyQt6.QtCore import (
    QEasingCurve, QPointF, QPropertyAnimation, QRectF, Qt, QTimer,
    pyqtProperty, pyqtSignal,
)
from PyQt6.QtGui import QColor, QFont, QPainter, QPen, QRadialGradient, QBrush
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ui.styles.theme import Colors, Fonts


class MicButton(QWidget):
    """Circular microphone button with glow and pulse animation."""

    clicked = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedSize(70, 70)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self._active = False
        self._hover = False
        self._pulse = 0.0

        self._pulse_anim = QPropertyAnimation(self, b"pulseVal")
        self._pulse_anim.setDuration(1000)
        self._pulse_anim.setStartValue(0.0)
        self._pulse_anim.setEndValue(1.0)
        self._pulse_anim.setEasingCurve(QEasingCurve.Type.InOutSine)
        self._pulse_anim.setLoopCount(-1)

    @pyqtProperty(float)
    def pulseVal(self) -> float:
        return self._pulse

    @pulseVal.setter
    def pulseVal(self, v: float) -> None:
        self._pulse = v
        self.update()

    def set_active(self, active: bool) -> None:
        self._active = active
        if active:
            self._pulse_anim.start()
        else:
            self._pulse_anim.stop()
            self._pulse = 0.0
        self.update()

    @property
    def is_active(self) -> bool:
        return self._active

    def enterEvent(self, event) -> None:
        self._hover = True
        self.update()

    def leaveEvent(self, event) -> None:
        self._hover = False
        self.update()

    def mousePressEvent(self, event) -> None:
        self.clicked.emit()

    def paintEvent(self, event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        w, h = self.width(), self.height()
        cx, cy = w / 2, h / 2
        radius = min(w, h) * 0.42

        # ── Outer glow when active ───────────────────────────────────
        if self._active:
            glow_r = radius * (1.3 + 0.15 * math.sin(self._pulse * math.pi * 2))
            grad = QRadialGradient(QPointF(cx, cy), glow_r)
            grad.setColorAt(0.0, QColor(0, 230, 118, 50))
            grad.setColorAt(1.0, QColor(0, 230, 118, 0))
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QBrush(grad))
            p.drawEllipse(QPointF(cx, cy), glow_r, glow_r)

        # ── Button body ──────────────────────────────────────────────
        body_color = QColor(0, 230, 118, 200) if self._active else QColor(Colors.BG_PANEL_LIGHT)
        border_color = QColor(0, 230, 118) if self._active else QColor(Colors.BORDER)

        if self._hover and not self._active:
            body_color = QColor(Colors.BG_HOVER)
            border_color = QColor(Colors.CYAN_DIM)

        p.setPen(QPen(border_color, 2))
        p.setBrush(QBrush(body_color))
        p.drawEllipse(QPointF(cx, cy), radius, radius)

        # ── Mic icon (simplified) ────────────────────────────────────
        icon_color = QColor(Colors.BG_DARKEST) if self._active else QColor(Colors.CYAN)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(icon_color))

        # Mic body
        mic_w, mic_h = 8, 14
        p.drawRoundedRect(
            QRectF(cx - mic_w / 2, cy - mic_h / 2 - 2, mic_w, mic_h),
            3, 3,
        )
        # Mic arc
        arc_pen = QPen(icon_color, 2)
        arc_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(arc_pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        arc_r = 10
        p.drawArc(
            QRectF(cx - arc_r, cy - 4, arc_r * 2, arc_r * 2),
            0 * 16, -180 * 16,
        )
        # Mic stand
        p.drawLine(QPointF(cx, cy + arc_r - 2), QPointF(cx, cy + arc_r + 4))
        p.drawLine(QPointF(cx - 5, cy + arc_r + 4), QPointF(cx + 5, cy + arc_r + 4))

        p.end()


class VoiceControl(QWidget):
    """
    Voice control strip: mic button + status label.
    Emits `mic_toggled(bool)` when the mic button is clicked.
    """

    mic_toggled = pyqtSignal(bool)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setStyleSheet("background: transparent; border: none;")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ── Mic button ───────────────────────────────────────────────
        self._mic = MicButton()
        self._mic.clicked.connect(self._toggle)
        layout.addWidget(self._mic)

        # ── Status label ─────────────────────────────────────────────
        self._status = QLabel("READY")
        self._status.setStyleSheet(f"""
            color: {Colors.TEXT_SECONDARY};
            font-size: {Fonts.SIZE_MD}px;
            font-weight: bold;
            letter-spacing: 2px;
            background: transparent;
            border: none;
        """)
        layout.addWidget(self._status)

    def _toggle(self) -> None:
        new_state = not self._mic.is_active
        self._mic.set_active(new_state)
        self.mic_toggled.emit(new_state)
        if new_state:
            self.set_status("listening")
        else:
            self.set_status("idle")

    def set_status(self, state: str) -> None:
        """Update the display for the current voice state."""
        labels = {
            "idle": ("READY", Colors.TEXT_SECONDARY),
            "listening": ("⦿  LISTENING…", Colors.GREEN),
            "processing": ("◎  PROCESSING…", Colors.PURPLE),
            "speaking": ("◈  SPEAKING…", Colors.CYAN),
        }
        text, color = labels.get(state, ("READY", Colors.TEXT_SECONDARY))
        self._status.setText(text)
        self._status.setStyleSheet(f"""
            color: {color};
            font-size: {Fonts.SIZE_MD}px;
            font-weight: bold;
            letter-spacing: 2px;
            background: transparent;
            border: none;
        """)

        if state == "listening":
            self._mic.set_active(True)
        elif state in ("idle", "speaking", "processing"):
            self._mic.set_active(False)

    def set_mic_available(self, available: bool) -> None:
        """Disable mic button if no microphone is available."""
        self._mic.setEnabled(available)
        if not available:
            self._status.setText("MIC UNAVAILABLE")
            self._status.setStyleSheet(f"""
                color: {Colors.TEXT_MUTED};
                font-size: {Fonts.SIZE_MD}px;
                letter-spacing: 2px;
                background: transparent;
                border: none;
            """)
