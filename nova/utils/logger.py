"""
NOVA Structured Logger
======================
Provides a singleton logger that writes to both a rotating log file and
coloured terminal output (via *rich* if available).

Usage anywhere in the project::

    from nova.utils import logger as log
    log.info("System ready")
    log.error("Something broke", exc_info=True)
    log.nova_say("NOVA", "Hello, KK Sir!")
"""

from __future__ import annotations

import logging
import logging.handlers
import os
import sys
from typing import Optional

from nova.config.settings import (
    LOG_FILE,
    LOG_LEVEL,
    LOG_MAX_BYTES,
    LOG_BACKUP_COUNT,
)

# ─── Ensure log directory exists ─────────────────────────────────────────────
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

# ─── Rich console (optional, graceful fallback) ─────────────────────────────
_rich_available = False
console: Optional[object] = None

try:
    from rich.console import Console
    from rich.logging import RichHandler

    _rich_available = True
    console = Console()
except ImportError:
    pass


# ─── Logger factory ─────────────────────────────────────────────────────────

def _build_logger(name: str = "NOVA") -> logging.Logger:
    """Create and configure the singleton NOVA logger."""
    logger = logging.getLogger(name)

    # Prevent duplicate handlers on reimport
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.DEBUG))

    # ── Rotating file handler (always captures everything) ────────────────
    file_handler = logging.handlers.RotatingFileHandler(
        LOG_FILE,
        maxBytes=LOG_MAX_BYTES,
        backupCount=LOG_BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(
        "[%(asctime)s] [%(levelname)-7s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    ))
    logger.addHandler(file_handler)

    # ── Console handler ──────────────────────────────────────────────────
    if _rich_available:
        console_handler = RichHandler(
            rich_tracebacks=True,
            show_path=False,
            markup=True,
        )
        console_handler.setLevel(logging.INFO)
    else:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter(
            "[%(levelname)s] %(message)s"
        ))
    logger.addHandler(console_handler)

    return logger


# ─── Singleton ───────────────────────────────────────────────────────────────
_logger = _build_logger("NOVA")


# ─── Public convenience API ──────────────────────────────────────────────────

def info(msg: str, *args, **kwargs) -> None:
    _logger.info(msg, *args, **kwargs)

def warn(msg: str, *args, **kwargs) -> None:
    _logger.warning(msg, *args, **kwargs)

def error(msg: str, *args, **kwargs) -> None:
    _logger.error(msg, *args, **kwargs)

def debug(msg: str, *args, **kwargs) -> None:
    _logger.debug(msg, *args, **kwargs)

def critical(msg: str, *args, **kwargs) -> None:
    _logger.critical(msg, *args, **kwargs)

def exception(msg: str, *args, **kwargs) -> None:
    """Log an error together with the current exception traceback."""
    _logger.exception(msg, *args, **kwargs)


def nova_say(label: str, text: str) -> None:
    """Pretty-print NOVA's spoken output to the terminal."""
    if _rich_available and console is not None:
        console.print(f"[bold cyan]⬡ {label}:[/bold cyan] {text}")  # type: ignore[union-attr]
    else:
        print(f"\n⬡ {label}: {text}")


def get_logger(name: str = "NOVA") -> logging.Logger:
    """Return a child logger (useful inside modules that want their own name)."""
    return _logger.getChild(name)
