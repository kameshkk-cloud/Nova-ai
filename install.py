#!/usr/bin/env python3
"""
NOVA Dependency Installer
=========================
Run once to install all required packages.

Usage:
    python install.py
"""

import subprocess
import sys

REQUIRED = [
    ("pyttsx3",            "Text-to-Speech engine"),
    ("SpeechRecognition",  "Voice input"),
    ("psutil",             "System monitoring"),
    ("rich",               "Beautiful terminal UI"),
    ("groq",               "Groq LLM API (free tier)"),
    ("openai",             "OpenAI LLM API"),
    ("requests",           "HTTP requests"),
    ("pyautogui",          "Screenshots & automation"),
    ("python-dotenv",      ".env file support"),
]

OPTIONAL = [
    ("pyaudio", "Microphone access (may need special install on Windows)"),
]


def install(package: str, description: str) -> bool:
    print(f"  Installing {package} ({description})...")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", package],
        capture_output=True, text=True,
    )
    if result.returncode == 0:
        print(f"  ✓ {package}")
        return True
    else:
        print(f"  ✗ {package}: {result.stderr.strip()[:120]}")
        return False


def verify(package: str) -> bool:
    """Check if a package can be imported."""
    import_name = package.replace("-", "_").lower()
    # Special cases
    mapping = {"SpeechRecognition": "speech_recognition", "python-dotenv": "dotenv"}
    import_name = mapping.get(package, import_name)
    try:
        __import__(import_name)
        return True
    except ImportError:
        return False


if __name__ == "__main__":
    print("\n╔══════════════════════════════════════════╗")
    print("║  NOVA AI — Dependency Installer v2.0     ║")
    print("╚══════════════════════════════════════════╝\n")

    failed = []
    for pkg, desc in REQUIRED:
        if not install(pkg, desc):
            failed.append(pkg)

    print("\n── Optional packages ──")
    for pkg, desc in OPTIONAL:
        install(pkg, desc)

    # Verification
    print("\n── Verification ──")
    for pkg, _ in REQUIRED:
        status = "✓" if verify(pkg) else "✗ MISSING"
        print(f"  {pkg}: {status}")

    if failed:
        print(f"\n⚠ {len(failed)} package(s) failed: {', '.join(failed)}")
    else:
        print("\n✓ All packages installed successfully!")

    print("\n── Next Steps ──")
    print("  1. (Optional) Create a .env file with your API key:")
    print('     GROQ_API_KEY=your_key_here')
    print("  2. Run NOVA:")
    print("     python main.py\n")

    if sys.platform == "win32":
        print("── PyAudio on Windows ──")
        print("  If mic doesn't work, try:")
        print("    pip install pipwin && pipwin install pyaudio\n")
