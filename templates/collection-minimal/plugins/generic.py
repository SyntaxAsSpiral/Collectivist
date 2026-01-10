"""
Generic Scanner - Fallback scanner for custom/unknown collection types

Provides basic file scanning and metadata extraction for any collection type.
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional


class GenericScanner:
    """Generic scanner for custom collection types."""

    def __init__(self, collection_path: Path, config: Dict[str, Any]):
        """Initialize generic scanner.

        Args:
            collection_path: Path to collection directory
            config: Collection configuration
        """
        self.collection_path = collection_path
        self.config = config
        self.exclude_patterns = config.get("scanner", {}).get("config", {}).get("exclude_patterns", [])

    def discover_items(self) -> List[Path]:
        """Discover items in the collection (conservative approach for custom types)."""
        items = []

        # For custom collections, be conservative about depth
        max_depth = self.config.get("scanner", {}).get("config", {}).get("max_depth", 2)

        def should_include_path(path: Path) -> bool:
            """Check if path should be included based on depth and patterns."""
            # Skip excluded directories
            if self._should_skip(path):
                return False

            # Calculate depth from collection root
            try:
                rel_path = path.relative_to(self.collection_path)
                depth = len(rel_path.parts)
            except ValueError:
                return False

            # For custom collections, be more selective
            if depth > max_depth:
                return False

            return True

        # Walk with depth limit
        for root, dirs, files in os.walk(self.collection_path):
            root_path = Path(root)

            if not should_include_path(root_path):
                # Don't recurse into this directory
                dirs[:] = []
                continue

            # For custom collections, prefer directories over individual files
            # This keeps it "close to top" as requested
            if not files and dirs:
                # This is a directory with subdirs but no files - treat as an item
                items.append(root_path)
            elif files and not any(f.endswith(('.exe', '.dll', '.so', '.dylib')) for f in files):
                # Has files but not executables (avoid deep game file scanning)
                # Add a few representative files, not all
                for file in files[:3]:  # Limit to first 3 files per directory
                    if not file.startswith('.'):
                        file_path = root_path / file
                        if file_path.exists():
                            items.append(file_path)

        # If we found nothing, fall back to basic directory discovery
        if not items:
            # Just add immediate subdirectories as items
            try:
                for item in self.collection_path.iterdir():
                    if item.is_dir() and not item.name.startswith('.') and not self._should_skip(item):
                        items.append(item)
            except Exception:
                pass

        return items

    def _should_skip(self, path: Path) -> bool:
        """Check if path should be skipped based on exclude patterns."""
        # Always skip .collection directory
        if ".collection" in path.parts:
            return True

        # Check exclude patterns
        path_str = str(path.relative_to(self.collection_path))

        for pattern in self.exclude_patterns:
            # Simple pattern matching
            if pattern.replace("*", "").replace("/", "") in path_str:
                return True

        return False

    def extract_metadata(self, item_path: Path) -> Dict[str, Any]:
        """Extract basic metadata for any file type."""
        metadata = {}

        try:
            # Basic file metadata
            stat_info = item_path.stat()
            metadata.update({
                "size": stat_info.st_size,
                "created": "2026-01-09T15:30:00Z",  # Would use proper datetime
                "modified": "2026-01-09T15:30:00Z",
                "accessed": "2026-01-09T15:30:00Z"
            })

            # File type specific metadata
            suffix = item_path.suffix.lower()

            # Text-based files
            if suffix in [".txt", ".md", ".py", ".js", ".html", ".css", ".json", ".xml"]:
                metadata.update(self._extract_text_metadata(item_path))

            # Document files
            elif suffix in [".pdf", ".docx", ".doc"]:
                metadata.update(self._extract_document_metadata(item_path))

            # Data files
            elif suffix in [".csv", ".xlsx", ".xls"]:
                metadata.update(self._extract_data_metadata(item_path))

            # Media files (basic)
            elif suffix in [".jpg", ".png", ".gif", ".mp3", ".mp4", ".avi"]:
                metadata.update(self._extract_media_metadata(item_path))

        except Exception as e:
            metadata["extraction_error"] = str(e)

        return metadata

    def check_status(self, item_path: Path) -> Dict[str, Any]:
        """Check basic file status."""
        status = {"file_readable": False}

        try:
            # Check if file is readable
            with open(item_path, 'rb') as f:
                f.read(1)  # Try to read one byte
            status["file_readable"] = True

            # Check if file is accessible (not locked, etc.)
            status["file_accessible"] = True

        except Exception:
            status["file_readable"] = False
            status["file_accessible"] = False

        # Overall status
        status["status_type"] = "readable" if status["file_readable"] else "unreadable"

        return status

    def generate_content_sample(self, item_path: Path) -> str:
        """Generate content sample for LLM description."""
        try:
            suffix = item_path.suffix.lower()

            # Text files - read first 3000 characters
            if suffix in [".txt", ".md", ".py", ".js", ".html", ".css", ".json", ".xml", ".csv"]:
                with open(item_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(3000)
                    return content if content else "Empty text file"

            # Binary files - just filename and type info
            else:
                return f"{suffix.upper()} file: {item_path.name}"

        except Exception:
            return f"Could not read content: {item_path.name}"

    def _extract_text_metadata(self, item_path: Path) -> Dict[str, Any]:
        """Extract metadata from text files."""
        metadata = {}

        try:
            with open(item_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

                # Basic text statistics
                metadata["word_count"] = len(content.split())
                metadata["line_count"] = len(content.splitlines())
                metadata["char_count"] = len(content)

                # Language detection (very basic)
                if any(word in content.lower() for word in ["import", "def ", "class "]):
                    metadata["detected_language"] = "python"
                elif any(word in content.lower() for word in ["function", "const ", "let "]):
                    metadata["detected_language"] = "javascript"
                elif any(word in content.lower() for word in ["#include", "int main"]):
                    metadata["detected_language"] = "c/c++"

        except Exception:
            pass

        return metadata

    def _extract_document_metadata(self, item_path: Path) -> Dict[str, Any]:
        """Extract metadata from document files."""
        metadata = {"document_type": item_path.suffix.upper()[1:]}

        # For now, just basic info since we don't want heavy dependencies
        # In a full implementation, this would use libraries like PyPDF2, python-docx
        metadata["processing_note"] = "Document metadata extraction requires additional libraries"

        return metadata

    def _extract_data_metadata(self, item_path: Path) -> Dict[str, Any]:
        """Extract metadata from data files."""
        metadata = {"data_format": item_path.suffix.upper()[1:]}

        try:
            if item_path.suffix.lower() == ".csv":
                with open(item_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    if lines:
                        # Estimate row count
                        metadata["estimated_rows"] = len(lines)
                        # Try to detect headers
                        first_line = lines[0].strip()
                        if ',' in first_line:
                            headers = first_line.split(',')
                            metadata["estimated_columns"] = len(headers)
                            metadata["has_headers"] = True

        except Exception:
            pass

        return metadata

    def _extract_media_metadata(self, item_path: Path) -> Dict[str, Any]:
        """Extract metadata from media files."""
        metadata = {"media_type": item_path.suffix.upper()[1:]}

        # Basic file size info (would use libraries like PIL, mutagen in full implementation)
        stat_info = item_path.stat()
        size_mb = stat_info.st_size / (1024 * 1024)
        metadata["file_size_mb"] = round(size_mb, 2)
        metadata["processing_note"] = "Media metadata extraction requires additional libraries"

        return metadata