"""LLM Manager - Manages multiple LLM providers with fallback support."""

from __future__ import annotations

import os
from typing import Any, AsyncGenerator
from dataclasses import dataclass

from ke.llm.providers import (
    LLMProvider,
    LLMResponse,
    OpenAIProvider,
    AnthropicProvider,
    GeminiProvider,
    OllamaProvider,
    VLLMProvider,
    LocalProvider,
)


@dataclass
class ProviderConfig:
    """Configuration for an LLM provider."""
    name: str
    enabled: bool = True
    priority: int = 0  # Higher priority = preferred
    api_key: str | None = None
    model: str | None = None
    base_url: str | None = None
    config: dict[str, Any] | None = None


class LLMManager:
    """
    Manages multiple LLM providers with automatic fallback.

    Features:
    - Multiple provider support
    - Automatic fallback on failure
    - Priority-based selection
    - Streaming support
    - Health checking
    """

    def __init__(self):
        self._providers: dict[str, LLMProvider] = {}
        self._configs: dict[str, ProviderConfig] = {}
        self._load_config()

    def _load_config(self):
        """Load provider configurations from environment and config."""
        # OpenAI
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            self._configs["openai"] = ProviderConfig(
                name="openai",
                priority=100,
                api_key=openai_key,
                model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
                base_url=os.getenv("OPENAI_BASE_URL"),
            )

        # Anthropic
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if anthropic_key:
            self._configs["anthropic"] = ProviderConfig(
                name="anthropic",
                priority=90,
                api_key=anthropic_key,
                model=os.getenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307"),
            )

        # Google Gemini
        gemini_key = os.getenv("GOOGLE_API_KEY")
        if gemini_key:
            self._configs["gemini"] = ProviderConfig(
                name="gemini",
                priority=80,
                api_key=gemini_key,
                model=os.getenv("GEMINI_MODEL", "gemini-pro"),
            )

        # Ollama (local)
        ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self._configs["ollama"] = ProviderConfig(
            name="ollama",
            priority=50,
            base_url=ollama_url,
            model=os.getenv("OLLAMA_MODEL", "llama2"),
        )

        # vLLM (local)
        vllm_url = os.getenv("VLLM_BASE_URL")
        if vllm_url:
            self._configs["vllm"] = ProviderConfig(
                name="vllm",
                priority=60,
                base_url=vllm_url,
                model=os.getenv("VLLM_MODEL", "default"),
            )

        # Local transformers
        self._configs["local"] = ProviderConfig(
            name="local",
            priority=10,
            model=os.getenv("LOCAL_MODEL", "microsoft/DialoGPT-medium"),
        )

    def get_provider(self, name: str | None = None) -> LLMProvider:
        """Get a specific provider or the best available one."""
        if name:
            if name in self._providers:
                return self._providers[name]
            provider = self._create_provider(name)
            if provider:
                self._providers[name] = provider
                return provider
            raise ValueError(f"Provider '{name}' is not available")

        # Get best available provider
        return self._get_best_provider()

    def _get_best_provider(self) -> LLMProvider:
        """Get the best available provider based on priority."""
        sorted_configs = sorted(
            self._configs.values(),
            key=lambda c: c.priority,
            reverse=True,
        )

        for config in sorted_configs:
            if config.enabled:
                try:
                    provider = self._create_provider(config.name)
                    if provider and provider.is_available():
                        return provider
                except Exception:
                    continue

        # Fallback to local
        return self._create_provider("local") or self._create_provider("ollama")

    def _create_provider(self, name: str) -> LLMProvider | None:
        """Create a provider instance."""
        config = self._configs.get(name)
        if not config:
            return None

        kwargs = {
            "api_key": config.api_key,
            "model": config.model,
            "base_url": config.base_url,
        }
        if config.config:
            kwargs.update(config.config)

        provider_map = {
            "openai": OpenAIProvider,
            "anthropic": AnthropicProvider,
            "gemini": GeminiProvider,
            "ollama": OllamaProvider,
            "vllm": VLLMProvider,
            "local": LocalProvider,
        }

        provider_class = provider_map.get(name)
        if provider_class:
            return provider_class(**kwargs)

        return None

    def chat(
        self,
        messages: list[dict[str, str]],
        provider: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs,
    ) -> LLMResponse:
        """Send chat completion request with fallback."""
        llm = self.get_provider(provider)

        try:
            return llm.chat(messages, temperature, max_tokens, **kwargs)
        except Exception as e:
            # Try fallback providers
            return self._fallback_chat(messages, temperature, max_tokens, exclude=provider, **kwargs)

    def _fallback_chat(
        self,
        messages: list[dict[str, str]],
        temperature: float,
        max_tokens: int,
        exclude: str | None = None,
        **kwargs,
    ) -> LLMResponse:
        """Try fallback providers."""
        for name, config in sorted(self._configs.items(), key=lambda x: x[1].priority, reverse=True):
            if name == exclude or not config.enabled:
                continue

            try:
                provider = self._create_provider(name)
                if provider and provider.is_available():
                    return provider.chat(messages, temperature, max_tokens, **kwargs)
            except Exception:
                continue

        raise RuntimeError("No available LLM providers")

    async def stream_chat(
        self,
        messages: list[dict[str, str]],
        provider: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        """Stream chat completion with fallback."""
        llm = self.get_provider(provider)

        try:
            async for token in llm.stream_chat(messages, temperature, max_tokens, **kwargs):
                yield token
        except Exception:
            # Try fallback
            async for token in self._fallback_stream(messages, temperature, max_tokens, exclude=provider, **kwargs):
                yield token

    async def _fallback_stream(
        self,
        messages: list[dict[str, str]],
        temperature: float,
        max_tokens: int,
        exclude: str | None = None,
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        """Try fallback providers for streaming."""
        for name, config in sorted(self._configs.items(), key=lambda x: x[1].priority, reverse=True):
            if name == exclude or not config.enabled:
                continue

            try:
                provider = self._create_provider(name)
                if provider and provider.is_available():
                    async for token in provider.stream_chat(messages, temperature, max_tokens, **kwargs):
                        yield token
                    return
            except Exception:
                continue

    def list_providers(self) -> list[dict[str, Any]]:
        """List all configured providers and their status."""
        result = []
        for name, config in self._configs.items():
            provider = self._create_provider(name)
            result.append({
                "name": name,
                "enabled": config.enabled,
                "priority": config.priority,
                "available": provider.is_available() if provider else False,
                "model": config.model,
            })
        return result

    def health_check(self) -> dict[str, bool]:
        """Check health of all providers."""
        result = {}
        for name in self._configs:
            try:
                provider = self._create_provider(name)
                result[name] = provider.is_available() if provider else False
            except Exception:
                result[name] = False
        return result
