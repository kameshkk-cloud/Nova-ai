"""
NOVA GUI — Settings Panel
===========================
Collapsible settings sidebar with wake word toggle, voice mode selector,
and LLM provider display.
"""

from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox, QFrame, QHBoxLayout, QLabel, QPushButton,
    QSizePolicy, QVBoxLayout, QWidget,
)

from ui.styles.theme import Colors, Dimensions, Fonts, panel_style, section_title_style


class ToggleSwitch(QWidget):
    """Custom ON/OFF toggle switch."""

    toggled = pyqtSignal(bool)

    def __init__(self, initial: bool = True, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._on = initial
        self.setFixedSize(50, 26)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def is_on(self) -> bool:
        return self._on

    def set_on(self, on: bool) -> None:
        self._on = on
        self.update()
        self.toggled.emit(on)

    def mousePressEvent(self, event) -> None:
        self._on = not self._on
        self.update()
        self.toggled.emit(self._on)

    def paintEvent(self, event) -> None:
        from PyQt6.QtGui import QPainter, QColor, QPen, QBrush

        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        w, h = self.width(), self.height()
        radius = h / 2

        # Track
        track_color = QColor(Colors.CYAN_DIM) if self._on else QColor(Colors.BG_HOVER)
        border_color = QColor(Colors.CYAN) if self._on else QColor(Colors.BORDER)
        p.setPen(QPen(border_color, 1))
        p.setBrush(QBrush(track_color))
        p.drawRoundedRect(1, 1, w - 2, h - 2, radius, radius)

        # Thumb
        thumb_x = w - h + 2 if self._on else 2
        thumb_color = QColor(Colors.TEXT_BRIGHT) if self._on else QColor(Colors.TEXT_SECONDARY)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(thumb_color))
        p.drawEllipse(thumb_x + 2, 3, h - 6, h - 6)

        p.end()


class SettingsPanel(QWidget):
    """
    Settings sidebar with wake word toggle, voice mode selector,
    and LLM provider info.
    """

    wake_word_toggled = pyqtSignal(bool)
    voice_mode_changed = pyqtSignal(str)

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
        layout.setSpacing(12)

        # ── Title ────────────────────────────────────────────────────
        title = QLabel("⚙  SETTINGS")
        title.setStyleSheet(section_title_style())
        layout.addWidget(title)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"background-color: {Colors.BORDER}; max-height: 1px; border: none;")
        layout.addWidget(sep)

        # ── Wake word toggle ─────────────────────────────────────────
        ww_row = QHBoxLayout()
        ww_label = QLabel("Wake Word")
        ww_label.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: {Fonts.SIZE_MD}px; background: transparent; border: none;")
        self._wake_toggle = ToggleSwitch(initial=True)
        self._wake_toggle.toggled.connect(self.wake_word_toggled.emit)
        ww_row.addWidget(ww_label)
        ww_row.addStretch()
        ww_row.addWidget(self._wake_toggle)
        layout.addLayout(ww_row)

        ww_hint = QLabel('"Hey NOVA"')
        ww_hint.setStyleSheet(f"color: {Colors.TEXT_MUTED}; font-size: {Fonts.SIZE_XS}px; background: transparent; border: none;")
        layout.addWidget(ww_hint)

        # ── Voice mode selector ──────────────────────────────────────
        vm_label = QLabel("Voice Mode")
        vm_label.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: {Fonts.SIZE_MD}px; background: transparent; border: none; margin-top: 8px;")
        layout.addWidget(vm_label)

        self._voice_combo = QComboBox()
        self._voice_combo.addItems(["JARVIS", "Calm", "Energetic", "Alert"])
        self._voice_combo.setCurrentText("JARVIS")
        self._voice_combo.currentTextChanged.connect(
            lambda t: self.voice_mode_changed.emit(t.lower())
        )
        layout.addWidget(self._voice_combo)

        # ── LLM Provider ────────────────────────────────────────────
        layout.addSpacing(8)
        llm_label = QLabel("LLM Provider")
        llm_label.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: {Fonts.SIZE_MD}px; background: transparent; border: none;")
        layout.addWidget(llm_label)

        self._llm_value = QLabel("—")
        self._llm_value.setStyleSheet(f"""
            color: {Colors.CYAN};
            font-size: {Fonts.SIZE_MD}px;
            font-weight: bold;
            padding: 8px 12px;
            background-color: {Colors.BG_DARKEST};
            border: 1px solid {Colors.BORDER};
            border-radius: {Dimensions.BORDER_RADIUS_SM}px;
        """)
        layout.addWidget(self._llm_value)

        # ── User name ───────────────────────────────────────────────
        layout.addSpacing(8)
        user_lbl = QLabel("User")
        user_lbl.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: {Fonts.SIZE_MD}px; background: transparent; border: none;")
        layout.addWidget(user_lbl)

        self._user_value = QLabel("—")
        self._user_value.setStyleSheet(f"""
            color: {Colors.PURPLE};
            font-size: {Fonts.SIZE_MD}px;
            font-weight: bold;
            padding: 8px 12px;
            background-color: {Colors.BG_DARKEST};
            border: 1px solid {Colors.BORDER};
            border-radius: {Dimensions.BORDER_RADIUS_SM}px;
        """)
        layout.addWidget(self._user_value)

        layout.addStretch()

        # ── Version footer ───────────────────────────────────────────
        version = QLabel("NOVA v2.0")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version.setStyleSheet(f"""
            color: {Colors.TEXT_MUTED};
            font-size: {Fonts.SIZE_XS}px;
            padding: 4px;
            background: transparent;
            border: none;
        """)
        layout.addWidget(version)

    def set_llm_provider(self, name: str) -> None:
        self._llm_value.setText(name.upper())

    def set_user_name(self, name: str) -> None:
        self._user_value.setText(name)
