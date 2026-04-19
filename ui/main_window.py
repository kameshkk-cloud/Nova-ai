"""
NOVA GUI — Main Window
========================
Assembles all panels into the main application window with a
custom frameless title bar and three-column layout.
"""

from __future__ import annotations

from PyQt6.QtCore import QPoint, QSize, Qt
from PyQt6.QtGui import QFont, QIcon, QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QApplication, QFrame, QHBoxLayout, QLabel, QMainWindow,
    QPushButton, QSizePolicy, QSplitter, QVBoxLayout, QWidget,
)

from ui.bridge import NovaBridge
from ui.components.activity_log import ActivityLog
from ui.components.ai_orb import AIOrb
from ui.components.chat_panel import ChatPanel
from ui.components.notification_bar import NotificationBar
from ui.components.quick_actions import QuickActions
from ui.components.settings_panel import SettingsPanel
from ui.components.status_panel import StatusPanel
from ui.components.voice_control import VoiceControl
from ui.styles.theme import Colors, Dimensions, Fonts, panel_style


class TitleBar(QWidget):
    """Custom frameless title bar with drag-to-move and window controls."""

    def __init__(self, parent: QMainWindow) -> None:
        super().__init__(parent)
        self._parent = parent
        self._drag_pos = None
        self.setFixedHeight(40)
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {Colors.BG_DARKEST};
                border-bottom: 1px solid {Colors.BORDER};
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 8, 0)
        layout.setSpacing(12)

        # ── Logo / title ─────────────────────────────────────────────
        logo = QLabel("⬡")
        logo.setStyleSheet(f"color: {Colors.CYAN}; font-size: 20px; background: transparent; border: none;")
        layout.addWidget(logo)

        title = QLabel("NOVA AI")
        title.setStyleSheet(f"""
            color: {Colors.CYAN};
            font-size: {Fonts.SIZE_TITLE}px;
            font-weight: bold;
            letter-spacing: 3px;
            background: transparent;
            border: none;
        """)
        layout.addWidget(title)

        version = QLabel("v2.0")
        version.setStyleSheet(f"""
            color: {Colors.TEXT_MUTED};
            font-size: {Fonts.SIZE_XS}px;
            background: transparent;
            border: none;
        """)
        layout.addWidget(version)

        layout.addStretch()

        # ── Status indicator ─────────────────────────────────────────
        self._status_dot = QLabel()
        self._status_dot.setFixedSize(8, 8)
        self._status_dot.setStyleSheet(f"""
            background-color: {Colors.YELLOW};
            border-radius: 4px;
            border: none;
        """)
        layout.addWidget(self._status_dot)

        self._status_label = QLabel("BOOTING")
        self._status_label.setStyleSheet(f"""
            color: {Colors.YELLOW};
            font-size: {Fonts.SIZE_XS}px;
            letter-spacing: 1px;
            background: transparent;
            border: none;
        """)
        layout.addWidget(self._status_label)

        layout.addSpacing(20)

        # ── Window controls ──────────────────────────────────────────
        btn_style = f"""
            QPushButton {{
                background: transparent;
                color: {Colors.TEXT_SECONDARY};
                border: none;
                font-size: 16px;
                padding: 4px 10px;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {Colors.BG_HOVER};
                color: {Colors.TEXT_PRIMARY};
            }}
        """
        close_style = f"""
            QPushButton {{
                background: transparent;
                color: {Colors.TEXT_SECONDARY};
                border: none;
                font-size: 16px;
                padding: 4px 10px;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {Colors.RED};
                color: {Colors.TEXT_BRIGHT};
            }}
        """

        btn_min = QPushButton("─")
        btn_min.setStyleSheet(btn_style)
        btn_min.setFixedSize(36, 28)
        btn_min.clicked.connect(parent.showMinimized)

        btn_max = QPushButton("□")
        btn_max.setStyleSheet(btn_style)
        btn_max.setFixedSize(36, 28)
        btn_max.clicked.connect(self._toggle_maximize)

        btn_close = QPushButton("✕")
        btn_close.setStyleSheet(close_style)
        btn_close.setFixedSize(36, 28)
        btn_close.clicked.connect(parent.close)

        layout.addWidget(btn_min)
        layout.addWidget(btn_max)
        layout.addWidget(btn_close)

    def set_status(self, text: str, color: str) -> None:
        self._status_label.setText(text)
        self._status_label.setStyleSheet(f"""
            color: {color};
            font-size: {Fonts.SIZE_XS}px;
            letter-spacing: 1px;
            background: transparent;
            border: none;
        """)
        self._status_dot.setStyleSheet(f"""
            background-color: {color};
            border-radius: 4px;
            border: none;
        """)

    def _toggle_maximize(self) -> None:
        if self._parent.isMaximized():
            self._parent.showNormal()
        else:
            self._parent.showMaximized()

    # ── Drag to move ─────────────────────────────────────────────────

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self._parent.frameGeometry().topLeft()

    def mouseMoveEvent(self, event) -> None:
        if self._drag_pos and event.buttons() & Qt.MouseButton.LeftButton:
            self._parent.move(event.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, event) -> None:
        self._drag_pos = None

    def mouseDoubleClickEvent(self, event) -> None:
        self._toggle_maximize()


class MainWindow(QMainWindow):
    """
    NOVA AI main application window.
    Assembles all panels and wires them to the backend bridge.
    """

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("NOVA AI")
        self.setMinimumSize(Dimensions.MIN_WINDOW_W, Dimensions.MIN_WINDOW_H)
        self.resize(1400, 850)

        # Frameless window
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.setStyleSheet(f"QMainWindow {{ background-color: {Colors.BG_DARKEST}; }}")

        # ── Bridge ───────────────────────────────────────────────────
        self._bridge = NovaBridge(self)

        # ── Central widget ───────────────────────────────────────────
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── Title bar ────────────────────────────────────────────────
        self._title_bar = TitleBar(self)
        main_layout.addWidget(self._title_bar)

        # ── Body ─────────────────────────────────────────────────────
        body = QWidget()
        body.setStyleSheet(f"background-color: {Colors.BG_DARKEST};")
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(8, 8, 8, 8)
        body_layout.setSpacing(8)

        # ── LEFT COLUMN (Status + Quick Actions) ─────────────────────
        left_col = QWidget()
        left_col.setFixedWidth(240)
        left_layout = QVBoxLayout(left_col)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(8)

        self._status_panel = StatusPanel()
        self._quick_actions = QuickActions()

        left_layout.addWidget(self._status_panel, 3)
        left_layout.addWidget(self._quick_actions, 2)

        # ── CENTER COLUMN (Orb + Voice + Chat) ───────────────────────
        center_col = QWidget()
        center_layout = QVBoxLayout(center_col)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(8)

        # Orb container
        orb_container = QWidget()
        orb_container.setStyleSheet(f"""
            background-color: {Colors.BG_PANEL};
            border: 1px solid {Colors.BORDER_GLOW};
            border-radius: {Dimensions.BORDER_RADIUS_LG}px;
        """)
        orb_layout = QVBoxLayout(orb_container)
        orb_layout.setContentsMargins(16, 16, 16, 12)
        orb_layout.setSpacing(8)

        self._ai_orb = AIOrb()
        self._voice_control = VoiceControl()

        orb_layout.addWidget(self._ai_orb, 1)
        orb_layout.addWidget(self._voice_control)

        # Chat
        self._chat_panel = ChatPanel()

        center_layout.addWidget(orb_container, 2)
        center_layout.addWidget(self._chat_panel, 3)

        # ── RIGHT COLUMN (Settings + Activity Log) ───────────────────
        right_col = QWidget()
        right_col.setFixedWidth(240)
        right_layout = QVBoxLayout(right_col)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(8)

        self._settings_panel = SettingsPanel()
        self._activity_log = ActivityLog()

        right_layout.addWidget(self._settings_panel, 2)
        right_layout.addWidget(self._activity_log, 3)

        # ── Assemble columns ─────────────────────────────────────────
        body_layout.addWidget(left_col)
        body_layout.addWidget(center_col, 1)
        body_layout.addWidget(right_col)

        main_layout.addWidget(body, 1)

        # ── Notification overlay ─────────────────────────────────────
        self._notifications = NotificationBar(self)

        # ── Wire signals ─────────────────────────────────────────────
        self._connect_signals()

        # ── Keyboard shortcuts ───────────────────────────────────────
        self._setup_shortcuts()

        # ── Populate settings ────────────────────────────────────────
        config = self._bridge.get_config()
        self._settings_panel.set_user_name(config.get("user_name", "—"))
        self._settings_panel.set_llm_provider(config.get("llm_provider", "—"))

        # ── Boot sequence ────────────────────────────────────────────
        self._chat_panel.add_system_message("⬡ NOVA AI — Initializing systems…")
        self._bridge.start_boot()

    # ── Signal wiring ────────────────────────────────────────────────

    def _connect_signals(self) -> None:
        b = self._bridge

        # Bridge → UI
        b.state_changed.connect(self._on_state_changed)
        b.response_ready.connect(self._on_response_ready)
        b.system_stats.connect(self._status_panel.update_stats)
        b.alert_fired.connect(self._on_alert)
        b.boot_complete.connect(self._on_boot_complete)
        b.boot_error.connect(self._on_boot_error)
        b.activity.connect(self._activity_log.add_entry)

        # UI → Bridge
        self._chat_panel.command_submitted.connect(b.send_command)
        self._quick_actions.action_requested.connect(self._on_quick_action)
        self._voice_control.mic_toggled.connect(self._on_mic_toggle)
        self._settings_panel.voice_mode_changed.connect(b.set_voice_mode)

    def _setup_shortcuts(self) -> None:
        # Ctrl+M to toggle mic (Space was conflicting with chat input)
        sc_mic = QShortcut(QKeySequence("Ctrl+M"), self)
        sc_mic.setContext(Qt.ShortcutContext.ApplicationShortcut)
        sc_mic.activated.connect(self._toggle_mic_shortcut)

        # Escape to minimize
        sc_esc = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
        sc_esc.activated.connect(self.showMinimized)

        # Ctrl+Q to quit
        sc_quit = QShortcut(QKeySequence("Ctrl+Q"), self)
        sc_quit.activated.connect(self.close)

    # ── Event handlers ───────────────────────────────────────────────

    def _on_state_changed(self, state: str) -> None:
        self._ai_orb.set_state(state)
        self._voice_control.set_status(state)

    def _on_response_ready(self, user_input: str, response: str) -> None:
        self._chat_panel.add_nova_message(response, typing_effect=True)

    def _on_alert(self, message: str, severity: str) -> None:
        sev_map = {"CRITICAL": "critical", "WARNING": "warning"}
        self._notifications.show_notification(
            message, sev_map.get(severity, "warning"),
        )

    def _on_boot_complete(self) -> None:
        self._title_bar.set_status("ONLINE", Colors.GREEN)
        self._chat_panel.add_system_message("✓ NOVA is online. All systems operational.")
        self._voice_control.set_mic_available(self._bridge.mic_available)

        # Refresh config
        config = self._bridge.get_config()
        self._settings_panel.set_user_name(config.get("user_name", "—"))
        self._settings_panel.set_llm_provider(config.get("llm_provider", "—"))

    def _on_boot_error(self, error: str) -> None:
        self._title_bar.set_status("ERROR", Colors.RED)
        self._chat_panel.add_system_message(f"⚠ Boot error: {error[:120]}")
        self._notifications.show_notification(
            f"Boot failed: {error[:80]}", "critical", 10000,
        )

    def _on_quick_action(self, command: str) -> None:
        self._chat_panel.add_user_message(command)
        self._bridge.send_command(command)

    def _on_mic_toggle(self, active: bool) -> None:
        if active:
            self._bridge.start_listening()
        else:
            self._bridge.stop_listening()

    def _toggle_mic_shortcut(self) -> None:
        self._voice_control._toggle()

    # ── Overrides ────────────────────────────────────────────────────

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        # Position notification bar in top-right
        self._notifications.setGeometry(
            self.width() - 340, 48, 330, 400,
        )

    def closeEvent(self, event) -> None:
        self._bridge.shutdown()
        event.accept()
