#!/usr/bin/env python3
"""
README Generator - Universal markdown documentation from collection index
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from collections import defaultdict

from plugin_interface import CollectionItem
from events import EventEmitter, EventStage


def format_size(bytes: int) -> str:
    """Format bytes to human-readable size"""
    if bytes >= 1_000_000_000:
        return f"{bytes / 1_000_000_000:.1f} GB"
    elif bytes >= 1_000_000:
        return f"{bytes / 1_000_000:.0f} MB"
    elif bytes >= 1_000:
        return f"{bytes / 1_000:.0f} KB"
    else:
        return f"{bytes} B"


def format_date(date_str: str) -> str:
    """Extract date from ISO timestamp"""
    return date_str[:10] if date_str else "unknown"


def get_status_emoji(item: CollectionItem) -> str:
    """Get status emoji from metadata (repository-specific)"""
    git_status = item.metadata.get('git_status')

    status_map = {
        'up_to_date': '[OK]',
        'updates_available': '[^]',
        'error': '[!]',
        'no_remote': '[o]',
        'not_a_repo': '[O]'
    }

    return status_map.get(git_status, '')


def generate_readme(
    items: List[CollectionItem],
    collection_name: str,
    collection_type: str,
    output_path: Path,
    event_emitter: Optional[EventEmitter] = None
):
    """
    Generate README.md from collection items.

    Args:
        items: List of collection items
        collection_name: Name of the collection
        collection_type: Type of collection (repositories, media, etc.)
        output_path: Path to save README.md
        event_emitter: Optional event emitter for progress updates
    """
    emitter = event_emitter
    
    if emitter:
        emitter.set_stage(EventStage.RENDER)
        emitter.info("Starting README generation")

    # Calculate stats
    if emitter:
        emitter.info("Calculating collection statistics")
    total_items = len(items)
    total_size = sum(item.size for item in items)
    described = sum(1 for item in items if item.description)
    categorized = sum(1 for item in items if item.category)

    # Repository-specific stats (if applicable)
    git_stats = None
    if collection_type == 'repositories':
        git_repos = sum(1 for item in items if item.metadata.get('git_status') != 'not_a_repo')
        up_to_date = sum(1 for item in items if item.metadata.get('git_status') == 'up_to_date')
        updates_avail = sum(1 for item in items if item.metadata.get('git_status') == 'updates_available')
        errors = sum(1 for item in items if item.metadata.get('git_status') == 'error')

        git_stats = {
            'git_repos': git_repos,
            'up_to_date': up_to_date,
            'updates_available': updates_avail,
            'errors': errors
        }

    # Build header
    if emitter:
        emitter.info("Building README header and overview")
    header_parts = [
        f"# {collection_name}\n",
        f"> Indexed {collection_type} collection\n",
        "## Overview\n",
        f"**Total Items:** {total_items}  ",
        f"**Total Size:** {format_size(total_size)}  ",
        f"**Described:** {described}  ",
        f"**Categorized:** {categorized}  \n",
    ]

    # Add git-specific stats if applicable
    if git_stats:
        header_parts.append(
            f"**Git Tracked:** {git_stats['git_repos']} | "
            f"**Up to Date:** {git_stats['up_to_date']} | "
            f"**Updates Available:** {git_stats['updates_available']} | "
            f"**Errors:** {git_stats['errors']}  \n"
        )

    header_parts.append("\n---\n\n")
    header_parts.append("## Index\n\n")

    # Add legend if repositories
    if collection_type == 'repositories':
        header_parts.append(
            "**Legend:** [OK] up-to-date | [^] updates available | "
            "[!] error | [o] no remote | [O] not a git repo\n\n"
        )

    header = ''.join(header_parts)

    # Build table
    if emitter:
        emitter.info("Building item table")
    table_rows = []
    for item in items:
        status = get_status_emoji(item) if collection_type == 'repositories' else ''
        desc = item.description or "_No description_"
        cat = f"`{item.category}`" if item.category else "—"
        date = format_date(item.created)

        if status:
            row = f"| {status} | **{item.short_name}** | {desc} | {cat} | {date} |"
        else:
            row = f"| **{item.short_name}** | {desc} | {cat} | {date} |"

        table_rows.append(row)

    if collection_type == 'repositories':
        table_header = "| Status | Name | Description | Category | Created |\n"
        table_separator = "|--------|------|-------------|----------|---------|"
    else:
        table_header = "| Name | Description | Category | Created |\n"
        table_separator = "|------|-------------|----------|---------|"

    table = table_header + table_separator + "\n" + '\n'.join(table_rows) + "\n\n---\n\n"

    # Build category sections
    if emitter:
        emitter.info("Building categorized sections")
    categories = defaultdict(list)
    for item in items:
        if item.category:
            categories[item.category].append(item)

    category_sections = []
    for category, cat_items in sorted(categories.items()):
        # Format category name (convert snake_case to Title Case)
        cat_display = category.replace('_', ' ').title()

        section = f"## {cat_display}\n\n"

        for item in cat_items:
            status = get_status_emoji(item) if collection_type == 'repositories' else ''
            size_str = format_size(item.size)
            desc = item.description or "_No description available_"

            if status:
                section += f"### {item.short_name} {status} `{size_str}`\n"
            else:
                section += f"### {item.short_name} `{size_str}`\n"

            section += f"{desc}\n\n"

        section += "---\n\n"
        category_sections.append(section)

    # Build footer
    today = datetime.now().strftime("%Y-%m-%d")
    footer = f"""## Index Maintenance

This README is automatically generated from `.collection/index.yaml`.

**To update the index:**
```bash
python -m .collection update
```

**To regenerate this README only:**
```bash
python -m .collection render
```

**Last generated:** {today}
"""

    # Combine all sections
    readme_content = header + table + ''.join(category_sections) + footer

    # Save
    if emitter:
        emitter.info(f"Writing README to {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)

    if emitter:
        emitter.complete_stage(f"README generated at {output_path}")
    else:
        print(f"[OK] README generated at {output_path}")


def main():
    """CLI entry point for standalone README generation"""
    import sys
    import yaml
    from pathlib import Path

    if len(sys.argv) < 2:
        print("Usage: python readme_generator.py <collection_path>")
        sys.exit(1)

    collection_path = Path(sys.argv[1]).resolve()
    index_path = collection_path / '.collection' / 'index.yaml'
    config_path = collection_path / 'collection.yaml'

    # Load config
    if not config_path.exists():
        print(f"[X] No collection.yaml found at {config_path}")
        sys.exit(1)

    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    # Load index
    if not index_path.exists():
        print(f"[X] No collection-index.yaml found at {index_path}")
        sys.exit(1)

    with open(index_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f) or []

    # Convert to CollectionItem objects
    items = []
    for item_data in data:
        standard_fields = {
            'short_name', 'type', 'size', 'created', 'modified',
            'accessed', 'path', 'description', 'category'
        }
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

    # Generate README
    readme_path = collection_path / 'README.md'
    generate_readme(
        items=items,
        collection_name=config['name'],
        collection_type=config['collection_type'],
        output_path=readme_path
    )


if __name__ == '__main__':
    main()
