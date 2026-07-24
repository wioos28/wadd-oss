"""LLM Client - Interface for calling Large Language Models."""

from __future__ import annotations

import json
import os
from typing import Any

import requests


class LLMClient:
    """Client for calling OpenAI-compatible LLM APIs."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.base_url = (base_url or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")).rstrip("/")
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def chat(
        self,
        messages: list[dict[str, str]],
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """Send a chat completion request."""
        url = f"{self.base_url}/chat/completions"

        headers = {
            "Content-Type": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature or self.temperature,
            "max_tokens": max_tokens or self.max_tokens,
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except requests.exceptions.RequestException as e:
            return f"Error calling LLM: {e}"
        except (KeyError, IndexError) as e:
            return f"Error parsing LLM response: {e}"

    def complete(self, prompt: str, **kwargs: Any) -> str:
        """Simple completion using a single prompt."""
        messages = [{"role": "user", "content": prompt}]
        return self.chat(messages, **kwargs)

    def complete_with_system(
        self, system_prompt: str, user_prompt: str, **kwargs: Any
    ) -> str:
        """Completion with system and user messages."""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        return self.chat(messages, **kwargs)

    def is_available(self) -> bool:
        """Check if LLM is configured and available."""
        if not self.api_key:
            return False
        try:
            url = f"{self.base_url}/models"
            headers = {"Authorization": f"Bearer {self.api_key}"}
            response = requests.get(url, headers=headers, timeout=10)
            return response.status_code == 200
        except Exception:
            return False
