#!/usr/bin/env python3
"""
Main Pipeline - The Collectivist
Orchestrates: Analyzer → Scanner → Describer → README Generator
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any, Dict, Any
import yaml

from llm import create_client_from_config, test_llm_connection
from plugin_interface import PluginRegistry, CollectionItem
from analyzer import CollectionAnalyzer
from describer import CollectionDescriber
from events import EventEmitter, create_console_emitter
from organic import ContentProcessor

# Import plugins to trigger registration
import repository_scanner  # noqa: F401
import fallback_scanner  # noqa: F401

# Import additional plugins from plugins directory
import sys
plugins_path = Path(__file__).parent.parent / 'plugins'
if plugins_path.exists():
    sys.path.insert(0, str(plugins_path))
    try:
        import media  # noqa: F401
        import documents  # noqa: F401
        import obsidian  # noqa: F401
        import fallback as fallback_plugin  # noqa: F401
    except ImportError:
        pass  # Plugins not available


def load_collection_config(collection_path: Path) -> Dict[str, Any]:
    """Load collection.yaml schema configuration"""
    config_path = collection_path / '.collection' / 'collection.yaml'
    
    # Also check for collection.yaml in root (legacy support)
    if not config_path.exists():
        legacy_config_path = collection_path / 'collection.yaml'
        if legacy_config_path.exists():
            config_path = legacy_config_path

    if not config_path.exists():
        raise FileNotFoundError(
            f"No collection.yaml found at {config_path}\n"
            f"Run analyzer first to create configuration."
        )

    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # Ensure schedule configuration exists with defaults
    if 'schedule' not in config:
        config['schedule'] = {
            'enabled': False,
            'interval_days': 7,
            'operations': ['scan', 'describe', 'render'],
            'auto_file': False,
            'confidence_threshold': 0.8
        }
    
    return config


def get_workflow_config_from_collection(collection_path: Path) -> Dict[str, Any]:
    """
    Extract workflow configuration from collection.yaml.
    Returns workflow mode and parameters based on schedule settings.
    """
    config = load_collection_config(collection_path)
    schedule = config.get('schedule', {})
    
    # Determine workflow mode from schedule configuration
    if not schedule.get('enabled', False):
        workflow_mode = "manual"
    elif schedule.get('enabled') == "organic":
        workflow_mode = "organic"
    elif schedule.get('enabled') is True:
        workflow_mode = "scheduled"
    else:
        workflow_mode = "manual"
    
    # Extract workflow parameters
    workflow_config = {
        'mode': workflow_mode,
        'auto_file': schedule.get('auto_file', False),
        'confidence_threshold': schedule.get('confidence_threshold', 0.7),
        'operations': schedule.get('operations', ['scan', 'describe', 'render']),
        'interval_days': schedule.get('interval_days', 7)
    }
    
    return workflow_config


def save_index(items: list[CollectionItem], index_path: Path, collection_overview: Optional[str] = None):
    """Save items to collection-index.yaml with optional collection overview"""
    # Convert items to dictionaries
    items_data = []
    for item in items:
        item_dict = {
            'short_name': item.short_name,
            'type': item.type,
            'size': item.size,
            'created': item.created,
            'modified': item.modified,
            'accessed': item.accessed,
            'path': item.path,
            'description': item.description,
            'category': item.category,
        }
        # Add metadata fields (flattened)
        if item.metadata:
            item_dict.update(item.metadata)

        items_data.append(item_dict)

    # Create the complete document structure
    if collection_overview:
        # Save as a document with collection_overview and items
        document = {
            'collection_overview': collection_overview,
            'items': items_data
        }
    else:
        # Save as direct array for backward compatibility
        document = items_data

    with open(index_path, 'w', encoding='utf-8') as f:
        yaml.dump(document, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


def load_index(index_path: Path) -> tuple[list[CollectionItem], Optional[str]]:
    """Load items from collection-index.yaml, returning items and collection overview"""
    if not index_path.exists():
        return [], None

    with open(index_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f) or []

    # Handle both formats: new format (dict with collection_overview) and old format (direct list)
    collection_overview = None
    items_data = []
    
    if isinstance(data, dict):
        # New format: document with collection_overview and items
        collection_overview = data.get('collection_overview')
        items_data = data.get('items', [])
    elif isinstance(data, list):
        # Old format: direct array of items
        items_data = data
    else:
        # Fallback: treat as empty
        items_data = []

    # Convert to CollectionItem objects
    items = []
    for item_data in items_data:
        # Extract standard fields
        standard_fields = {
            'short_name', 'type', 'size', 'created', 'modified',
            'accessed', 'path', 'description', 'category'
        }

        # Everything else goes to metadata
        metadata = {k: v for k, v in item_data.items() if k not in standard_fields}

        item = CollectionItem(
            short_name=item_data['short_name'],
            type=item_data['type'],
            size=item_data['size'],
            created=item_data['created'],
            modified=item_data['modified'],
            accessed=item_data['accessed'],
            path=item_data['path'],
            description=item_data.get('description'),
            category=item_data.get('category'),
            metadata=metadata
        )
        items.append(item)

    return items, collection_overview


def run_full_pipeline(
    collection_path: Path,
    skip_analyze: bool = False,
    skip_scan: bool = False,
    skip_describe: bool = False,
    skip_readme: bool = False,
    skip_process_new: bool = False,
    force_type: Optional[str] = None,
    max_workers: int = 5,
    auto_file: bool = False,
    confidence_threshold: float = 0.7,
    event_emitter: Optional[EventEmitter] = None,
    workflow_mode: str = "manual"
):
    """
    Run the complete Collectivist pipeline.

    Args:
        collection_path: Root path of collection
        skip_analyze: Skip analyzer stage (requires existing collection.yaml)
        skip_scan: Skip scanner stage (requires existing index)
        skip_describe: Skip describer stage
        skip_readme: Skip README generation stage
        skip_process_new: Skip new content processing stage
        force_type: Force collection type (skip LLM detection)
        max_workers: Number of concurrent workers for describer
        auto_file: Automatically move new items with high confidence
        confidence_threshold: Minimum confidence for auto-filing
        event_emitter: Optional event emitter for progress updates
        workflow_mode: Workflow mode - "manual", "scheduled", or "organic"
    """
    collection_path = collection_path.resolve()
    index_dir = collection_path / '.collection'
    index_path = index_dir / 'collection-index.yaml'
    config_path = index_dir / 'collection.yaml'

    # Use console emitter if none provided (backward compatibility)
    emitter = event_emitter or create_console_emitter()

    # Create .collection directory if needed
    index_dir.mkdir(exist_ok=True)

    if not event_emitter:  # Only print header for console mode
        print(f"Collectivist Pipeline")
        print(f"Collection: {collection_path}")
        print(f"Mode: {workflow_mode}")
        print()

    # Determine workflow behavior based on mode
    if workflow_mode == "manual":
        # Manual mode: respect all skip flags, no automatic processing
        pass
    elif workflow_mode == "scheduled":
        # Scheduled mode: regular indexing, no new content processing
        skip_process_new = True
        auto_file = False
    elif workflow_mode == "organic":
        # Organic mode: full workflow with intelligent curation
        skip_process_new = False
        # auto_file and confidence_threshold can be configured per collection

    # Stage 0: Process New Content (organic workflow)
    if not skip_process_new:
        if not event_emitter:  # Console mode
            print("=" * 60)
            print("STAGE 0: ORGANIC - New Content Processing")
            print("=" * 60)

        # Create content processor
        llm_client = create_client_from_config()
        processor = ContentProcessor(llm_client, emitter)

        # Process new content
        results = processor.process_new_content(
            collection_path,
            auto_file=auto_file,
            confidence_threshold=confidence_threshold
        )

        if not event_emitter and results:  # Console mode
            auto_filed = sum(1 for r in results if r['auto_filed'])
            suggestions = sum(1 for r in results if not r['auto_filed'] and not r['error'])
            print(f"[OK] Processed {len(results)} new items: {auto_filed} auto-filed, {suggestions} suggestions")
            print()

    # Stage 1: Analyze (create collection.yaml)
    if not skip_analyze:
        if not event_emitter:  # Only print stage headers for console mode
            print("=" * 60)
            print("STAGE 1: ANALYZER - Collection Type Detection")
            print("=" * 60)

        llm_client = create_client_from_config()
        analyzer = CollectionAnalyzer(llm_client, emitter)

        if not config_path.exists():
            if emitter and not event_emitter:  # Console mode
                print("No collection.yaml found, creating...")
            analyzer.create_collection(collection_path, force_type=force_type)
        else:
            if emitter and not event_emitter:  # Console mode
                print("[OK] collection.yaml already exists")

        if not event_emitter:  # Console mode
            print()

    # Load config
    config = load_collection_config(collection_path)
    collection_type = config['collection_type']

    # Get scanner
    scanner_class = PluginRegistry.get_plugin(collection_type)
    if not scanner_class:
        raise ValueError(f"No scanner plugin found for type: {collection_type}")

    scanner = scanner_class()

    # Stage 2: Scan (discover items, extract metadata)
    if not skip_scan:
        if not event_emitter:  # Console mode
            print("=" * 60)
            print("STAGE 2: SCANNER - Item Discovery & Metadata Extraction")
            print("=" * 60)
            print(f"Scanner: {scanner.get_name()}")
            print("Scanning collection...")

        # Load existing index to preserve descriptions/categories
        existing_items, existing_overview = load_index(index_path)
        preserve_data = {
            item.path: {
                'description': item.description,
                'category': item.category
            }
            for item in existing_items
        }

        # Add preserve_data to scanner config
        scanner_config = config.get('scanner_config', {})
        scanner_config['preserve_data'] = preserve_data
        scanner_config['exclude_hidden'] = config.get('exclude_hidden', True)

        # Scan collection
        items = scanner.scan(collection_path, scanner_config)

        # Save index (preserve existing overview for now)
        save_index(items, index_path, existing_overview)

        if not event_emitter:  # Console mode
            print(f"[OK] Scanned {len(items)} items")
            print(f"  Saved to {index_path}")
            print()
    else:
        # Load existing index
        items, collection_overview = load_index(index_path)

    # Stage 3: Describe (LLM description generation)
    if not skip_describe:
        if not event_emitter:  # Console mode
            print("=" * 60)
            print("STAGE 3: DESCRIBER - LLM Description Generation")
            print("=" * 60)

        # Create LLM client and test connection
        llm_client = create_client_from_config()

        if not event_emitter:  # Console mode
            print("Testing LLM connection...")
        if not test_llm_connection(llm_client):
            error_msg = "Cannot reach LLM endpoint - Configure LLM_PROVIDER in .env file"
            if emitter:
                emitter.error(error_msg)
            else:
                print(f"[X] FATAL: {error_msg}")
            sys.exit(1)

        if not event_emitter:  # Console mode
            print("[OK] LLM connection OK\n")

        # Create describer
        describer = CollectionDescriber(llm_client, scanner, max_workers, emitter)

        # Define save callback for incremental saves (preserve existing overview during incremental saves)
        def save_callback(updated_items):
            save_index(updated_items, index_path, collection_overview)

        # Generate descriptions and collection overview
        items, new_overview = describer.describe_collection(items, save_callback=save_callback)
        
        # Update collection overview if we got a new one
        if new_overview:
            collection_overview = new_overview
            # Final save with the new overview
            save_index(items, index_path, collection_overview)

        if not event_emitter:  # Console mode
            print()

    # Stage 4: README Generation
    if not skip_readme:
        if not event_emitter:  # Console mode
            print("=" * 60)
            print("STAGE 4: README GENERATOR - Documentation Generation")
            print("=" * 60)

        from readme_generator import generate_collection, generate_html_collection

        # Generate markdown documentation
        readme_path = collection_path / 'Collection.md'
        generate_collection(
            items=items,
            collection_name=config['name'],
            collection_type=collection_type,
            output_path=readme_path,
            collection_overview=collection_overview,
            event_emitter=emitter
        )

        # Generate HTML index
        html_path = collection_path / 'Collection.html'
        generate_html_collection(
            items=items,
            collection_name=config['name'],
            collection_type=collection_type,
            output_path=html_path,
            collection_overview=collection_overview,
            event_emitter=emitter
        )

        if not event_emitter:  # Console mode
            print()

    # Final summary
    if not event_emitter:  # Console mode
        print("=" * 60)
        print("PIPELINE COMPLETE")
        print("=" * 60)
        print(f"Total items: {len(items)}")
        print(f"Described: {sum(1 for item in items if item.description)}")
        print(f"Categorized: {sum(1 for item in items if item.category)}")
        print()


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="The Collectivist - Universal collection indexing system"
    )
    parser.add_argument(
        'collection_path',
        type=str,
        help='Path to collection directory'
    )
    parser.add_argument(
        '--skip-analyze',
        action='store_true',
        help='Skip analyzer stage (requires existing collection.yaml)'
    )
    parser.add_argument(
        '--skip-scan',
        action='store_true',
        help='Skip scanner stage (requires existing index)'
    )
    parser.add_argument(
        '--skip-describe',
        action='store_true',
        help='Skip describer stage'
    )
    parser.add_argument(
        '--skip-readme',
        action='store_true',
        help='Skip README generation'
    )
    parser.add_argument(
        '--force-type',
        type=str,
        help='Force collection type (e.g., repositories, media, documents)'
    )
    parser.add_argument(
        '--max-workers',
        type=int,
        default=5,
        help='Number of concurrent workers for describer (default: 5)'
    )
    parser.add_argument(
        '--skip-process-new',
        action='store_true',
        help='Skip new content processing stage'
    )
    parser.add_argument(
        '--auto-file',
        action='store_true',
        help='Automatically move new items with high confidence'
    )
    parser.add_argument(
        '--confidence-threshold',
        type=float,
        default=0.7,
        help='Minimum confidence for auto-filing (default: 0.7)'
    )
    parser.add_argument(
        '--workflow-mode',
        type=str,
        choices=['manual', 'scheduled', 'organic'],
        default='manual',
        help='Workflow mode: manual (default), scheduled, or organic'
    )

    args = parser.parse_args()

    try:
        run_full_pipeline(
            collection_path=Path(args.collection_path),
            skip_analyze=args.skip_analyze,
            skip_scan=args.skip_scan,
            skip_describe=args.skip_describe,
            skip_readme=args.skip_readme,
            skip_process_new=args.skip_process_new,
            force_type=args.force_type,
            max_workers=args.max_workers,
            auto_file=args.auto_file,
            confidence_threshold=args.confidence_threshold,
            workflow_mode=args.workflow_mode
        )
    except Exception as e:
        print(f"\nX Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
