#!/usr/bin/env python3
"""
LLM Provider Abstraction - ported from .shared/go/llm pattern
Supports local (LMStudio, Ollama) and cloud (OpenRouter, Pollinations, Anthropic, OpenAI) providers
"""

import os
import re
import requests
import yaml
from enum import Enum
from pathlib import Path
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

# Smart defaults for models when not specified
DEFAULT_MODELS = {
    ProviderType.LMSTUDIO: "local-model",
    ProviderType.OPENROUTER: "openai/gpt-oss-120b:free",
    ProviderType.POLLINATIONS: "openai",
    ProviderType.OLLAMA: "llama3.1",
    ProviderType.OPENAI: "gpt-4o-mini",
    ProviderType.ANTHROPIC: "claude-3-haiku-20240307",
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
        model: Optional[str] = None,
        timeout: int = 120
    ):
        self.provider = provider
        self.api_key = api_key
        self.base_url = base_url or DEFAULT_BASE_URLS.get(provider)
        self.model = model or DEFAULT_MODELS.get(provider, "gpt-4o-mini")
        self.timeout = timeout

        # Validate configuration
        if not self.base_url:
            raise ValueError(f"No base URL configured for provider: {provider}")

        # Cloud providers require API key
        if provider in [ProviderType.OPENROUTER, ProviderType.ANTHROPIC, ProviderType.OPENAI]:
            if not self.api_key:
                raise ValueError(f"API key required for provider: {provider}")

    def get_default_model(self) -> str:
        """Get the default model for this client."""
        return self.model

    def chat(
        self,
        model: Optional[str] = None,
        messages: List[Message] = None,
        temperature: float = 0.7,
        top_p: Optional[float] = None,
        max_tokens: int = 4096
    ) -> str:
        """
        Send chat completion request to LLM provider.
        
        Args:
            model: Model to use (defaults to client's configured model)
            messages: List of messages for the conversation
            temperature: Sampling temperature
            top_p: Top-p sampling parameter
            max_tokens: Maximum tokens to generate
            
        Returns:
            The response text.
        """
        # Use default model if not specified
        if model is None:
            model = self.model
        
        # Ensure messages is not None
        if messages is None:
            messages = []
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
    def from_config(cls, config_path: Optional[str] = None) -> 'LLMClient':
        """
        Create client from multi-location configuration discovery.
        
        Priority order (highest to lowest):
        1. .collection/collectivist.yaml - Collection-specific configuration
        2. .collection/collectivist.md - Markdown-embedded (Obsidian-friendly)
        3. collectivist.md - Collection root config
        4. ~/.collectivist/config.yaml - Global user configuration
        5. Custom path via config_path parameter
        
        Supports both YAML and Markdown-embedded YAML formats.
        """
        config = cls._discover_config(config_path)
        
        # Extract configuration values
        provider_str = config.get("llm_provider", "lmstudio")
        api_key = config.get("llm_api_key")
        base_url = config.get("llm_base_url")
        model = config.get("llm_model")
        
        # Parse provider
        try:
            provider = ProviderType(provider_str.lower())
        except ValueError:
            raise ValueError(f"Unknown provider: {provider_str}")
        
        # Use smart default for model if not specified
        if not model:
            model = DEFAULT_MODELS.get(provider, "gpt-4o-mini")
        
        return cls(provider=provider, api_key=api_key, base_url=base_url, model=model)
    
    @classmethod
    def _discover_config(cls, custom_path: Optional[str] = None) -> Dict[str, str]:
        """
        Discover configuration from multiple locations.
        Returns merged configuration dict.
        """
        config = {}
        
        # Define search paths in priority order (lowest to highest)
        search_paths = [
            Path.home() / ".collectivist" / "config.yaml",  # Global user config
            Path.cwd() / "collectivist.md",                 # Collection root config
            Path.cwd() / ".collection" / "collectivist.md", # Markdown-embedded
            Path.cwd() / ".collection" / "collectivist.yaml", # Collection-specific
        ]
        
        # Add custom path if specified (highest priority)
        if custom_path:
            search_paths.append(Path(custom_path))
        
        # Load configs in order (later configs override earlier ones)
        for config_path in search_paths:
            if config_path.exists():
                try:
                    file_config = cls._load_config_file(config_path)
                    config.update(file_config)
                except Exception as e:
                    print(f"Warning: Failed to load config from {config_path}: {e}")
        
        # Fallback to environment variables if no config found
        if not config:
            config = cls._load_env_config()
        
        return config
    
    @classmethod
    def _load_config_file(cls, config_path: Path) -> Dict[str, str]:
        """Load configuration from YAML or Markdown file."""
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if config_path.suffix.lower() == '.md':
            # Extract YAML from Markdown (first yaml code block)
            return cls._extract_yaml_from_markdown(content)
        else:
            # Parse as YAML
            return yaml.safe_load(content) or {}
    
    @classmethod
    def _extract_yaml_from_markdown(cls, markdown_content: str) -> Dict[str, str]:
        """Extract YAML configuration from Markdown content."""
        # Find first yaml code block
        yaml_pattern = r'```yaml\s*\n(.*?)\n```'
        match = re.search(yaml_pattern, markdown_content, re.DOTALL | re.IGNORECASE)
        
        if match:
            yaml_content = match.group(1)
            try:
                return yaml.safe_load(yaml_content) or {}
            except yaml.YAMLError as e:
                raise ValueError(f"Invalid YAML in Markdown: {e}")
        
        return {}
    
    @classmethod
    def _load_env_config(cls) -> Dict[str, str]:
        """Load configuration from environment variables (fallback)."""
        config = {}
        
        # Map environment variables to config keys
        env_mappings = {
            "LLM_PROVIDER": "llm_provider",
            "LLM_API_KEY": "llm_api_key",
            "LLM_BASE_URL": "llm_base_url",
            "LLM_MODEL": "llm_model",
        }
        
        for env_key, config_key in env_mappings.items():
            value = os.getenv(env_key)
            if value:
                config[config_key] = value
        
        # Try provider-specific API keys if LLM_API_KEY not set
        if not config.get("llm_api_key"):
            provider_key_map = {
                "openrouter": "OPENROUTER_API_KEY",
                "anthropic": "ANTHROPIC_API_KEY", 
                "openai": "OPENAI_API_KEY",
                "lmstudio": "LMSTUDIO_API_KEY",
                "pollinations": "POLLINATIONS_API_KEY",
            }
            
            provider = config.get("llm_provider", "lmstudio").lower()
            if provider in provider_key_map:
                api_key = os.getenv(provider_key_map[provider])
                if api_key:
                    config["llm_api_key"] = api_key
        
        return config


def create_client_from_config(config_path: str = None) -> LLMClient:
    """
    Create LLM client from configuration using multi-location discovery.
    
    Args:
        config_path: Optional custom config path (overrides discovery)
    
    Returns:
        Configured LLMClient instance
    """
    return LLMClient.from_config(config_path)


# Fast-fail: test LLM connectivity on import for critical systems
def test_llm_connection(client: LLMClient, model: Optional[str] = None) -> bool:
    """
    Test LLM connectivity with minimal request.
    Returns True if reachable, False otherwise.
    Fast-fail pattern for critical systems.
    """
    try:
        # Use client's default model if none specified
        test_model = model or client.get_default_model()
        
        response = client.chat(
            model=test_model,
            messages=[Message(role="user", content="ping")],
            temperature=0.0,
            max_tokens=10
        )
        return len(response) > 0
    except Exception:
        return False
