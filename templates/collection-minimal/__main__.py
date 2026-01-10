#!/usr/bin/env python3
"""
Collectivist - Minimal Level CLI

Zero-install collection curator. Drop this .collection/ folder into any directory
containing files you want to organize as an intentional collection.

Usage:
    python -m .collection analyze    # Analyze directory and create config
    python -m .collection update     # Full pipeline: scan → describe → render
    python -m .collection scan       # Just scan for changes
    python -m .collection describe   # Just generate descriptions
    python -m .collection render     # Just regenerate outputs
    python -m .collection categories # Edit/add/remove categories in collection.yaml

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
from analyzer import CollectionAnalyzer


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
        choices=["analyze", "scan", "describe", "render", "update", "categories"],
        help="Command to execute"
    )

    parser.add_argument(
        "--force-type",
        choices=["repositories", "research", "media", "creative", "datasets"],
        help="Force specific collection type (skip LLM analysis)"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )

    args = parser.parse_args()

    try:
        # Initialize pipeline
        pipeline = CollectionPipeline()

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

        elif args.command == "categories":
            print("🎯 Category Editor")
            collection_path = Path.cwd()
            collection_dir = collection_path / ".collection"

            if not collection_dir.exists():
                print("❌ No .collection directory found. Run 'analyze' first.")
                return

            analyzer = CollectionAnalyzer(collection_path, collection_dir)
            current_legend = analyzer.get_category_legend()

            print(f"\nCurrent categories in {collection_dir}/collection.yaml:")
            for key, desc in current_legend.items():
                print(f"  {key}: {desc}")

            print("\nOptions:")
            print("  1. Add new category")
            print("  2. Edit existing category")
            print("  3. Remove category")
            print("  4. Show current categories")
            print("  5. Exit")

            while True:
                try:
                    choice = input("\nChoose option (1-5): ").strip()

                    if choice == "1":
                        key = input("Category key (no spaces, use underscores): ").strip()
                        if key in current_legend:
                            print("❌ Category already exists!")
                            continue
                        desc = input("Category description: ").strip()
                        current_legend[key] = desc
                        analyzer.update_category_legend(current_legend)
                        print(f"✅ Added category '{key}'")

                    elif choice == "2":
                        if not current_legend:
                            print("❌ No categories to edit!")
                            continue
                        print("Available categories:")
                        for i, (key, desc) in enumerate(current_legend.items(), 1):
                            print(f"  {i}. {key}: {desc}")
                        try:
                            idx = int(input("Choose category number to edit: ")) - 1
                            if 0 <= idx < len(current_legend):
                                key = list(current_legend.keys())[idx]
                                desc = input(f"New description for '{key}': ").strip()
                                current_legend[key] = desc
                                analyzer.update_category_legend(current_legend)
                                print(f"✅ Updated category '{key}'")
                            else:
                                print("❌ Invalid choice!")
                        except ValueError:
                            print("❌ Invalid number!")

                    elif choice == "3":
                        if not current_legend:
                            print("❌ No categories to remove!")
                            continue
                        print("Available categories:")
                        for i, (key, desc) in enumerate(current_legend.items(), 1):
                            print(f"  {i}. {key}: {desc}")
                        try:
                            idx = int(input("Choose category number to remove: ")) - 1
                            if 0 <= idx < len(current_legend):
                                key = list(current_legend.keys())[idx]
                                confirm = input(f"Remove '{key}'? (y/N): ").strip().lower()
                                if confirm == 'y':
                                    del current_legend[key]
                                    analyzer.update_category_legend(current_legend)
                                    print(f"✅ Removed category '{key}'")
                            else:
                                print("❌ Invalid choice!")
                        except ValueError:
                            print("❌ Invalid number!")

                    elif choice == "4":
                        print("Current categories:")
                        for key, desc in current_legend.items():
                            print(f"  {key}: {desc}")

                    elif choice == "5":
                        break

                    else:
                        print("❌ Invalid choice!")

                except KeyboardInterrupt:
                    print("\n⚠️  Cancelled")
                    break

            return  # Don't print "Complete!" for this command

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