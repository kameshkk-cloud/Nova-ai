"""
NOVA Plugin Loader
==================
Discovers and loads Python plugin files from ``data/plugins/``.

Each plugin is a ``.py`` file that defines a ``register(registry)`` function.
The function receives the CommandRegistry and can add new commands.

Example plugin (``data/plugins/joke.py``)::

    from nova.commands.registry import command, CommandResult

    @command(intents=["tell_joke"], description="Tell a joke", category="fun")
    def cmd_joke(arg, memory):
        return CommandResult(response="Why do programmers prefer dark mode? Because light attracts bugs!")

    def register(registry):
        pass  # The @command decorator handles registration automatically
"""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path

from nova.config.settings import PLUGIN_DIR
from nova.utils import logger as log


def load_plugins() -> int:
    """
    Scan the plugin directory and import every ``.py`` file found.
    Each file's ``@command`` decorators will auto-register with the
    pending list (drained later by the registry).

    Returns the number of plugin files successfully loaded.
    """
    plugin_path = Path(PLUGIN_DIR)
    if not plugin_path.is_dir():
        os.makedirs(plugin_path, exist_ok=True)
        log.debug(f"Created plugin directory: {plugin_path}")
        return 0

    loaded = 0
    for py_file in sorted(plugin_path.glob("*.py")):
        if py_file.name.startswith("_"):
            continue
        try:
            spec = importlib.util.spec_from_file_location(
                f"nova_plugin_{py_file.stem}", str(py_file)
            )
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                # Call register() if it exists
                if hasattr(module, "register"):
                    module.register(None)  # registry passed later during drain
                loaded += 1
                log.info(f"Plugin loaded: {py_file.name}")
        except Exception as exc:
            log.error(f"Plugin '{py_file.name}' failed to load: {exc}")

    if loaded:
        log.info(f"Loaded {loaded} plugin(s) from {plugin_path}")
    return loaded
