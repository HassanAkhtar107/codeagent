"""
llm_client.py
Wraps the DeepSeek API (OpenAI-compatible) with:
  - Configurable model name
  - Disk-based response cache (keyed by SHA-256 of prompt)
  - Retry logic with exponential backoff
  - Stop event support (for GUI "Stop" button)
  - Returns (content: str, usage: dict)
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time
import threading
from pathlib import Path
from typing import Any

try:
    from openai import OpenAI, APIError, APITimeoutError, RateLimitError
except ImportError:
    raise ImportError("openai package not installed. Run: pip install openai")


# ---------------------------------------------------------------------------
# Constants (override via environment or pass to constructor)
# ---------------------------------------------------------------------------
DEFAULT_MODEL = "deepseek-chat"          # DeepSeek V3; update if V4-pro becomes available
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEFAULT_MAX_TOKENS = 4096
DEFAULT_TEMPERATURE = 0.2
MAX_RETRIES = 3
RETRY_BASE_DELAY = 2.0                   # seconds; doubles each retry


class LLMClient:
    """
    OpenAI-compatible client targeting the DeepSeek API.

    Parameters
    ----------
    api_key : str
        DeepSeek API key.
    model : str
        Model name (default: deepseek-chat / deepseek-v3).
    cache_dir : Path | str | None
        Directory for prompt-response cache. None = no cache.
    stop_event : threading.Event | None
        If set, long-running calls are aborted.
    log_callback : callable | None
        Called with (str) log messages.
    """

    def __init__(
        self,
        api_key: str,
        model: str = DEFAULT_MODEL,
        cache_dir: Path | str | None = None,
        stop_event: threading.Event | None = None,
        log_callback=None,
    ) -> None:
        self.model = model
        self.cache_dir = Path(cache_dir) if cache_dir else None
        self.stop_event = stop_event
        self._log = log_callback or (lambda msg: None)

        self._client = OpenAI(
            api_key=api_key,
            base_url=DEEPSEEK_BASE_URL,
            timeout=120.0,
        )

        if self.cache_dir:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def chat(
        self,
        messages: list[dict[str, str]],
        max_tokens: int = DEFAULT_MAX_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE,
        use_cache: bool = True,
    ) -> tuple[str, dict[str, int]]:
        """
        Send a chat completion request.

        Returns
        -------
        (content, usage)
            content : str – the assistant reply text
            usage   : dict – {"prompt_tokens": int, "completion_tokens": int, "total_tokens": int}
        """
        cache_key = self._make_cache_key(messages, max_tokens, temperature)

        # --- Cache hit ---
        if use_cache and self.cache_dir:
            cached = self._cache_get(cache_key)
            if cached:
                self._log("[LLM] Cache hit – skipping API call.")
                return cached["content"], cached["usage"]

        # --- API call with retries ---
        last_error: Exception | None = None
        for attempt in range(1, MAX_RETRIES + 1):
            if self.stop_event and self.stop_event.is_set():
                raise RuntimeError("Generation stopped by user.")

            try:
                self._log(f"[LLM] Calling {self.model} (attempt {attempt}/{MAX_RETRIES}) …")
                response = self._client.chat.completions.create(
                    model=self.model,
                    messages=messages,  # type: ignore[arg-type]
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
                content = response.choices[0].message.content or ""
                usage_obj = response.usage
                usage = {
                    "prompt_tokens": usage_obj.prompt_tokens if usage_obj else 0,
                    "completion_tokens": usage_obj.completion_tokens if usage_obj else 0,
                    "total_tokens": usage_obj.total_tokens if usage_obj else 0,
                }

                # Store in cache
                if use_cache and self.cache_dir:
                    self._cache_set(cache_key, content, usage)

                return content, usage

            except RateLimitError as e:
                last_error = e
                delay = RETRY_BASE_DELAY * (2 ** (attempt - 1))
                self._log(f"[LLM] Rate limited. Retrying in {delay:.0f}s …")
                self._interruptible_sleep(delay)

            except APITimeoutError as e:
                last_error = e
                delay = RETRY_BASE_DELAY * attempt
                self._log(f"[LLM] Timeout. Retrying in {delay:.0f}s …")
                self._interruptible_sleep(delay)

            except APIError as e:
                last_error = e
                self._log(f"[LLM] API error: {e}")
                if "invalid_api_key" in str(e).lower() or "authentication" in str(e).lower():
                    raise ValueError(f"Invalid DeepSeek API key: {e}") from e
                if attempt < MAX_RETRIES:
                    self._interruptible_sleep(RETRY_BASE_DELAY * attempt)
                else:
                    raise

        raise RuntimeError(f"LLM call failed after {MAX_RETRIES} attempts: {last_error}") from last_error

    def chat_single(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE,
        use_cache: bool = True,
    ) -> tuple[str, dict[str, int]]:
        """Convenience wrapper for a simple system + user message."""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        return self.chat(messages, max_tokens=max_tokens, temperature=temperature, use_cache=use_cache)

    # ------------------------------------------------------------------
    # Cache helpers
    # ------------------------------------------------------------------

    def _make_cache_key(
        self,
        messages: list[dict],
        max_tokens: int,
        temperature: float,
    ) -> str:
        payload = json.dumps(
            {"model": self.model, "messages": messages, "max_tokens": max_tokens, "temperature": temperature},
            sort_keys=True,
        )
        return hashlib.sha256(payload.encode()).hexdigest()

    def _cache_path(self, key: str) -> Path:
        assert self.cache_dir is not None
        return self.cache_dir / f"{key}.json"

    def _cache_get(self, key: str) -> dict | None:
        p = self._cache_path(key)
        if p.exists():
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                return None
        return None

    def _cache_set(self, key: str, content: str, usage: dict) -> None:
        p = self._cache_path(key)
        p.write_text(
            json.dumps({"content": content, "usage": usage}, ensure_ascii=False),
            encoding="utf-8",
        )

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    def _interruptible_sleep(self, seconds: float) -> None:
        """Sleep in small increments so the stop_event can interrupt."""
        end = time.monotonic() + seconds
        while time.monotonic() < end:
            if self.stop_event and self.stop_event.is_set():
                raise RuntimeError("Generation stopped by user.")
            time.sleep(0.25)


# ---------------------------------------------------------------------------
# Mock client (used in tests to avoid API spend)
# ---------------------------------------------------------------------------

class MockLLMClient:
    """
    Drop-in replacement for LLMClient that returns deterministic
    hard-coded responses without any API calls.
    """

    def __init__(self, *args, **kwargs) -> None:
        self.model = kwargs.get("model", DEFAULT_MODEL)
        self._log = kwargs.get("log_callback") or (lambda msg: None)
        self.stop_event: threading.Event | None = kwargs.get("stop_event")
        self._call_count = 0

    def chat(self, messages, max_tokens=4096, temperature=0.2, use_cache=True):
        self._call_count += 1
        user_msg = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
        content = self._generate_mock_response(user_msg)
        usage = {"prompt_tokens": 100, "completion_tokens": 200, "total_tokens": 300}
        return content, usage

    def chat_single(self, system_prompt, user_prompt, max_tokens=4096, temperature=0.2, use_cache=True):
        return self.chat(
            [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
        )

    def _generate_mock_response(self, user_msg: str) -> str:
        """Return appropriate mock JSON or code based on the user message."""
        user_lower = user_msg.lower()

        if "project plan" in user_lower or "folder structure" in user_lower or "list of files" in user_lower:
            return json.dumps(
                {
                    "project_name": "SpaceFractions",
                    "description": "Educational fraction game for 6th graders (mock plan)",
                    "folder_structure": ["src/", "tests/", "data/"],
                    "files": [
                        {
                            "path": "main.py",
                            "purpose": "Entry point – launches the Tkinter GUI",
                            "depends_on": ["src/game.py", "src/ui.py"],
                        },
                        {
                            "path": "src/__init__.py",
                            "purpose": "Package init",
                            "depends_on": [],
                        },
                        {
                            "path": "src/models.py",
                            "purpose": "Game, Question, User, Admin data classes",
                            "depends_on": [],
                        },
                        {
                            "path": "src/game.py",
                            "purpose": "Core game logic and state machine",
                            "depends_on": ["src/models.py"],
                        },
                        {
                            "path": "src/ui.py",
                            "purpose": "Tkinter main window and screens",
                            "depends_on": ["src/game.py", "src/models.py"],
                        },
                        {
                            "path": "src/question_bank.py",
                            "purpose": "Load/save questions from JSON file",
                            "depends_on": ["src/models.py"],
                        },
                        {
                            "path": "data/questions.json",
                            "purpose": "Default fraction questions dataset",
                            "depends_on": [],
                        },
                        {
                            "path": "tests/test_game.py",
                            "purpose": "Unit tests for scoring and state transitions",
                            "depends_on": ["src/game.py", "src/models.py"],
                        },
                        {
                            "path": "requirements.txt",
                            "purpose": "Python dependencies",
                            "depends_on": [],
                        },
                        {
                            "path": "README.md",
                            "purpose": "Setup and run instructions",
                            "depends_on": [],
                        },
                    ],
                },
                indent=2,
            )

        if "generate" in user_lower and "requirements.txt" in user_lower:
            return "# No external dependencies needed\ntk\n"

        if "generate" in user_lower and "readme" in user_lower:
            return "# Space Fractions\nMock README.\n## Run\n```python main.py```\n"

        if "generate" in user_lower and "questions.json" in user_lower:
            return json.dumps(
                [
                    {"id": 1, "text": "What is 1/2 + 1/4?", "options": ["3/4", "1/2", "2/4", "1/3"], "answer": "3/4"},
                    {"id": 2, "text": "What is 2/3 - 1/3?", "options": ["1/3", "1", "2/3", "0"], "answer": "1/3"},
                ],
                indent=2,
            )

        # Generic Python file mock
        return (
            '"""Mock generated module."""\n\n'
            "def placeholder():\n"
            '    """Placeholder function."""\n'
            "    pass\n"
        )
