#!/usr/bin/env python3
"""
Organic Workflow Integration for Collectivist
Handles "drop and process" workflows and intelligent content placement
"""

import os
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import yaml

from llm import LLMClient, Message
from plugin_interface import PluginRegistry, CollectionItem
from analyzer import CollectionAnalyzer
from events import EventEmitter, EventStage


class ContentProcessor:
    """
    Processes new content dropped into collections.
    Provides intelligent placement suggestions and automated filing.
    """

    def __init__(self, llm_client: LLMClient, event_emitter: Optional[EventEmitter] = None):
        self.llm = llm_client
        self.emitter = event_emitter

    def detect_new_content(self, collection_path: Path, since_hours: int = 24) -> List[Path]:
        """
        Detect new content added to collection in the last N hours.
        
        Args:
            collection_path: Root path of collection
            since_hours: Look for content added in last N hours
            
        Returns:
            List of paths to new content items
        """
        if self.emitter:
            self.emitter.info(f"Scanning for new content in {collection_path}")

        cutoff_time = datetime.now() - timedelta(hours=since_hours)
        new_items = []

        # Scan for new files and directories
        for item in collection_path.rglob('*'):
            # Skip hidden files and .collection directory
            if any(part.startswith('.') for part in item.parts):
                continue
                
            # Check if item is newer than cutoff
            try:
                created_time = datetime.fromtimestamp(item.stat().st_ctime)
                if created_time > cutoff_time:
                    new_items.append(item)
            except (OSError, ValueError):
                continue

        if self.emitter:
            self.emitter.info(f"Found {len(new_items)} new items")

        return new_items

    def analyze_content_placement(
        self, 
        item_path: Path, 
        collection_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze new content and suggest optimal placement within collection.
        Learns from existing filesystem structure - structure IS the memory.
        
        Args:
            item_path: Path to new content item
            collection_config: Collection configuration from collection.yaml
            
        Returns:
            Placement analysis with suggested location and reasoning
        """
        if self.emitter:
            self.emitter.info(f"Analyzing placement for {item_path.name}")

        # Get collection type and scanner
        collection_type = collection_config['collection_type']
        scanner_class = PluginRegistry.get_plugin(collection_type)
        
        if not scanner_class:
            return {
                'suggested_path': item_path,
                'confidence': 0.0,
                'reasoning': f"No scanner available for type: {collection_type}",
                'category': 'utilities_misc'
            }

        scanner = scanner_class()

        # Extract basic metadata
        try:
            stat = item_path.stat()
            metadata = {
                'size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'is_directory': item_path.is_dir(),
                'extension': item_path.suffix.lower() if item_path.is_file() else None
            }
        except OSError:
            metadata = {'size': 0, 'created': datetime.now().isoformat()}

        # Learn from existing structure - structure IS the memory
        collection_root = Path(collection_config['path'])
        structural_patterns = self._learn_from_structure(collection_root, collection_config)

        # Get content sample for LLM analysis
        content_sample = self._get_content_sample(item_path, scanner)

        # Use LLM to analyze content and suggest placement with structural context
        placement = self._llm_analyze_placement(
            item_path, 
            content_sample, 
            collection_config, 
            metadata,
            structural_patterns
        )

        return placement

    def _get_content_sample(self, item_path: Path, scanner) -> str:
        """Extract content sample for LLM analysis"""
        if item_path.is_file():
            # For files, try to read content sample
            try:
                if item_path.suffix.lower() in ['.txt', '.md', '.py', '.js', '.ts', '.json']:
                    with open(item_path, 'r', encoding='utf-8', errors='ignore') as f:
                        return f.read()[:2000]  # First 2000 chars
            except Exception:
                pass
            return f"File: {item_path.name} ({item_path.suffix})"
        
        elif item_path.is_dir():
            # For directories, analyze structure
            try:
                contents = list(item_path.iterdir())[:10]  # First 10 items
                content_summary = f"Directory: {item_path.name}\nContents:\n"
                for item in contents:
                    content_summary += f"  - {item.name}\n"
                
                # Look for README or similar files
                readme_patterns = ['README.md', 'readme.md', 'README', 'package.json']
                for pattern in readme_patterns:
                    readme_path = item_path / pattern
                    if readme_path.exists():
                        try:
                            with open(readme_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content_summary += f"\n{pattern}:\n{f.read()[:1000]}"
                                break
                        except Exception:
                            continue
                
                return content_summary
            except Exception:
                return f"Directory: {item_path.name}"
        
        return str(item_path.name)

    def _learn_from_structure(self, collection_root: Path, collection_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Learn organizational patterns from existing filesystem structure.
        Structure IS the memory - no external pattern storage needed.
        
        Args:
            collection_root: Root path of collection
            collection_config: Collection configuration
            
        Returns:
            Structural patterns extracted from filesystem reality
        """
        patterns = {
            'folder_hierarchy': {},
            'category_folders': {},
            'naming_conventions': {},
            'size_distributions': {},
            'depth_preferences': {}
        }

        try:
            # Load existing index to understand current categorization
            index_path = collection_root / '.collection' / 'index.yaml'
            if index_path.exists():
                with open(index_path, 'r', encoding='utf-8') as f:
                    index_data = yaml.safe_load(f) or []
                
                # Extract category → folder mapping from reality
                for item in index_data:
                    if item.get('category') and item.get('path'):
                        item_path = Path(item['path'])
                        relative_path = item_path.relative_to(collection_root)
                        folder_name = relative_path.parts[0] if relative_path.parts else 'root'
                        
                        category = item['category']
                        if category not in patterns['category_folders']:
                            patterns['category_folders'][category] = {}
                        
                        if folder_name not in patterns['category_folders'][category]:
                            patterns['category_folders'][category][folder_name] = 0
                        patterns['category_folders'][category][folder_name] += 1

            # Analyze current folder structure
            for item in collection_root.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    folder_name = item.name
                    
                    # Count items in folder
                    try:
                        item_count = len([x for x in item.rglob('*') if x.is_file()])
                        patterns['folder_hierarchy'][folder_name] = {
                            'item_count': item_count,
                            'depth': len(list(item.rglob('*'))) - item_count,  # Subfolder depth
                            'naming_style': self._analyze_naming_style(folder_name)
                        }
                    except (OSError, PermissionError):
                        continue

            # Extract preferred organizational depth
            if patterns['folder_hierarchy']:
                avg_depth = sum(
                    folder['depth'] for folder in patterns['folder_hierarchy'].values()
                ) / len(patterns['folder_hierarchy'])
                patterns['depth_preferences']['average'] = avg_depth
                patterns['depth_preferences']['max_observed'] = max(
                    folder['depth'] for folder in patterns['folder_hierarchy'].values()
                )

        except Exception as e:
            if self.emitter:
                self.emitter.warn(f"Could not analyze structure patterns: {e}")

        return patterns

    def _analyze_naming_style(self, folder_name: str) -> str:
        """Analyze naming convention from folder name"""
        if '-' in folder_name:
            return 'kebab-case'
        elif '_' in folder_name:
            return 'snake_case'
        elif folder_name.islower():
            return 'lowercase'
        elif folder_name.isupper():
            return 'uppercase'
        else:
            return 'mixed'

    def _llm_analyze_placement(
        self, 
        item_path: Path, 
        content_sample: str, 
        collection_config: Dict[str, Any], 
        metadata: Dict[str, Any],
        structural_patterns: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Use LLM to analyze content and suggest placement with structural context"""
        
        categories = collection_config.get('categories', ['utilities_misc'])
        collection_root = Path(collection_config['path'])
        
        # Build structural context for LLM
        structural_context = ""
        if structural_patterns['category_folders']:
            structural_context += "\nEXISTING ORGANIZATIONAL PATTERNS:\n"
            for category, folders in structural_patterns['category_folders'].items():
                most_common_folder = max(folders.items(), key=lambda x: x[1])[0]
                structural_context += f"- {category} items → typically in '{most_common_folder}/' folder\n"
        
        if structural_patterns['folder_hierarchy']:
            structural_context += f"\nCURRENT FOLDER STRUCTURE:\n"
            for folder, info in structural_patterns['folder_hierarchy'].items():
                structural_context += f"- {folder}/ ({info['item_count']} items, {info['naming_style']} naming)\n"

        # Build prompt for placement analysis
        prompt = f"""Analyze this new content and suggest optimal placement in the collection.
Learn from the existing organizational structure - structure IS the memory.

COLLECTION TYPE: {collection_config['collection_type']}
AVAILABLE CATEGORIES: {', '.join(categories)}

{structural_context}

NEW CONTENT:
Path: {item_path.name}
Type: {'Directory' if metadata.get('is_directory') else 'File'}
Size: {metadata.get('size', 0)} bytes
Extension: {metadata.get('extension', 'N/A')}

CONTENT SAMPLE:
{content_sample[:1500]}

Based on this analysis and the existing organizational patterns, suggest:
1. The most appropriate category from the available categories
2. A suggested folder structure that follows existing patterns
3. Your confidence level (0.0-1.0)
4. Brief reasoning that references existing organizational patterns

Respond with JSON:
{{
  "category": "category_name",
  "suggested_folder": "category/subfolder/path",
  "confidence": 0.0-1.0,
  "reasoning": "Brief explanation referencing existing patterns"
}}"""

        try:
            response = self.llm.chat(
                model="gpt-oss-20b",
                messages=[Message(role="user", content=prompt)],
                temperature=0.1,
                max_tokens=300
            )

            # Parse JSON response
            import json
            result = json.loads(response.strip())
            
            # Validate category
            suggested_category = result.get('category', 'utilities_misc')
            if suggested_category not in categories:
                suggested_category = categories[-1]  # Default to last category
            
            # Build suggested path using structural patterns
            suggested_folder = result.get('suggested_folder', suggested_category)
            
            # If we have structural patterns, prefer existing folder structure
            if (suggested_category in structural_patterns['category_folders'] and 
                structural_patterns['category_folders'][suggested_category]):
                # Use most common folder for this category
                most_common_folder = max(
                    structural_patterns['category_folders'][suggested_category].items(),
                    key=lambda x: x[1]
                )[0]
                suggested_folder = most_common_folder
            
            suggested_path = collection_root / suggested_folder / item_path.name
            
            return {
                'suggested_path': suggested_path,
                'category': suggested_category,
                'confidence': float(result.get('confidence', 0.5)),
                'reasoning': result.get('reasoning', 'LLM analysis with structural context'),
                'suggested_folder': suggested_folder,
                'structural_patterns_used': bool(structural_patterns['category_folders'])
            }

        except Exception as e:
            if self.emitter:
                self.emitter.warn(f"LLM placement analysis failed: {e}")
            
            # Fallback to structural heuristics
            return self._structural_heuristic_placement(
                item_path, collection_config, metadata, structural_patterns
            )

    def _structural_heuristic_placement(
        self, 
        item_path: Path, 
        collection_config: Dict[str, Any], 
        metadata: Dict[str, Any],
        structural_patterns: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Fallback heuristic placement using structural patterns when LLM fails"""
        
        categories = collection_config.get('categories', ['utilities_misc'])
        collection_root = Path(collection_config['path'])
        
        # Try to use structural patterns first
        name_lower = item_path.name.lower()
        
        # Look for existing patterns that match content
        suggested_category = categories[-1]  # Default fallback
        suggested_folder = suggested_category
        confidence = 0.2  # Low confidence for heuristics
        reasoning = "Heuristic placement"
        
        # If we have structural patterns, use them
        if structural_patterns['category_folders']:
            # Repository-specific heuristics with structural awareness
            if collection_config['collection_type'] == 'repositories':
                if any(keyword in name_lower for keyword in ['ai', 'llm', 'gpt', 'agent']):
                    if 'ai_llm_agents' in structural_patterns['category_folders']:
                        suggested_category = 'ai_llm_agents'
                        # Use most common folder for this category
                        folders = structural_patterns['category_folders']['ai_llm_agents']
                        suggested_folder = max(folders.items(), key=lambda x: x[1])[0]
                        confidence = 0.4
                        reasoning = "Heuristic + structural pattern: AI/LLM content → existing ai_llm_agents folder"
                elif any(keyword in name_lower for keyword in ['terminal', 'cli', 'tui']):
                    if 'terminal_ui' in structural_patterns['category_folders']:
                        suggested_category = 'terminal_ui'
                        folders = structural_patterns['category_folders']['terminal_ui']
                        suggested_folder = max(folders.items(), key=lambda x: x[1])[0]
                        confidence = 0.4
                        reasoning = "Heuristic + structural pattern: Terminal content → existing terminal_ui folder"
                elif any(keyword in name_lower for keyword in ['tool', 'util']):
                    if 'dev_tools' in structural_patterns['category_folders']:
                        suggested_category = 'dev_tools'
                        folders = structural_patterns['category_folders']['dev_tools']
                        suggested_folder = max(folders.items(), key=lambda x: x[1])[0]
                        confidence = 0.4
                        reasoning = "Heuristic + structural pattern: Tool content → existing dev_tools folder"
        
        # Ensure category exists in available categories
        if suggested_category not in categories:
            suggested_category = categories[-1]
            suggested_folder = suggested_category
            confidence = 0.2
            reasoning = "Fallback to default category"
        
        suggested_path = collection_root / suggested_folder / item_path.name
        
        return {
            'suggested_path': suggested_path,
            'category': suggested_category,
            'confidence': confidence,
            'reasoning': reasoning,
            'suggested_folder': suggested_folder,
            'structural_patterns_used': bool(structural_patterns['category_folders'])
        }

    def process_new_content(
        self, 
        collection_path: Path, 
        auto_file: bool = False,
        confidence_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Process all new content in collection.
        
        Args:
            collection_path: Root path of collection
            auto_file: Automatically move items with high confidence
            confidence_threshold: Minimum confidence for auto-filing
            
        Returns:
            List of processing results for each new item
        """
        if self.emitter:
            self.emitter.set_stage(EventStage.ANALYZE)
            self.emitter.info("Starting new content processing")

        # Load collection config
        config_path = collection_path / 'collection.yaml'
        if not config_path.exists():
            if self.emitter:
                self.emitter.error(f"No collection.yaml found at {config_path}")
            return []

        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        # Detect new content
        new_items = self.detect_new_content(collection_path)
        
        if not new_items:
            if self.emitter:
                self.emitter.info("No new content detected")
            return []

        results = []
        
        for i, item_path in enumerate(new_items, 1):
            if self.emitter:
                self.emitter.set_progress(i, item_path.name)

            # Analyze placement
            placement = self.analyze_content_placement(item_path, config)
            
            # Decide whether to auto-file
            should_auto_file = (
                auto_file and 
                placement['confidence'] >= confidence_threshold
            )

            result = {
                'item_path': item_path,
                'placement': placement,
                'auto_filed': False,
                'error': None
            }

            if should_auto_file:
                try:
                    # Create target directory if needed
                    target_path = placement['suggested_path']
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Move the item
                    shutil.move(str(item_path), str(target_path))
                    result['auto_filed'] = True
                    
                    if self.emitter:
                        self.emitter.success(f"Auto-filed {item_path.name} → {placement['suggested_folder']}")
                        
                except Exception as e:
                    result['error'] = str(e)
                    if self.emitter:
                        self.emitter.error(f"Failed to auto-file {item_path.name}: {e}")
            else:
                if self.emitter:
                    confidence_pct = int(placement['confidence'] * 100)
                    self.emitter.info(f"Suggest: {item_path.name} → {placement['suggested_folder']} ({confidence_pct}% confidence)")

            results.append(result)

        if self.emitter:
            auto_filed_count = sum(1 for r in results if r['auto_filed'])
            self.emitter.complete_stage(f"Processed {len(results)} items, auto-filed {auto_filed_count}")

        return results


def process_collection_cli(
    collection_path: str, 
    auto_file: bool = False,
    confidence_threshold: float = 0.7
):
    """
    CLI helper for processing new content in a collection.
    
    Args:
        collection_path: Path to collection directory
        auto_file: Automatically move items with high confidence
        confidence_threshold: Minimum confidence for auto-filing
    """
    from llm import create_client_from_config
    from events import create_console_emitter

    collection_path = Path(collection_path).resolve()
    
    # Create LLM client and event emitter
    llm_client = create_client_from_config()
    emitter = create_console_emitter()
    
    # Create processor
    processor = ContentProcessor(llm_client, emitter)
    
    # Process new content
    results = processor.process_new_content(
        collection_path, 
        auto_file=auto_file,
        confidence_threshold=confidence_threshold
    )
    
    # Show summary
    if results:
        print(f"\n[OK] Processing complete:")
        print(f"  Total items: {len(results)}")
        print(f"  Auto-filed: {sum(1 for r in results if r['auto_filed'])}")
        print(f"  Suggestions: {sum(1 for r in results if not r['auto_filed'] and not r['error'])}")
        print(f"  Errors: {sum(1 for r in results if r['error'])}")
        
        # Show suggestions for manual review
        suggestions = [r for r in results if not r['auto_filed'] and not r['error']]
        if suggestions:
            print(f"\n[!] Manual review suggested:")
            for result in suggestions:
                placement = result['placement']
                confidence_pct = int(placement['confidence'] * 100)
                print(f"  {result['item_path'].name} → {placement['suggested_folder']} ({confidence_pct}%)")
                print(f"    Reason: {placement['reasoning']}")
    else:
        print("[OK] No new content to process")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2 or '--help' in sys.argv:
        print("Usage: python organic.py <collection_path> [--auto-file] [--threshold 0.7]")
        print("\nExample: python organic.py C:\\Users\\synta\\repos --auto-file --threshold 0.8")
        print("\nOptions:")
        print("  --auto-file    Automatically move items with high confidence")
        print("  --threshold N  Minimum confidence for auto-filing (default: 0.7)")
        sys.exit(0 if '--help' in sys.argv else 1)
    
    collection_path = sys.argv[1]
    auto_file = '--auto-file' in sys.argv
    
    # Parse threshold
    threshold = 0.7
    if '--threshold' in sys.argv:
        try:
            threshold_idx = sys.argv.index('--threshold') + 1
            threshold = float(sys.argv[threshold_idx])
        except (IndexError, ValueError):
            print("Invalid threshold value")
            sys.exit(1)
    
    try:
        process_collection_cli(collection_path, auto_file, threshold)
    except Exception as e:
        print(f"[X] Processing failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)