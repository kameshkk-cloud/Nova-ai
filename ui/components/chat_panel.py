"""
NOVA GUI — Chat Panel
======================
Scrollable chat-style interface with styled message bubbles.
NOVA responses display with a typing effect (character-by-character).
"""

from __future__ import annotations

import datetime

from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QKeyEvent
from PyQt6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton, QScrollArea,
    QSizePolicy, QVBoxLayout, QWidget,
)

from ui.styles.theme import (
    Colors, Dimensions, Fonts, accent_button_style, panel_style,
    section_title_style,
)


class ChatBubble(QWidget):
    """Single chat message bubble."""

    def __init__(
        self, text: str, is_user: bool = True,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(2)

        # ── Header row: sender + timestamp ───────────────────────────
        header = QHBoxLayout()
        header.setSpacing(8)

        sender_name = "YOU" if is_user else "NOVA"
        sender = QLabel(sender_name)
        sender.setStyleSheet(f"""
            color: {Colors.CYAN if not is_user else Colors.PURPLE};
            font-size: {Fonts.SIZE_XS}px;
            font-weight: bold;
            letter-spacing: 1px;
            background: transparent;
            border: none;
        """)

        timestamp = QLabel(datetime.datetime.now().strftime("%H:%M"))
        timestamp.setStyleSheet(f"""
            color: {Colors.TEXT_MUTED};
            font-size: {Fonts.SIZE_XS}px;
            background: transparent;
            border: none;
        """)

        if is_user:
            header.addStretch()
            header.addWidget(timestamp)
            header.addWidget(sender)
        else:
            header.addWidget(sender)
            header.addWidget(timestamp)
            header.addStretch()

        layout.addLayout(header)

        # ── Message body ─────────────────────────────────────────────
        bg = Colors.BG_HOVER if is_user else Colors.BG_PANEL_LIGHT
        border_color = Colors.PURPLE_GLOW if is_user else Colors.CYAN_GLOW
        align = "right" if is_user else "left"

        self._body = QLabel(text)
        self._body.setWordWrap(True)
        self._body.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        self._body.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum,
        )
        self._body.setStyleSheet(f"""
            QLabel {{
                background-color: {bg};
                color: {Colors.TEXT_PRIMARY};
                border: 1px solid {border_color};
                border-radius: {Dimensions.BORDER_RADIUS_SM}px;
                padding: 10px 14px;
                font-size: {Fonts.SIZE_MD}px;
                line-height: 1.4;
            }}
        """)

        # Alignment wrapper
        body_layout = QHBoxLayout()
        body_layout.setContentsMargins(0, 0, 0, 0)
        if is_user:
            body_layout.addStretch(1)
            body_layout.addWidget(self._body, 4)
        else:
            body_layout.addWidget(self._body, 4)
            body_layout.addStretch(1)

        layout.addLayout(body_layout)

    def set_text(self, text: str) -> None:
        self._body.setText(text)


class ChatPanel(QWidget):
    """
    Scrollable chat panel with text input field.
    Emits `command_submitted` when the user sends a message.
    """

    command_submitted = pyqtSignal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setStyleSheet(f"""
            QWidget {{
                {panel_style()}
                padding: 0;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # ── Title ────────────────────────────────────────────────────
        title = QLabel("◈  COMMAND INTERFACE")
        title.setStyleSheet(section_title_style())
        layout.addWidget(title)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"background-color: {Colors.BORDER}; max-height: 1px; border: none;")
        layout.addWidget(sep)

        # ── Scroll area for chat messages ────────────────────────────
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

        self._messages_widget = QWidget()
        self._messages_widget.setStyleSheet(f"background-color: {Colors.BG_DARKEST}; border: none;")
        self._messages_layout = QVBoxLayout(self._messages_widget)
        self._messages_layout.setContentsMargins(4, 8, 4, 8)
        self._messages_layout.setSpacing(6)
        self._messages_layout.addStretch()

        self._scroll.setWidget(self._messages_widget)
        layout.addWidget(self._scroll, 1)

        # ── Input row ────────────────────────────────────────────────
        input_row = QHBoxLayout()
        input_row.setSpacing(8)

        self._input = QLineEdit()
        self._input.setPlaceholderText("Type a command…")
        self._input.setMinimumHeight(42)
        self._input.returnPressed.connect(self._on_send)
        input_row.addWidget(self._input, 1)

        self._send_btn = QPushButton("▶")
        self._send_btn.setFixedSize(42, 42)
        self._send_btn.setToolTip("Send command (Enter)")
        self._send_btn.setStyleSheet(accent_button_style())
        self._send_btn.clicked.connect(self._on_send)
        input_row.addWidget(self._send_btn)

        layout.addLayout(input_row)

        # ── Typing effect state ──────────────────────────────────────
        self._typing_timer = QTimer(self)
        self._typing_timer.setInterval(18)
        self._typing_timer.timeout.connect(self._type_next_char)
        self._typing_text = ""
        self._typing_index = 0
        self._typing_bubble: ChatBubble | None = None

    # ── Public API ───────────────────────────────────────────────────

    def add_user_message(self, text: str) -> None:
        """Add a user message bubble immediately."""
        bubble = ChatBubble(text, is_user=True)
        self._messages_layout.insertWidget(
            self._messages_layout.count() - 1, bubble,
        )
        self._scroll_to_bottom()

    def add_nova_message(self, text: str, typing_effect: bool = True) -> None:
        """Add a NOVA response with optional typing effect."""
        if typing_effect and len(text) > 0:
            bubble = ChatBubble("", is_user=False)
            self._messages_layout.insertWidget(
                self._messages_layout.count() - 1, bubble,
            )
            self._typing_bubble = bubble
            self._typing_text = text
            self._typing_index = 0
            self._typing_timer.start()
        else:
            bubble = ChatBubble(text, is_user=False)
            self._messages_layout.insertWidget(
                self._messages_layout.count() - 1, bubble,
            )
        self._scroll_to_bottom()

    def add_system_message(self, text: str) -> None:
        """Add a system info message (centered, muted)."""
        lbl = QLabel(text)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setWordWrap(True)
        lbl.setStyleSheet(f"""
            color: {Colors.TEXT_MUTED};
            font-size: {Fonts.SIZE_XS}px;
            padding: 6px;
            background: transparent;
            border: none;
        """)
        self._messages_layout.insertWidget(
            self._messages_layout.count() - 1, lbl,
        )
        self._scroll_to_bottom()

    def set_input_enabled(self, enabled: bool) -> None:
        self._input.setEnabled(enabled)
        self._send_btn.setEnabled(enabled)

    # ── Internal ─────────────────────────────────────────────────────

    def _on_send(self) -> None:
        text = self._input.text().strip()
        if not text:
            return
        self._input.clear()
        self.add_user_message(text)
        self.command_submitted.emit(text)

    def _type_next_char(self) -> None:
        if self._typing_index < len(self._typing_text):
            # Type in chunks for speed
            chunk_size = 2
            end = min(self._typing_index + chunk_size, len(self._typing_text))
            self._typing_bubble.set_text(self._typing_text[:end])
            self._typing_index = end
            self._scroll_to_bottom()
        else:
            self._typing_timer.stop()
            self._typing_bubble = None

    def _scroll_to_bottom(self) -> None:
        QTimer.singleShot(50, lambda: self._scroll.verticalScrollBar().setValue(
            self._scroll.verticalScrollBar().maximum()
        ))
