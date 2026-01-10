#!/usr/bin/env python3
"""
Plugin Interface for Collectivist Scanners

Defines the base interfaces and registry for collection scanner plugins.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime


@dataclass
class CollectionItem:
    """Represents a single item in a collection."""
    short_name: str
    type: str  # "dir", "file", etc.
    size: int
    created: str  # ISO format datetime
    modified: str  # ISO format datetime
    accessed: str  # ISO format datetime
    path: str
    description: Optional[str] = None
    category: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class CollectionScanner(ABC):
    """Base class for collection scanner plugins."""

    @abstractmethod
    def get_name(self) -> str:
        """Return the plugin name (e.g., 'repositories', 'obsidian')."""
        pass

    @abstractmethod
    def get_supported_types(self) -> List[str]:
        """Return list of supported item types (e.g., ['dir'], ['file'])."""
        pass

    @abstractmethod
    def get_categories(self) -> List[str]:
        """Return list of default categories for this collection type."""
        pass

    @abstractmethod
    def detect(self, path: Path) -> bool:
        """Detect if the given path contains this type of collection."""
        pass

    @abstractmethod
    def scan(self, root_path: Path, config: Dict[str, Any]) -> List[CollectionItem]:
        """Scan the collection and return list of items."""
        pass

    @abstractmethod
    def get_description_prompt_template(self) -> str:
        """Return the LLM prompt template for generating descriptions."""
        pass

    @abstractmethod
    def get_example_descriptions(self) -> List[str]:
        """Return example descriptions for this collection type."""
        pass

    @abstractmethod
    def get_content_for_description(self, item: CollectionItem) -> str:
        """Extract content from an item for LLM description generation."""
        pass


class PluginRegistry:
    """Registry for managing scanner plugins."""

    _plugins: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def register(cls, name: str, scanner_class: type, version: str, description: str):
        """Register a scanner plugin."""
        cls._plugins[name] = {
            'class': scanner_class,
            'version': version,
            'description': description
        }

    @classmethod
    def get_scanner(cls, name: str) -> Optional[type]:
        """Get a scanner class by name."""
        plugin = cls._plugins.get(name)
        return plugin['class'] if plugin else None

    @classmethod
    def list_plugins(cls) -> Dict[str, Dict[str, Any]]:
        """List all registered plugins."""
        return cls._plugins.copy()

    @classmethod
    def get_available_scanners(cls) -> List[str]:
        """Get list of available scanner names."""
        return list(cls._plugins.keys())