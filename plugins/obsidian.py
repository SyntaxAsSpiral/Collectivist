#!/usr/bin/env python3
"""
Obsidian Vault Scanner Plugin
Scans Obsidian vaults and extracts rich metadata including frontmatter, tags, links, and knowledge graph structure.
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import yaml

from .plugin_interface import CollectionScanner, CollectionItem, PluginRegistry


class ObsidianScanner(CollectionScanner):
    """Scanner for Obsidian vault collections."""

    def get_name(self) -> str:
        return "obsidian"

    def get_supported_types(self) -> List[str]:
        return ["file"]

    def get_categories(self) -> List[str]:
        return [
            "knowledge_base",
            "personal_notes",
            "research_notes",
            "project_docs",
            "creative_writing",
            "learning_notes",
            "utilities_misc"
        ]

    def detect(self, path: Path) -> bool:
        """
        Detect if this path contains an Obsidian vault.
        Looks for .obsidian directory and .md files.
        """
        if not path.is_dir():
            return False

        # Check for .obsidian directory (Obsidian vault indicator)
        obsidian_dir = path / '.obsidian'
        if not obsidian_dir.exists() or not obsidian_dir.is_dir():
            return False

        # Check for markdown files
        md_files = list(path.glob('*.md'))
        if len(md_files) < 3:  # Require at least a few markdown files
            return False

        return True

    def scan(self, root_path: Path, config: Dict[str, Any]) -> List[CollectionItem]:
        """
        Scan Obsidian vault for markdown files.

        Config options:
        - exclude_hidden: bool (default True) - exclude files starting with '.'
        - exclude_patterns: list - additional patterns to exclude
        - preserve_data: dict - existing descriptions/categories to preserve
        """
        exclude_hidden = config.get('exclude_hidden', True)
        exclude_patterns = config.get('exclude_patterns', [])
        preserve_data = config.get('preserve_data', {})

        items = []

        # Default Obsidian exclusions
        default_exclusions = [
            '.obsidian/',
            '.git/',
            '.DS_Store',
            'Thumbs.db',
            '.obsidian/cache',
            '.obsidian/plugins',
            '.obsidian/themes',
            '.obsidian/workspace',
            '.obsidian/workspace.json',
        ]

        all_exclusions = default_exclusions + exclude_patterns

        # Find all .md files
        for root, dirs, files in os.walk(root_path):
            root_path_obj = Path(root)

            # Skip excluded directories
            dirs[:] = [d for d in dirs if not any(
                pattern in str(root_path_obj / d) for pattern in all_exclusions
            )]

            for file in files:
                if not file.endswith('.md'):
                    continue

                # Skip hidden files if configured
                if exclude_hidden and file.startswith('.'):
                    continue

                file_path = root_path_obj / file

                # Skip excluded files
                if any(pattern in str(file_path) for pattern in all_exclusions):
                    continue

                # Get file stats
                stat = file_path.stat()

                # Extract Obsidian-specific metadata
                obsidian_metadata = self._extract_obsidian_metadata(file_path)

                # Preserve existing description/category if available
                existing = preserve_data.get(str(file_path), {})

                # Create item
                item = CollectionItem(
                    short_name=file_path.stem,
                    type="file",
                    size=stat.st_size,
                    created=datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    modified=datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    accessed=datetime.fromtimestamp(stat.st_atime).isoformat(),
                    path=str(file_path),
                    description=existing.get('description'),
                    category=existing.get('category'),
                    metadata={
                        'file_extension': '.md',
                        'obsidian_metadata': obsidian_metadata,
                        'tags': obsidian_metadata.get('tags', []),
                        'links': obsidian_metadata.get('wiki_links', []),
                        'word_count': obsidian_metadata.get('word_count', 0),
                        'has_frontmatter': bool(obsidian_metadata.get('frontmatter')),
                    }
                )

                items.append(item)

        # Sort by modification time (most recent first)
        items.sort(key=lambda x: x.modified, reverse=True)

        return items

    def _extract_obsidian_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract Obsidian-specific metadata from a markdown file."""
        metadata = {}

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception:
            return metadata

        # Parse frontmatter
        frontmatter, body = self._parse_frontmatter(content)
        metadata['frontmatter'] = frontmatter

        # Extract tags
        metadata['tags'] = self._extract_tags(frontmatter, body)

        # Extract wiki links
        metadata['wiki_links'] = self._extract_wiki_links(body)

        # Basic content stats
        metadata['word_count'] = len(body.split())
        metadata['heading_count'] = len(re.findall(r'^\s*#+\s', body, re.MULTILINE))
        metadata['link_count'] = len(metadata['wiki_links'])

        # Check for dataview queries
        metadata['has_dataview'] = bool(re.search(r'```dataview', body, re.IGNORECASE))

        return metadata

    def _parse_frontmatter(self, content: str) -> tuple[Dict[str, Any], str]:
        """Parse YAML frontmatter from markdown content."""
        frontmatter = {}
        body = content

        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                try:
                    frontmatter = yaml.safe_load(parts[1]) or {}
                    body = parts[2].strip()
                except yaml.YAMLError:
                    pass  # Invalid YAML, keep empty frontmatter

        return frontmatter, body

    def _extract_tags(self, frontmatter: Dict[str, Any], body: str) -> List[str]:
        """Extract tags from frontmatter and body."""
        tags = set()

        # From frontmatter
        fm_tags = frontmatter.get('tags', [])
        if isinstance(fm_tags, str):
            tags.update(t.strip() for t in fm_tags.split(',') if t.strip())
        elif isinstance(fm_tags, list):
            tags.update(str(t).strip() for t in fm_tags if str(t).strip())

        # From body (#tag format)
        body_tags = re.findall(r'(?<!\w)#([a-zA-Z0-9_/-]+)', body)
        tags.update(body_tags)

        return sorted(list(tags))

    def _extract_wiki_links(self, body: str) -> List[str]:
        """Extract Obsidian wiki links from content."""
        # Match [[link]] or [[link|alias]]
        links = re.findall(r'\[\[([^\]]+)\]\]', body)
        # Remove aliases, keep just the link targets
        return [link.split('|')[0].strip() for link in links]

    def get_description_prompt_template(self) -> str:
        return """You are a technical documentation assistant. Generate a one-sentence description and category for an Obsidian note based on its content and metadata.

Available categories (choose ONE):
- knowledge_base: Core knowledge, concepts, and foundational information
- personal_notes: Personal thoughts, reflections, and journaling
- research_notes: Research findings, studies, and academic content
- project_docs: Project documentation, plans, and specifications
- creative_writing: Stories, poems, creative writing, and fiction
- learning_notes: Study notes, tutorials, and learning materials
- utilities_misc: Templates, utilities, and miscellaneous notes

Note Metadata:
Tags: {metadata_tags}
Word Count: {word_count}
Has Frontmatter: {has_frontmatter}
Links: {link_count}

Content Sample:
---
{content}
---

Generate a JSON response with:
1. "description": A single-sentence description (max 150 characters) that captures the note's core purpose. Be concise and capture the essence of the knowledge contained.
2. "category": ONE category from the list above that best matches this note.

Example format:
{"description": "Comprehensive guide to knowledge management systems and note-taking methodologies", "category": "knowledge_base"}

JSON Response:"""

    def get_example_descriptions(self) -> List[str]:
        return [
            "Comprehensive guide to personal knowledge management systems and workflows",
            "Technical documentation for project architecture and implementation details",
            "Personal reflections on learning experiences and growth mindset development",
            "Research notes on machine learning algorithms and their applications",
            "Creative writing piece exploring themes of technology and human connection",
            "Study notes on advanced mathematics and theoretical computer science",
            "Utility template for daily planning and task management workflows"
        ]

    def get_content_for_description(self, item: CollectionItem) -> str:
        """
        Extract content from Obsidian note for LLM description generation.
        Returns first 3000 chars, prioritizing content after frontmatter.
        """
        try:
            with open(item.path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception:
            return item.short_name

        # Parse frontmatter and return body
        _, body = self._parse_frontmatter(content)
        return body[:3000] if body else content[:3000]


# Register plugin on import
PluginRegistry.register(
    name="obsidian",
    scanner_class=ObsidianScanner,
    version="1.0.0",
    description="Scanner for Obsidian vault collections with rich metadata extraction"
)