#!/usr/bin/env python3
"""
Collectivist CLI Entry Point
Usage: python .collection/src/__main__.py <command> [options]
   or: python -m .collection.src <command> [options] (if .collection is in PYTHONPATH)

Commands:
  analyze   - Detect collection type and generate collection.yaml
  scan      - Discover items and extract metadata
  describe  - Generate LLM descriptions and categories
  render    - Generate README.md and other outputs
  update    - Run full pipeline (analyze + scan + describe + render)

The CLI operates on the current working directory as the collection path.
"""

import sys
import argparse
from pathlib import Path
from typing import Optional

# Add current directory to Python path for imports
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Import pipeline components
from pipeline import run_full_pipeline, load_collection_config, get_workflow_config_from_collection
from analyzer import CollectionAnalyzer
from describer import CollectionDescriber
from readme_generator import generate_collection
from llm import create_client_from_config, test_llm_connection
from plugin_interface import PluginRegistry
from events import create_console_emitter

# Import plugins to trigger registration
import repository_scanner  # noqa: F401
import fallback_scanner  # noqa: F401

# Import additional plugins from plugins directory
plugins_path = current_dir.parent / 'plugins'
if plugins_path.exists():
    sys.path.insert(0, str(plugins_path))
    try:
        import media  # noqa: F401
        import documents  # noqa: F401
        import obsidian  # noqa: F401
        import fallback as fallback_plugin  # noqa: F401
    except ImportError:
        pass  # Plugins not available


def get_collection_path() -> Path:
    """Get current working directory as collection path"""
    return Path.cwd().resolve()


def cmd_analyze(args):
    """Analyze collection and generate collection.yaml"""
    collection_path = get_collection_path()
    
    print(f"Analyzing collection: {collection_path}")
    print()
    
    try:
        # Create LLM client
        llm_client = create_client_from_config()
        
        # Test LLM connection
        print("Testing LLM connection...")
        if not test_llm_connection(llm_client):
            print("[X] FATAL: Cannot reach LLM endpoint")
            print("  Configure LLM provider in .collection/collectivist.yaml or ~/.collectivist/config.yaml")
            return False
        print("[OK] LLM connection OK\n")
        
        # Create analyzer
        analyzer = CollectionAnalyzer(llm_client)
        
        # Analyze and create collection.yaml
        config_path = analyzer.create_collection(
            collection_path, 
            force_type=args.force_type
        )
        
        print(f"\n[OK] Analysis complete: {config_path}")
        return True
        
    except Exception as e:
        print(f"[X] Analysis failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return False


def cmd_scan(args):
    """Scan collection and extract metadata"""
    collection_path = get_collection_path()
    
    print(f"Scanning collection: {collection_path}")
    print()
    
    try:
        # Run pipeline with only scan stage
        run_full_pipeline(
            collection_path=collection_path,
            skip_analyze=True,
            skip_describe=True,
            skip_readme=True,
            skip_process_new=True
        )
        return True
        
    except Exception as e:
        print(f"[X] Scan failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return False


def cmd_describe(args):
    """Generate LLM descriptions and categories"""
    collection_path = get_collection_path()
    
    print(f"Describing collection: {collection_path}")
    print()
    
    try:
        # Run pipeline with only describe stage
        run_full_pipeline(
            collection_path=collection_path,
            skip_analyze=True,
            skip_scan=True,
            skip_readme=True,
            skip_process_new=True,
            max_workers=args.max_workers
        )
        return True
        
    except Exception as e:
        print(f"[X] Description failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return False


def cmd_render(args):
    """Generate README.md and other outputs"""
    collection_path = get_collection_path()
    
    print(f"Rendering collection: {collection_path}")
    print()
    
    try:
        # Run pipeline with only render stage
        run_full_pipeline(
            collection_path=collection_path,
            skip_analyze=True,
            skip_scan=True,
            skip_describe=True,
            skip_process_new=True
        )
        return True
        
    except Exception as e:
        print(f"[X] Render failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return False


def cmd_update(args):
    """Run full pipeline (analyze + scan + describe + render)"""
    collection_path = get_collection_path()
    
    print(f"Updating collection: {collection_path}")
    print()
    
    try:
        # Determine workflow configuration from collection.yaml if it exists
        workflow_config = {"mode": "manual"}  # Default
        
        try:
            workflow_config = get_workflow_config_from_collection(collection_path)
        except FileNotFoundError:
            # No collection.yaml yet, will be created by analyzer
            pass
        
        # Run full pipeline
        run_full_pipeline(
            collection_path=collection_path,
            skip_analyze=args.skip_analyze,
            skip_scan=args.skip_scan,
            skip_describe=args.skip_describe,
            skip_readme=args.skip_render,
            skip_process_new=args.skip_process_new,
            force_type=args.force_type,
            max_workers=args.max_workers,
            auto_file=workflow_config.get('auto_file', False),
            confidence_threshold=workflow_config.get('confidence_threshold', 0.7),
            workflow_mode=workflow_config.get('mode', 'manual')
        )
        return True
        
    except Exception as e:
        print(f"[X] Update failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return False


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        prog="python .collection/src/__main__.py",
        description="Collectivist - AI-powered collection curator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python .collection/__main__.py analyze              # Detect collection type
  python .collection/__main__.py scan                 # Scan for items and metadata
  python .collection/__main__.py describe             # Generate descriptions
  python .collection/__main__.py render               # Generate README.md
  python .collection/__main__.py update               # Run full pipeline
  
  python .collection/__main__.py analyze --force-type repositories
  python .collection/__main__.py describe --max-workers 10
  python .collection/__main__.py update --skip-analyze --skip-scan
        """
    )
    
    # Global options
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output and error tracebacks'
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(
        dest='command',
        help='Available commands',
        metavar='COMMAND'
    )
    
    # analyze command
    analyze_parser = subparsers.add_parser(
        'analyze',
        help='Detect collection type and generate collection.yaml'
    )
    analyze_parser.add_argument(
        '--force-type',
        type=str,
        help='Force collection type (e.g., repositories, media, documents)'
    )
    
    # scan command
    scan_parser = subparsers.add_parser(
        'scan',
        help='Discover items and extract metadata'
    )
    
    # describe command
    describe_parser = subparsers.add_parser(
        'describe',
        help='Generate LLM descriptions and categories'
    )
    describe_parser.add_argument(
        '--max-workers',
        type=int,
        default=5,
        help='Number of concurrent workers for LLM requests (default: 5)'
    )
    
    # render command
    render_parser = subparsers.add_parser(
        'render',
        help='Generate README.md and other outputs'
    )
    
    # update command (full pipeline)
    update_parser = subparsers.add_parser(
        'update',
        help='Run full pipeline (analyze + scan + describe + render)'
    )
    update_parser.add_argument(
        '--skip-analyze',
        action='store_true',
        help='Skip analyzer stage (requires existing collection.yaml)'
    )
    update_parser.add_argument(
        '--skip-scan',
        action='store_true',
        help='Skip scanner stage (requires existing index)'
    )
    update_parser.add_argument(
        '--skip-describe',
        action='store_true',
        help='Skip describer stage'
    )
    update_parser.add_argument(
        '--skip-render',
        action='store_true',
        help='Skip render stage'
    )
    update_parser.add_argument(
        '--skip-process-new',
        action='store_true',
        help='Skip new content processing stage'
    )
    update_parser.add_argument(
        '--force-type',
        type=str,
        help='Force collection type (e.g., repositories, media, documents)'
    )
    update_parser.add_argument(
        '--max-workers',
        type=int,
        default=5,
        help='Number of concurrent workers for LLM requests (default: 5)'
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Show help if no command specified
    if not args.command:
        parser.print_help()
        return 1
    
    # Dispatch to command handlers
    command_handlers = {
        'analyze': cmd_analyze,
        'scan': cmd_scan,
        'describe': cmd_describe,
        'render': cmd_render,
        'update': cmd_update,
    }
    
    handler = command_handlers.get(args.command)
    if not handler:
        print(f"Unknown command: {args.command}")
        return 1
    
    # Execute command
    try:
        success = handler(args)
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user")
        return 1
    except Exception as e:
        print(f"[X] Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())