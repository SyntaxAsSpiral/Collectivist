#!/usr/bin/env python3
"""
Configuration Management for Collectivist Web Backend
Handles LLM provider configuration and testing
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import BaseModel

from fastapi import HTTPException
import yaml


class LLMProviderConfig(BaseModel):
    provider: str  # openai, anthropic, openrouter, lmstudio, ollama
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: Optional[str] = None
    temperature: float = 0.1
    max_tokens: int = 2000


class ConfigManager:
    """Manages application configuration including LLM providers"""
    
    def __init__(self, config_dir: Optional[Path] = None):
        if config_dir is None:
            config_dir = Path.home() / '.collectivist'
        
        self.config_dir = config_dir
        self.config_file = config_dir / 'config.yaml'
        
        # Ensure config directory exists
        self.config_dir.mkdir(exist_ok=True)
        
        # Load or create default config
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create defaults"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f) or {}
            except Exception:
                pass
        
        # Default configuration
        return {
            'llm': {
                'provider': 'openrouter',
                'api_key': None,
                'base_url': 'https://openrouter.ai/api/v1',
                'model': 'gpt-oss-20b',
                'temperature': 0.1,
                'max_tokens': 2000
            },
            'web': {
                'host': '0.0.0.0',
                'port': 8000,
                'cors_origins': ['http://localhost:5173', 'http://localhost:3000']
            }
        }
    
    def _save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save config: {e}")
    
    def get_llm_config(self) -> LLMProviderConfig:
        """Get current LLM configuration"""
        llm_config = self.config.get('llm', {})
        return LLMProviderConfig(
            provider=llm_config.get('provider', 'openrouter'),
            api_key=llm_config.get('api_key'),
            base_url=llm_config.get('base_url'),
            model=llm_config.get('model'),
            temperature=llm_config.get('temperature', 0.1),
            max_tokens=llm_config.get('max_tokens', 2000)
        )
    
    def update_llm_config(self, config: LLMProviderConfig):
        """Update LLM configuration"""
        self.config['llm'] = {
            'provider': config.provider,
            'api_key': config.api_key,
            'base_url': config.base_url,
            'model': config.model,
            'temperature': config.temperature,
            'max_tokens': config.max_tokens
        }
        self._save_config()
        
        # Update environment variables for the pipeline
        self._update_env_vars(config)
    
    def _update_env_vars(self, config: LLMProviderConfig):
        """Update environment variables for pipeline compatibility"""
        # Map provider names to environment variable format
        provider_map = {
            'openai': 'OPENAI',
            'anthropic': 'ANTHROPIC', 
            'openrouter': 'OPENROUTER',
            'lmstudio': 'LMSTUDIO',
            'ollama': 'OLLAMA'
        }
        
        # Set LLM_PROVIDER
        os.environ['LLM_PROVIDER'] = config.provider
        
        # Set provider-specific variables
        if config.provider in provider_map:
            provider_prefix = provider_map[config.provider]
            
            if config.api_key:
                os.environ[f'{provider_prefix}_API_KEY'] = config.api_key
            
            if config.base_url:
                os.environ[f'{provider_prefix}_BASE_URL'] = config.base_url
            
            if config.model:
                os.environ[f'{provider_prefix}_MODEL'] = config.model
    
    def test_llm_connection(self) -> Dict[str, Any]:
        """Test LLM connection with current configuration"""
        try:
            # Import here to avoid circular imports
            import sys
            sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'collectivist-portable' / 'src'))
            from llm import create_client_from_config, test_llm_connection
            
            # Update environment with current config
            llm_config = self.get_llm_config()
            self._update_env_vars(llm_config)
            
            # Create client and test
            client = create_client_from_config()
            success = test_llm_connection(client)
            
            if success:
                return {
                    "status": "success",
                    "message": "LLM connection successful",
                    "provider": llm_config.provider,
                    "model": llm_config.model
                }
            else:
                return {
                    "status": "error",
                    "message": "LLM connection failed - check configuration",
                    "provider": llm_config.provider
                }
                
        except Exception as e:
            return {
                "status": "error", 
                "message": f"LLM connection test failed: {str(e)}",
                "provider": llm_config.provider if 'llm_config' in locals() else 'unknown'
            }
    
    def get_provider_presets(self) -> Dict[str, Dict[str, Any]]:
        """Get configuration presets for different LLM providers"""
        return {
            'openai': {
                'name': 'OpenAI',
                'base_url': 'https://api.openai.com/v1',
                'models': ['gpt-4', 'gpt-4-turbo', 'gpt-3.5-turbo'],
                'requires_api_key': True,
                'description': 'OpenAI GPT models'
            },
            'anthropic': {
                'name': 'Anthropic',
                'base_url': 'https://api.anthropic.com',
                'models': ['claude-3-opus', 'claude-3-sonnet', 'claude-3-haiku'],
                'requires_api_key': True,
                'description': 'Anthropic Claude models'
            },
            'openrouter': {
                'name': 'OpenRouter',
                'base_url': 'https://openrouter.ai/api/v1',
                'models': ['gpt-oss-20b', 'anthropic/claude-3-opus', 'meta-llama/llama-2-70b-chat'],
                'requires_api_key': True,
                'description': 'Access to multiple LLM providers'
            },
            'lmstudio': {
                'name': 'LM Studio',
                'base_url': 'http://localhost:1234/v1',
                'models': ['local-model'],
                'requires_api_key': False,
                'description': 'Local LM Studio server'
            },
            'ollama': {
                'name': 'Ollama',
                'base_url': 'http://localhost:11434/v1',
                'models': ['llama2', 'codellama', 'mistral'],
                'requires_api_key': False,
                'description': 'Local Ollama server'
            }
        }


# Global config manager instance
config_manager = ConfigManager()