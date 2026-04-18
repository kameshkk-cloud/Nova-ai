"""
NOVA GUI — Animated AI Orb
============================
Central visual element: a glowing, animated orb that represents NOVA.

States:
    idle       — Slow breathing pulse with cyan glow
    listening  — Faster pulse + expanding ripple rings
    processing — Rotating arc spinner around the orb
    speaking   — Animated waveform oscillation around perimeter
"""

from __future__ import annotations

import math

from PyQt6.QtCore import (
    QEasingCurve, QPointF, QPropertyAnimation, QRectF, Qt, QTimer,
    pyqtProperty,
)
from PyQt6.QtGui import (
    QBrush, QColor, QLinearGradient, QPainter, QPainterPath, QPen,
    QRadialGradient,
)
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

from ui.styles.theme import Colors, Fonts


class AIOrb(QWidget):
    """Animated orb widget with state-driven visual effects."""

    STATES = ("idle", "listening", "processing", "speaking")

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setMinimumSize(260, 280)

        self._state = "idle"
        self._pulse_value = 0.0       # 0..1 breathing
        self._rotation = 0.0          # degrees for processing spinner
        self._ripple_value = 0.0      # 0..1 for ripple expansion
        self._wave_phase = 0.0        # radians for waveform
        self._glow_opacity = 0.5

        # ── Status label beneath the orb ─────────────────────────────
        self._status_label = QLabel("NOVA ONLINE", self)
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._status_label.setStyleSheet(f"""
            color: {Colors.CYAN};
            font-size: {Fonts.SIZE_LG}px;
            font-weight: bold;
            letter-spacing: 3px;
            background: transparent;
            border: none;
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addStretch()
        layout.addWidget(self._status_label)

        # ── Animations ───────────────────────────────────────────────
        self._pulse_anim = QPropertyAnimation(self, b"pulseValue")
        self._pulse_anim.setDuration(2400)
        self._pulse_anim.setStartValue(0.0)
        self._pulse_anim.setEndValue(1.0)
        self._pulse_anim.setEasingCurve(QEasingCurve.Type.InOutSine)
        self._pulse_anim.setLoopCount(-1)  # infinite
        self._pulse_anim.start()

        # Rotation timer for processing state
        self._rotation_timer = QTimer(self)
        self._rotation_timer.setInterval(16)  # ~60fps
        self._rotation_timer.timeout.connect(self._tick_rotation)

        # Ripple timer for listening state
        self._ripple_timer = QTimer(self)
        self._ripple_timer.setInterval(16)
        self._ripple_timer.timeout.connect(self._tick_ripple)

        # Wave timer for speaking state
        self._wave_timer = QTimer(self)
        self._wave_timer.setInterval(16)
        self._wave_timer.timeout.connect(self._tick_wave)

    # ── Properties for QPropertyAnimation ────────────────────────────

    @pyqtProperty(float)
    def pulseValue(self) -> float:
        return self._pulse_value

    @pulseValue.setter
    def pulseValue(self, val: float) -> None:
        self._pulse_value = val
        self.update()

    # ── State management ─────────────────────────────────────────────

    def set_state(self, state: str) -> None:
        if state not in self.STATES:
            return
        old = self._state
        self._state = state

        # Stop all auxiliary timers
        self._rotation_timer.stop()
        self._ripple_timer.stop()
        self._wave_timer.stop()

        # Adjust pulse speed and start relevant timers
        if state == "idle":
            self._pulse_anim.setDuration(2400)
            self._status_label.setText("NOVA ONLINE")
            self._status_label.setStyleSheet(self._label_style(Colors.CYAN))
        elif state == "listening":
            self._pulse_anim.setDuration(1200)
            self._ripple_value = 0.0
            self._ripple_timer.start()
            self._status_label.setText("⦿  LISTENING")
            self._status_label.setStyleSheet(self._label_style(Colors.GREEN))
        elif state == "processing":
            self._pulse_anim.setDuration(1800)
            self._rotation_timer.start()
            self._status_label.setText("◎  PROCESSING")
            self._status_label.setStyleSheet(self._label_style(Colors.PURPLE))
        elif state == "speaking":
            self._pulse_anim.setDuration(1600)
            self._wave_timer.start()
            self._status_label.setText("◈  SPEAKING")
            self._status_label.setStyleSheet(self._label_style(Colors.CYAN))

        self.update()

    @property
    def state(self) -> str:
        return self._state

    # ── Timer ticks ──────────────────────────────────────────────────

    def _tick_rotation(self) -> None:
        self._rotation = (self._rotation + 3.0) % 360.0
        self.update()

    def _tick_ripple(self) -> None:
        self._ripple_value = (self._ripple_value + 0.012) % 1.0
        self.update()

    def _tick_wave(self) -> None:
        self._wave_phase += 0.08
        self.update()

    # ── Painting ─────────────────────────────────────────────────────

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        w, h = self.width(), self.height() - 40  # reserve space for label
        cx, cy = w / 2, h / 2
        base_radius = min(w, h) * 0.30

        # Pulse factor: oscillates between 0.92 and 1.08
        pulse = 0.92 + 0.16 * abs(math.sin(self._pulse_value * math.pi))
        radius = base_radius * pulse

        # ── Outer glow ───────────────────────────────────────────────
        self._draw_glow(painter, cx, cy, radius)

        # ── State-specific effects ───────────────────────────────────
        if self._state == "listening":
            self._draw_ripples(painter, cx, cy, radius)
        elif self._state == "processing":
            self._draw_spinner(painter, cx, cy, radius)
        elif self._state == "speaking":
            self._draw_waveform(painter, cx, cy, radius)

        # ── Orb core ────────────────────────────────────────────────
        self._draw_orb(painter, cx, cy, radius)

        # ── Inner highlight ──────────────────────────────────────────
        self._draw_highlight(painter, cx, cy, radius)

        painter.end()

    def _draw_glow(self, p: QPainter, cx: float, cy: float, r: float) -> None:
        """Ambient glow behind the orb."""
        glow_r = r * 1.8
        gradient = QRadialGradient(QPointF(cx, cy), glow_r)

        if self._state == "listening":
            gradient.setColorAt(0.0, QColor(0, 230, 118, 40))
            gradient.setColorAt(0.5, QColor(0, 230, 118, 12))
        elif self._state == "processing":
            gradient.setColorAt(0.0, QColor(108, 99, 255, 40))
            gradient.setColorAt(0.5, QColor(108, 99, 255, 12))
        elif self._state == "speaking":
            gradient.setColorAt(0.0, QColor(0, 212, 255, 50))
            gradient.setColorAt(0.5, QColor(0, 212, 255, 15))
        else:
            gradient.setColorAt(0.0, QColor(0, 212, 255, 30))
            gradient.setColorAt(0.5, QColor(0, 212, 255, 8))
        gradient.setColorAt(1.0, QColor(0, 0, 0, 0))

        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(gradient))
        p.drawEllipse(QPointF(cx, cy), glow_r, glow_r)

    def _draw_orb(self, p: QPainter, cx: float, cy: float, r: float) -> None:
        """Main orb body with radial gradient."""
        gradient = QRadialGradient(QPointF(cx - r * 0.3, cy - r * 0.3), r * 1.4)

        if self._state == "listening":
            gradient.setColorAt(0.0, QColor(0, 230, 118, 180))
            gradient.setColorAt(0.4, QColor(0, 168, 84, 140))
            gradient.setColorAt(1.0, QColor(10, 30, 20, 200))
        elif self._state == "processing":
            gradient.setColorAt(0.0, QColor(108, 99, 255, 180))
            gradient.setColorAt(0.4, QColor(74, 66, 204, 140))
            gradient.setColorAt(1.0, QColor(15, 12, 40, 200))
        elif self._state == "speaking":
            gradient.setColorAt(0.0, QColor(0, 212, 255, 200))
            gradient.setColorAt(0.4, QColor(0, 136, 204, 150))
            gradient.setColorAt(1.0, QColor(8, 18, 35, 210))
        else:
            gradient.setColorAt(0.0, QColor(0, 212, 255, 140))
            gradient.setColorAt(0.4, QColor(0, 100, 160, 110))
            gradient.setColorAt(1.0, QColor(8, 14, 25, 190))

        p.setPen(QPen(QColor(0, 212, 255, 60), 1.5))
        p.setBrush(QBrush(gradient))
        p.drawEllipse(QPointF(cx, cy), r, r)

    def _draw_highlight(self, p: QPainter, cx: float, cy: float, r: float) -> None:
        """Specular highlight on the orb for glass effect."""
        hr = r * 0.55
        hx, hy = cx - r * 0.18, cy - r * 0.25
        gradient = QRadialGradient(QPointF(hx, hy), hr)
        gradient.setColorAt(0.0, QColor(255, 255, 255, 50))
        gradient.setColorAt(1.0, QColor(255, 255, 255, 0))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(gradient))
        p.drawEllipse(QPointF(hx, hy), hr, hr)

    def _draw_ripples(self, p: QPainter, cx: float, cy: float, r: float) -> None:
        """Concentric expanding ripple rings for listening state."""
        for i in range(3):
            offset = (self._ripple_value + i * 0.33) % 1.0
            ripple_r = r * (1.2 + offset * 0.9)
            alpha = int(80 * (1.0 - offset))
            pen = QPen(QColor(0, 230, 118, alpha), 1.5)
            p.setPen(pen)
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawEllipse(QPointF(cx, cy), ripple_r, ripple_r)

    def _draw_spinner(self, p: QPainter, cx: float, cy: float, r: float) -> None:
        """Rotating arc around the orb for processing state."""
        spinner_r = r + 12
        rect = QRectF(cx - spinner_r, cy - spinner_r, spinner_r * 2, spinner_r * 2)

        for i, (span, alpha) in enumerate([(80, 200), (50, 120), (30, 70)]):
            angle = int(self._rotation * 16 + i * 120 * 16)
            pen = QPen(QColor(108, 99, 255, alpha), 3 - i * 0.5)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            p.setPen(pen)
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawArc(rect, angle, span * 16)

    def _draw_waveform(self, p: QPainter, cx: float, cy: float, r: float) -> None:
        """Sine-wave ring around the orb perimeter for speaking state."""
        wave_r = r + 15
        points = 120
        path = QPainterPath()

        for i in range(points + 1):
            angle = (i / points) * 2 * math.pi
            amplitude = 6 * math.sin(self._wave_phase + angle * 6)
            px = cx + (wave_r + amplitude) * math.cos(angle)
            py = cy + (wave_r + amplitude) * math.sin(angle)
            if i == 0:
                path.moveTo(px, py)
            else:
                path.lineTo(px, py)

        pen = QPen(QColor(0, 212, 255, 160), 2)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawPath(path)

        # Second wave layer, offset
        path2 = QPainterPath()
        for i in range(points + 1):
            angle = (i / points) * 2 * math.pi
            amplitude = 4 * math.sin(self._wave_phase * 1.3 + angle * 8 + 1.0)
            px = cx + (wave_r + 5 + amplitude) * math.cos(angle)
            py = cy + (wave_r + 5 + amplitude) * math.sin(angle)
            if i == 0:
                path2.moveTo(px, py)
            else:
                path2.lineTo(px, py)

        pen2 = QPen(QColor(0, 212, 255, 70), 1.5)
        p.setPen(pen2)
        p.drawPath(path2)

    # ── Helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _label_style(color: str) -> str:
        return f"""
            color: {color};
            font-size: {Fonts.SIZE_LG}px;
            font-weight: bold;
            letter-spacing: 3px;
            background: transparent;
            border: none;
        """
