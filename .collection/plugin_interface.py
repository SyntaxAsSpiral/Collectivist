#!/usr/bin/env python3
"""
Plugin Interface for The Collectivist
Defines the contract for domain-specific scanners
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CollectionItem:
    """
    Standardized item representation across all collection types.
    Plugins populate this structure with domain-specific metadata.
    """
    # Core fields (required)
    short_name: str  # Unique identifier within collection
    type: str  # Item type (e.g., "dir", "file", "video", "audio")
    size: int  # Size in bytes
    created: str  # ISO format timestamp
    modified: str  # ISO format timestamp
    accessed: str  # ISO format timestamp
    path: str  # Full path to item

    # Optional common fields
    description: Optional[str] = None
    category: Optional[str] = None

    # Domain-specific metadata (flexible dict)
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class CollectionScanner(ABC):
    """
    Abstract base class for collection scanners.
    Each domain implements this interface as a plugin.
    """

    @abstractmethod
    def get_name(self) -> str:
        """Return scanner name (e.g., 'repositories', 'media', 'documents')"""
        pass

    @abstractmethod
    def get_supported_types(self) -> List[str]:
        """Return list of file/directory patterns this scanner handles"""
        pass

    @abstractmethod
    def get_categories(self) -> List[str]:
        """Return list of valid categories for this collection type"""
        pass

    @abstractmethod
    def detect(self, path: Path) -> bool:
        """
        Detect if this scanner can handle the given path.
        Returns True if this scanner should process this collection.
        """
        pass

    @abstractmethod
    def scan(self, root_path: Path, config: Dict[str, Any]) -> List[CollectionItem]:
        """
        Scan the collection and return list of items.

        Args:
            root_path: Root directory to scan
            config: Configuration dict from collection.yaml

        Returns:
            List of CollectionItem objects with metadata populated
        """
        pass

    @abstractmethod
    def get_description_prompt_template(self) -> str:
        """
        Return prompt template for LLM description generation.
        Template should include {content} placeholder for item content.
        """
        pass

    @abstractmethod
    def get_example_descriptions(self) -> List[str]:
        """
        Return 3-5 example descriptions for few-shot learning.
        These guide the LLM in generating similar descriptions.
        """
        pass

    def get_content_for_description(self, item: CollectionItem) -> str:
        """
        Extract content from item for LLM description generation.
        Default implementation returns empty string.
        Plugins override to provide relevant content (e.g., README, metadata).
        """
        return ""


@dataclass
class PluginMetadata:
    """Metadata about a registered plugin"""
    name: str
    scanner_class: type
    version: str = "1.0.0"
    description: str = ""


class PluginRegistry:
    """
    Registry for collection scanner plugins.
    Plugins self-register on import.
    """

    _plugins: Dict[str, PluginMetadata] = {}

    @classmethod
    def register(
        cls,
        name: str,
        scanner_class: type,
        version: str = "1.0.0",
        description: str = ""
    ):
        """Register a scanner plugin"""
        if not issubclass(scanner_class, CollectionScanner):
            raise TypeError(f"{scanner_class} must inherit from CollectionScanner")

        cls._plugins[name] = PluginMetadata(
            name=name,
            scanner_class=scanner_class,
            version=version,
            description=description
        )

    @classmethod
    def get_plugin(cls, name: str) -> Optional[type]:
        """Get scanner class by name"""
        metadata = cls._plugins.get(name)
        return metadata.scanner_class if metadata else None

    @classmethod
    def list_plugins(cls) -> List[PluginMetadata]:
        """List all registered plugins"""
        return list(cls._plugins.values())

    @classmethod
    def auto_detect(cls, path: Path) -> Optional[type]:
        """
        Auto-detect appropriate scanner for path.
        Returns first scanner whose detect() method returns True.
        """
        for metadata in cls._plugins.values():
            scanner = metadata.scanner_class()
            if scanner.detect(path):
                return metadata.scanner_class
        return None
