#!/usr/bin/env python3
"""
LLM Provider Abstraction - ported from .shared/go/llm pattern
Supports local (LMStudio, Ollama) and cloud (OpenRouter, Pollinations, Anthropic, OpenAI) providers
"""

import os
import requests
from enum import Enum
from typing import Optional, Dict, List
from dataclasses import dataclass


class ProviderType(Enum):
    """Supported LLM providers"""
    OPENROUTER = "openrouter"
    LMSTUDIO = "lmstudio"
    POLLINATIONS = "pollinations"
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    OLLAMA = "ollama"
    CUSTOM = "custom"


DEFAULT_BASE_URLS = {
    ProviderType.OPENROUTER: "https://openrouter.ai/api/v1",
    ProviderType.LMSTUDIO: "http://localhost:1234/v1",
    ProviderType.POLLINATIONS: "https://text.pollinations.ai/openai",
    ProviderType.ANTHROPIC: "https://api.anthropic.com/v1",
    ProviderType.OPENAI: "https://api.openai.com/v1",
    ProviderType.OLLAMA: "http://localhost:11434/v1",
}


@dataclass
class Message:
    """Chat message"""
    role: str  # "user", "assistant", "system"
    content: str


class LLMClient:
    """Unified LLM client with provider abstraction"""

    def __init__(
        self,
        provider: ProviderType,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 120
    ):
        self.provider = provider
        self.api_key = api_key
        self.base_url = base_url or DEFAULT_BASE_URLS.get(provider)
        self.timeout = timeout

        # Validate configuration
        if not self.base_url:
            raise ValueError(f"No base URL configured for provider: {provider}")

        # Cloud providers require API key
        if provider in [ProviderType.OPENROUTER, ProviderType.ANTHROPIC, ProviderType.OPENAI]:
            if not self.api_key:
                raise ValueError(f"API key required for provider: {provider}")

    def chat(
        self,
        model: str,
        messages: List[Message],
        temperature: float = 0.7,
        top_p: Optional[float] = None,
        max_tokens: int = 4096
    ) -> str:
        """
        Send chat completion request to LLM provider.
        Returns the response text.
        """
        # Build request payload (OpenAI-compatible format)
        payload = {
            "model": model,
            "messages": [{"role": msg.role, "content": msg.content} for msg in messages],
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        if top_p is not None:
            payload["top_p"] = top_p

        # Build headers
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        # Make request
        url = f"{self.base_url}/chat/completions"

        try:
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()

            data = response.json()

            # Extract response text
            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0]["message"]["content"]
            else:
                raise ValueError(f"Unexpected response format: {data}")

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"LLM request failed: {e}")

    @classmethod
    def from_env(cls, env_file: Optional[str] = None) -> 'LLMClient':
        """
        Create client from environment variables or .env file.

        Expected variables:
        - LLM_PROVIDER: Provider type (openrouter, lmstudio, etc.)
        - LLM_API_KEY: API key (if required by provider)
        - <PROVIDER>_API_KEY: Provider-specific key (fallback)
        - LLM_BASE_URL: Custom base URL (optional)
        """
        # Load .env if specified
        if env_file and os.path.exists(env_file):
            from dotenv import load_dotenv
            load_dotenv(env_file)

        # Get configuration
        provider_str = os.getenv("LLM_PROVIDER", "lmstudio")
        api_key = os.getenv("LLM_API_KEY")
        base_url = os.getenv("LLM_BASE_URL")

        # Parse provider
        try:
            provider = ProviderType(provider_str.lower())
        except ValueError:
            raise ValueError(f"Unknown provider: {provider_str}")

        # If no LLM_API_KEY, try provider-specific key
        if not api_key:
            provider_key_map = {
                ProviderType.OPENROUTER: "OPENROUTER_API_KEY",
                ProviderType.ANTHROPIC: "ANTHROPIC_API_KEY",
                ProviderType.OPENAI: "OPENAI_API_KEY",
                ProviderType.LMSTUDIO: "LMSTUDIO_API_KEY",
                ProviderType.POLLINATIONS: "POLLINATIONS_API_KEY",
            }
            if provider in provider_key_map:
                api_key = os.getenv(provider_key_map[provider])

        return cls(provider=provider, api_key=api_key, base_url=base_url)


def create_client_from_config(config_path: str = None) -> LLMClient:
    """
    Create LLM client from configuration.
    Looks for .env in current directory or specified path.
    """
    if config_path is None:
        # Try common locations
        candidates = [
            "C:\\Users\\synta.ZK-ZRRH\\.dev\\.env",
            ".env"
        ]
        for candidate in candidates:
            if os.path.exists(candidate):
                config_path = candidate
                break

    return LLMClient.from_env(config_path)


# Fast-fail: test LLM connectivity on import for critical systems
def test_llm_connection(client: LLMClient, model: str = "gpt-oss-20b") -> bool:
    """
    Test LLM connectivity with minimal request.
    Returns True if reachable, False otherwise.
    Fast-fail pattern for critical systems.
    """
    try:
        response = client.chat(
            model=model,
            messages=[Message(role="user", content="ping")],
            temperature=0.0,
            max_tokens=10
        )
        return len(response) > 0
    except Exception:
        return False
