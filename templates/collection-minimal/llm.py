"""
LLM Client Abstraction - Provider Agnostic Interface

Supports local models (LMStudio, Ollama) and cloud providers (OpenRouter, etc.)
"""

import os
import requests
from typing import Dict, List, Optional, Any
from pathlib import Path


class LLMClient:
    """Unified interface for different LLM providers."""

    # Provider configurations
    PROVIDERS = {
        "lmstudio": {
            "base_url": "http://localhost:1234/v1",
            "api_key_required": False
        },
        "ollama": {
            "base_url": "http://localhost:11434/v1",
            "api_key_required": False
        },
        "openrouter": {
            "base_url": "https://openrouter.ai/api/v1",
            "api_key_required": True
        },
        "openai": {
            "base_url": "https://api.openai.com/v1",
            "api_key_required": True
        },
        "anthropic": {
            "base_url": "https://api.anthropic.com/v1",
            "api_key_required": True
        },
        "pollinations": {
            "base_url": "https://text.pollinations.ai",
            "api_key_required": False
        }
    }

    def __init__(self, provider: str, api_key: Optional[str] = None, base_url: Optional[str] = None, model: Optional[str] = None):
        """Initialize LLM client.

        Args:
            provider: Provider name (lmstudio, ollama, openrouter, openai)
            api_key: API key for cloud providers
            base_url: Custom base URL override
            model: Specific model to use (optional, uses provider default if not specified)
        """
        if provider not in self.PROVIDERS:
            raise ValueError(f"Unknown provider: {provider}")

        self.provider = provider
        self.config = self.PROVIDERS[provider]
        self.api_key = api_key
        self.base_url = base_url or self.config["base_url"]
        self.model = model or self._get_default_model()

        # Validate configuration
        if self.config["api_key_required"] and not self.api_key:
            raise ValueError(f"API key required for provider: {provider}")

    def _get_default_model(self) -> str:
        """Get default model for provider."""
        default_models = {
            "lmstudio": "local-model",  # Whatever is loaded
            "ollama": "llama3.1",        # Modern default
            "openrouter": "meta-llama/llama-3.1-8b-instruct",
            "openai": "gpt-4o-mini",     # Cost-effective default
            "anthropic": "claude-3-haiku-20240307",
            "pollinations": "openai"
        }
        return default_models.get(self.provider, "default-model")

    @classmethod
    def from_env(cls) -> 'LLMClient':
        """Create client from environment variables.

        Looks for:
        - COLLECTIVIST_LLM_PROVIDER (default: lmstudio)
        - COLLECTIVIST_LLM_API_KEY
        - COLLECTIVIST_LLM_BASE_URL
        - COLLECTIVIST_LLM_MODEL
        """
        provider = os.getenv("COLLECTIVIST_LLM_PROVIDER", "lmstudio")
        api_key = os.getenv("COLLECTIVIST_LLM_API_KEY")
        base_url = os.getenv("COLLECTIVIST_LLM_BASE_URL")
        model = os.getenv("COLLECTIVIST_LLM_MODEL")

        # Try to load from .dev/.env if it exists
        dev_env = Path.home() / ".dev" / ".env"
        if dev_env.exists():
            try:
                with open(dev_env, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("LLM_PROVIDER="):
                            provider = line.split("=", 1)[1].strip()
                        elif line.startswith("LLM_API_KEY="):
                            api_key = line.split("=", 1)[1].strip()
                        elif line.startswith("LLM_BASE_URL="):
                            base_url = line.split("=", 1)[1].strip()
                        elif line.startswith("LLM_MODEL="):
                            model = line.split("=", 1)[1].strip()
            except Exception:
                pass  # Ignore .env reading errors

        return cls(provider, api_key, base_url, model)

    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.1) -> str:
        """Send chat completion request.

        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0.0-1.0)

        Returns:
            Response content string
        """
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 2000  # Reasonable default
        }

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=headers,
                timeout=60
            )

            if response.status_code != 200:
                raise Exception(f"API error: {response.status_code} - {response.text}")

            result = response.json()
            return result["choices"][0]["message"]["content"]

        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error: {e}")
        except (KeyError, IndexError) as e:
            raise Exception(f"Response parsing error: {e}")
        except Exception as e:
            raise Exception(f"LLM request failed: {e}")

    def test_connection(self) -> bool:
        """Test if the LLM provider is accessible."""
        try:
            # Simple test message
            messages = [{"role": "user", "content": "Hello"}]

            # Use the configured model for testing
            self.chat(messages, temperature=0.1)
            return True

        except Exception:
            return False


    def get_available_models(self) -> List[str]:
        """Get list of available models (if supported by provider)."""
        try:
            response = requests.get(f"{self.base_url}/models", timeout=10)

            if response.status_code == 200:
                data = response.json()
                return [model["id"] for model in data.get("data", [])]

        except Exception:
            pass

        # Fallback: return known models for provider
        fallback_models = {
            "lmstudio": ["local-model"],
            "ollama": ["llama2", "llama3", "llama3.1", "mistral"],
            "openrouter": ["meta-llama/llama-3.1-8b-instruct", "anthropic/claude-3-haiku", "openai/gpt-4o-mini"],
            "openai": ["gpt-3.5-turbo", "gpt-4", "gpt-4o-mini"],
            "anthropic": ["claude-3-haiku-20240307", "claude-3-sonnet-20240229", "claude-3-opus-20240229"],
            "pollinations": ["openai", "anthropic"]
        }

        return fallback_models.get(self.provider, ["default-model"])