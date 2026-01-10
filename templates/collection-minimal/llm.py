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
    def from_config(cls, config_path: Path = None) -> 'LLMClient':
        """Create client from config file.

        Looks for config in this order:
        1. Specified config_path
        2. .collection/collectivist.yaml (collection-specific config)
        3. ~/.collectivist/config.yaml (global config)
        4. Environment variables (fallback)

        Args:
            config_path: Optional specific config file path
        """
        config = {}

        # Priority 1: Specified config file
        if config_path and config_path.exists():
            config = cls._load_config_file(config_path)

        # Priority 2: Collection-specific config (.collection/collectivist.yaml or .md)
        elif Path(".collection/collectivist.yaml").exists():
            config = cls._load_config_file(Path(".collection/collectivist.yaml"))
        elif Path(".collection/collectivist.md").exists():
            config = cls._load_config_file(Path(".collection/collectivist.md"))

        # Priority 3: Global config (~/.collectivist/config.yaml or .md)
        elif (Path.home() / ".collectivist" / "config.yaml").exists():
            config = cls._load_config_file(Path.home() / ".collectivist" / "config.yaml")
        elif (Path.home() / ".collectivist" / "config.md").exists():
            config = cls._load_config_file(Path.home() / ".collectivist" / "config.md")

        # Priority 4: Environment variables (fallback)
        else:
            config = cls._load_from_env()

        return cls(
            provider=config.get("llm_provider", "lmstudio"),
            api_key=config.get("llm_api_key"),
            base_url=config.get("llm_base_url"),
            model=config.get("llm_model")
        )

    @classmethod
    def _load_config_file(cls, config_path: Path) -> dict:
        """Load configuration from YAML file or Markdown-embedded YAML."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check if it's a Markdown file with embedded YAML
            if config_path.suffix.lower() == '.md':
                yaml_content = cls._extract_yaml_from_markdown(content)
                if yaml_content:
                    return yaml.safe_load(yaml_content) or {}

            # Regular YAML file
            return yaml.safe_load(content) or {}

        except Exception:
            return {}

    @classmethod
    def _extract_yaml_from_markdown(cls, content: str) -> str:
        """Extract YAML from the first ```yaml fenced code block in Markdown."""
        # Look for the first ```yaml fenced block
        yaml_start = content.find('```yaml')
        if yaml_start == -1:
            yaml_start = content.find('```yml')  # Also support .yml extension

        if yaml_start == -1:
            return ""

        # Find the end of the opening fence
        after_open = content[yaml_start:]
        newline_pos = after_open.find('\n')
        if newline_pos == -1:
            return ""

        # Find the closing fence
        yaml_content_start = yaml_start + newline_pos + 1
        yaml_end = content.find('```', yaml_content_start)
        if yaml_end == -1:
            return ""

        # Extract and clean the YAML content
        yaml_text = content[yaml_content_start:yaml_end].strip()
        return yaml_text if yaml_text else ""

    @classmethod
    def _load_from_env(cls) -> dict:
        """Load configuration from environment variables (legacy fallback)."""
        return {
            "llm_provider": os.getenv("COLLECTIVIST_LLM_PROVIDER", "lmstudio"),
            "llm_api_key": os.getenv("COLLECTIVIST_LLM_API_KEY"),
            "llm_base_url": os.getenv("COLLECTIVIST_LLM_BASE_URL"),
            "llm_model": os.getenv("COLLECTIVIST_LLM_MODEL")
        }

    @classmethod
    def from_env(cls) -> 'LLMClient':
        """Legacy method for backward compatibility."""
        return cls.from_config()

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