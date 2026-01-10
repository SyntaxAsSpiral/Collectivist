#!/usr/bin/env python3
"""
PLUGIN_NAME Plugin Template
Replace PLUGIN_NAME with your plugin name (e.g., mycollection, photos, music)

This is a template for creating new Collectivist plugins.
Copy this file and modify it to implement your collection scanner.
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import yaml

from plugin_interface import CollectionScanner, CollectionItem, PluginRegistry


class PLUGIN_NAMEScanner(CollectionScanner):
    """
    Scanner for PLUGIN_DESCRIPTION collections.

    Replace this docstring with a description of what your plugin scans.
    """

    def get_name(self) -> str:
        """Return the plugin name identifier."""
        return "PLUGIN_NAME"  # Replace with your plugin name

    def get_supported_types(self) -> List[str]:
        """Return list of supported item types."""
        return ["file"]  # or ["dir"] or ["file", "dir"]

    def get_categories(self) -> List[str]:
        """Return list of default categories for this collection type."""
        return [
            # Replace with categories relevant to your collection type
            "category1",
            "category2",
            "category3",
            "utilities_misc"
        ]

    def detect(self, path: Path) -> bool:
        """
        Detect if this path contains a PLUGIN_NAME collection.

        Implement your detection logic here. Return True if this scanner
        should handle the collection.
        """
        if not path.is_dir():
            return False

        # Example detection logic - replace with your own:
        # Look for specific file extensions, directory structure, etc.

        # plugin_extensions = ['.ext1', '.ext2', '.ext3']
        # files = []
        # for ext in plugin_extensions:
        #     files.extend(list(path.glob(f'**/*{ext}')))
        # return len(files) >= 5  # Require minimum number of files

        return False  # Replace with your detection logic

    def scan(self, root_path: Path, config: Dict[str, Any]) -> List[CollectionItem]:
        """
        Scan the collection and return list of items.

        Config options (automatically handled):
        - exclude_hidden: bool (default True) - exclude files starting with '.'
        - exclude_patterns: list - additional glob patterns to exclude
        - preserve_data: dict - existing descriptions/categories to preserve
        """
        exclude_hidden = config.get('exclude_hidden', True)
        exclude_patterns = config.get('exclude_patterns', [])
        preserve_data = config.get('preserve_data', {})

        items = []

        # TODO: Implement your scanning logic
        # Walk through directories, find items, extract metadata

        # Example structure:
        # for root, dirs, files in os.walk(root_path):
        #     # Apply exclusions
        #     # Create CollectionItem for each found item
        #     # Extract metadata specific to your collection type

        # Placeholder - replace with actual scanning:
        # for item_path in self._find_items(root_path):
        #     if self._should_exclude(item_path, exclude_hidden, exclude_patterns):
        #         continue
        #
        #     metadata = self._extract_metadata(item_path)
        #     existing = preserve_data.get(str(item_path), {})
        #
        #     item = CollectionItem(
        #         short_name=item_path.name,
        #         type="file",  # or "dir"
        #         size=item_path.stat().st_size,
        #         created=datetime.fromtimestamp(item_path.stat().st_ctime).isoformat(),
        #         modified=datetime.fromtimestamp(item_path.stat().st_mtime).isoformat(),
        #         accessed=datetime.fromtimestamp(item_path.stat().st_atime).isoformat(),
        #         path=str(item_path),
        #         description=existing.get('description'),
        #         category=existing.get('category'),
        #         metadata=metadata
        #     )
        #     items.append(item)

        return items

    def get_description_prompt_template(self) -> str:
        """Return the LLM prompt template for generating descriptions."""
        return """You are a technical documentation assistant. Generate a one-sentence description and category for a PLUGIN_NAME item based on its content and metadata.

Available categories (choose ONE):
<% get_categories().forEach(cat => { -%>
- <%= cat %>: Description of <%= cat %> category
<% }); %>

Item Metadata:
<% Object.keys(metadata).forEach(key => { -%>
<%= key %>: <%= metadata[key] %>
<% }); %>

Content Sample:
---
{content}
---

Generate a JSON response with:
1. "description": A single-sentence description (max 150 characters) that captures the item's core purpose.
2. "category": ONE category from the list above that best matches this item.

Example format:
{"description": "Example description for PLUGIN_NAME item", "category": "category1"}

JSON Response:"""

    def get_example_descriptions(self) -> List[str]:
        """Return example descriptions for this collection type."""
        return [
            # Replace with examples relevant to your collection type
            "Example description for a typical PLUGIN_NAME item",
            "Another example showing different content type",
            "Third example demonstrating variety in your collection"
        ]

    def get_content_for_description(self, item: CollectionItem) -> str:
        """
        Extract content from an item for LLM description generation.
        Return up to 3000 characters of relevant content.
        """
        item_path = Path(item.path)

        try:
            # TODO: Implement content extraction specific to your file types
            # For text files:
            # if item_path.suffix in ['.txt', '.md']:
            #     with open(item_path, 'r', encoding='utf-8', errors='ignore') as f:
            #         return f.read()[:3000]

            # For binary files, return descriptive text:
            # return f"PLUGIN_NAME file: {item_path.stem}"

            # Placeholder:
            return f"PLUGIN_NAME item: {item_path.stem}"

        except Exception:
            return f"PLUGIN_NAME item: {item_path.stem}"

    # Helper methods - implement as needed for your plugin

    def _find_items(self, root_path: Path) -> List[Path]:
        """Find all items that should be included in this collection."""
        items = []

        # TODO: Implement item discovery logic
        # Look for files with specific extensions, directories with certain structure, etc.

        return items

    def _should_exclude(self, item_path: Path, exclude_hidden: bool, exclude_patterns: List[str]) -> bool:
        """Check if an item should be excluded from scanning."""
        # Check hidden files
        if exclude_hidden and item_path.name.startswith('.'):
            return True

        # Check exclude patterns
        item_str = str(item_path)
        for pattern in exclude_patterns:
            # Simple glob matching - could use fnmatch or pathlib.Path.match
            if pattern in item_str:
                return True

        return False

    def _extract_metadata(self, item_path: Path) -> Dict[str, Any]:
        """Extract metadata specific to your collection type."""
        metadata = {}

        # TODO: Implement metadata extraction
        # File size, creation date, type-specific properties, etc.

        # Example:
        # stat = item_path.stat()
        # metadata['file_size'] = stat.st_size
        # metadata['created'] = datetime.fromtimestamp(stat.st_ctime).isoformat()
        # metadata['modified'] = datetime.fromtimestamp(stat.st_mtime).isoformat()

        return metadata


# Register plugin on import
PluginRegistry.register(
    name="PLUGIN_NAME",  # Replace with your plugin name
    scanner_class=PLUGIN_NAMEScanner,  # Replace with your class name
    version="1.0.0",
    description="PLUGIN_DESCRIPTION"  # Replace with your plugin description
)