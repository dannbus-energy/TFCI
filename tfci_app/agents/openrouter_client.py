"""OpenAI-compatible client for OpenRouter with a hard per-run call budget.

Agents must fail cheap: every call goes through this wrapper, which counts
LLM invocations and refuses to exceed MAX_CALLS_PER_RUN. No agent in this
codebase may call an LLM any other way.
"""
import json, os
from openai import OpenAI

BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = os.environ.get("TFCI_MODEL", "openai/gpt-4o-mini")

class BudgetExceeded(RuntimeError):
    pass

class OpenRouterClient:
    def __init__(self, max_calls: int = 20):
        key = os.environ.get("OPENROUTER_API_KEY")
        if not key:
            raise RuntimeError(
                "OPENROUTER_API_KEY not set. "
                "Run: setx OPENROUTER_API_KEY \u0022sk-or-v1-...\u0022 then open a NEW PowerShell window.")
        self._client = OpenAI(base_url=BASE_URL, api_key=key)
        self._calls = 0
        self.max_calls = max_calls

    @property
    def calls_used(self):
        return self._calls

    def chat(self, messages, model=None, online=False, temperature=0.0,
             json_mode=False):
        """One chat completion. online=True appends :online for web search."""
        if self._calls >= self.max_calls:
            raise BudgetExceeded(
                "LLM call budget (%d) exceeded - refusing to spend more "
                "this run." % self.max_calls)
        m = model or DEFAULT_MODEL
        if online:
            m = m + ":online"
        kwargs = dict(model=m, messages=messages, temperature=temperature)
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        resp = self._client.chat.completions.create(**kwargs)
        self._calls += 1
        return resp.choices[0].message.content
