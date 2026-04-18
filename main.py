#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║         NOVA AI ASSISTANT — Main Entry Point                 ║
║         Neural Operative Virtual Assistant v2.0              ║
╚══════════════════════════════════════════════════════════════╝

Usage:
    python main.py

NOVA will boot all subsystems, greet you, and enter the
interactive loop.  If no microphone is available, keyboard
mode is used automatically.
"""

import sys
import os

# ─── Force UTF-8 on Windows ─────────────────────────────────────────────────
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# ─── Ensure project root is importable ───────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def main() -> None:
    from nova.core.orchestrator import Orchestrator

    nova = Orchestrator()
    try:
        nova.boot()
        nova.run()
    except KeyboardInterrupt:
        print("\n[NOVA] Force quit.")
    except SystemExit:
        pass
    except Exception as exc:
        print(f"\n[NOVA] Fatal error: {exc}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
