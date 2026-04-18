"""
NOVA LLM Client
================
Unified interface to multiple LLM backends: Groq, OpenAI, and Ollama.
Falls back gracefully if none are configured.
"""

from __future__ import annotations

import datetime
import json
from typing import Any, Dict, List, Optional

from nova.brain.prompts import SYSTEM_PROMPT
from nova.config.settings import (
    GROQ_API_KEY, GROQ_MODEL,
    OPENAI_API_KEY, OPENAI_MODEL,
    OLLAMA_HOST, OLLAMA_MODEL,
    LLM_PROVIDER, LLM_MAX_TOKENS, LLM_TEMPERATURE, USER_NAME,
)
from nova.utils import logger as log
from nova.utils.retry import retry


class LLMClient:
    """
    Pluggable LLM client that auto-selects the best available backend.

    Priority: configured provider → fallback providers → rule-based.
    """

    def __init__(self) -> None:
        self._provider: Optional[str] = None
        self._client: Any = None
        self._init_provider()

    def _init_provider(self) -> None:
        """Try to initialise the configured provider, then fallbacks."""
        order = self._provider_order()
        for provider in order:
            if self._try_init(provider):
                self._provider = provider
                log.info(f"LLM backend: {provider}")
                return
        log.warn("No LLM backend available. Using rule-based fallback.")

    def _provider_order(self) -> list:
        """Return providers in priority order, configured one first."""
        primary = LLM_PROVIDER.lower()
        all_providers = ["groq", "openai", "ollama"]
        if primary in all_providers:
            all_providers.remove(primary)
            return [primary] + all_providers
        return all_providers

    def _try_init(self, provider: str) -> bool:
        try:
            if provider == "groq" and GROQ_API_KEY:
                from groq import Groq
                self._client = Groq(api_key=GROQ_API_KEY)
                return True
            elif provider == "openai" and OPENAI_API_KEY:
                from openai import OpenAI
                self._client = OpenAI(api_key=OPENAI_API_KEY)
                return True
            elif provider == "ollama":
                import urllib.request
                req = urllib.request.Request(f"{OLLAMA_HOST}/api/tags", method="GET")
                urllib.request.urlopen(req, timeout=3)
                self._client = "ollama"
                return True
        except ImportError as exc:
            log.debug(f"[LLM] {provider} package not installed: {exc}")
        except Exception as exc:
            log.debug(f"[LLM] {provider} init failed: {exc}")
        return False

    @property
    def available(self) -> bool:
        return self._provider is not None

    @property
    def provider_name(self) -> str:
        return self._provider or "none"

    @retry(max_attempts=2, backoff=1.0, on=(Exception,), reraise=False)
    def chat(
        self,
        user_message: str,
        context: Optional[List[Dict[str, str]]] = None,
    ) -> str:
        """
        Send a message and return the assistant's reply.
        Returns a fallback string if no provider is available.
        """
        if not self.available:
            return self._fallback(user_message)

        now = datetime.datetime.now().strftime("%A, %B %d at %I:%M %p")
        system_msg = SYSTEM_PROMPT.format(datetime=now)

        messages = [{"role": "system", "content": system_msg}]
        if context:
            for turn in context:
                messages.append({"role": "user", "content": turn["user"]})
                messages.append({"role": "assistant", "content": turn["nova"]})
        messages.append({"role": "user", "content": user_message})

        if self._provider == "groq":
            return self._chat_groq(messages)
        elif self._provider == "openai":
            return self._chat_openai(messages)
        elif self._provider == "ollama":
            return self._chat_ollama(messages)

        return self._fallback(user_message)

    # ── Provider-specific implementations ─────────────────────────────────

    def _chat_groq(self, messages: list) -> str:
        resp = self._client.chat.completions.create(
            model=GROQ_MODEL, messages=messages,
            max_tokens=LLM_MAX_TOKENS, temperature=LLM_TEMPERATURE,
        )
        return resp.choices[0].message.content.strip()

    def _chat_openai(self, messages: list) -> str:
        resp = self._client.chat.completions.create(
            model=OPENAI_MODEL, messages=messages,
            max_tokens=LLM_MAX_TOKENS, temperature=LLM_TEMPERATURE,
        )
        return resp.choices[0].message.content.strip()

    def _chat_ollama(self, messages: list) -> str:
        import urllib.request
        payload = json.dumps({
            "model": OLLAMA_MODEL,
            "messages": messages,
            "stream": False,
            "options": {"temperature": LLM_TEMPERATURE},
        }).encode("utf-8")
        req = urllib.request.Request(
            f"{OLLAMA_HOST}/api/chat",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return data.get("message", {}).get("content", "").strip()

    # ── Fallback ─────────────────────────────────────────────────────────

    @staticmethod
    def _fallback(message: str) -> str:
        return (
            f"I understood: '{message}'. I don't have a specific skill for that yet. "
            "Configure an LLM (Groq/OpenAI/Ollama) in settings for smart responses!"
        )
