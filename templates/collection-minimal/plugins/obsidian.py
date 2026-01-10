"""
Obsidian Vault Scanner - Knowledge Base Collection Plugin

Scans Obsidian vaults and extracts rich metadata including
frontmatter, tags, links, and knowledge graph structure.
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
import yaml

from .generic import GenericIndexer


class ObsidianIndexer(GenericIndexer):
    """Indexer for Obsidian vault collections."""

    def __init__(self, collection_path: Path, config: Dict[str, Any]):
        """Initialize Obsidian indexer.

        Args:
            collection_path: Path to vault directory
            config: Collection configuration
        """
        super().__init__(collection_path, config)
        self.exclude_patterns = [
            ".obsidian/",
            ".git/",
            ".DS_Store",
            "Thumbs.db",
            ".obsidian/cache",
            ".obsidian/plugins",
            ".obsidian/themes",
            ".obsidian/workspace",
        ] + self.exclude_patterns

    def discover_items(self) -> List[Path]:
        """Discover Markdown files in the Obsidian vault."""
        items = []

        # Find all .md files
        for root, dirs, files in os.walk(self.collection_path):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if not any(pattern in os.path.join(root, d) for pattern in self.exclude_patterns)]

            for file in files:
                if file.endswith('.md'):
                    file_path = Path(root) / file
                    items.append(file_path)

        return sorted(items)

    def extract_metadata(self, item_path: Path) -> Dict[str, Any]:
        """Extract Obsidian-specific metadata from a note."""
        metadata = super().extract_metadata(item_path)

        try:
            with open(item_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parse frontmatter
            frontmatter = self._parse_frontmatter(content)
            if frontmatter:
                metadata.update(frontmatter)

            # Extract Obsidian-specific metadata
            obsidian_meta = self._extract_obsidian_metadata(content, item_path)
            metadata.update(obsidian_meta)

        except Exception as e:
            metadata["error"] = f"Failed to parse: {e}"

        return metadata

    def _parse_frontmatter(self, content: str) -> Optional[Dict[str, Any]]:
        """Parse YAML frontmatter from Obsidian note."""
        # Look for --- delimited frontmatter at the start
        if not content.startswith('---'):
            return None

        try:
            # Find the end of frontmatter
            end_pos = content.find('---', 3)
            if end_pos == -1:
                return None

            frontmatter_text = content[3:end_pos].strip()
            return yaml.safe_load(frontmatter_text) or {}

        except Exception:
            return None

    def _extract_obsidian_metadata(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Extract Obsidian-specific metadata from note content."""
        metadata = {}

        # Extract tags (both #tag and frontmatter tags)
        tags = self._extract_tags(content)
        if tags:
            metadata["tags"] = tags

        # Extract wiki links ([[link]])
        links = self._extract_wiki_links(content)
        if links:
            metadata["wiki_links"] = links

        # Extract aliases
        aliases = self._extract_aliases(content)
        if aliases:
            metadata["aliases"] = aliases

        # Extract dataview queries
        dataview_queries = self._extract_dataview_queries(content)
        if dataview_queries:
            metadata["dataview_queries"] = dataview_queries

        # Calculate note statistics
        stats = self._calculate_note_stats(content, file_path)
        metadata.update(stats)

        return metadata

    def _extract_tags(self, content: str) -> List[str]:
        """Extract tags from content (#tag format)."""
        # Find all #tag patterns (not inside code blocks or links)
        tag_pattern = r'(?<![\w#\\])\#([\w\-/]+)'
        tags = re.findall(tag_pattern, content)
        return list(set(tags))  # Remove duplicates

    def _extract_wiki_links(self, content: str) -> List[str]:
        """Extract wiki-style links ([[link]])."""
        link_pattern = r'\[\[([^\]]+)\]\]'
        links = re.findall(link_pattern, content)

        # Clean up links (remove aliases like [[Note|Alias]])
        cleaned_links = []
        for link in links:
            # Take the first part before | if it exists
            actual_link = link.split('|')[0].strip()
            cleaned_links.append(actual_link)

        return cleaned_links

    def _extract_aliases(self, content: str) -> List[str]:
        """Extract aliases from frontmatter or content."""
        # Look for aliases in content (after | in wiki links)
        alias_pattern = r'\[\[[^\]]+\|([^\]]+)\]\]'
        aliases = re.findall(alias_pattern, content)
        return list(set(aliases))

    def _extract_dataview_queries(self, content: str) -> List[str]:
        """Extract dataview query blocks."""
        # Look for dataview code blocks
        dataview_pattern = r'```\s*dataview\s*\n(.*?)\n```'
        matches = re.findall(dataview_pattern, content, re.DOTALL)
        return matches

    def _calculate_note_stats(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Calculate statistics for the note."""
        stats = {}

        # Basic text statistics
        lines = content.split('\n')
        stats["line_count"] = len(lines)

        # Remove frontmatter for content stats
        content_without_frontmatter = self._remove_frontmatter(content)
        words = re.findall(r'\b\w+\b', content_without_frontmatter)
        stats["word_count"] = len(words)

        # Heading analysis
        headings = re.findall(r'^#{1,6}\s+(.+)$', content, re.MULTILINE)
        stats["heading_count"] = len(headings)
        if headings:
            stats["headings"] = headings[:10]  # Limit to first 10

        # Link analysis
        internal_links = len(re.findall(r'\[\[([^\]]+)\]\]', content))
        external_links = len(re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content))
        stats["internal_links"] = internal_links
        stats["external_links"] = external_links

        # File metadata
        stat_info = file_path.stat()
        stats["file_size"] = stat_info.st_size
        stats["created"] = stat_info.st_ctime
        stats["modified"] = stat_info.st_mtime

        return stats

    def _remove_frontmatter(self, content: str) -> str:
        """Remove YAML frontmatter from content."""
        if not content.startswith('---'):
            return content

        end_pos = content.find('---', 3)
        if end_pos == -1:
            return content

        return content[end_pos + 3:].strip()

    def check_status(self, item_path: Path) -> Dict[str, Any]:
        """Check the status of an Obsidian note."""
        status = {"readable": True, "valid": True}

        try:
            with open(item_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check if it's valid Markdown
            if not content.strip():
                status["valid"] = False
                status["issues"] = ["Empty file"]

            # Check frontmatter validity
            if content.startswith('---'):
                try:
                    frontmatter = self._parse_frontmatter(content)
                    if frontmatter is None:
                        status["frontmatter_valid"] = False
                    else:
                        status["frontmatter_valid"] = True
                except Exception:
                    status["frontmatter_valid"] = False

        except UnicodeDecodeError:
            status["readable"] = False
            status["issues"] = ["Encoding error"]
        except Exception as e:
            status["readable"] = False
            status["issues"] = [str(e)]

        return status

    def generate_content_sample(self, item_path: Path) -> str:
        """Generate a content sample for an Obsidian note."""
        try:
            with open(item_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Remove frontmatter for sample
            content = self._remove_frontmatter(content)

            # Take first meaningful paragraph
            paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]

            # Prefer paragraph with links or tags
            for para in paragraphs[:3]:
                if '[[' in para or '#' in para:
                    return para[:500] + "..." if len(para) > 500 else para

            # Fallback to first paragraph
            if paragraphs:
                para = paragraphs[0]
                return para[:500] + "..." if len(para) > 500 else para

            return "No content sample available"

        except Exception:
            return "Error generating content sample"