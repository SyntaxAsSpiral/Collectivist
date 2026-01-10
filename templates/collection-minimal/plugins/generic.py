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
        """Discover items with intelligent depth control for custom collections."""
        items = []

        # Analyze collection structure first to determine safe recursion depth
        structure_analysis = self._analyze_collection_structure()

        # Start conservative, expand only if safe
        max_depth = 1  # Start with just immediate children

        # If collection seems safe to recurse deeper, increase depth
        if structure_analysis['safe_to_recurse']:
            max_depth = min(3, structure_analysis['recommended_depth'])

        def should_include_path(path: Path) -> bool:
            """Check if path should be included based on intelligent analysis."""
            if self._should_skip(path):
                return False

            try:
                rel_path = path.relative_to(self.collection_path)
                depth = len(rel_path.parts)
            except ValueError:
                return False

            return depth <= max_depth

        # Walk with intelligent depth control
        for root, dirs, files in os.walk(self.collection_path):
            root_path = Path(root)

            if not should_include_path(root_path):
                dirs[:] = []  # Don't recurse deeper
                continue

            # Add this directory as an item if it contains interesting content
            if self._directory_is_interesting(root_path, files, dirs):
                items.append(root_path)

                # If this directory has many files, don't add individual files
                if len(files) > 10:
                    continue

            # Add representative files from this directory
            file_items = self._select_representative_files(root_path, files)
            items.extend(file_items)

        # Ensure we have at least some items
        if not items:
            items = self._fallback_discovery()

        return items

    def _analyze_collection_structure(self) -> Dict[str, Any]:
        """Analyze collection structure to determine safe recursion strategy."""
        analysis = {
            'total_files': 0,
            'total_dirs': 0,
            'deeply_nested': False,
            'has_many_files': False,
            'safe_to_recurse': False,
            'recommended_depth': 1
        }

        max_files_per_dir = 0
        max_depth_seen = 0

        for root, dirs, files in os.walk(self.collection_path):
            if self._should_skip(Path(root)):
                dirs[:] = []
                continue

            try:
                rel_path = Path(root).relative_to(self.collection_path)
                depth = len(rel_path.parts)
                max_depth_seen = max(max_depth_seen, depth)

                file_count = len([f for f in files if not f.startswith('.')])
                max_files_per_dir = max(max_files_per_dir, file_count)

                analysis['total_files'] += file_count
                analysis['total_dirs'] += len(dirs)

                # Stop analysis if we see signs of deep nesting
                if depth > 3 or analysis['total_files'] > 1000:
                    analysis['deeply_nested'] = True
                    break

            except ValueError:
                continue

        # Determine if it's safe to recurse
        analysis['has_many_files'] = analysis['total_files'] > 100
        analysis['safe_to_recurse'] = (
            not analysis['deeply_nested'] and
            not analysis['has_many_files'] and
            max_depth_seen <= 2
        )

        if analysis['safe_to_recurse']:
            analysis['recommended_depth'] = 2
        elif analysis['total_dirs'] > analysis['total_files']:
            # Many directories, few files - probably safe to go to depth 2
            analysis['recommended_depth'] = 2

        return analysis

    def _directory_is_interesting(self, dir_path: Path, files: List[str], dirs: List[str]) -> bool:
        """Determine if a directory should be treated as a collection item."""
        # Empty directories aren't interesting
        if not files and not dirs:
            return False

        # Directories with many subdirs are interesting (organizational units)
        if len(dirs) > 5:
            return True

        # Directories with important files are interesting
        important_files = ['readme.md', 'readme.txt', 'package.json', 'setup.py', 'dockerfile']
        has_important_files = any(f.lower() in important_files for f in files)

        # Directories with many files might be content containers
        has_many_files = len([f for f in files if not f.startswith('.')]) > 5

        return has_important_files or has_many_files or bool(dirs)

    def _select_representative_files(self, dir_path: Path, files: List[str]) -> List[Path]:
        """Select a few representative files from a directory."""
        selected_files = []

        # Filter out hidden files and common uninteresting files
        interesting_files = [
            f for f in files
            if not f.startswith('.') and
            not f.lower().endswith(('.tmp', '.temp', '.log', '.cache', '.lock'))
        ]

        # Prioritize certain file types
        priority_files = []
        other_files = []

        for f in interesting_files[:10]:  # Limit to first 10 to avoid overload
            if f.lower() in ['readme.md', 'readme.txt', 'package.json', 'setup.py']:
                priority_files.append(f)
            else:
                other_files.append(f)

        # Select up to 3 files, prioritizing important ones
        selected_names = (priority_files + other_files)[:3]

        for filename in selected_names:
            file_path = dir_path / filename
            if file_path.exists():
                selected_files.append(file_path)

        return selected_files

    def _fallback_discovery(self) -> List[Path]:
        """Fallback: just return immediate children."""
        items = []
        try:
            for item in self.collection_path.iterdir():
                if not item.name.startswith('.') and not self._should_skip(item):
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