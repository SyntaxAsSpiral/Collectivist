"""
Collection Analyzer - LLM-Based Collection Type Detection

Analyzes directory structure and contents to determine collection type
and generate appropriate configuration.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
import yaml

from llm import LLMClient


class CollectionAnalyzer:
    """Analyzes collections to determine type and generate config."""

    # Supported collection types and their characteristics
    COLLECTION_TYPES = {
        "repositories": {
            "name": "Repository Collection",
            "description": "Git repositories with commit tracking and metadata",
            "indicators": [".git", "README.md", "LICENSE", ".gitignore"],
            "categories": [
                "ai_llm_agents", "terminal_ui", "dev_tools",
                "esoteric_experimental", "system_infrastructure", "utilities_misc"
            ]
        },
        "research": {
            "name": "Research Paper Collection",
            "description": "Academic papers, citations, and research materials",
            "indicators": [".pdf", ".bib", "citations", "abstract"],
            "categories": [
                "machine_learning", "computer_vision", "nlp",
                "robotics", "systems", "theory"
            ]
        },
        "media": {
            "name": "Media Library",
            "description": "Photos, videos, audio files with metadata",
            "indicators": [".jpg", ".png", ".mp3", ".mp4", ".mov"],
            "categories": [
                "photography", "music", "videos", "artwork", "memories"
            ]
        },
        "creative": {
            "name": "Creative Project Collection",
            "description": "Design projects, artwork, and creative assets",
            "indicators": ["assets", "designs", "portfolio", ".psd", ".ai"],
            "categories": [
                "web_design", "graphic_design", "illustration",
                "animation", "photography", "branding"
            ]
        },
        "datasets": {
            "name": "Dataset Collection",
            "description": "Data files, CSVs, and structured datasets",
            "indicators": [".csv", ".json", ".parquet", ".sql", "data"],
            "categories": [
                "machine_learning", "analytics", "research",
                "visualization", "training_data", "benchmarks"
            ]
        }
    }

    def __init__(self, collection_path: Path, collection_dir: Path):
        """Initialize analyzer.

        Args:
            collection_path: Path to collection directory
            collection_dir: Path to .collection directory
        """
        self.collection_path = collection_path
        self.collection_dir = collection_dir
        self.llm_client = LLMClient.from_env()

    def analyze(self, force_type: Optional[str] = None) -> None:
        """Analyze collection and generate configuration.

        Args:
            force_type: Force specific collection type (skip LLM analysis)
        """
        if force_type:
            collection_type = force_type
            confidence = 1.0
            reasoning = f"Manually specified as {force_type}"
        else:
            collection_type, confidence, reasoning = self._analyze_with_llm()

        # Generate configuration
        config = self._generate_config(collection_type, confidence, reasoning)

        # Save configuration
        config_path = self.collection_dir / "collection.yaml"
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

        print(f"📝 Generated config for {collection_type} collection")
        print(f"   Confidence: {confidence:.2f}")
        print(f"   Saved to: {config_path}")

    def _analyze_with_llm(self) -> tuple[str, float, str]:
        """Use LLM to analyze collection type."""
        # Gather directory information
        dir_info = self._gather_directory_info()

        # Create analysis prompt
        prompt = self._create_analysis_prompt(dir_info)

        try:
            # Query LLM
            messages = [
                {"role": "system", "content": "You are a collection type analyzer. Analyze the provided directory structure and determine the most appropriate collection type."},
                {"role": "user", "content": prompt}
            ]

            response = self.llm_client.chat("llama3.1-8b-instant", messages, temperature=0.1)
            result = self._parse_llm_response(response)

            return result["collection_type"], result["confidence"], result["reasoning"]

        except Exception as e:
            print(f"⚠️  LLM analysis failed: {e}")
            print("🔄 Falling back to heuristic analysis...")
            return self._fallback_analysis(dir_info)

    def _gather_directory_info(self) -> Dict[str, Any]:
        """Gather information about the collection directory."""
        info = {
            "total_files": 0,
            "file_types": {},
            "special_files": [],
            "directory_structure": [],
            "sample_files": []
        }

        # Walk directory and gather info
        for root, dirs, files in os.walk(self.collection_path):
            # Skip .collection directory
            if ".collection" in Path(root).parts:
                continue

            # Track directory structure (first level only)
            rel_root = Path(root).relative_to(self.collection_path)
            if len(rel_root.parts) == 1 and rel_root.name:
                info["directory_structure"].append(rel_root.name)

            for file in files:
                if file.startswith('.'):
                    continue

                info["total_files"] += 1

                # Track file extensions
                ext = Path(file).suffix.lower()
                if ext:
                    info["file_types"][ext] = info["file_types"].get(ext, 0) + 1

                # Track special files
                if file.lower() in ["readme.md", "license", ".gitignore", "package.json",
                                  "requirements.txt", "setup.py", "dockerfile"]:
                    info["special_files"].append(file)

                # Sample file content (first 5 files, first 1000 chars)
                if len(info["sample_files"]) < 5:
                    file_path = Path(root) / file
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read(1000)
                            info["sample_files"].append({
                                "name": file,
                                "path": str(Path(root).relative_to(self.collection_path)),
                                "content": content[:500] + "..." if len(content) > 500 else content
                            })
                    except Exception:
                        # Skip binary files or files we can't read
                        pass

        return info

    def _create_analysis_prompt(self, dir_info: Dict[str, Any]) -> str:
        """Create LLM prompt for collection analysis."""
        prompt = f"""Analyze this directory structure and determine the collection type.

DIRECTORY STRUCTURE:
{', '.join(dir_info['directory_structure'][:10])}

FILE TYPES ({dir_info['total_files']} total files):
{', '.join([f'{ext}: {count}' for ext, count in sorted(dir_info['file_types'].items(), key=lambda x: x[1], reverse=True)][:10])}

SPECIAL FILES FOUND:
{', '.join(dir_info['special_files'][:10])}

SAMPLE FILE CONTENTS:
"""

        for i, sample in enumerate(dir_info['sample_files'][:3]):
            prompt += f"\n--- {sample['name']} ---\n{sample['content'][:300]}\n"

        prompt += """

Available collection types:
- repositories: Git repositories with development tools and code
- research: Academic papers, citations, and research materials
- media: Photos, videos, audio files, and media assets
- creative: Design projects, artwork, and creative assets
- datasets: Data files, CSVs, and structured datasets

Return JSON:
{
  "collection_type": "one of the types above",
  "confidence": 0.0-1.0,
  "reasoning": "brief explanation of your decision"
}
"""

        return prompt

    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response into structured data."""
        try:
            # Try to extract JSON from response
            import json
            import re

            # Look for JSON block
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                return result
            else:
                # Fallback: try parsing entire response
                return json.loads(response)

        except Exception:
            # Fallback to default
            return {
                "collection_type": "repositories",
                "confidence": 0.5,
                "reasoning": "LLM response parsing failed, defaulting to repositories"
            }

    def _fallback_analysis(self, dir_info: Dict[str, Any]) -> tuple[str, float, str]:
        """Fallback analysis based on file types and structure."""
        # Simple heuristic-based analysis
        file_types = dir_info["file_types"]

        # Check for repository indicators
        if any(ext in [".git", ".gitignore", "readme.md", "license"] for ext in [f.lower() for f in dir_info["special_files"]]):
            return "repositories", 0.8, "Detected repository indicators (.git, README, etc.)"

        # Check for media files
        media_exts = {".jpg", ".png", ".mp3", ".mp4", ".mov", ".avi"}
        if any(ext in media_exts for ext in file_types):
            return "media", 0.7, "Detected media file extensions"

        # Check for data files
        data_exts = {".csv", ".json", ".parquet", ".sql", ".xlsx"}
        if any(ext in data_exts for ext in file_types):
            return "datasets", 0.7, "Detected data file extensions"

        # Default to repositories (most common)
        return "repositories", 0.5, "Defaulting to repositories based on general file structure"

    def _generate_config(self, collection_type: str, confidence: float, reasoning: str) -> Dict[str, Any]:
        """Generate collection configuration."""
        type_info = self.COLLECTION_TYPES[collection_type]

        config = {
            "collection_id": self.collection_path.name,
            "domain": collection_type,
            "title": f"{type_info['name']}",
            "description": type_info["description"],
            "created": "2026-01-09T15:30:00Z",  # Would use datetime.now() in real implementation
            "analysis": {
                "confidence": confidence,
                "reasoning": reasoning,
                "analyzed_at": "2026-01-09T15:30:00Z"
            },
            "scanner": {
                "plugin": collection_type,
                "config": {
                    "exclude_patterns": [
                        "*/node_modules/*",
                        "*/.venv/*",
                        "*/__pycache__/*",
                        "*/.git/*"
                    ]
                }
            },
            "metadata_fields": self._get_metadata_fields(collection_type),
            "status_checks": self._get_status_checks(collection_type),
            "categories": type_info["categories"],
            "output": {
                "formats": ["markdown", "html", "json", "nushell"],
                "template": "default"
            }
        }

        return config

    def _get_metadata_fields(self, collection_type: str) -> list[str]:
        """Get appropriate metadata fields for collection type."""
        base_fields = ["size", "created", "modified"]

        type_fields = {
            "repositories": ["git_status", "remote", "branch", "last_commit"],
            "research": ["author", "year", "journal", "citations"],
            "media": ["duration", "resolution", "codec", "artist", "album"],
            "creative": ["format", "dimensions", "color_space", "layers"],
            "datasets": ["format", "rows", "columns", "schema", "source"]
        }

        return base_fields + type_fields.get(collection_type, [])

    def _get_status_checks(self, collection_type: str) -> list[str]:
        """Get appropriate status checks for collection type."""
        checks = {
            "repositories": ["git_fetch", "upstream_tracking"],
            "research": ["file_readable", "metadata_complete"],
            "media": ["file_integrity", "metadata_present"],
            "creative": ["file_readable", "format_supported"],
            "datasets": ["file_readable", "schema_valid"]
        }

        return checks.get(collection_type, ["file_readable"])