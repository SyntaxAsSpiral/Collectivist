#!/usr/bin/env python3
"""
Plugin loader for Collectivist
Ensures all plugins are properly registered with the PluginRegistry
"""

# Import all plugins to trigger their registration
from . import repository_scanner
from . import media
from . import documents
from . import obsidian
from . import fallback

# Import the registry for external access
from .plugin_interface import PluginRegistry

__all__ = ['PluginRegistry']