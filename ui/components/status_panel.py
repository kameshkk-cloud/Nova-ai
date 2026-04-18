"""
NOVA GUI — System Status Panel
================================
Real-time CPU / RAM / Disk / Battery / Network gauges drawn with QPainter.
Updated every 2 seconds via the bridge's system_stats signal.
"""

from __future__ import annotations

import math

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QColor, QFont, QPainter, QPen, QRadialGradient, QBrush
from PyQt6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QSizePolicy, QVBoxLayout, QWidget,
)

from ui.styles.theme import Colors, Dimensions, Fonts, panel_style, section_title_style


class ArcGauge(QWidget):
    """Circular arc gauge drawn with QPainter."""

    def __init__(
        self, label: str = "", value: float = 0, unit: str = "%",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._label = label
        self._value = value
        self._unit = unit
        self.setMinimumSize(90, 100)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)

    def set_value(self, value: float) -> None:
        self._value = max(0, min(100, value))
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        w, h = self.width(), self.height()
        cx, cy = w / 2, h / 2 - 8
        radius = min(w, h) * 0.34

        # ── Determine color ─────────────────────────────────────────
        if self._value < 60:
            color = QColor(Colors.GREEN)
            glow = QColor(0, 230, 118, 30)
        elif self._value < 85:
            color = QColor(Colors.YELLOW)
            glow = QColor(255, 171, 0, 30)
        else:
            color = QColor(Colors.RED)
            glow = QColor(255, 51, 102, 30)

        # ── Background arc (track) ──────────────────────────────────
        rect = QRectF(cx - radius, cy - radius, radius * 2, radius * 2)
        start_angle = 225 * 16
        span_angle = -270 * 16

        track_pen = QPen(QColor(Colors.BORDER), 5)
        track_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(track_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawArc(rect, start_angle, span_angle)

        # ── Value arc ───────────────────────────────────────────────
        value_span = int(-270 * (self._value / 100.0)) * 16
        value_pen = QPen(color, 5)
        value_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(value_pen)
        painter.drawArc(rect, start_angle, value_span)

        # ── Center text ─────────────────────────────────────────────
        painter.setPen(QPen(QColor(Colors.TEXT_PRIMARY)))
        font = QFont()
        font.setPixelSize(18)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(
            QRectF(cx - radius, cy - radius * 0.4, radius * 2, radius * 0.8),
            Qt.AlignmentFlag.AlignCenter,
            f"{self._value:.0f}{self._unit}",
        )

        # ── Label below ─────────────────────────────────────────────
        painter.setPen(QPen(QColor(Colors.TEXT_SECONDARY)))
        font.setPixelSize(11)
        font.setBold(False)
        painter.setFont(font)
        painter.drawText(
            QRectF(0, cy + radius * 0.5, w, 20),
            Qt.AlignmentFlag.AlignCenter,
            self._label,
        )

        painter.end()


class StatusIndicator(QWidget):
    """Small horizontal status row: dot + label + value."""

    def __init__(self, label: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._label_text = label
        self._value_text = "—"
        self._color = Colors.TEXT_MUTED

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(8)

        self._dot = QLabel()
        self._dot.setFixedSize(10, 10)
        self._dot.setStyleSheet(f"""
            background-color: {Colors.TEXT_MUTED};
            border-radius: 5px;
            border: none;
        """)

        self._lbl = QLabel(label)
        self._lbl.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: {Fonts.SIZE_SM}px; background: transparent; border: none;")

        self._val = QLabel("—")
        self._val.setAlignment(Qt.AlignmentFlag.AlignRight)
        self._val.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: {Fonts.SIZE_SM}px; font-weight: bold; background: transparent; border: none;")

        layout.addWidget(self._dot)
        layout.addWidget(self._lbl, 1)
        layout.addWidget(self._val)

    def set_value(self, text: str, color: str = Colors.GREEN) -> None:
        self._val.setText(text)
        self._dot.setStyleSheet(f"background-color: {color}; border-radius: 5px; border: none;")


class StatusPanel(QWidget):
    """
    System status panel with CPU/RAM arc gauges and supplementary indicators.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setMinimumWidth(200)
        self.setMaximumWidth(260)
        self.setStyleSheet(f"""
            QWidget {{
                {panel_style(glow=True)}
                padding: 0;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 16, 12, 16)
        layout.setSpacing(6)

        # ── Section title ────────────────────────────────────────────
        title = QLabel("⬡  SYSTEM STATUS")
        title.setStyleSheet(section_title_style())
        layout.addWidget(title)

        # ── Separator ────────────────────────────────────────────────
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"background-color: {Colors.BORDER}; max-height: 1px; border: none;")
        layout.addWidget(sep)

        # ── Arc gauges row ───────────────────────────────────────────
        gauges_row = QHBoxLayout()
        gauges_row.setSpacing(4)
        self._cpu_gauge = ArcGauge("CPU", 0)
        self._ram_gauge = ArcGauge("RAM", 0)
        gauges_row.addWidget(self._cpu_gauge)
        gauges_row.addWidget(self._ram_gauge)
        layout.addLayout(gauges_row)

        # ── Additional indicators ────────────────────────────────────
        self._disk_ind = StatusIndicator("Disk")
        self._battery_ind = StatusIndicator("Battery")
        self._network_ind = StatusIndicator("Network")

        layout.addWidget(self._disk_ind)
        layout.addWidget(self._battery_ind)
        layout.addWidget(self._network_ind)

        layout.addStretch()

        # ── Health summary ───────────────────────────────────────────
        self._health_label = QLabel("● System Healthy")
        self._health_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._health_label.setStyleSheet(f"""
            color: {Colors.GREEN};
            font-size: {Fonts.SIZE_SM}px;
            font-weight: bold;
            padding: 8px;
            background-color: {Colors.BG_DARKEST};
            border-radius: {Dimensions.BORDER_RADIUS_SM}px;
            border: 1px solid {Colors.GREEN_DIM}40;
        """)
        layout.addWidget(self._health_label)

    def update_stats(self, stats: dict) -> None:
        """Receive a stats dict from the bridge and update all gauges."""
        cpu = stats.get("cpu", {})
        ram = stats.get("ram", {})
        disk = stats.get("disk", {})
        battery = stats.get("battery", {})
        internet = stats.get("internet", True)

        # Gauges
        self._cpu_gauge.set_value(cpu.get("usage_percent", 0))
        self._ram_gauge.set_value(ram.get("usage_percent", 0))

        # Disk
        disk_pct = disk.get("usage_percent", 0)
        disk_color = Colors.RED if disk_pct >= 90 else Colors.YELLOW if disk_pct >= 75 else Colors.GREEN
        self._disk_ind.set_value(f"{disk_pct}%  ({disk.get('free_gb', '?')} GB free)", disk_color)

        # Battery
        if battery.get("available"):
            bat_pct = battery.get("percent", 0)
            plugged = battery.get("plugged", False)
            bat_icon = "⚡" if plugged else "🔋"
            bat_color = Colors.RED if bat_pct <= 20 else Colors.YELLOW if bat_pct <= 40 else Colors.GREEN
            self._battery_ind.set_value(f"{bat_icon} {bat_pct}%", bat_color)
        else:
            self._battery_ind.set_value("Desktop PC", Colors.TEXT_MUTED)

        # Network
        net_color = Colors.GREEN if internet else Colors.RED
        net_text = "Online" if internet else "Offline"
        self._network_ind.set_value(net_text, net_color)

        # Health summary
        alerts = []
        if cpu.get("alert"):
            alerts.append("CPU")
        if ram.get("alert"):
            alerts.append("RAM")
        if disk.get("alert"):
            alerts.append("Disk")
        if not internet:
            alerts.append("Net")

        if alerts:
            self._health_label.setText(f"⚠ Alert: {', '.join(alerts)}")
            self._health_label.setStyleSheet(f"""
                color: {Colors.RED};
                font-size: {Fonts.SIZE_SM}px;
                font-weight: bold;
                padding: 8px;
                background-color: {Colors.BG_DARKEST};
                border-radius: {Dimensions.BORDER_RADIUS_SM}px;
                border: 1px solid {Colors.RED_DIM}40;
            """)
        else:
            self._health_label.setText("● System Healthy")
            self._health_label.setStyleSheet(f"""
                color: {Colors.GREEN};
                font-size: {Fonts.SIZE_SM}px;
                font-weight: bold;
                padding: 8px;
                background-color: {Colors.BG_DARKEST};
                border-radius: {Dimensions.BORDER_RADIUS_SM}px;
                border: 1px solid {Colors.GREEN_DIM}40;
            """)
