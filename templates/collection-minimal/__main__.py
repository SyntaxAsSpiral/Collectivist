#!/usr/bin/env python3
"""
Collectivist - Minimal Level CLI

Zero-install collection curator. Drop this .collection/ folder into any directory
containing files you want to organize as an intentional collection.

Usage:
    python -m .collection analyze    # Initialize collection (WARNING: resets schema evolution)
    python -m .collection update     # Full pipeline: scan → describe → render
    python -m .collection scan       # Just scan for changes
    python -m .collection describe   # Just generate descriptions
    python -m .collection render     # Just regenerate outputs

For interactive viewing:
    nu .collection/view.nu           # CLI dashboard
    open .collection/dashboard.html  # HTML dashboard
"""

import argparse
import sys
from pathlib import Path
import traceback

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from pipeline import CollectionPipeline


def main():
    """Main CLI entry point for Collectivist minimal level."""

    parser = argparse.ArgumentParser(
        prog="collectivist",
        description="AI-powered collection curator for intentional collections",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m .collection analyze    # First-time setup
  python -m .collection update     # Full pipeline
  nu .collection/view.nu           # Interactive CLI view
  open .collection/dashboard.html  # Static HTML dashboard

Collection Types Supported:
  • repositories  - Git-aware metadata and commit summaries
  • research      - Citation extraction and topic clustering
  • media         - Timeline-aware organization and mood inference
  • creative      - Version tracking and asset linking
  • datasets      - Schema inference and sample previews
        """
    )

    parser.add_argument(
        "command",
        choices=["analyze", "scan", "describe", "render", "update"],
        help="Command to execute"
    )

    parser.add_argument(
        "--force-type",
        choices=["repositories", "research", "media", "creative", "datasets"],
        help="Force specific collection type (skip LLM analysis)"
    )

    parser.add_argument(
        "--config",
        type=str,
        help="Path to custom config file (default: auto-detect)"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )

    args = parser.parse_args()

    try:
        # Initialize LLM client with config
        from llm import LLMClient
        from pathlib import Path

        config_path = Path(args.config) if args.config else None
        llm_client = LLMClient.from_config(config_path)

        # Initialize pipeline with LLM client
        pipeline = CollectionPipeline(llm_client=llm_client)

        if args.command == "analyze":
            if args.force_type:
                print(f"🔍 Analyzing as {args.force_type} collection...")
                pipeline.analyze(force_type=args.force_type)
            else:
                print("🔍 Analyzing collection type...")
                pipeline.analyze()

        elif args.command == "scan":
            print("🔎 Scanning for items...")
            pipeline.scan()

        elif args.command == "describe":
            print("🧠 Generating descriptions...")
            pipeline.describe()

        elif args.command == "render":
            print("📝 Rendering outputs...")
            pipeline.render()

        elif args.command == "update":
            print("🚀 Running full pipeline...")
            pipeline.update(force_type=args.force_type if args.force_type else None)

        print("✅ Complete!")

        # Show next steps
        collection_path = Path.cwd()
        if (collection_path / ".collection" / "index.yaml").exists():
            print("
📊 View results:"            print(f"  nu {collection_path}/.collection/view.nu")
            print(f"  open {collection_path}/.collection/dashboard.html")

    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        if args.verbose:
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()