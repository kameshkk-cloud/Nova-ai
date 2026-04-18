"""
NOVA Command Registry
=====================
Self-registering command system.  Each command module decorates its
handler functions with ``@command(...)``; on import the decorator
auto-registers them with the global ``CommandRegistry``.

Adding a new command is trivial — just write a function and decorate it::

    @command(
        intents=["greet_user", "say_hello"],
        description="Greet the user",
    )
    def greet(arg: str | None, memory: MemoryManager) -> CommandResult:
        return CommandResult(response="Hello!")

The registry is then queried by the ``brain.router`` to dispatch intents.
"""

from __future__ import annotations

import importlib
import pkgutil
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set

from nova.utils import logger as log


# ─── Result container ────────────────────────────────────────────────────────

@dataclass
class CommandResult:
    """Value returned by every command handler."""

    response: str = ""
    """Text that NOVA will speak aloud."""

    data: Dict[str, Any] = field(default_factory=dict)
    """Optional structured payload (for dashboards / plugins)."""

    continue_running: bool = True
    """Set to False to signal NOVA shutdown."""


# ─── Decorator ────────────────────────────────────────────────────────────────

# Temporary holding list populated at import time (before the registry exists).
_pending_registrations: List[dict] = []


def command(
    intents: List[str],
    description: str = "",
    category: str = "general",
) -> Callable:
    """
    Decorator that marks a function as a NOVA command handler.

    Parameters
    ----------
    intents : list[str]
        One or more intent names this handler responds to.
    description : str
        Human-readable help string.
    category : str
        Grouping label for the ``help`` command.
    """
    def decorator(fn: Callable) -> Callable:
        _pending_registrations.append({
            "fn": fn,
            "intents": intents,
            "description": description,
            "category": category,
        })
        return fn
    return decorator


# ─── Registry ────────────────────────────────────────────────────────────────

class CommandRegistry:
    """
    Central store of all registered command handlers.

    Call ``load_builtin_commands()`` once at boot to import every module
    in ``nova.commands``, which triggers the ``@command`` decorators.
    """

    def __init__(self) -> None:
        self._handlers: Dict[str, Callable] = {}
        self._metadata: Dict[str, dict] = {}
        self._categories: Dict[str, List[str]] = {}

    # ── Registration ─────────────────────────────────────────────────────
    def register(
        self,
        fn: Callable,
        intents: List[str],
        description: str = "",
        category: str = "general",
    ) -> None:
        for intent in intents:
            intent_key = intent.lower().strip()
            self._handlers[intent_key] = fn
            self._metadata[intent_key] = {
                "function": fn.__name__,
                "description": description,
                "category": category,
            }
            self._categories.setdefault(category, [])
            if intent_key not in self._categories[category]:
                self._categories[category].append(intent_key)

    def _drain_pending(self) -> None:
        """Move any decorators that fired before the registry existed."""
        global _pending_registrations
        for entry in _pending_registrations:
            self.register(
                entry["fn"],
                entry["intents"],
                entry["description"],
                entry["category"],
            )
        _pending_registrations = []

    # ── Lookup ───────────────────────────────────────────────────────────
    def get_handler(self, intent: str) -> Optional[Callable]:
        return self._handlers.get(intent.lower().strip())

    def has_intent(self, intent: str) -> bool:
        return intent.lower().strip() in self._handlers

    @property
    def intents(self) -> Set[str]:
        return set(self._handlers.keys())

    @property
    def categories(self) -> Dict[str, List[str]]:
        return dict(self._categories)

    # ── Help text generation ─────────────────────────────────────────────
    def help_text(self) -> str:
        """Generate a spoken-friendly list of capabilities by category."""
        lines = []
        for cat, intent_list in sorted(self._categories.items()):
            descriptions = []
            seen: Set[str] = set()
            for intent in intent_list:
                desc = self._metadata[intent]["description"]
                if desc and desc not in seen:
                    descriptions.append(desc)
                    seen.add(desc)
            if descriptions:
                lines.append(f"{cat.title()}: {', '.join(descriptions)}")
        return ". ".join(lines) + "." if lines else "No commands registered."

    # ── Auto-discovery ───────────────────────────────────────────────────
    def load_builtin_commands(self) -> int:
        """
        Import every sub-module in ``nova.commands`` so their ``@command``
        decorators fire, then drain the pending list.

        Returns the number of intents registered.
        """
        import nova.commands as pkg

        for _importer, modname, _ispkg in pkgutil.iter_modules(pkg.__path__):
            if modname == "registry":
                continue  # don't re-import ourselves
            try:
                importlib.import_module(f"nova.commands.{modname}")
            except Exception as exc:
                log.error(f"Failed to load command module '{modname}': {exc!r}")

        self._drain_pending()
        count = len(self._handlers)
        log.info(f"Command registry loaded: {count} intents across {len(self._categories)} categories.")
        return count
