"""
NOVA Command Router
===================
Bridges intent classification → command execution → response.
This is the brain's "decision layer".
"""

from __future__ import annotations

from typing import Tuple

from nova.brain.intent import Intent, IntentClassifier
from nova.brain.llm import LLMClient
from nova.commands.registry import CommandRegistry, CommandResult
from nova.memory.manager import MemoryManager
from nova.utils import logger as log


class Router:
    """
    Accepts raw user input, classifies intent, dispatches to the
    appropriate command handler, and returns the spoken response.
    """

    def __init__(
        self,
        registry: CommandRegistry,
        memory: MemoryManager,
        llm: LLMClient,
    ) -> None:
        self._registry = registry
        self._memory = memory
        self._llm = llm
        self._classifier = IntentClassifier()

    def process(self, user_input: str) -> Tuple[str, bool]:
        """
        Process a user command.

        Returns
        -------
        (response_text, keep_running)
        """
        intent: Intent = self._classifier.classify(user_input)
        log.info(f"[Router] Intent: {intent.name} | entity: {intent.entity!r}")

        # ── Try registered command handler ────────────────────────────────
        handler = self._registry.get_handler(intent.name)
        if handler is not None:
            try:
                result: CommandResult = handler(intent.entity, self._memory)
                return result.response, result.continue_running
            except Exception as exc:
                log.exception(f"[Router] Command handler '{intent.name}' failed: {exc}")
                return f"Sorry, an error occurred while processing that: {exc}", True

        # ── Fallback: LLM conversation ────────────────────────────────────
        if intent.name == "general_conversation":
            context = self._memory.get_context(n=5)
            response = self._llm.chat(user_input, context=context)
            if response is None:
                response = "I'm sorry, I couldn't generate a response right now."
            return response, True

        # ── Unknown intent with no handler (shouldn't happen) ─────────────
        log.warn(f"[Router] No handler for intent '{intent.name}'")
        return f"I recognised the intent '{intent.name}' but don't have a handler for it yet.", True
