"""
NOVA Configuration
==================
All constants, paths, and tunables for the NOVA AI system.
Values can be overridden by environment variables or a `.env` file in the
project root.

Usage in other modules:
    from nova.config.settings import USER_NAME, GROQ_API_KEY
"""

from __future__ import annotations

import os
import pathlib

# ─── .env support ────────────────────────────────────────────────────────────
# python-dotenv is optional — works fine without it.
try:
    from dotenv import load_dotenv  # type: ignore[import]
    _env_path = pathlib.Path(__file__).resolve().parents[2] / ".env"
    load_dotenv(_env_path)
except ImportError:
    pass


def _env(key: str, default: str = "") -> str:
    """Read an environment variable, falling back to *default*."""
    return os.environ.get(key, default)


def _env_int(key: str, default: int) -> int:
    try:
        return int(os.environ.get(key, default))
    except (TypeError, ValueError):
        return default


def _env_float(key: str, default: float) -> float:
    try:
        return float(os.environ.get(key, default))
    except (TypeError, ValueError):
        return default


def _env_bool(key: str, default: bool) -> bool:
    val = os.environ.get(key)
    if val is None:
        return default
    return val.lower() in ("1", "true", "yes")


# ─── USER PROFILE ────────────────────────────────────────────────────────────
USER_NAME: str       = _env("NOVA_USER_NAME", "KK Sir")
ASSISTANT_NAME: str  = _env("NOVA_ASSISTANT_NAME", "NOVA")
WAKE_WORD: str       = _env("NOVA_WAKE_WORD", "hey nova").lower()
ACTIVATE_MODE: str   = "activate nova mode"

# ─── VOICE SETTINGS (JARVIS-TUNED) ──────────────────────────────────────────
# Rate 165 = smooth, deliberate delivery like JARVIS. Not too fast, not slow.
VOICE_RATE: int      = _env_int("NOVA_VOICE_RATE", 165)
VOICE_VOLUME: float  = _env_float("NOVA_VOICE_VOLUME", 1.0)
VOICE_GENDER: str    = _env("NOVA_VOICE_GENDER", "male")   # "male" | "female"

# JARVIS-style voice profiles — NOVA automatically picks the best profile
# based on time-of-day, alert severity, or explicit user request.
# All rates are tuned for smooth, clear delivery without stuttering.
VOICE_PROFILES: dict = {
    "jarvis": {
        "rate": 165,
        "volume": 1.0,
        "description": "JARVIS — smooth, authoritative, everyday voice",
    },
    "calm": {
        "rate": 150,
        "volume": 0.85,
        "description": "Slow and gentle — late-night or relaxed mode",
    },
    "default": {
        "rate": 165,
        "volume": 1.0,
        "description": "Alias for JARVIS profile",
    },
    "energetic": {
        "rate": 180,
        "volume": 1.0,
        "description": "Upbeat morning voice — clear but brisk",
    },
    "alert": {
        "rate": 175,
        "volume": 1.0,
        "description": "Urgent but clear — used for critical alerts",
    },
}

# ─── LLM / AI BACKEND ────────────────────────────────────────────────────────
# Supported providers: "groq", "openai", "ollama"
LLM_PROVIDER: str    = _env("NOVA_LLM_PROVIDER", "groq")

# Groq (free tier, fast inference)
GROQ_API_KEY: str    = _env("GROQ_API_KEY", "")
GROQ_MODEL: str      = _env("GROQ_MODEL", "llama3-8b-8192")

# OpenAI
OPENAI_API_KEY: str  = _env("OPENAI_API_KEY", "")
OPENAI_MODEL: str    = _env("OPENAI_MODEL", "gpt-3.5-turbo")

# Ollama (fully offline)
OLLAMA_HOST: str     = _env("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL: str    = _env("OLLAMA_MODEL", "llama3")

LLM_MAX_TOKENS: int  = _env_int("NOVA_LLM_MAX_TOKENS", 250)
LLM_TEMPERATURE: float = _env_float("NOVA_LLM_TEMPERATURE", 0.7)

# ─── SYSTEM THRESHOLDS ───────────────────────────────────────────────────────
CPU_ALERT_THRESHOLD: int      = _env_int("NOVA_CPU_ALERT", 85)
RAM_ALERT_THRESHOLD: int      = _env_int("NOVA_RAM_ALERT", 85)
BATTERY_LOW_THRESHOLD: int    = _env_int("NOVA_BATTERY_LOW", 20)
BATTERY_CRIT_THRESHOLD: int   = _env_int("NOVA_BATTERY_CRIT", 10)
DISK_ALERT_THRESHOLD: int     = _env_int("NOVA_DISK_ALERT", 90)
TEMP_ALERT_THRESHOLD: int     = _env_int("NOVA_TEMP_ALERT", 80)

# ─── MONITORING ──────────────────────────────────────────────────────────────
MONITOR_INTERVAL_SECONDS: int = _env_int("NOVA_MONITOR_INTERVAL", 30)
ALERT_COOLDOWN_SECONDS: int   = _env_int("NOVA_ALERT_COOLDOWN", 300)  # 5 min

# ─── PATHS ───────────────────────────────────────────────────────────────────
_PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[2]   # NOVA AI/
_NOVA_PKG     = pathlib.Path(__file__).resolve().parents[1]   # NOVA AI/nova/

BASE_DIR: str       = str(_NOVA_PKG)
DATA_DIR: str       = str(_PROJECT_ROOT / "data")

MEMORY_DIR: str     = str(_PROJECT_ROOT / "data" / "memory")
MEMORY_FILE: str    = str(_PROJECT_ROOT / "data" / "memory" / "memory.json")
CONVO_FILE: str     = str(_PROJECT_ROOT / "data" / "memory" / "conversations.json")

LOG_DIR: str        = str(_PROJECT_ROOT / "data" / "logs")
LOG_FILE: str       = str(_PROJECT_ROOT / "data" / "logs" / "nova.log")
ACTIVITY_FILE: str  = str(_PROJECT_ROOT / "data" / "logs" / "activity.json")

PLUGIN_DIR: str     = str(_PROJECT_ROOT / "data" / "plugins")

# ─── LOGGING ─────────────────────────────────────────────────────────────────
LOG_LEVEL: str      = _env("NOVA_LOG_LEVEL", "DEBUG")
LOG_MAX_BYTES: int  = _env_int("NOVA_LOG_MAX_BYTES", 5 * 1024 * 1024)  # 5 MB
LOG_BACKUP_COUNT: int = _env_int("NOVA_LOG_BACKUPS", 3)

# ─── RETRY / RESILIENCE ─────────────────────────────────────────────────────
MAX_RETRIES: int       = _env_int("NOVA_MAX_RETRIES", 3)
RETRY_BACKOFF: float   = _env_float("NOVA_RETRY_BACKOFF", 1.5)

# ─── FILE ORGANIZER CATEGORIES ───────────────────────────────────────────────
FILE_CATEGORIES: dict = {
    "Images":      [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".heic"],
    "Videos":      [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv"],
    "Documents":   [".pdf", ".docx", ".doc", ".txt", ".xlsx", ".pptx", ".csv", ".odt"],
    "Music":       [".mp3", ".wav", ".flac", ".aac", ".ogg"],
    "Archives":    [".zip", ".rar", ".7z", ".tar", ".gz"],
    "Code":        [".py", ".js", ".html", ".css", ".java", ".cpp", ".c", ".ts", ".json"],
    "Executables": [".exe", ".msi", ".bat", ".sh", ".apk"],
}
