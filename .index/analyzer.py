#!/usr/bin/env python3
"""
Analyzer Stage - Collection Type Detection
Uses LLM to inspect directory and determine collection type, then generates collection.yaml
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
import yaml

from llm import LLMClient, Message
from plugin_interface import PluginRegistry


class CollectionAnalyzer:
    """Analyzes directories to determine collection type and generate configuration"""

    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    def inspect_directory(self, path: Path, max_depth: int = 2, max_samples: int = 20) -> Dict[str, Any]:
        """
        Inspect directory structure and contents.
        Returns metadata about directory for LLM analysis.
        """
        if not path.is_dir():
            raise ValueError(f"Path is not a directory: {path}")

        inspection = {
            'path': str(path),
            'total_items': 0,
            'total_dirs': 0,
            'total_files': 0,
            'file_types': {},  # extension -> count
            'directory_names': [],  # sample of dir names
            'file_samples': [],  # sample of file names
            'has_git_repos': False,
            'readme_content': None
        }

        # Walk directory up to max_depth
        items = []
        for item in path.iterdir():
            if item.name.startswith('.'):
                continue
            items.append(item)
            if len(items) >= max_samples:
                break

        # Analyze items
        for item in items:
            inspection['total_items'] += 1

            if item.is_dir():
                inspection['total_dirs'] += 1
                inspection['directory_names'].append(item.name)

                # Check if git repo
                if (item / '.git').exists():
                    inspection['has_git_repos'] = True

            elif item.is_file():
                inspection['total_files'] += 1
                inspection['file_samples'].append(item.name)

                # Track file extensions
                ext = item.suffix.lower()
                if ext:
                    inspection['file_types'][ext] = inspection['file_types'].get(ext, 0) + 1

        # Look for README at collection root
        readme_patterns = ['README.md', 'readme.md', 'README', 'Readme.md']
        for pattern in readme_patterns:
            readme_path = path / pattern
            if readme_path.exists():
                try:
                    with open(readme_path, 'r', encoding='utf-8', errors='ignore') as f:
                        inspection['readme_content'] = f.read()[:2000]
                        break
                except Exception:
                    continue

        return inspection

    def generate_collection_config(
        self,
        path: Path,
        force_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate collection.yaml configuration.

        If force_type is specified, skip LLM detection and use that type.
        Otherwise, use LLM to analyze directory and determine type.

        Returns dict that can be saved as collection.yaml
        """
        # Inspect directory
        inspection = self.inspect_directory(path)

        # Determine collection type
        if force_type:
            collection_type = force_type
        else:
            # Use LLM to determine type
            collection_type = self._detect_collection_type(inspection)

        # Get appropriate scanner
        scanner_class = PluginRegistry.get_plugin(collection_type)
        if not scanner_class:
            raise ValueError(f"No scanner found for collection type: {collection_type}")

        scanner = scanner_class()

        # Build config
        config = {
            'collection_type': collection_type,
            'name': path.name,
            'path': str(path),
            'categories': scanner.get_categories(),
            'exclude_hidden': True,
            'scanner_config': {}
        }

        return config

    def _detect_collection_type(self, inspection: Dict[str, Any]) -> str:
        """
        Use LLM to detect collection type from inspection data.
        Returns collection type name (e.g., 'repositories', 'media', 'documents')
        """
        # Get available plugins
        plugins = PluginRegistry.list_plugins()
        plugin_info = '\n'.join([
            f"- {p.name}: {p.description}" for p in plugins
        ])

        # Build prompt
        prompt = f"""You are analyzing a directory to determine what type of collection it contains.

Available collection types:
{plugin_info}

Directory inspection:
- Total items: {inspection['total_items']}
- Directories: {inspection['total_dirs']}
- Files: {inspection['total_files']}
- Contains git repositories: {inspection['has_git_repos']}
- File types: {json.dumps(inspection['file_types'], indent=2)}
- Sample directory names: {', '.join(inspection['directory_names'][:10])}
- Sample file names: {', '.join(inspection['file_samples'][:10])}

README content (if present):
{inspection.get('readme_content', 'No README found')[:500]}

Based on this inspection, determine the collection type. Respond with ONLY the collection type name (e.g., "repositories", "media", "documents").

Collection type:"""

        # Query LLM
        try:
            response = self.llm.chat(
                model="gpt-oss-20b",  # Use configured model
                messages=[Message(role="user", content=prompt)],
                temperature=0.1,
                max_tokens=50
            )

            collection_type = response.strip().lower().replace('"', '')

            # Validate against registered plugins
            if PluginRegistry.get_plugin(collection_type):
                return collection_type
            else:
                # Fallback: use heuristics
                return self._heuristic_detection(inspection)

        except Exception as e:
            print(f"LLM detection failed: {e}, falling back to heuristics")
            return self._heuristic_detection(inspection)

    def _heuristic_detection(self, inspection: Dict[str, Any]) -> str:
        """
        Fallback heuristic-based detection when LLM fails.
        """
        # Check if mostly git repos
        if inspection['has_git_repos'] and inspection['total_dirs'] > 0:
            return "repositories"

        # Check file types for media
        media_extensions = {'.mp4', '.mkv', '.avi', '.mp3', '.flac', '.wav', '.jpg', '.png', '.gif'}
        if any(ext in media_extensions for ext in inspection['file_types'].keys()):
            return "media"

        # Check for documents
        doc_extensions = {'.pdf', '.doc', '.docx', '.txt', '.md'}
        if any(ext in doc_extensions for ext in inspection['file_types'].keys()):
            return "documents"

        # Default to utilities_misc
        return "repositories"  # Safe default since we have that plugin

    def create_collection(
        self,
        path: Path,
        force_type: Optional[str] = None,
        output_path: Optional[Path] = None
    ) -> Path:
        """
        Analyze directory and create collection.yaml config file.

        Returns path to created collection.yaml
        """
        # Generate config
        config = self.generate_collection_config(path, force_type=force_type)

        # Determine output path
        if output_path is None:
            output_path = path / 'collection.yaml'

        # Save config
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

        print(f"[OK] Created collection config: {output_path}")
        print(f"  Type: {config['collection_type']}")
        print(f"  Name: {config['name']}")
        print(f"  Categories: {len(config['categories'])}")

        return output_path


def analyze_collection(collection_path: str, force_type: Optional[str] = None) -> Path:
    """
    CLI helper: analyze a directory and create collection.yaml

    Args:
        collection_path: Path to directory to analyze
        force_type: Optional collection type to force (skip LLM detection)

    Returns:
        Path to created collection.yaml
    """
    from llm import create_client_from_config

    # Create LLM client
    llm_client = create_client_from_config()

    # Create analyzer
    analyzer = CollectionAnalyzer(llm_client)

    # Analyze and create collection
    path = Path(collection_path).resolve()
    return analyzer.create_collection(path, force_type=force_type)


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: python analyzer.py <collection_path> [force_type]")
        print("\nExample: python analyzer.py C:\\Users\\synta\\repos repositories")
        sys.exit(1)

    collection_path = sys.argv[1]
    force_type = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        result = analyze_collection(collection_path, force_type)
        print(f"\n[OK] Analysis complete: {result}")
    except Exception as e:
        print(f"[X] Analysis failed: {e}")
        sys.exit(1)
