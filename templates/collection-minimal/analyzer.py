"""
Collection Analyzer - LLM-Based Collection Type Detection

Analyzes directory structure and contents to determine collection type
and generate appropriate configuration.
"""

import os
import threading
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
                "ai_llm_agents", "dev_tools", "esoteric_experimental"
            ]
        },
        "media": {
            "name": "Media Library",
            "description": "Photos, videos, audio files with metadata",
            "indicators": [".jpg", ".png", ".mp3", ".mp4", ".mov"],
            "categories": [
                "creative_aesthetic", "utilities_misc"
            ]
        },
        "creative": {
            "name": "Creative Project Collection",
            "description": "Design projects, artwork, and creative assets",
            "indicators": ["assets", "designs", "portfolio", ".psd", ".ai"],
            "categories": [
                "creative_aesthetic", "dev_tools", "terminal_ui"
            ]
        },
        "datasets": {
            "name": "Dataset Collection",
            "description": "Data files, CSVs, and structured datasets",
            "indicators": [".csv", ".json", ".parquet", ".sql", "data"],
            "categories": [
                "ai_llm_agents", "dev_tools", "utilities_misc"
            ]
        },
        "obsidian": {
            "name": "Obsidian Vault Collection",
            "description": "Knowledge base with interconnected notes, tags, and metadata",
            "indicators": [".obsidian", "frontmatter", ".md", "[[links]]"],
            "categories": [
                "creative_aesthetic", "dev_tools", "utilities_misc"
            ]
        }
    }

    def __init__(self, collection_path: Path, collection_dir: Path, llm_client=None):
        """Initialize analyzer.

        Args:
            collection_path: Path to collection directory
            collection_dir: Path to .collection directory
            llm_client: Optional LLM client instance (auto-loaded if not provided)
        """
        self.collection_path = collection_path
        self.collection_dir = collection_dir
        self.llm_client = llm_client or LLMClient.from_config()

    def analyze(self, force_type: Optional[str] = None) -> None:
        """Analyze collection and generate configuration.

        Args:
            force_type: Force specific collection type (skip LLM analysis)
        """
        if force_type:
            collection_type = force_type
            confidence = 1.0
            reasoning = f"Manually specified as {force_type}"
            llm_response = None
        else:
            collection_type, confidence, reasoning, llm_response = self._analyze_with_llm()

        # Generate configuration
        config = self._generate_config(collection_type, confidence, reasoning, llm_response)

        # Save configuration
        config_path = self.collection_dir / "collection.yaml"
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

        print(f"📝 Generated config for {collection_type} collection")
        print(f"   Confidence: {confidence:.2f}")
        print(f"   Saved to: {config_path}")

    def _analyze_with_llm(self) -> tuple[str, float, str]:
        """Use three-phase LLM analysis with intelligent context compilation."""
        # Phase 1: Gather and compile directory context, identify collection type
        raw_dir_info = self._gather_directory_info()
        phase1_context = self._compile_phase1_context(raw_dir_info)
        identification_result = self._phase1_identification(phase1_context)

        if not identification_result:
            # Fallback to heuristic analysis
            print("🔄 Falling back to heuristic analysis...")
            result = self._fallback_analysis(raw_dir_info)
            return result[0], result[1], result[2], None

        # Phase 2 & 3: Concurrent analysis with compiled contexts
        results = {}
        threads = []

        # Schema generation thread - compile context specific to schema needs
        def run_schema_generation():
            phase2_context = self._compile_phase2_context(raw_dir_info, identification_result)
            results["schema"] = self._phase2_schema_generation(phase2_context, identification_result)

        # Categorization thread - compile context specific to categorization needs
        def run_categorization():
            phase3_context = self._compile_phase3_context(raw_dir_info, identification_result)
            results["categories"] = self._phase3_categorization(phase3_context, identification_result)

        # Start both threads
        schema_thread = threading.Thread(target=run_schema_generation)
        category_thread = threading.Thread(target=run_categorization)

        schema_thread.start()
        category_thread.start()

        # Wait for both to complete
        schema_thread.join()
        category_thread.join()

        # Combine results
        combined_result = {
            **identification_result,
            **results["schema"],
            **results["categories"]
        }

        return (
            combined_result["collection_type"],
            combined_result["confidence"],
            combined_result["reasoning"],
            combined_result
        )

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
- obsidian: Knowledge base with interconnected notes, tags, and metadata

If this doesn't match any known types, specify "custom" and generate a custom schema. For ALL collections (known types or custom), analyze the content and generate 4-8 appropriate categories that would help organize this specific collection.

Consider the collection's purpose, content types, and organizational needs when suggesting categories.

Return JSON:
{
  "collection_type": "one of the types above, or 'custom'",
  "confidence": 0.0-1.0,
  "reasoning": "brief explanation of your decision",
  "custom_name": "optional: human-readable name for custom type",
  "custom_description": "optional: description for custom type",
  "custom_categories": {
    "category_key": "description of what this category represents",
    "another_key": "description of another category",
    ...
  }
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
                "reasoning": "LLM response parsing failed, defaulting to repositories",
                "custom_categories": {
                    "core": "Core functionality and main features",
                    "utilities": "Helper tools and utilities",
                    "experimental": "Experimental or prototype code",
                    "documentation": "Documentation and examples"
                }
            }

    def _fallback_analysis(self, dir_info: Dict[str, Any]) -> tuple[str, float, str]:
        """Fallback analysis based on file types and structure."""
        # Simple heuristic-based analysis
        file_types = dir_info["file_types"]

        # Check for Obsidian vault indicators
        if ".obsidian" in dir_info["directory_structure"]:
            return "obsidian", 0.9, "Detected .obsidian directory (Obsidian vault)"

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

    def _generate_config(self, collection_type: str, confidence: float, reasoning: str, llm_response: Optional[Dict] = None) -> Dict[str, Any]:
        """Generate collection configuration."""
        # Handle custom collection types
        if collection_type not in self.COLLECTION_TYPES:
            return self._generate_custom_config(collection_type, confidence, reasoning, llm_response)

        # Handle known collection types
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
            "metadata_fields": self._get_metadata_fields(collection_type) + [
                field["field_name"] for field in llm_response.get("additional_metadata_fields", [])
            ] if llm_response else self._get_metadata_fields(collection_type),
            "status_checks": self._get_status_checks(collection_type),
            "categories": list(llm_response.get("custom_categories", {}).keys()) if llm_response and "custom_categories" in llm_response else list(type_info["categories"]),
            "category_legend": llm_response.get("custom_categories", {}) if llm_response and "custom_categories" in llm_response else {cat: f"Category for {cat}" for cat in type_info["categories"]},
            "schema_design": llm_response.get("field_rationale", "Standard schema") if llm_response and "field_rationale" in llm_response else "Standard schema",
            "categorization_approach": llm_response.get("categorization_strategy", "Standard categorization") if llm_response and "categorization_strategy" in llm_response else "Standard categorization",
            "output": {
                "formats": ["markdown", "html", "json", "nushell"],
                "template": "default"
            }
        }

        return config

    def _generate_custom_config(self, collection_type: str, confidence: float, reasoning: str, llm_response: Optional[Dict] = None) -> Dict[str, Any]:
        """Generate configuration for custom/unknown collection types."""
        # Extract custom info from LLM response if available
        custom_name = llm_response.get("custom_name", "Custom Collection") if llm_response else "Custom Collection"
        custom_description = llm_response.get("custom_description", "Custom collection type") if llm_response else "Custom collection type"
        suggested_categories = llm_response.get("suggested_categories", ["general", "misc", "other"]) if llm_response else ["general", "misc", "other"]

        # Generate basic metadata fields based on file types we found
        dir_info = self._gather_directory_info()
        custom_metadata_fields = ["size", "created", "modified"]

        # Add type-specific fields based on file extensions
        file_types = dir_info["file_types"]
        if any(ext in [".jpg", ".png", ".gif", ".mp4", ".mp3"] for ext in file_types):
            custom_metadata_fields.extend(["dimensions", "duration", "format"])
        if any(ext in [".pdf", ".docx", ".txt"] for ext in file_types):
            custom_metadata_fields.extend(["word_count", "author", "language"])
        if any(ext in [".csv", ".json", ".xml"] for ext in file_types):
            custom_metadata_fields.extend(["row_count", "column_count", "schema"])

        config = {
            "collection_id": self.collection_path.name,
            "domain": "custom",
            "custom_type": collection_type,
            "title": custom_name,
            "description": custom_description,
            "created": "2026-01-09T15:30:00Z",
            "analysis": {
                "confidence": confidence,
                "reasoning": reasoning,
                "analyzed_at": "2026-01-09T15:30:00Z",
                "custom_schema_generated": True
            },
            "scanner": {
                "plugin": "generic",  # Use generic scanner for custom types
                "config": {
                    "exclude_patterns": [
                        "*/node_modules/*",
                        "*/.venv/*",
                        "*/__pycache__/*",
                        "*/.git/*",
                        "*/.DS_Store",
                        "*/Thumbs.db",
                        "*/.pytest_cache/*",
                        "*/target/*",  # Rust build artifacts
                        "*/build/*",   # Build directories
                        "*/dist/*",    # Distribution directories
                        "*/.next/*",   # Next.js build
                        "*/.nuxt/*",   # Nuxt build
                        "*/coverage/*", # Test coverage
                        "*/.vscode/*", # Editor settings
                    ]
                }
            },
            "metadata_fields": custom_metadata_fields + [
                field["field_name"] for field in llm_response.get("additional_metadata_fields", [])
            ] if llm_response and "additional_metadata_fields" in llm_response else custom_metadata_fields,
            "status_checks": ["file_readable"],  # Basic status check for custom types
            "categories": list(llm_response.get("custom_categories", {}).keys()) if llm_response and "custom_categories" in llm_response else suggested_categories,
            "category_legend": llm_response.get("custom_categories", {}) if llm_response and "custom_categories" in llm_response else {cat: f"Custom category: {cat}" for cat in suggested_categories},
            "schema_design": llm_response.get("field_rationale", "Custom schema") if llm_response and "field_rationale" in llm_response else "Custom schema",
            "categorization_approach": llm_response.get("categorization_strategy", "Custom categorization") if llm_response and "categorization_strategy" in llm_response else "Custom categorization",
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
            "datasets": ["format", "rows", "columns", "schema", "source"],
            "obsidian": ["tags", "aliases", "wiki_links", "frontmatter", "word_count", "internal_links", "external_links"]
        }

        return base_fields + type_fields.get(collection_type, [])

    def _get_status_checks(self, collection_type: str) -> list[str]:
        """Get appropriate status checks for collection type."""
        checks = {
            "repositories": ["git_fetch", "upstream_tracking"],
            "research": ["file_readable", "metadata_complete"],
            "media": ["file_integrity", "metadata_present"],
            "creative": ["file_readable", "format_supported"],
            "datasets": ["file_readable", "schema_valid"],
            "obsidian": ["file_readable", "frontmatter_valid"]
        }

        return checks.get(collection_type, ["file_readable"])

    def _compile_phase1_context(self, raw_dir_info: Dict[str, Any]) -> Dict[str, Any]:
        """Compile intelligent context for Phase 1: Collection identification.

        Focuses on high-level patterns without overwhelming detail.
        """
        context = {
            "overview": {
                "total_files": raw_dir_info["total_files"],
                "top_level_dirs": raw_dir_info["directory_structure"][:8],  # Limit depth
                "file_type_distribution": self._summarize_file_types(raw_dir_info["file_types"]),
                "special_indicators": raw_dir_info["special_files"][:5]  # Key indicators only
            },
            "patterns": {
                "structural_hints": self._extract_structural_patterns(raw_dir_info),
                "content_hints": self._extract_content_hints(raw_dir_info["sample_files"][:2])  # Limited samples
            }
        }
        return context

    def _compile_phase2_context(self, raw_dir_info: Dict[str, Any], identification_result: Dict[str, Any]) -> Dict[str, Any]:
        """Compile intelligent context for Phase 2: Schema generation.

        Provides type-specific information for deep schema consideration.
        """
        collection_type = identification_result["collection_type"]

        context = {
            "collection_type": collection_type,
            "schema_focus": self._get_schema_focus_for_type(collection_type),
            "relevant_samples": self._select_relevant_samples(raw_dir_info["sample_files"], collection_type),
            "structural_insights": self._extract_type_specific_structure(raw_dir_info, collection_type),
            "metadata_candidates": self._suggest_metadata_candidates(raw_dir_info, collection_type)
        }
        return context

    def _compile_phase3_context(self, raw_dir_info: Dict[str, Any], identification_result: Dict[str, Any]) -> Dict[str, Any]:
        """Compile intelligent context for Phase 3: Category generation.

        Focuses on organizational themes and content clustering.
        """
        collection_type = identification_result["collection_type"]

        context = {
            "collection_type": collection_type,
            "organizational_patterns": self._extract_organizational_patterns(raw_dir_info),
            "content_themes": self._extract_content_themes(raw_dir_info["sample_files"]),
            "structural_hierarchy": raw_dir_info["directory_structure"][:10],  # Hierarchical view
            "categorization_hints": self._get_categorization_hints_for_type(collection_type)
        }
        return context

    def _summarize_file_types(self, file_types: Dict[str, str]) -> Dict[str, Any]:
        """Summarize file types intelligently for identification."""
        # Group and prioritize file types
        groups = {
            "code": [".py", ".js", ".ts", ".java", ".cpp", ".rs", ".go"],
            "documents": [".md", ".txt", ".pdf", ".docx"],
            "data": [".json", ".csv", ".xml", ".yaml"],
            "media": [".jpg", ".png", ".mp3", ".mp4"],
            "config": [".toml", ".ini", ".conf"]
        }

        summary = {}
        for group_name, extensions in groups.items():
            group_count = sum(file_types.get(ext, 0) for ext in extensions)
            if group_count > 0:
                summary[group_name] = group_count

        # Add top individual extensions not in groups
        all_group_exts = [ext for group_exts in groups.values() for ext in group_exts]
        individual = {k: v for k, v in file_types.items() if k not in all_group_exts}
        top_individual = sorted(individual.items(), key=lambda x: x[1], reverse=True)[:3]

        for ext, count in top_individual:
            summary[f"ext_{ext}"] = count

        return summary

    def _extract_structural_patterns(self, dir_info: Dict[str, Any]) -> List[str]:
        """Extract key structural patterns for identification."""
        patterns = []

        # Directory naming patterns
        dir_names = dir_info["directory_structure"]
        if any("src" in d.lower() for d in dir_names):
            patterns.append("source_code_structure")
        if any("test" in d.lower() for d in dir_names):
            patterns.append("testing_framework")
        if any("doc" in d.lower() or "readme" in d.lower() for d in dir_names):
            patterns.append("documentation_present")

        # File distribution patterns
        total_files = dir_info["total_files"]
        if total_files > 100:
            patterns.append("large_collection")
        elif total_files < 10:
            patterns.append("small_collection")

        return patterns[:5]  # Limit patterns

    def _extract_content_hints(self, sample_files: List[Dict[str, Any]]) -> List[str]:
        """Extract content hints from sample files without full content."""
        hints = []
        for sample in sample_files[:3]:  # Limit processing
            filename = sample["name"].lower()
            if "readme" in filename:
                hints.append("readme_present")
            elif "package" in filename and "json" in filename:
                hints.append("package_config")
            elif "dockerfile" in filename:
                hints.append("containerized")
            elif "license" in filename:
                hints.append("licensed_project")
        return hints

    def _get_schema_focus_for_type(self, collection_type: str) -> Dict[str, Any]:
        """Get schema focus areas for different collection types."""
        focuses = {
            "repositories": {
                "primary_fields": ["git_status", "language", "framework"],
                "considerations": ["version_control", "code_organization", "dependencies"]
            },
            "research": {
                "primary_fields": ["authors", "publication_year", "citations"],
                "considerations": ["academic_metadata", "cross_references", "field_classification"]
            },
            "media": {
                "primary_fields": ["dimensions", "duration", "format"],
                "considerations": ["media_metadata", "creation_dates", "content_description"]
            },
            "creative": {
                "primary_fields": ["dimensions", "color_space", "layers"],
                "considerations": ["asset_metadata", "creation_workflow", "version_tracking"]
            },
            "datasets": {
                "primary_fields": ["schema", "row_count", "data_types"],
                "considerations": ["data_structure", "quality_metrics", "usage_context"]
            }
        }
        return focuses.get(collection_type, {
            "primary_fields": ["size", "created", "modified"],
            "considerations": ["basic_metadata", "content_type", "organizational_structure"]
        })

    def _select_relevant_samples(self, sample_files: List[Dict[str, Any]], collection_type: str) -> List[Dict[str, Any]]:
        """Select most relevant sample files for schema generation."""
        if not sample_files:
            return []

        # Type-specific file prioritization
        priority_patterns = {
            "repositories": ["readme", "package.json", ".py", ".js", ".rs"],
            "research": ["readme", ".pdf", ".bib", ".tex"],
            "media": ["readme", ".md", ".txt"],
            "creative": ["readme", ".psd", ".ai", ".md"],
            "datasets": ["readme", ".csv", ".json", "schema"]
        }

        patterns = priority_patterns.get(collection_type, ["readme", ".md"])

        # Score and sort samples
        scored_samples = []
        for sample in sample_files:
            score = 0
            filename = sample["name"].lower()
            for pattern in patterns:
                if pattern in filename:
                    score += 1
            scored_samples.append((score, sample))

        # Return top 3 most relevant samples
        return [sample for _, sample in sorted(scored_samples, key=lambda x: x[0], reverse=True)][:3]

    def _extract_type_specific_structure(self, dir_info: Dict[str, Any], collection_type: str) -> Dict[str, Any]:
        """Extract structure insights specific to collection type."""
        structure = {}

        if collection_type == "repositories":
            # Look for typical repo structure
            dirs = dir_info["directory_structure"]
            structure["has_src"] = any("src" in d.lower() for d in dirs)
            structure["has_tests"] = any("test" in d.lower() for d in dirs)
            structure["has_docs"] = any("doc" in d.lower() for d in dirs)

        elif collection_type == "research":
            # Look for research organization
            structure["has_citations"] = any("citation" in f.lower() for f in dir_info["special_files"])
            structure["has_abstracts"] = any("abstract" in f.lower() for f in dir_info["special_files"])

        # Add general structure insights
        structure["directory_depth"] = len(dir_info["directory_structure"])
        structure["file_concentration"] = "scattered" if len(dir_info["directory_structure"]) > 10 else "organized"

        return structure

    def _suggest_metadata_candidates(self, dir_info: Dict[str, Any], collection_type: str) -> List[str]:
        """Suggest potential metadata fields based on file analysis."""
        candidates = ["size", "created", "modified"]  # Base fields

        # Type-specific suggestions
        if collection_type == "repositories":
            if any("dockerfile" in f.lower() for f in dir_info["special_files"]):
                candidates.extend(["containerized", "base_image"])
            if any("license" in f.lower() for f in dir_info["special_files"]):
                candidates.extend(["license_type", "license_year"])

        elif collection_type == "media":
            if any(ext in dir_info["file_types"] for ext in [".jpg", ".png"]):
                candidates.extend(["resolution", "color_depth"])
            if any(ext in dir_info["file_types"] for ext in [".mp3", ".mp4"]):
                candidates.extend(["duration", "bitrate"])

        return candidates[:8]  # Limit suggestions

    def _extract_organizational_patterns(self, dir_info: Dict[str, Any]) -> List[str]:
        """Extract patterns that suggest how content is organized."""
        patterns = []

        dir_names = [d.lower() for d in dir_info["directory_structure"]]

        # Categorization patterns
        if any("by_" in d or "group" in d for d in dir_names):
            patterns.append("explicit_categorization")
        if any(d in ["archive", "old", "backup"] for d in dir_names):
            patterns.append("temporal_organization")
        if any(d in ["personal", "work", "client"] for d in dir_names):
            patterns.append("contextual_grouping")

        return patterns

    def _extract_content_themes(self, sample_files: List[Dict[str, Any]]) -> List[str]:
        """Extract thematic hints from file contents."""
        themes = []
        content_snippets = []

        # Collect content snippets (limited)
        for sample in sample_files[:3]:
            if "content" in sample:
                snippet = sample["content"][:200]  # Limited content
                content_snippets.append(snippet.lower())

        # Simple theme detection
        combined_content = " ".join(content_snippets)

        if any(word in combined_content for word in ["api", "endpoint", "request", "response"]):
            themes.append("api_development")
        if any(word in combined_content for word in ["algorithm", "model", "training", "dataset"]):
            themes.append("machine_learning")
        if any(word in combined_content for word in ["design", "ui", "ux", "interface"]):
            themes.append("user_interface")

        return themes[:5]

    def _get_categorization_hints_for_type(self, collection_type: str) -> Dict[str, Any]:
        """Get categorization hints for different collection types."""
        hints = {
            "repositories": {
                "dimensions": ["language", "framework", "domain", "maturity"],
                "examples": ["web_frameworks", "data_science", "cli_tools", "libraries"]
            },
            "research": {
                "dimensions": ["field", "methodology", "year", "impact"],
                "examples": ["machine_learning", "computer_vision", "theory", "applications"]
            },
            "media": {
                "dimensions": ["type", "subject", "quality", "usage"],
                "examples": ["photography", "videos", "music", "artwork"]
            },
            "creative": {
                "dimensions": ["medium", "purpose", "style", "complexity"],
                "examples": ["web_design", "illustrations", "prototypes", "assets"]
            },
            "datasets": {
                "dimensions": ["domain", "size", "structure", "quality"],
                "examples": ["training_data", "benchmarks", "research", "analytics"]
            }
        }
        return hints.get(collection_type, {
            "dimensions": ["purpose", "type", "complexity"],
            "examples": ["general", "specific", "miscellaneous"]
        })

    def _phase1_identification(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Phase 1: Identify collection type with compiled context."""
        prompt = f"""Analyze this compiled directory context to identify the collection type.

CONTEXT SUMMARY:
- {context["overview"]["total_files"]} total files
- Top directories: {", ".join(context["overview"]["top_level_dirs"])}
- File type groups: {", ".join(f"{k}:{v}" for k,v in context["overview"]["file_type_distribution"].items())}
- Special indicators: {", ".join(context["overview"]["special_indicators"]) if context["overview"]["special_indicators"] else "none"}
- Structural patterns: {", ".join(context["patterns"]["structural_hints"]) if context["patterns"]["structural_hints"] else "none detected"}
- Content hints: {", ".join(context["patterns"]["content_hints"]) if context["patterns"]["content_hints"] else "none detected"}

Available collection types:
- repositories: Git repositories with development tools and code
- research: Academic papers, citations, and research materials
- media: Photos, videos, audio files, and media assets
- creative: Design projects, artwork, and creative assets
- datasets: Data files, CSVs, and structured datasets

Return JSON:
{{
  "collection_type": "one of the types above",
  "confidence": 0.0-1.0,
  "reasoning": "brief explanation based on the patterns observed",
  "key_indicators": ["list of 2-3 key indicators that led to this conclusion"]
}}
"""

        try:
            messages = [
                {"role": "system", "content": "You are a collection type identifier. Analyze the provided compiled context and determine the most appropriate collection type. Focus on patterns and indicators, not raw file listings."},
                {"role": "user", "content": prompt}
            ]

            response = self.llm_client.chat(messages, temperature=0.1)
            result = self._parse_llm_response(response)

            return result

        except Exception as e:
            print(f"⚠️  Phase 1 identification failed: {e}")
            return None

    def _phase2_schema_generation(self, context: Dict[str, Any], identification_result: Dict[str, Any]) -> Dict[str, Any]:
        """Phase 2: Generate schema with type-specific context."""
        collection_type = identification_result["collection_type"]
        schema_focus = context["schema_focus"]

        prompt = f"""Design additional metadata fields for a {collection_type} collection.

COLLECTION TYPE: {collection_type}
PRIMARY FIELDS TO CONSIDER: {", ".join(schema_focus["primary_fields"])}
KEY CONSIDERATIONS: {", ".join(schema_focus["considerations"])}

SAMPLE FILE INSIGHTS:
{chr(10).join([f"- {s['name']}: {s['content'][:100]}..." for s in context["relevant_samples"]]) if context["relevant_samples"] else "Limited samples available"}

SUGGESTED CANDIDATES: {", ".join(context["metadata_candidates"])}

Design 3-6 additional metadata fields that would be valuable for organizing and understanding items in this {collection_type} collection. Consider what information would help with:
- Discovery and filtering
- Content understanding
- Relationship mapping
- Quality assessment

Return JSON:
{{
  "additional_metadata_fields": [
    {{
      "field_name": "camelCase_field_name",
      "description": "What this field captures",
      "data_type": "string|number|boolean|array|object",
      "required": false,
      "example_values": ["example1", "example2"]
    }}
  ],
  "field_rationale": "Explanation of why these fields are valuable for this collection type"
}}
"""

        try:
            messages = [
                {"role": "system", "content": "You are a metadata schema designer. Design additional fields that enhance understanding and organization of collection items."},
                {"role": "user", "content": prompt}
            ]

            response = self.llm_client.chat(messages, temperature=0.1)

            # Parse and return schema result
            try:
                result = self._parse_llm_response(response)
                return {
                    "additional_metadata_fields": result.get("additional_metadata_fields", []),
                    "field_rationale": result.get("field_rationale", "Schema designed for collection type")
                }
            except:
                # Fallback schema
                return {
                    "additional_metadata_fields": [
                        {"field_name": "notes", "description": "Additional notes", "data_type": "string", "required": False}
                    ],
                    "field_rationale": "Fallback schema due to parsing error"
                }

        except Exception as e:
            print(f"⚠️  Phase 2 schema generation failed: {e}")
            return {
                "additional_metadata_fields": [],
                "field_rationale": f"Schema generation failed: {e}"
            }

    def _phase3_categorization(self, context: Dict[str, Any], identification_result: Dict[str, Any]) -> Dict[str, Any]:
        """Phase 3: Generate category legend with organizational context."""
        collection_type = identification_result["collection_type"]
        hints = context["categorization_hints"]

        prompt = f"""Generate a custom category legend for a {collection_type} collection.

COLLECTION TYPE: {collection_type}
DIMENSIONS TO CONSIDER: {", ".join(hints["dimensions"])}
EXAMPLE CATEGORIES: {", ".join(hints["examples"])}

ORGANIZATIONAL PATTERNS: {", ".join(context["organizational_patterns"]) if context["organizational_patterns"] else "none detected"}
CONTENT THEMES: {", ".join(context["content_themes"]) if context["content_themes"] else "none detected"}
DIRECTORY STRUCTURE: {", ".join(context["structural_hierarchy"]) if context["structural_hierarchy"] else "flat structure"}

Create 4-8 categories that would help organize items in this collection. Each category should have:
- A clear, descriptive name
- A brief explanation of what belongs in it
- Consider the collection's purpose and content patterns

Return JSON:
{{
  "custom_categories": {{
    "category_key_1": "description of what this category contains",
    "category_key_2": "description of what this category contains",
    ...
  }},
  "categorization_strategy": "Brief explanation of the categorization approach used"
}}
"""

        try:
            messages = [
                {"role": "system", "content": "You are a categorization expert. Create meaningful categories that help organize and discover items in collections."},
                {"role": "user", "content": prompt}
            ]

            response = self.llm_client.chat(messages, temperature=0.1)

            # Parse and return categorization result
            try:
                result = self._parse_llm_response(response)
                return {
                    "custom_categories": result.get("custom_categories", {}),
                    "categorization_strategy": result.get("categorization_strategy", "Categories generated for collection")
                }
            except:
                # Fallback categories
                return {
                    "custom_categories": {
                        "general": "General items",
                        "specific": "Specific items",
                        "misc": "Miscellaneous items"
                    },
                    "categorization_strategy": "Fallback categorization due to parsing error"
                }

        except Exception as e:
            print(f"⚠️  Phase 3 categorization failed: {e}")
            return {
                "custom_categories": {
                    "general": "General items",
                    "misc": "Miscellaneous items"
                },
                "categorization_strategy": f"Categorization failed: {e}"
            }