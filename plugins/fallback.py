#!/usr/bin/env python3
"""
Fallback Scanner Plugin
Generic scanner for collections that don't match specific types
"""

import os
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

from plugin_interface import CollectionScanner, CollectionItem, PluginRegistry


class FallbackScanner(CollectionScanner):
    """Fallback scanner for mixed or unidentified collections"""

    def get_name(self) -> str:
        return "fallback"

    def get_supported_types(self) -> List[str]:
        return ["dir", "file"]

    def get_categories(self) -> List[str]:
        return [
            "documents",
            "media_files", 
            "code_projects",
            "data_files",
            "archives",
            "configuration",
            "utilities",
            "miscellaneous"
        ]

    def detect(self, path: Path) -> bool:
        """
        Fallback scanner always returns True - it's the last resort.
        """
        return True

    def get_directory_size(self, path: Path) -> int:
        """Calculate total size of directory"""
        total = 0
        try:
            for entry in path.rglob('*'):
                if entry.is_file():
                    total += entry.stat().st_size
        except (PermissionError, OSError):
            pass
        return total

    def get_file_type_category(self, path: Path) -> str:
        """Determine category based on file extension"""
        if path.is_dir():
            return "directories"
        
        ext = path.suffix.lower()
        
        # Document extensions
        if ext in ['.pdf', '.doc', '.docx', '.txt', '.md', '.rtf']:
            return "documents"
        
        # Media extensions
        elif ext in ['.mp3', '.mp4', '.avi', '.mkv', '.jpg', '.png', '.gif']:
            return "media_files"
        
        # Code extensions
        elif ext in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs']:
            return "code_projects"
        
        # Data extensions
        elif ext in ['.csv', '.json', '.xml', '.yaml', '.yml', '.sql']:
            return "data_files"
        
        # Archive extensions
        elif ext in ['.zip', '.tar', '.gz', '.rar', '.7z']:
            return "archives"
        
        # Config extensions
        elif ext in ['.conf', '.cfg', '.ini', '.toml']:
            return "configuration"
        
        # Executable extensions
        elif ext in ['.exe', '.msi', '.deb', '.rpm', '.dmg']:
            return "utilities"
        
        else:
            return "miscellaneous"

    def scan(self, root_path: Path, config: Dict[str, Any]) -> List[CollectionItem]:
        """
        Scan collection using fallback logic.
        
        Config options:
        - exclude_hidden: bool (default True) - exclude files/dirs starting with '.'
        - preserve_data: dict - existing descriptions/categories to preserve
        - max_depth: int (default 2) - maximum directory depth to scan
        """
        exclude_hidden = config.get('exclude_hidden', True)
        preserve_data = config.get('preserve_data', {})
        max_depth = config.get('max_depth', 2)

        items = []

        # Scan directory up to max_depth
        for item_path in root_path.rglob('*'):
            # Skip if too deep
            try:
                relative_path = item_path.relative_to(root_path)
                if len(relative_path.parts) > max_depth:
                    continue
            except ValueError:
                continue

            # Skip hidden files/dirs if configured
            if exclude_hidden and any(part.startswith('.') for part in relative_path.parts):
                continue

            # Skip if it's the root path itself
            if item_path == root_path:
                continue

            # Get filesystem metadata
            try:
                stat = item_path.stat()
            except (PermissionError, OSError):
                continue

            # Determine size
            if item_path.is_dir():
                size = self.get_directory_size(item_path)
                item_type = "dir"
            else:
                size = stat.st_size
                item_type = "file"

            # Determine category based on file type
            auto_category = self.get_file_type_category(item_path)

            # Preserve existing description/category if available
            existing = preserve_data.get(str(item_path), {})

            # Create item
            item = CollectionItem(
                short_name=item_path.name,
                type=item_type,
                size=size,
                created=datetime.fromtimestamp(stat.st_ctime).isoformat(),
                modified=datetime.fromtimestamp(stat.st_mtime).isoformat(),
                accessed=datetime.fromtimestamp(stat.st_atime).isoformat(),
                path=str(item_path),
                description=existing.get('description'),
                category=existing.get('category', auto_category),
                metadata={
                    'extension': item_path.suffix.lower() if item_path.is_file() else None,
                    'auto_category': auto_category,
                    'readonly': not os.access(item_path, os.W_OK),
                    'depth': len(relative_path.parts)
                }
            )

            items.append(item)

        # Sort by size descending
        items.sort(key=lambda x: x.size, reverse=True)

        return items

    def get_description_prompt_template(self) -> str:
        return """You are a file organization assistant. Generate a one-sentence description and category for this item based on its name, type, and any available content.

Available categories (choose ONE):
- documents: Text documents, PDFs, notes, manuals
- media_files: Images, videos, audio files
- code_projects: Source code, scripts, development projects
- data_files: CSV, JSON, databases, structured data
- archives: ZIP files, compressed archives
- configuration: Config files, settings, preferences
- utilities: Executable programs, tools, applications
- miscellaneous: Other files that don't fit specific categories

Item information:
---
{content}
---

Generate a JSON response with:
1. "description": A single-sentence description (max 150 characters) that captures the item's purpose or content. Be concise and descriptive.
2. "category": ONE category from the list above that best matches this item.

Example format:
{{"description": "Configuration file for application settings and preferences", "category": "configuration"}}

JSON Response:"""

    def get_example_descriptions(self) -> List[str]:
        return [
            "PDF document containing technical specifications and user manual",
            "Image file with high-resolution photograph or artwork",
            "Python script for data processing and analysis automation",
            "JSON configuration file with application settings",
            "Compressed archive containing project files and resources"
        ]

    def get_content_for_description(self, item: CollectionItem) -> str:
        """
        Extract content for LLM description generation.
        Returns basic file information and first few lines for text files.
        """
        item_path = Path(item.path)
        
        content_parts = [
            f"Name: {item_path.name}",
            f"Type: {item.type}",
            f"Size: {item.size} bytes"
        ]
        
        if item.metadata:
            if item.metadata.get('extension'):
                content_parts.append(f"Extension: {item.metadata['extension']}")
        
        # Try to read first few lines for text files
        if item_path.is_file() and item.size < 1024 * 1024:  # Only for files < 1MB
            try:
                with open(item_path, 'r', encoding='utf-8', errors='ignore') as f:
                    first_lines = []
                    for i, line in enumerate(f):
                        if i >= 10:  # Only first 10 lines
                            break
                        first_lines.append(line.strip())
                    
                    if first_lines:
                        content_parts.append("Content preview:")
                        content_parts.extend(first_lines)
            except Exception:
                pass
        
        return '\n'.join(content_parts)


# Register plugin on import
PluginRegistry.register(
    name="fallback",
    scanner_class=FallbackScanner,
    version="1.0.0",
    description="Fallback scanner for mixed or unidentified collections"
)