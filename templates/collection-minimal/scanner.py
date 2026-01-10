"""
Collection Scanner - Domain-Specific Item Discovery

Scans collections using domain-specific plugins to discover items
and extract rich metadata.
"""

import os
import stat
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
import yaml

from plugins.repositories import RepositoryScanner


class CollectionScanner:
    """Scans collections for items using domain-specific plugins."""

    def __init__(self, collection_path: Path, collection_dir: Path):
        """Initialize scanner.

        Args:
            collection_path: Path to collection directory
            collection_dir: Path to .collection directory
        """
        self.collection_path = collection_path
        self.collection_dir = collection_dir

        # Load collection config
        config_path = collection_dir / "collection.yaml"
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
        else:
            # Default config if not analyzed yet
            self.config = {"domain": "repositories"}

        # Initialize scanner plugin
        self.plugin = self._get_scanner_plugin()

    def _get_scanner_plugin(self):
        """Get appropriate scanner plugin for collection type."""
        domain = self.config.get("domain", "repositories")

        # Map domains to scanner classes
        scanners = {
            "repositories": RepositoryScanner,
            # Add more scanners as they're implemented
            # "research": ResearchScanner,
            # "media": MediaScanner,
            # "creative": CreativeScanner,
            # "datasets": DatasetScanner,
        }

        scanner_class = scanners.get(domain, RepositoryScanner)  # Default fallback

        return scanner_class(
            collection_path=self.collection_path,
            config=self.config
        )

    def scan(self) -> None:
        """Scan collection for items and extract metadata."""
        print(f"🔍 Scanning {self.config.get('domain', 'unknown')} collection...")

        # Discover items
        items = self.plugin.discover_items()

        # Extract metadata for each item
        enriched_items = []
        for item_path in items:
            try:
                metadata = self._extract_basic_metadata(item_path)
                domain_metadata = self.plugin.extract_metadata(item_path)
                status = self.plugin.check_status(item_path)
                content_sample = self.plugin.generate_content_sample(item_path)

                item = {
                    "id": self._generate_item_id(item_path),
                    "path": str(item_path.relative_to(self.collection_path)),
                    "name": item_path.name,
                    "type": "dir" if item_path.is_dir() else "file",
                    "metadata": {**metadata, **domain_metadata},
                    "status": status,
                    "content_sample": content_sample,
                    "description": None,  # Will be filled by describer
                    "category": None      # Will be filled by describer
                }

                enriched_items.append(item)

            except Exception as e:
                print(f"⚠️  Error processing {item_path}: {e}")
                continue

        # Create index data
        index_data = {
            "collection_id": self.config.get("collection_id", self.collection_path.name),
            "last_scan": datetime.now().isoformat(),
            "scan_duration_seconds": 0.0,  # Would track actual duration
            "total_items": len(enriched_items),
            "domain": self.config.get("domain"),
            "items": enriched_items
        }

        # Save index
        index_path = self.collection_dir / "index.yaml"
        with open(index_path, 'w', encoding='utf-8') as f:
            yaml.dump(index_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

        print(f"📊 Indexed {len(enriched_items)} items")
        print(f"   Saved to: {index_path}")

    def _extract_basic_metadata(self, item_path: Path) -> Dict[str, Any]:
        """Extract basic filesystem metadata."""
        try:
            stat_info = item_path.stat()

            # Convert timestamps to ISO format
            created = datetime.fromtimestamp(stat_info.st_ctime).isoformat()
            modified = datetime.fromtimestamp(stat_info.st_mtime).isoformat()
            accessed = datetime.fromtimestamp(stat_info.st_atime).isoformat()

            return {
                "size": stat_info.st_size,
                "created": created,
                "modified": modified,
                "accessed": accessed
            }

        except Exception:
            # Fallback metadata
            return {
                "size": 0,
                "created": datetime.now().isoformat(),
                "modified": datetime.now().isoformat(),
                "accessed": datetime.now().isoformat()
            }

    def _generate_item_id(self, item_path: Path) -> str:
        """Generate unique ID for item."""
        # Use relative path as ID, sanitized
        rel_path = item_path.relative_to(self.collection_path)
        return str(rel_path).replace('/', '_').replace('\\', '_').replace(' ', '_')