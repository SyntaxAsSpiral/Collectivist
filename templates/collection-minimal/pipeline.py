"""
Collectivist Pipeline - Core Orchestration

Three-stage pipeline for intentional collections:
1. Analyze - LLM determines collection type and generates config
2. Scan - Domain-specific plugins discover items and extract metadata
3. Describe - LLM generates descriptions and assigns categories
4. Render - Generate beautiful outputs (Markdown, HTML, JSON, Nushell)
"""

import time
from pathlib import Path
from typing import Optional
import yaml

from analyzer import CollectionAnalyzer
from indexer import CollectionIndexer
from describer import CollectionDescriber
from renderer import CollectionRenderer


class CollectionPipeline:
    """Main pipeline orchestrator for Collectivist minimal level."""

    def __init__(self, collection_path: Optional[Path] = None, llm_client=None):
        """Initialize pipeline for a collection.

        Args:
            collection_path: Path to collection directory (defaults to cwd)
            llm_client: Optional LLM client instance (auto-loaded if not provided)
        """
        self.collection_path = collection_path or Path.cwd()
        self.collection_dir = self.collection_path / ".collection"

        # Ensure .collection directory exists
        self.collection_dir.mkdir(exist_ok=True)

        # Initialize components
        self.analyzer = CollectionAnalyzer(self.collection_path, self.collection_dir, llm_client)
        self.indexer = CollectionIndexer(self.collection_path, self.collection_dir)
        self.describer = CollectionDescriber(self.collection_path, self.collection_dir, llm_client)
        self.renderer = CollectionRenderer(self.collection_path, self.collection_dir)

    def analyze(self, force_type: Optional[str] = None) -> None:
        """Stage 1: Analyze collection and generate config."""
        self.analyzer.analyze(force_type=force_type)

    def scan(self) -> None:
        """Stage 2: Scan collection for items and extract metadata."""
        self.scanner.scan()

    def describe(self) -> None:
        """Stage 3: Generate LLM descriptions and categories."""
        self.describer.describe()

    def render(self) -> None:
        """Stage 4: Generate output files (README.md, index.html, etc.)."""
        self.renderer.render()

    def update(self, force_type: Optional[str] = None) -> None:
        """Run full pipeline: analyze → scan → describe → render."""
        start_time = time.time()

        print("🔍 Stage 1: Analyzing collection...")
        self.analyze(force_type=force_type)

        print("🔎 Stage 2: Scanning items...")
        self.scan()

        print("🧠 Stage 3: Generating descriptions...")
        self.describe()

        print("📝 Stage 4: Rendering outputs...")
        self.render()

        elapsed = time.time() - start_time
        print(".1f"
    def get_status(self) -> dict:
        """Get current collection status."""
        status = {
            "collection_path": str(self.collection_path),
            "has_config": (self.collection_dir / "collection.yaml").exists(),
            "has_index": (self.collection_dir / "index.yaml").exists(),
            "last_scan": None,
            "total_items": 0
        }

        # Read index.yaml if it exists
        index_path = self.collection_dir / "index.yaml"
        if index_path.exists():
            try:
                with open(index_path, 'r', encoding='utf-8') as f:
                    index_data = yaml.safe_load(f)
                    status["last_scan"] = index_data.get("last_scan")
                    status["total_items"] = index_data.get("total_items", 0)
            except Exception:
                pass

        return status