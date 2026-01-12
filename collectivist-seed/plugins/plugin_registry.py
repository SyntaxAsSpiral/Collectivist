#!/usr/bin/env python3
"""
Remote Plugin Registry for Collectivist

Manages automatic plugin discovery and installation from remote repositories.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import urllib.request
import urllib.error
import hashlib
import tempfile
import shutil


class RemotePluginRegistry:
    """Manages remote plugin discovery and installation."""

    def __init__(self, registry_url: str = None):
        """Initialize remote plugin registry.

        Args:
            registry_url: URL to plugin registry JSON file
        """
        self.registry_url = registry_url or "https://raw.githubusercontent.com/SyntaxAsSpiral/Collectivist/main/plugins/registry.json"
        self.local_cache_dir = Path.home() / ".collectivist" / "plugins"
        self.local_cache_dir.mkdir(parents=True, exist_ok=True)

    def get_available_plugins(self) -> Dict[str, Dict[str, Any]]:
        """Fetch available plugins from remote registry."""
        try:
            with urllib.request.urlopen(self.registry_url, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                return data.get('plugins', {})
        except (urllib.error.URLError, json.JSONDecodeError, KeyError):
            # Fallback to empty registry if network fails
            return {}

    def is_plugin_available_locally(self, plugin_name: str) -> bool:
        """Check if plugin is available locally."""
        plugin_path = self.local_cache_dir / f"{plugin_name}.py"
        return plugin_path.exists()

    def download_plugin(self, plugin_name: str, plugin_info: Dict[str, Any]) -> bool:
        """Download and install a plugin locally.

        Args:
            plugin_name: Name of the plugin to download
            plugin_info: Plugin metadata from registry

        Returns:
            bool: True if download successful
        """
        try:
            download_url = plugin_info.get('url')
            expected_hash = plugin_info.get('sha256')

            if not download_url:
                return False

            # Download plugin to temporary file
            with urllib.request.urlopen(download_url, timeout=30) as response:
                plugin_content = response.read()

            # Verify hash if provided
            if expected_hash:
                actual_hash = hashlib.sha256(plugin_content).hexdigest()
                if actual_hash != expected_hash:
                    print(f"⚠️  Plugin {plugin_name} hash verification failed")
                    return False

            # Save to local cache
            plugin_path = self.local_cache_dir / f"{plugin_name}.py"
            with open(plugin_path, 'wb') as f:
                f.write(plugin_content)

            print(f"✅ Downloaded plugin: {plugin_name}")
            return True

        except Exception as e:
            print(f"❌ Failed to download plugin {plugin_name}: {e}")
            return False

    def load_plugin(self, plugin_name: str):
        """Load a plugin into the current Python session.

        Args:
            plugin_name: Name of the plugin to load

        Returns:
            bool: True if plugin loaded successfully
        """
        plugin_path = self.local_cache_dir / f"{plugin_name}.py"

        if not plugin_path.exists():
            return False

        try:
            # Add plugin directory to Python path temporarily
            plugin_dir = str(self.local_cache_dir)
            if plugin_dir not in sys.path:
                sys.path.insert(0, plugin_dir)

            # Import the plugin module
            __import__(plugin_name)

            print(f"✅ Loaded plugin: {plugin_name}")
            return True

        except Exception as e:
            print(f"❌ Failed to load plugin {plugin_name}: {e}")
            return False

    def ensure_plugin_available(self, plugin_name: str) -> bool:
        """Ensure a plugin is available, downloading if necessary.

        Args:
            plugin_name: Name of the plugin to ensure is available

        Returns:
            bool: True if plugin is available and loaded
        """
        # Check if already available locally
        if self.is_plugin_available_locally(plugin_name):
            return self.load_plugin(plugin_name)

        # Try to download from remote registry
        print(f"🔍 Looking for plugin: {plugin_name}")
        available_plugins = self.get_available_plugins()

        if plugin_name in available_plugins:
            plugin_info = available_plugins[plugin_name]
            if self.download_plugin(plugin_name, plugin_info):
                return self.load_plugin(plugin_name)

        print(f"❌ Plugin {plugin_name} not found in registry")
        return False

    def list_installed_plugins(self) -> List[str]:
        """List locally installed plugins."""
        if not self.local_cache_dir.exists():
            return []

        return [f.stem for f in self.local_cache_dir.glob("*.py")]

    def update_plugins(self) -> Dict[str, bool]:
        """Update all installed plugins to latest versions."""
        results = {}
        installed_plugins = self.list_installed_plugins()
        available_plugins = self.get_available_plugins()

        for plugin_name in installed_plugins:
            if plugin_name in available_plugins:
                plugin_info = available_plugins[plugin_name]
                local_path = self.local_cache_dir / f"{plugin_name}.py"

                # Check if update needed (compare hashes if available)
                if 'sha256' in plugin_info:
                    try:
                        with open(local_path, 'rb') as f:
                            local_hash = hashlib.sha256(f.read()).hexdigest()

                        if local_hash != plugin_info['sha256']:
                            print(f"🔄 Updating plugin: {plugin_name}")
                            results[plugin_name] = self.download_plugin(plugin_name, plugin_info)
                        else:
                            results[plugin_name] = True  # Already up to date
                    except Exception:
                        results[plugin_name] = False
                else:
                    # No hash available, skip update
                    results[plugin_name] = True
            else:
                results[plugin_name] = True  # Plugin not in registry, keep as-is

        return results


# Global instance for easy access
remote_registry = RemotePluginRegistry()