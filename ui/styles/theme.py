"""
NOVA GUI — Theme & Stylesheet System
======================================
Centralized color palette, fonts, and QSS stylesheets for the
futuristic Jarvis-style interface.

All visual constants live here so components never hardcode colors.
"""

from __future__ import annotations


# ─── COLOR PALETTE ───────────────────────────────────────────────────────────

class Colors:
    """Named color constants for the NOVA UI."""

    # Backgrounds
    BG_DARKEST      = "#060a12"
    BG_DARK         = "#0a0e17"
    BG_PANEL        = "#0d1321"
    BG_PANEL_LIGHT  = "#111827"
    BG_HOVER        = "#162036"
    BG_INPUT        = "#0f1629"

    # Primary accent (cyan)
    CYAN            = "#00d4ff"
    CYAN_DIM        = "#0088cc"
    CYAN_GLOW       = "#00d4ff40"
    CYAN_SUBTLE     = "#00d4ff18"

    # Secondary accent (purple)
    PURPLE          = "#6c63ff"
    PURPLE_DIM      = "#4a42cc"
    PURPLE_GLOW     = "#6c63ff40"

    # Status colors
    GREEN           = "#00e676"
    GREEN_DIM       = "#00a854"
    YELLOW          = "#ffab00"
    YELLOW_DIM      = "#cc8800"
    RED             = "#ff3366"
    RED_DIM         = "#cc2952"
    ORANGE          = "#ff6d00"

    # Text
    TEXT_PRIMARY    = "#e0e6ed"
    TEXT_SECONDARY  = "#7a8ba5"
    TEXT_MUTED      = "#4a5568"
    TEXT_BRIGHT     = "#ffffff"

    # Borders
    BORDER          = "#1a2540"
    BORDER_GLOW     = "#00d4ff30"
    BORDER_ACTIVE   = "#00d4ff80"

    # Special
    TRANSPARENT     = "transparent"
    SHADOW          = "#00000080"


# ─── FONT CONFIGURATION ─────────────────────────────────────────────────────

class Fonts:
    """Font families and sizes."""

    FAMILY_PRIMARY  = "Segoe UI, Inter, -apple-system, sans-serif"
    FAMILY_MONO     = "JetBrains Mono, Cascadia Code, Consolas, monospace"

    SIZE_XS         = 10
    SIZE_SM         = 11
    SIZE_MD         = 13
    SIZE_LG         = 16
    SIZE_XL         = 20
    SIZE_XXL        = 28
    SIZE_TITLE      = 14


# ─── DIMENSIONS ──────────────────────────────────────────────────────────────

class Dimensions:
    """Common size constants."""

    BORDER_RADIUS       = 12
    BORDER_RADIUS_SM    = 8
    BORDER_RADIUS_LG    = 16
    BORDER_RADIUS_PILL  = 20

    PADDING             = 16
    PADDING_SM          = 8
    PADDING_LG          = 24

    SCROLLBAR_WIDTH     = 6
    ICON_SIZE           = 20

    MIN_WINDOW_W        = 1200
    MIN_WINDOW_H        = 750


# ─── GLOBAL STYLESHEET ──────────────────────────────────────────────────────

def global_stylesheet() -> str:
    """Return the master QSS stylesheet for the entire application."""
    return f"""
    /* ── Base ──────────────────────────────────────────────────────── */
    QWidget {{
        background-color: {Colors.BG_DARK};
        color: {Colors.TEXT_PRIMARY};
        font-family: {Fonts.FAMILY_PRIMARY};
        font-size: {Fonts.SIZE_MD}px;
    }}

    QMainWindow {{
        background-color: {Colors.BG_DARKEST};
    }}

    /* ── Scrollbar ─────────────────────────────────────────────────── */
    QScrollBar:vertical {{
        background: {Colors.BG_DARKEST};
        width: {Dimensions.SCROLLBAR_WIDTH}px;
        border: none;
        border-radius: {Dimensions.SCROLLBAR_WIDTH // 2}px;
        margin: 4px 0;
    }}
    QScrollBar::handle:vertical {{
        background: {Colors.CYAN_DIM};
        border-radius: {Dimensions.SCROLLBAR_WIDTH // 2}px;
        min-height: 30px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {Colors.CYAN};
    }}
    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical {{
        height: 0;
    }}
    QScrollBar::add-page:vertical,
    QScrollBar::sub-page:vertical {{
        background: none;
    }}
    QScrollBar:horizontal {{
        height: 0px;
    }}

    /* ── Labels ─────────────────────────────────────────────────────── */
    QLabel {{
        background: transparent;
        border: none;
        padding: 0;
    }}

    /* ── LineEdit ───────────────────────────────────────────────────── */
    QLineEdit {{
        background-color: {Colors.BG_INPUT};
        color: {Colors.TEXT_PRIMARY};
        border: 1px solid {Colors.BORDER};
        border-radius: {Dimensions.BORDER_RADIUS_SM}px;
        padding: 10px 14px;
        font-size: {Fonts.SIZE_MD}px;
        selection-background-color: {Colors.CYAN_DIM};
    }}
    QLineEdit:focus {{
        border-color: {Colors.CYAN};
        background-color: {Colors.BG_PANEL};
    }}

    /* ── PushButton ────────────────────────────────────────────────── */
    QPushButton {{
        background-color: {Colors.BG_PANEL_LIGHT};
        color: {Colors.TEXT_PRIMARY};
        border: 1px solid {Colors.BORDER};
        border-radius: {Dimensions.BORDER_RADIUS_SM}px;
        padding: 8px 18px;
        font-size: {Fonts.SIZE_MD}px;
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
    }}

    /* ── ComboBox ───────────────────────────────────────────────────── */
    QComboBox {{
        background-color: {Colors.BG_INPUT};
        color: {Colors.TEXT_PRIMARY};
        border: 1px solid {Colors.BORDER};
        border-radius: {Dimensions.BORDER_RADIUS_SM}px;
        padding: 8px 12px;
        font-size: {Fonts.SIZE_MD}px;
    }}
    QComboBox:hover {{
        border-color: {Colors.CYAN_DIM};
    }}
    QComboBox::drop-down {{
        border: none;
        width: 24px;
    }}
    QComboBox::down-arrow {{
        image: none;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 5px solid {Colors.CYAN};
        margin-right: 8px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {Colors.BG_PANEL};
        color: {Colors.TEXT_PRIMARY};
        border: 1px solid {Colors.BORDER};
        selection-background-color: {Colors.BG_HOVER};
        selection-color: {Colors.CYAN};
        outline: none;
    }}

    /* ── ToolTip ────────────────────────────────────────────────────── */
    QToolTip {{
        background-color: {Colors.BG_PANEL};
        color: {Colors.CYAN};
        border: 1px solid {Colors.CYAN_DIM};
        border-radius: 6px;
        padding: 6px 10px;
        font-size: {Fonts.SIZE_SM}px;
    }}

    /* ── GroupBox ───────────────────────────────────────────────────── */
    QGroupBox {{
        background-color: {Colors.BG_PANEL};
        border: 1px solid {Colors.BORDER};
        border-radius: {Dimensions.BORDER_RADIUS}px;
        margin-top: 12px;
        padding-top: 20px;
        font-size: {Fonts.SIZE_SM}px;
        color: {Colors.TEXT_SECONDARY};
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 16px;
        padding: 0 6px;
        color: {Colors.CYAN};
        font-weight: bold;
    }}
    """


# ─── COMPONENT STYLE HELPERS ────────────────────────────────────────────────

def panel_style(glow: bool = False) -> str:
    """Glass-like panel with optional border glow."""
    border = Colors.BORDER_GLOW if glow else Colors.BORDER
    return f"""
        background-color: {Colors.BG_PANEL};
        border: 1px solid {border};
        border-radius: {Dimensions.BORDER_RADIUS}px;
    """


def accent_button_style() -> str:
    """Bright cyan call-to-action button."""
    return f"""
        QPushButton {{
            background-color: {Colors.CYAN_DIM};
            color: {Colors.TEXT_BRIGHT};
            border: none;
            border-radius: {Dimensions.BORDER_RADIUS_SM}px;
            padding: 10px 22px;
            font-weight: bold;
            font-size: {Fonts.SIZE_MD}px;
        }}
        QPushButton:hover {{
            background-color: {Colors.CYAN};
        }}
        QPushButton:pressed {{
            background-color: {Colors.PURPLE};
        }}
    """


def icon_button_style() -> str:
    """Small square icon button."""
    return f"""
        QPushButton {{
            background-color: {Colors.BG_PANEL_LIGHT};
            border: 1px solid {Colors.BORDER};
            border-radius: {Dimensions.BORDER_RADIUS_SM}px;
            padding: 10px;
            min-width: 40px;
            min-height: 40px;
            font-size: 18px;
        }}
        QPushButton:hover {{
            background-color: {Colors.BG_HOVER};
            border-color: {Colors.CYAN_DIM};
        }}
    """


def section_title_style() -> str:
    """Style for section headers."""
    return f"""
        color: {Colors.CYAN};
        font-size: {Fonts.SIZE_TITLE}px;
        font-weight: bold;
        padding: 4px 0;
        background: transparent;
        border: none;
    """


def muted_label_style() -> str:
    """Style for secondary/muted text labels."""
    return f"""
        color: {Colors.TEXT_SECONDARY};
        font-size: {Fonts.SIZE_SM}px;
        background: transparent;
        border: none;
    """


def status_dot_style(color: str) -> str:
    """Colored dot indicator."""
    return f"""
        background-color: {color};
        border-radius: 5px;
        min-width: 10px;
        max-width: 10px;
        min-height: 10px;
        max-height: 10px;
        border: none;
    """
