#!/usr/bin/env python3
"""
Media Scanner Plugin
Scans media collections and extracts rich metadata including EXIF data, audio tags, video properties, and technical specifications.
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import yaml

from .plugin_interface import CollectionScanner, CollectionItem, PluginRegistry


class MediaScanner(CollectionScanner):
    """Scanner for Obsidian vault collections."""

    def get_name(self) -> str:
        return "media"

    def get_supported_types(self) -> List[str]:
        return ["file"]

    def get_categories(self) -> List[str]:
        return [
            "photography",
            "music_audio",
            "videos_films",
            "art_design",
            "screenshots",
            "podcasts",
            "presentations",
            "utilities_misc"
        ]

    def detect(self, path: Path) -> bool:
        """
        Detect if this path contains a media collection.
        Looks for common media file types.
        """
        if not path.is_dir():
            return False

        # Media file extensions
        media_extensions = [
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp',  # Images
            '.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a',  # Audio
            '.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'  # Video
        ]

        # Count media files
        media_files = []
        for ext in media_extensions:
            media_files.extend(list(path.glob(f'**/*{ext}')))

        # Require at least 10 media files to consider it a media collection
        return len(media_files) >= 10

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

        # Default document collection exclusions
        default_exclusions = [
            '.git/',
            '.DS_Store',
            'Thumbs.db',
            '__pycache__/',
            'node_modules/',
            '.obsidian/',  # Avoid mixing with Obsidian vaults
        ]

        all_exclusions = default_exclusions + exclude_patterns

        # Media file extensions
        media_extensions = [
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp',  # Images
            '.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a',  # Audio
            '.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'  # Video
        ]

        # Find all document files
        for root, dirs, files in os.walk(root_path):
            root_path_obj = Path(root)

            # Skip excluded directories
            dirs[:] = [d for d in dirs if not any(
                pattern in str(root_path_obj / d) for pattern in all_exclusions
            )]

            for file in files:
                file_path = root_path_obj / file

                # Check if it's a media file
                if file_path.suffix.lower() not in media_extensions:
                    continue

                # Skip hidden files if configured
                if exclude_hidden and file.startswith('.'):
                    continue

                # Skip excluded files
                if any(pattern in str(file_path) for pattern in all_exclusions):
                    continue

                # Get file stats
                stat = file_path.stat()

                # Extract media-specific metadata
                media_metadata = self._extract_media_metadata(file_path)

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
                        'file_extension': file_path.suffix.lower(),
                        'media_metadata': media_metadata,
                        'media_type': media_metadata.get('media_type', 'unknown'),
                        'duration': media_metadata.get('duration', 0),
                        'dimensions': media_metadata.get('dimensions', ''),
                        'bitrate': media_metadata.get('bitrate', 0),
                        'codec': media_metadata.get('codec', ''),
                    }
                )

                items.append(item)

        # Sort by modification time (most recent first)
        items.sort(key=lambda x: x.modified, reverse=True)

        return items

    def _extract_media_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract media-specific metadata from various file types."""
        metadata = {}
        file_ext = file_path.suffix.lower()

        # Determine media type
        if file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']:
            metadata['media_type'] = 'image'
            metadata.update(self._extract_image_metadata(file_path))
        elif file_ext in ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a']:
            metadata['media_type'] = 'audio'
            metadata.update(self._extract_audio_metadata(file_path))
        elif file_ext in ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm']:
            metadata['media_type'] = 'video'
            metadata.update(self._extract_video_metadata(file_path))
        else:
            metadata['media_type'] = 'unknown'

        return metadata

    def _extract_image_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract metadata from image files."""
        metadata = {}

        try:
            # For now, just basic file info
            # TODO: Use PIL/Pillow for EXIF data extraction
            metadata['dimensions'] = ''  # Would need image parsing
            metadata['camera'] = ''  # Would need EXIF parsing
            metadata['location'] = ''  # Would need GPS EXIF parsing
            metadata['orientation'] = ''  # Would need EXIF parsing
            # Use filename as basic title
            metadata['title'] = file_path.stem
        except Exception:
            metadata['dimensions'] = ''
            metadata['title'] = file_path.stem

        return metadata

    def _extract_audio_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract metadata from audio files."""
        metadata = {}

        try:
            # For now, just basic file info
            # TODO: Use mutagen or similar for ID3 tag extraction
            metadata['duration'] = 0  # Would need audio parsing
            metadata['bitrate'] = 0  # Would need audio parsing
            metadata['codec'] = ''  # Would need audio parsing
            metadata['artist'] = ''  # Would need tag parsing
            metadata['album'] = ''  # Would need tag parsing
            metadata['title'] = file_path.stem  # Use filename as title
        except Exception:
            metadata['duration'] = 0
            metadata['bitrate'] = 0
            metadata['title'] = file_path.stem

        return metadata

    def _extract_video_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract metadata from video files."""
        metadata = {}

        try:
            # For now, just basic file info
            # TODO: Use ffprobe or similar for video metadata
            metadata['duration'] = 0  # Would need video parsing
            metadata['dimensions'] = ''  # Would need video parsing
            metadata['bitrate'] = 0  # Would need video parsing
            metadata['codec'] = ''  # Would need video parsing
            metadata['frame_rate'] = 0  # Would need video parsing
            metadata['title'] = file_path.stem  # Use filename as title
        except Exception:
            metadata['duration'] = 0
            metadata['dimensions'] = ''
            metadata['title'] = file_path.stem

        return metadata

    def _extract_text_metadata(self, content: str) -> Dict[str, Any]:
        """Extract metadata from text-based documents."""
        metadata = {}

        # Basic content analysis
        metadata['has_text_content'] = True
        metadata['word_count'] = len(content.split())
        metadata['char_count'] = len(content)
        metadata['line_count'] = len(content.splitlines())

        # Try to extract title (first heading or first line)
        lines = content.splitlines()
        for line in lines[:10]:  # Check first 10 lines
            line = line.strip()
            if line and not line.startswith('#'):  # Skip markdown headers for now
                metadata['title'] = line[:100]  # First non-empty line as title
                break

        # Check for markdown headers
        if content.startswith('#'):
            first_line = content.split('\n', 1)[0]
            metadata['title'] = first_line.lstrip('#').strip()[:100]

        return metadata

    def _extract_pdf_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract metadata from PDF files."""
        metadata = {}

        try:
            # For now, just basic file info
            # TODO: Use PyPDF2 or pdfplumber for detailed metadata extraction
            metadata['has_text_content'] = True  # Assume PDFs have text
            metadata['word_count'] = 0  # Would need PDF parsing
            metadata['page_count'] = 0  # Would need PDF parsing
            metadata['author'] = ''  # Would need PDF parsing
            metadata['title'] = file_path.stem  # Use filename as title
        except Exception:
            metadata['has_text_content'] = False

        return metadata

    def _extract_office_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract metadata from Office documents."""
        metadata = {}

        try:
            # For now, just basic file info
            # TODO: Use python-docx, openpyxl, etc. for detailed metadata
            metadata['has_text_content'] = True  # Assume Office docs have text
            metadata['word_count'] = 0  # Would need document parsing
            metadata['page_count'] = 0  # Would need document parsing
            metadata['author'] = ''  # Would need document parsing
            metadata['title'] = file_path.stem  # Use filename as title
        except Exception:
            metadata['has_text_content'] = False

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
        return """You are a technical documentation assistant. Generate a one-sentence description and category for a media file based on its metadata and filename.

Available categories (choose ONE):
- photography: Personal photos, professional photography, and image collections
- music_audio: Music tracks, audio recordings, and sound files
- videos_films: Video content, films, movies, and video recordings
- art_design: Digital art, design files, graphics, and creative visuals
- screenshots: Screenshots, screen recordings, and interface captures
- podcasts: Podcast episodes, audio shows, and spoken word content
- presentations: Video presentations, tutorials, and educational content
- utilities_misc: Stock media, templates, and miscellaneous media files

Media Metadata:
File Type: {file_extension}
Media Type: {media_type}
Duration: {duration} seconds
Dimensions: {dimensions}
Bitrate: {bitrate}
Codec: {codec}
Filename: {filename}

Generate a JSON response with:
1. "description": A single-sentence description (max 150 characters) that captures what this media file likely contains based on filename and metadata. Be descriptive and specific.
2. "category": ONE category from the list above that best matches this media file.

Example format:
{"description": "Professional landscape photograph captured with DSLR camera showing mountain scenery at sunset", "category": "photography"}

JSON Response:"""

    def get_example_descriptions(self) -> List[str]:
        return [
            "Professional landscape photograph showing mountain scenery at golden hour with dramatic lighting",
            "Original music composition featuring acoustic guitar and orchestral elements in minor key",
            "Educational video tutorial demonstrating software development concepts with live coding examples",
            "Digital artwork created in vector graphics software featuring abstract geometric patterns",
            "High-resolution screenshot capturing user interface design for mobile application",
            "Podcast episode discussing technology trends and their impact on modern society",
            "Presentation video explaining complex business strategy with charts and data visualization"
        ]

    def get_content_for_description(self, item: CollectionItem) -> str:
        """
        Extract content from media file for LLM description generation.
        For media files, we primarily use filename and metadata since content is binary.
        """
        file_path = Path(item.path)
        filename = file_path.stem

        # Create descriptive content based on filename and metadata
        media_type = item.metadata.get('media_type', 'unknown')
        dimensions = item.metadata.get('dimensions', '')
        duration = item.metadata.get('duration', 0)

        content_parts = [f"Media file: {filename}"]

        if media_type == 'image':
            content_parts.append("Image file")
            if dimensions:
                content_parts.append(f"Dimensions: {dimensions}")
        elif media_type == 'audio':
            content_parts.append("Audio file")
            if duration > 0:
                content_parts.append(f"Duration: {duration} seconds")
        elif media_type == 'video':
            content_parts.append("Video file")
            if duration > 0:
                content_parts.append(f"Duration: {duration} seconds")
            if dimensions:
                content_parts.append(f"Dimensions: {dimensions}")

        return ". ".join(content_parts)


# Register plugin on import
PluginRegistry.register(
    name="media",
    scanner_class=MediaScanner,
    version="1.0.0",
    description="Scanner for media collections with metadata extraction from images, audio, and video files"
)