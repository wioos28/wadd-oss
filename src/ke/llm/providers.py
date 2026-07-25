"""LLM Providers - Multi-provider support for language models."""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from typing import AsyncGenerator, Any
from dataclasses import dataclass


@dataclass
class LLMResponse:
    """Response from LLM provider."""
    content: str
    model: str
    usage: dict[str, int] | None = None
    finish_reason: str | None = None
    metadata: dict[str, Any] | None = None


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    def __init__(self, api_key: str | None = None, **kwargs):
        self.api_key = api_key
        self.config = kwargs

    @abstractmethod
    def chat(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs,
    ) -> LLMResponse:
        """Send chat completion request."""
        ...

    @abstractmethod
    def stream_chat(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        """Stream chat completion response."""
        ...

    @abstractmethod
    def complete(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs,
    ) -> LLMResponse:
        """Complete a prompt."""
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is available."""
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name."""
        ...


class OpenAIProvider(LLMProvider):
    """OpenAI API provider (GPT-4, GPT-3.5, etc.)."""

    def __init__(self, api_key: str | None = None, **kwargs):
        super().__init__(api_key or os.getenv("OPENAI_API_KEY"), **kwargs)
        self.base_url = kwargs.get("base_url", "https://api.openai.com/v1")
        self.model = kwargs.get("model", "gpt-3.5-turbo")

    @property
    def name(self) -> str:
        return "openai"

    def chat(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs,
    ) -> LLMResponse:
        import requests

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        data = {
            "model": kwargs.get("model", self.model),
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=data,
            timeout=60,
        )
        response.raise_for_status()

        result = response.json()
        choice = result["choices"][0]

        return LLMResponse(
            content=choice["message"]["content"],
            model=result["model"],
            usage=result.get("usage"),
            finish_reason=choice.get("finish_reason"),
        )

    async def stream_chat(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        import requests

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        data = {
            "model": kwargs.get("model", self.model),
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }

        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=data,
            stream=True,
            timeout=60,
        )
        response.raise_for_status()

        for line in response.iter_lines():
            if line:
                line = line.decode("utf-8")
                if line.startswith("data: "):
                    line = line[6:]
                    if line.strip() == "[DONE]":
                        break
                    try:
                        import json
                        chunk = json.loads(line)
                        delta = chunk["choices"][0].get("delta", {})
                        if "content" in delta:
                            yield delta["content"]
                    except Exception:
                        continue

    def complete(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs,
    ) -> LLMResponse:
        messages = [{"role": "user", "content": prompt}]
        return self.chat(messages, temperature, max_tokens, **kwargs)

    def is_available(self) -> bool:
        return self.api_key is not None


class AnthropicProvider(LLMProvider):
    """Anthropic API provider (Claude)."""

    def __init__(self, api_key: str | None = None, **kwargs):
        super().__init__(api_key or os.getenv("ANTHROPIC_API_KEY"), **kwargs)
        self.model = kwargs.get("model", "claude-3-haiku-20240307")

    @property
    def name(self) -> str:
        return "anthropic"

    def chat(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs,
    ) -> LLMResponse:
        import requests

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }

        # Extract system message
        system = ""
        user_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system = msg["content"]
            else:
                user_messages.append(msg)

        data = {
            "model": kwargs.get("model", self.model),
            "messages": user_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        if system:
            data["system"] = system

        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=data,
            timeout=60,
        )
        response.raise_for_status()

        result = response.json()
        content = result["content"][0]["text"]

        return LLMResponse(
            content=content,
            model=result["model"],
            usage=result.get("usage"),
            finish_reason=result.get("stop_reason"),
        )

    async def stream_chat(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        import requests

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }

        system = ""
        user_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system = msg["content"]
            else:
                user_messages.append(msg)

        data = {
            "model": kwargs.get("model", self.model),
            "messages": user_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": True,
        }

        if system:
            data["system"] = system

        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=data,
            stream=True,
            timeout=60,
        )
        response.raise_for_status()

        for line in response.iter_lines():
            if line:
                line = line.decode("utf-8")
                if line.startswith("data: "):
                    try:
                        import json
                        event = json.loads(line[6:])
                        if event.get("type") == "content_block_delta":
                            yield event["delta"].get("text", "")
                    except Exception:
                        continue

    def complete(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs,
    ) -> LLMResponse:
        messages = [{"role": "user", "content": prompt}]
        return self.chat(messages, temperature, max_tokens, **kwargs)

    def is_available(self) -> bool:
        return self.api_key is not None


class GeminiProvider(LLMProvider):
    """Google Gemini API provider."""

    def __init__(self, api_key: str | None = None, **kwargs):
        super().__init__(api_key or os.getenv("GOOGLE_API_KEY"), **kwargs)
        self.model = kwargs.get("model", "gemini-pro")

    @property
    def name(self) -> str:
        return "gemini"

    def chat(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs,
    ) -> LLMResponse:
        import requests

        # Build prompt from messages
        prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"

        data = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            },
        }

        response = requests.post(url, json=data, timeout=60)
        response.raise_for_status()

        result = response.json()
        content = result["candidates"][0]["content"]["parts"][0]["text"]

        return LLMResponse(
            content=content,
            model=self.model,
        )

    async def stream_chat(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        import requests

        prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:streamGenerateContent?key={self.api_key}"

        data = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            },
        }

        response = requests.post(url, json=data, stream=True, timeout=60)
        response.raise_for_status()

        for line in response.iter_lines():
            if line:
                try:
                    import json
                    chunk = json.loads(line.decode("utf-8"))
                    content = chunk["candidates"][0]["content"]["parts"][0]["text"]
                    yield content
                except Exception:
                    continue

    def complete(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs,
    ) -> LLMResponse:
        messages = [{"role": "user", "content": prompt}]
        return self.chat(messages, temperature, max_tokens, **kwargs)

    def is_available(self) -> bool:
        return self.api_key is not None


class OllamaProvider(LLMProvider):
    """Ollama local model provider."""

    def __init__(self, api_key: str | None = None, **kwargs):
        super().__init__(api_key, **kwargs)
        self.base_url = kwargs.get("base_url", "http://localhost:11434")
        self.model = kwargs.get("model", "llama2")

    @property
    def name(self) -> str:
        return "ollama"

    def chat(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs,
    ) -> LLMResponse:
        import requests

        data = {
            "model": kwargs.get("model", self.model),
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        response = requests.post(
            f"{self.base_url}/api/chat",
            json=data,
            timeout=120,
        )
        response.raise_for_status()

        result = response.json()
        content = result["message"]["content"]

        return LLMResponse(
            content=content,
            model=result.get("model", self.model),
        )

    async def stream_chat(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        import requests
        import json

        data = {
            "model": kwargs.get("model", self.model),
            "messages": messages,
            "stream": True,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        response = requests.post(
            f"{self.base_url}/api/chat",
            json=data,
            stream=True,
            timeout=120,
        )
        response.raise_for_status()

        for line in response.iter_lines():
            if line:
                try:
                    chunk = json.loads(line.decode("utf-8"))
                    if "message" in chunk:
                        yield chunk["message"].get("content", "")
                except Exception:
                    continue

    def complete(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs,
    ) -> LLMResponse:
        messages = [{"role": "user", "content": prompt}]
        return self.chat(messages, temperature, max_tokens, **kwargs)

    def is_available(self) -> bool:
        try:
            import requests
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False


class VLLMProvider(LLMProvider):
    """vLLM local model provider (OpenAI-compatible API)."""

    def __init__(self, api_key: str | None = None, **kwargs):
        super().__init__(api_key, **kwargs)
        self.base_url = kwargs.get("base_url", "http://localhost:8000")
        self.model = kwargs.get("model", "default")

    @property
    def name(self) -> str:
        return "vllm"

    def chat(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs,
    ) -> LLMResponse:
        import requests

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        data = {
            "model": kwargs.get("model", self.model),
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        response = requests.post(
            f"{self.base_url}/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=120,
        )
        response.raise_for_status()

        result = response.json()
        choice = result["choices"][0]

        return LLMResponse(
            content=choice["message"]["content"],
            model=result.get("model", self.model),
            usage=result.get("usage"),
            finish_reason=choice.get("finish_reason"),
        )

    async def stream_chat(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        import requests
        import json

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        data = {
            "model": kwargs.get("model", self.model),
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }

        response = requests.post(
            f"{self.base_url}/v1/chat/completions",
            headers=headers,
            json=data,
            stream=True,
            timeout=120,
        )
        response.raise_for_status()

        for line in response.iter_lines():
            if line:
                line = line.decode("utf-8")
                if line.startswith("data: "):
                    line = line[6:]
                    if line.strip() == "[DONE]":
                        break
                    try:
                        chunk = json.loads(line)
                        delta = chunk["choices"][0].get("delta", {})
                        if "content" in delta:
                            yield delta["content"]
                    except Exception:
                        continue

    def complete(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs,
    ) -> LLMResponse:
        messages = [{"role": "user", "content": prompt}]
        return self.chat(messages, temperature, max_tokens, **kwargs)

    def is_available(self) -> bool:
        try:
            import requests
            response = requests.get(f"{self.base_url}/v1/models", timeout=5)
            return response.status_code == 200
        except Exception:
            return False


class LocalProvider(LLMProvider):
    """Local model provider using transformers."""

    def __init__(self, api_key: str | None = None, **kwargs):
        super().__init__(api_key, **kwargs)
        self.model_name = kwargs.get("model", "microsoft/DialoGPT-medium")
        self._model = None
        self._tokenizer = None

    @property
    def name(self) -> str:
        return "local"

    def _load_model(self):
        if self._model is None:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            import torch

            self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self._model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto" if torch.cuda.is_available() else None,
            )

    def chat(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs,
    ) -> LLMResponse:
        self._load_model()

        # Build prompt from messages
        prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
        prompt += "\nassistant:"

        inputs = self._tokenizer.encode(prompt, return_tensors="pt")

        import torch
        with torch.no_grad():
            outputs = self._model.generate(
                inputs,
                max_new_tokens=max_tokens,
                temperature=temperature,
                do_sample=True,
                top_p=0.9,
            )

        response = self._tokenizer.decode(outputs[0], skip_special_tokens=True)
        # Extract only the assistant's response
        response = response.split("assistant:")[-1].strip()

        return LLMResponse(
            content=response,
            model=self.model_name,
        )

    async def stream_chat(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        # Local models don't support streaming easily
        # Generate full response and yield tokens
        response = self.chat(messages, temperature, max_tokens, **kwargs)
        words = response.content.split()
        for i, word in enumerate(words):
            token = word + " " if i < len(words) - 1 else word
            yield token

    def complete(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs,
    ) -> LLMResponse:
        messages = [{"role": "user", "content": prompt}]
        return self.chat(messages, temperature, max_tokens, **kwargs)

    def is_available(self) -> bool:
        try:
            import transformers
            return True
        except ImportError:
            return False
