#!/usr/bin/env python3
"""
Collection Generator - Universal markdown documentation from collection index
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


def generate_html_collection(
    items: List[CollectionItem],
    collection_name: str,
    collection_type: str,
    output_path: Path,
    collection_overview: Optional[str] = None,
    event_emitter: Optional[EventEmitter] = None
):
    """
    Generate Collection.html from collection items with interactive features.

    Args:
        items: List of collection items
        collection_name: Name of the collection
        collection_type: Type of collection (repositories, media, etc.)
        output_path: Path to save Collection.html
        collection_overview: Optional LLM-generated collection overview
        event_emitter: Optional event emitter for progress updates
    """
    emitter = event_emitter
    
    if emitter:
        emitter.set_stage(EventStage.RENDER)
        emitter.info("Starting Collection.html generation")

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

    # Build categories for filtering
    categories = defaultdict(list)
    for item in items:
        if item.category:
            categories[item.category].append(item)

    # Generate HTML content
    html_content = _generate_html_template(
        items=items,
        collection_name=collection_name,
        collection_type=collection_type,
        collection_overview=collection_overview,
        total_items=total_items,
        total_size=total_size,
        described=described,
        categorized=categorized,
        git_stats=git_stats,
        categories=categories
    )

    # Save HTML file
    if emitter:
        emitter.info(f"Writing Collection.html to {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    if emitter:
        emitter.complete_stage(f"Collection.html generated at {output_path}")
    else:
        print(f"[OK] Collection.html generated at {output_path}")


def generate_collection(
    items: List[CollectionItem],
    collection_name: str,
    collection_type: str,
    output_path: Path,
    collection_overview: Optional[str] = None,
    event_emitter: Optional[EventEmitter] = None
):
    """
    Generate Collection.md from collection items.

    Args:
        items: List of collection items
        collection_name: Name of the collection
        collection_type: Type of collection (repositories, media, etc.)
        output_path: Path to save Collection.md
        collection_overview: Optional LLM-generated collection overview
        event_emitter: Optional event emitter for progress updates
    """
    emitter = event_emitter
    
    if emitter:
        emitter.set_stage(EventStage.RENDER)
        emitter.info("Starting Collection.md generation")

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
        emitter.info("Building Collection.md header and overview")
    header_parts = [
        f"# {collection_name}\n",
        f"> Indexed {collection_type} collection\n",
        "## Overview\n",
    ]
    
    # Add collection overview if available
    if collection_overview:
        header_parts.extend([
            f"{collection_overview}\n\n",
            "### Statistics\n\n",
        ])
    
    header_parts.extend([
        f"**Total Items:** {total_items}  ",
        f"**Total Size:** {format_size(total_size)}  ",
        f"**Described:** {described}  ",
        f"**Categorized:** {categorized}  \n",
    ])

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

This Collection.md is automatically generated from `.collection/index.yaml`.

**To update the index:**
```bash
python -m .collection update
```

**To regenerate this Collection.md only:**
```bash
python -m .collection render
```

**Last generated:** {today}
"""

    # Combine all sections
    collection_content = header + table + ''.join(category_sections) + footer

    # Save
    if emitter:
        emitter.info(f"Writing Collection.md to {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(collection_content)

    if emitter:
        emitter.complete_stage(f"Collection.md generated at {output_path}")
    else:
        print(f"[OK] Collection.md generated at {output_path}")


def _generate_html_template(
    items: List[CollectionItem],
    collection_name: str,
    collection_type: str,
    collection_overview: Optional[str],
    total_items: int,
    total_size: int,
    described: int,
    categorized: int,
    git_stats: Optional[Dict],
    categories: Dict[str, List[CollectionItem]]
) -> str:
    """Generate the complete HTML template with embedded CSS and JavaScript."""
    
    # Convert items to JSON for JavaScript
    import json
    items_json = []
    for item in items:
        item_data = {
            'short_name': item.short_name,
            'type': item.type,
            'size': item.size,
            'created': item.created,
            'modified': item.modified,
            'accessed': item.accessed,
            'path': item.path,
            'description': item.description or 'No description',
            'category': item.category or 'Uncategorized',
            'metadata': item.metadata
        }
        items_json.append(item_data)
    
    items_json_str = json.dumps(items_json, indent=2)
    
    # Get all unique categories for filter dropdown
    all_categories = sorted(set(item.category for item in items if item.category))
    
    # Generate status options based on collection type
    status_options = []
    if collection_type == 'repositories':
        status_options = ['up_to_date', 'updates_available', 'error', 'no_remote', 'not_a_repo']
    
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{collection_name} - Collection Index</title>
    <style>
        /* Import Recursive Mono Casual font */
        @import url('https://fonts.googleapis.com/css2?family=Recursive:slnt,wght,CASL,MONO@-15..0,300..1000,0..1,0..1&display=swap');

        /* Catppuccin Mocha Theme Variables */
        :root {{
            --ctp-rosewater: #f5e0dc;
            --ctp-flamingo: #f2cdcd;
            --ctp-pink: #f5c2e7;
            --ctp-mauve: #cba6f7;
            --ctp-red: #f38ba8;
            --ctp-maroon: #eba0ac;
            --ctp-peach: #fab387;
            --ctp-yellow: #f9e2af;
            --ctp-green: #a6e3a1;
            --ctp-teal: #94e2d5;
            --ctp-sky: #89dceb;
            --ctp-sapphire: #74c7ec;
            --ctp-blue: #89b4fa;
            --ctp-lavender: #b4befe;
            --ctp-text: #cdd6f4;
            --ctp-subtext1: #bac2de;
            --ctp-subtext0: #a6adc8;
            --ctp-overlay2: #9399b2;
            --ctp-overlay1: #7f849c;
            --ctp-overlay0: #6c7086;
            --ctp-surface2: #585b70;
            --ctp-surface1: #45475a;
            --ctp-surface0: #313244;
            --ctp-base: #1e1e2e;
            --ctp-mantle: #181825;
            --ctp-crust: #11111b;
        }}

        /* Catppuccin Frappé Theme */
        .theme-frappe {{
            --ctp-rosewater: #f2d5cf;
            --ctp-flamingo: #eebebe;
            --ctp-pink: #f4b8e4;
            --ctp-mauve: #ca9ee6;
            --ctp-red: #e78284;
            --ctp-maroon: #ea999c;
            --ctp-peach: #ef9f76;
            --ctp-yellow: #e5c890;
            --ctp-green: #a6d189;
            --ctp-teal: #81c8be;
            --ctp-sky: #99d1db;
            --ctp-sapphire: #85c1dc;
            --ctp-blue: #8caaee;
            --ctp-lavender: #babbf1;
            --ctp-text: #c6d0f5;
            --ctp-subtext1: #b5bfe2;
            --ctp-subtext0: #a5adce;
            --ctp-overlay2: #949cbb;
            --ctp-overlay1: #838ba7;
            --ctp-overlay0: #737994;
            --ctp-surface2: #626880;
            --ctp-surface1: #51576d;
            --ctp-surface0: #414559;
            --ctp-base: #303446;
            --ctp-mantle: #292c3c;
            --ctp-crust: #232634;
        }}

        /* Catppuccin Macchiato Theme */
        .theme-macchiato {{
            --ctp-rosewater: #f4dbd6;
            --ctp-flamingo: #f0c6c6;
            --ctp-pink: #f5bde6;
            --ctp-mauve: #c6a0f6;
            --ctp-red: #ed8796;
            --ctp-maroon: #ee99a0;
            --ctp-peach: #f5a97f;
            --ctp-yellow: #eed49f;
            --ctp-green: #a6da95;
            --ctp-teal: #8bd5ca;
            --ctp-sky: #91d7e3;
            --ctp-sapphire: #7dc4e4;
            --ctp-blue: #8aadf4;
            --ctp-lavender: #b7bdf8;
            --ctp-text: #cad3f5;
            --ctp-subtext1: #b8c0e0;
            --ctp-subtext0: #a5adcb;
            --ctp-overlay2: #939ab7;
            --ctp-overlay1: #8087a2;
            --ctp-overlay0: #6e738d;
            --ctp-surface2: #5b6078;
            --ctp-surface1: #494d64;
            --ctp-surface0: #363a4f;
            --ctp-base: #24273a;
            --ctp-mantle: #1e2030;
            --ctp-crust: #181926;
        }}

        /* Catppuccin Latte Theme (Light) */
        .theme-latte {{
            --ctp-rosewater: #dc8a78;
            --ctp-flamingo: #dd7878;
            --ctp-pink: #ea76cb;
            --ctp-mauve: #8839ef;
            --ctp-red: #d20f39;
            --ctp-maroon: #e64553;
            --ctp-peach: #fe640b;
            --ctp-yellow: #df8e1d;
            --ctp-green: #40a02b;
            --ctp-teal: #179299;
            --ctp-sky: #04a5e5;
            --ctp-sapphire: #209fb5;
            --ctp-blue: #1e66f5;
            --ctp-lavender: #7287fd;
            --ctp-text: #4c4f69;
            --ctp-subtext1: #5c5f77;
            --ctp-subtext0: #6c6f85;
            --ctp-overlay2: #7c7f93;
            --ctp-overlay1: #8c8fa1;
            --ctp-overlay0: #9ca0b0;
            --ctp-surface2: #acb0be;
            --ctp-surface1: #bcc0cc;
            --ctp-surface0: #ccd0da;
            --ctp-base: #eff1f5;
            --ctp-mantle: #e6e9ef;
            --ctp-crust: #dce0e8;
        }}

        /* Auto light theme detection */
        @media (prefers-color-scheme: light) {{
            :root {{
                --ctp-rosewater: #dc8a78;
                --ctp-flamingo: #dd7878;
                --ctp-pink: #ea76cb;
                --ctp-mauve: #8839ef;
                --ctp-red: #d20f39;
                --ctp-maroon: #e64553;
                --ctp-peach: #fe640b;
                --ctp-yellow: #df8e1d;
                --ctp-green: #40a02b;
                --ctp-teal: #179299;
                --ctp-sky: #04a5e5;
                --ctp-sapphire: #209fb5;
                --ctp-blue: #1e66f5;
                --ctp-lavender: #7287fd;
                --ctp-text: #4c4f69;
                --ctp-subtext1: #5c5f77;
                --ctp-subtext0: #6c6f85;
                --ctp-overlay2: #7c7f93;
                --ctp-overlay1: #8c8fa1;
                --ctp-overlay0: #9ca0b0;
                --ctp-surface2: #acb0be;
                --ctp-surface1: #bcc0cc;
                --ctp-surface0: #ccd0da;
                --ctp-base: #eff1f5;
                --ctp-mantle: #e6e9ef;
                --ctp-crust: #dce0e8;
            }}
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Recursive', 'Cascadia Code', 'Fira Code', 'JetBrains Mono', 'SF Mono', Monaco, 'Cascadia Mono', 'Roboto Mono', Consolas, 'Courier New', monospace;
            font-variation-settings: 'MONO' 1, 'CASL' 0.5, 'slnt' -5;
            background-color: var(--ctp-base);
            color: var(--ctp-text);
            line-height: 1.6;
            transition: all 0.3s ease;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }}

        .header {{
            text-align: center;
            margin-bottom: 3rem;
            padding: 2rem;
            background: var(--ctp-mantle);
            border-radius: 12px;
            border: 1px solid var(--ctp-surface0);
        }}

        .header h1 {{
            color: var(--ctp-mauve);
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
            font-weight: 700;
            font-variation-settings: 'MONO' 0.8, 'CASL' 0.7, 'slnt' -8;
        }}

        .header .subtitle {{
            color: var(--ctp-subtext1);
            font-size: 1.1rem;
            margin-bottom: 1.5rem;
            font-variation-settings: 'MONO' 0.9, 'CASL' 0.3, 'slnt' -3;
        }}

        .overview {{
            background: var(--ctp-surface0);
            padding: 1.5rem;
            border-radius: 8px;
            margin-bottom: 1.5rem;
            border-left: 4px solid var(--ctp-blue);
        }}

        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }}

        .stat-card {{
            background: var(--ctp-surface0);
            padding: 1.5rem;
            border-radius: 8px;
            text-align: center;
            border: 1px solid var(--ctp-surface1);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}

        .stat-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        }}

        .stat-value {{
            font-size: 2rem;
            font-weight: bold;
            color: var(--ctp-blue);
            display: block;
        }}

        .stat-label {{
            color: var(--ctp-subtext1);
            font-size: 0.9rem;
            margin-top: 0.5rem;
        }}

        .controls {{
            display: flex;
            flex-wrap: wrap;
            gap: 1rem;
            margin-bottom: 2rem;
            padding: 1.5rem;
            background: var(--ctp-mantle);
            border-radius: 8px;
            border: 1px solid var(--ctp-surface0);
        }}

        .control-group {{
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }}

        .control-group label {{
            color: var(--ctp-subtext1);
            font-size: 0.9rem;
            font-weight: 500;
        }}

        .control-group input,
        .control-group select {{
            padding: 0.5rem;
            border: 1px solid var(--ctp-surface1);
            border-radius: 6px;
            background: var(--ctp-surface0);
            color: var(--ctp-text);
            font-size: 0.9rem;
            transition: border-color 0.2s ease;
        }}

        .control-group input:focus,
        .control-group select:focus {{
            outline: none;
            border-color: var(--ctp-blue);
            box-shadow: 0 0 0 2px rgba(137, 180, 250, 0.2);
        }}

        .items-grid {{
            display: grid;
            gap: 1rem;
        }}

        .item-card {{
            background: var(--ctp-surface0);
            border: 1px solid var(--ctp-surface1);
            border-radius: 8px;
            padding: 1.5rem;
            transition: all 0.2s ease;
            position: relative;
        }}

        .item-card:hover {{
            border-color: var(--ctp-blue);
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        }}

        .item-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 1rem;
        }}

        .item-name {{
            font-size: 1.2rem;
            font-weight: 600;
            color: var(--ctp-text);
            text-decoration: none;
            cursor: pointer;
            transition: color 0.2s ease;
            font-variation-settings: 'MONO' 0.9, 'CASL' 0.4, 'slnt' -5;
        }}

        .item-name:hover {{
            color: var(--ctp-blue);
            font-variation-settings: 'MONO' 0.8, 'CASL' 0.6, 'slnt' -8;
        }}

        .item-status {{
            padding: 0.25rem 0.75rem;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-variation-settings: 'MONO' 1, 'CASL' 0.2, 'slnt' 0;
        }}

        .status-up_to_date {{
            background: var(--ctp-green);
            color: var(--ctp-base);
        }}

        .status-updates_available {{
            background: var(--ctp-yellow);
            color: var(--ctp-base);
        }}

        .status-error {{
            background: var(--ctp-red);
            color: var(--ctp-base);
        }}

        .status-no_remote {{
            background: var(--ctp-overlay1);
            color: var(--ctp-text);
        }}

        .status-not_a_repo {{
            background: var(--ctp-surface2);
            color: var(--ctp-subtext1);
        }}

        .item-description {{
            color: var(--ctp-subtext0);
            margin-bottom: 1rem;
            line-height: 1.5;
        }}

        .item-meta {{
            display: flex;
            flex-wrap: wrap;
            gap: 1rem;
            font-size: 0.85rem;
            color: var(--ctp-subtext1);
        }}

        .meta-item {{
            display: flex;
            align-items: center;
            gap: 0.25rem;
        }}

        .category-tag {{
            background: var(--ctp-mauve);
            color: var(--ctp-base);
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 500;
            font-variation-settings: 'MONO' 0.8, 'CASL' 0.3, 'slnt' -2;
        }}

        .no-results {{
            text-align: center;
            padding: 3rem;
            color: var(--ctp-subtext1);
            font-size: 1.1rem;
        }}

        .theme-selector {{
            position: fixed;
            top: 1rem;
            right: 1rem;
            background: var(--ctp-surface0);
            border: 1px solid var(--ctp-surface1);
            border-radius: 8px;
            padding: 0.5rem;
            display: flex;
            flex-direction: column;
            gap: 0.25rem;
            z-index: 1000;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            transition: all 0.2s ease;
        }}

        .theme-selector.collapsed {{
            padding: 0;
            overflow: hidden;
        }}

        .theme-toggle-btn {{
            background: none;
            border: none;
            color: var(--ctp-text);
            cursor: pointer;
            padding: 0.5rem;
            border-radius: 6px;
            transition: all 0.2s ease;
            font-size: 1.2rem;
            display: flex;
            align-items: center;
            justify-content: center;
            min-width: 2.5rem;
            min-height: 2.5rem;
        }}

        .theme-toggle-btn:hover {{
            background: var(--ctp-surface1);
        }}

        .theme-options {{
            display: flex;
            flex-direction: column;
            gap: 0.25rem;
            min-width: 120px;
        }}

        .theme-option {{
            background: none;
            border: none;
            color: var(--ctp-text);
            cursor: pointer;
            padding: 0.5rem 0.75rem;
            border-radius: 4px;
            transition: all 0.2s ease;
            text-align: left;
            font-size: 0.9rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-variation-settings: 'MONO' 0.9, 'CASL' 0.4, 'slnt' -3;
        }}

        .theme-option:hover {{
            background: var(--ctp-surface1);
        }}

        .theme-option.active {{
            background: var(--ctp-mauve);
            color: var(--ctp-base);
        }}

        .theme-indicator {{
            width: 12px;
            height: 12px;
            border-radius: 50%;
            flex-shrink: 0;
        }}

        .theme-mocha .theme-indicator {{ background: #1e1e2e; }}
        .theme-frappe .theme-indicator {{ background: #303446; }}
        .theme-macchiato .theme-indicator {{ background: #24273a; }}
        .theme-latte .theme-indicator {{ background: #eff1f5; border: 1px solid #ccc; }}

        /* Responsive Design */
        @media (max-width: 768px) {{
            .container {{
                padding: 1rem;
            }}

            .header h1 {{
                font-size: 2rem;
            }}

            .controls {{
                flex-direction: column;
            }}

            .stats {{
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            }}

            .item-header {{
                flex-direction: column;
                gap: 0.5rem;
            }}

            .item-meta {{
                flex-direction: column;
                gap: 0.5rem;
            }}
        }}

        /* Custom scrollbar */
        ::-webkit-scrollbar {{
            width: 8px;
        }}

        ::-webkit-scrollbar-track {{
            background: var(--ctp-base);
        }}

        ::-webkit-scrollbar-thumb {{
            background: var(--ctp-surface2);
            border-radius: 4px;
        }}

        ::-webkit-scrollbar-thumb:hover {{
            background: var(--ctp-overlay0);
        }}
    </style>
</head>
<body>
    <div class="theme-selector" id="theme-selector">
        <button class="theme-toggle-btn" onclick="toggleThemeSelector()" title="Select theme">
            🎨
        </button>
        <div class="theme-options" id="theme-options" style="display: none;">
            <button class="theme-option" onclick="setTheme('mocha')" data-theme="mocha">
                <div class="theme-indicator"></div>
                Mocha
            </button>
            <button class="theme-option" onclick="setTheme('frappe')" data-theme="frappe">
                <div class="theme-indicator"></div>
                Frappé
            </button>
            <button class="theme-option" onclick="setTheme('macchiato')" data-theme="macchiato">
                <div class="theme-indicator"></div>
                Macchiato
            </button>
            <button class="theme-option" onclick="setTheme('latte')" data-theme="latte">
                <div class="theme-indicator"></div>
                Latte
            </button>
        </div>
    </div>

    <div class="container">
        <header class="header">
            <h1>{collection_name}</h1>
            <p class="subtitle">Indexed {collection_type} collection</p>
            
            {f'<div class="overview">{collection_overview}</div>' if collection_overview else ''}
        </header>

        <div class="stats">
            <div class="stat-card">
                <span class="stat-value">{total_items}</span>
                <span class="stat-label">Total Items</span>
            </div>
            <div class="stat-card">
                <span class="stat-value">{format_size(total_size)}</span>
                <span class="stat-label">Total Size</span>
            </div>
            <div class="stat-card">
                <span class="stat-value">{described}</span>
                <span class="stat-label">Described</span>
            </div>
            <div class="stat-card">
                <span class="stat-value">{categorized}</span>
                <span class="stat-label">Categorized</span>
            </div>
            {_generate_git_stats_html(git_stats) if git_stats else ''}
        </div>

        <div class="controls">
            <div class="control-group">
                <label for="search">Search</label>
                <input type="text" id="search" placeholder="Search items..." oninput="filterItems()">
            </div>
            
            <div class="control-group">
                <label for="category-filter">Category</label>
                <select id="category-filter" onchange="filterItems()">
                    <option value="">All Categories</option>
                    {_generate_category_options(all_categories)}
                </select>
            </div>
            
            {_generate_status_filter_html(status_options) if status_options else ''}
            
            <div class="control-group">
                <label for="sort-by">Sort By</label>
                <select id="sort-by" onchange="sortItems()">
                    <option value="name">Name</option>
                    <option value="size">Size</option>
                    <option value="created">Created</option>
                    <option value="modified">Modified</option>
                    <option value="category">Category</option>
                </select>
            </div>
            
            <div class="control-group">
                <label for="sort-order">Order</label>
                <select id="sort-order" onchange="sortItems()">
                    <option value="asc">Ascending</option>
                    <option value="desc">Descending</option>
                </select>
            </div>
        </div>

        <div class="items-grid" id="items-container">
            <!-- Items will be populated by JavaScript -->
        </div>

        <div class="no-results" id="no-results" style="display: none;">
            No items match your current filters.
        </div>
    </div>

    <script>
        // Collection data
        const collectionItems = {items_json_str};
        let filteredItems = [...collectionItems];
        let currentTheme = 'mocha';
        let themeSelectorOpen = false;

        // Theme definitions
        const themes = {{
            mocha: {{
                name: 'Mocha',
                colors: {{
                    '--ctp-rosewater': '#f5e0dc',
                    '--ctp-flamingo': '#f2cdcd',
                    '--ctp-pink': '#f5c2e7',
                    '--ctp-mauve': '#cba6f7',
                    '--ctp-red': '#f38ba8',
                    '--ctp-maroon': '#eba0ac',
                    '--ctp-peach': '#fab387',
                    '--ctp-yellow': '#f9e2af',
                    '--ctp-green': '#a6e3a1',
                    '--ctp-teal': '#94e2d5',
                    '--ctp-sky': '#89dceb',
                    '--ctp-sapphire': '#74c7ec',
                    '--ctp-blue': '#89b4fa',
                    '--ctp-lavender': '#b4befe',
                    '--ctp-text': '#cdd6f4',
                    '--ctp-subtext1': '#bac2de',
                    '--ctp-subtext0': '#a6adc8',
                    '--ctp-overlay2': '#9399b2',
                    '--ctp-overlay1': '#7f849c',
                    '--ctp-overlay0': '#6c7086',
                    '--ctp-surface2': '#585b70',
                    '--ctp-surface1': '#45475a',
                    '--ctp-surface0': '#313244',
                    '--ctp-base': '#1e1e2e',
                    '--ctp-mantle': '#181825',
                    '--ctp-crust': '#11111b'
                }}
            }},
            frappe: {{
                name: 'Frappé',
                colors: {{
                    '--ctp-rosewater': '#f2d5cf',
                    '--ctp-flamingo': '#eebebe',
                    '--ctp-pink': '#f4b8e4',
                    '--ctp-mauve': '#ca9ee6',
                    '--ctp-red': '#e78284',
                    '--ctp-maroon': '#ea999c',
                    '--ctp-peach': '#ef9f76',
                    '--ctp-yellow': '#e5c890',
                    '--ctp-green': '#a6d189',
                    '--ctp-teal': '#81c8be',
                    '--ctp-sky': '#99d1db',
                    '--ctp-sapphire': '#85c1dc',
                    '--ctp-blue': '#8caaee',
                    '--ctp-lavender': '#babbf1',
                    '--ctp-text': '#c6d0f5',
                    '--ctp-subtext1': '#b5bfe2',
                    '--ctp-subtext0': '#a5adce',
                    '--ctp-overlay2': '#949cbb',
                    '--ctp-overlay1': '#838ba7',
                    '--ctp-overlay0': '#737994',
                    '--ctp-surface2': '#626880',
                    '--ctp-surface1': '#51576d',
                    '--ctp-surface0': '#414559',
                    '--ctp-base': '#303446',
                    '--ctp-mantle': '#292c3c',
                    '--ctp-crust': '#232634'
                }}
            }},
            macchiato: {{
                name: 'Macchiato',
                colors: {{
                    '--ctp-rosewater': '#f4dbd6',
                    '--ctp-flamingo': '#f0c6c6',
                    '--ctp-pink': '#f5bde6',
                    '--ctp-mauve': '#c6a0f6',
                    '--ctp-red': '#ed8796',
                    '--ctp-maroon': '#ee99a0',
                    '--ctp-peach': '#f5a97f',
                    '--ctp-yellow': '#eed49f',
                    '--ctp-green': '#a6da95',
                    '--ctp-teal': '#8bd5ca',
                    '--ctp-sky': '#91d7e3',
                    '--ctp-sapphire': '#7dc4e4',
                    '--ctp-blue': '#8aadf4',
                    '--ctp-lavender': '#b7bdf8',
                    '--ctp-text': '#cad3f5',
                    '--ctp-subtext1': '#b8c0e0',
                    '--ctp-subtext0': '#a5adcb',
                    '--ctp-overlay2': '#939ab7',
                    '--ctp-overlay1': '#8087a2',
                    '--ctp-overlay0': '#6e738d',
                    '--ctp-surface2': '#5b6078',
                    '--ctp-surface1': '#494d64',
                    '--ctp-surface0': '#363a4f',
                    '--ctp-base': '#24273a',
                    '--ctp-mantle': '#1e2030',
                    '--ctp-crust': '#181926'
                }}
            }},
            latte: {{
                name: 'Latte',
                colors: {{
                    '--ctp-rosewater': '#dc8a78',
                    '--ctp-flamingo': '#dd7878',
                    '--ctp-pink': '#ea76cb',
                    '--ctp-mauve': '#8839ef',
                    '--ctp-red': '#d20f39',
                    '--ctp-maroon': '#e64553',
                    '--ctp-peach': '#fe640b',
                    '--ctp-yellow': '#df8e1d',
                    '--ctp-green': '#40a02b',
                    '--ctp-teal': '#179299',
                    '--ctp-sky': '#04a5e5',
                    '--ctp-sapphire': '#209fb5',
                    '--ctp-blue': '#1e66f5',
                    '--ctp-lavender': '#7287fd',
                    '--ctp-text': '#4c4f69',
                    '--ctp-subtext1': '#5c5f77',
                    '--ctp-subtext0': '#6c6f85',
                    '--ctp-overlay2': '#7c7f93',
                    '--ctp-overlay1': '#8c8fa1',
                    '--ctp-overlay0': '#9ca0b0',
                    '--ctp-surface2': '#acb0be',
                    '--ctp-surface1': '#bcc0cc',
                    '--ctp-surface0': '#ccd0da',
                    '--ctp-base': '#eff1f5',
                    '--ctp-mantle': '#e6e9ef',
                    '--ctp-crust': '#dce0e8'
                }}
            }}
        }};

        // Initialize the page
        document.addEventListener('DOMContentLoaded', function() {{
            renderItems();
            
            // Load saved theme preference
            const savedTheme = localStorage.getItem('collection-theme') || 'mocha';
            setTheme(savedTheme);
            
            // Close theme selector when clicking outside
            document.addEventListener('click', function(e) {{
                const selector = document.getElementById('theme-selector');
                if (!selector.contains(e.target) && themeSelectorOpen) {{
                    toggleThemeSelector();
                }}
            }});
        }});

        function renderItems() {{
            const container = document.getElementById('items-container');
            const noResults = document.getElementById('no-results');
            
            if (filteredItems.length === 0) {{
                container.style.display = 'none';
                noResults.style.display = 'block';
                return;
            }}
            
            container.style.display = 'grid';
            noResults.style.display = 'none';
            
            container.innerHTML = filteredItems.map(item => `
                <div class="item-card">
                    <div class="item-header">
                        <a href="file:///${{item.path}}" class="item-name" title="Open ${{item.path}}">
                            ${{item.short_name}}
                        </a>
                        ${{getStatusBadge(item)}}
                    </div>
                    
                    <div class="item-description">
                        ${{item.description}}
                    </div>
                    
                    <div class="item-meta">
                        <div class="meta-item">
                            <span>📁</span>
                            <span>${{item.type}}</span>
                        </div>
                        <div class="meta-item">
                            <span>📏</span>
                            <span>${{formatSize(item.size)}}</span>
                        </div>
                        <div class="meta-item">
                            <span>📅</span>
                            <span>${{formatDate(item.created)}}</span>
                        </div>
                        ${{item.category ? `<span class="category-tag">${{item.category.replace('_', ' ').replace(/\\b\\w/g, l => l.toUpperCase())}}</span>` : ''}}
                    </div>
                </div>
            `).join('');
        }}

        function getStatusBadge(item) {{
            const gitStatus = item.metadata?.git_status;
            if (!gitStatus) return '';
            
            const statusMap = {{
                'up_to_date': 'UP TO DATE',
                'updates_available': 'UPDATES',
                'error': 'ERROR',
                'no_remote': 'NO REMOTE',
                'not_a_repo': 'NOT REPO'
            }};
            
            const statusText = statusMap[gitStatus] || gitStatus.toUpperCase();
            return `<span class="item-status status-${{gitStatus}}">${{statusText}}</span>`;
        }}

        function formatSize(bytes) {{
            if (bytes >= 1000000000) {{
                return (bytes / 1000000000).toFixed(1) + ' GB';
            }} else if (bytes >= 1000000) {{
                return (bytes / 1000000).toFixed(0) + ' MB';
            }} else if (bytes >= 1000) {{
                return (bytes / 1000).toFixed(0) + ' KB';
            }} else {{
                return bytes + ' B';
            }}
        }}

        function formatDate(dateStr) {{
            return dateStr ? dateStr.substring(0, 10) : 'unknown';
        }}

        function filterItems() {{
            const searchTerm = document.getElementById('search').value.toLowerCase();
            const categoryFilter = document.getElementById('category-filter').value;
            const statusFilter = document.getElementById('status-filter')?.value || '';
            
            filteredItems = collectionItems.filter(item => {{
                const matchesSearch = !searchTerm || 
                    item.short_name.toLowerCase().includes(searchTerm) ||
                    item.description.toLowerCase().includes(searchTerm) ||
                    (item.category && item.category.toLowerCase().includes(searchTerm));
                
                const matchesCategory = !categoryFilter || item.category === categoryFilter;
                
                const matchesStatus = !statusFilter || 
                    (item.metadata?.git_status === statusFilter);
                
                return matchesSearch && matchesCategory && matchesStatus;
            }});
            
            sortItems();
        }}

        function sortItems() {{
            const sortBy = document.getElementById('sort-by').value;
            const sortOrder = document.getElementById('sort-order').value;
            
            filteredItems.sort((a, b) => {{
                let aVal, bVal;
                
                switch (sortBy) {{
                    case 'name':
                        aVal = a.short_name.toLowerCase();
                        bVal = b.short_name.toLowerCase();
                        break;
                    case 'size':
                        aVal = a.size;
                        bVal = b.size;
                        break;
                    case 'created':
                        aVal = new Date(a.created);
                        bVal = new Date(b.created);
                        break;
                    case 'modified':
                        aVal = new Date(a.modified);
                        bVal = new Date(b.modified);
                        break;
                    case 'category':
                        aVal = a.category || '';
                        bVal = b.category || '';
                        break;
                    default:
                        aVal = a.short_name.toLowerCase();
                        bVal = b.short_name.toLowerCase();
                }}
                
                if (aVal < bVal) return sortOrder === 'asc' ? -1 : 1;
                if (aVal > bVal) return sortOrder === 'asc' ? 1 : -1;
                return 0;
            }});
            
            renderItems();
        }}

        function toggleThemeSelector() {{
            const options = document.getElementById('theme-options');
            const selector = document.getElementById('theme-selector');
            
            themeSelectorOpen = !themeSelectorOpen;
            
            if (themeSelectorOpen) {{
                options.style.display = 'flex';
                selector.classList.remove('collapsed');
            }} else {{
                options.style.display = 'none';
                selector.classList.add('collapsed');
            }}
        }}

        function setTheme(themeName) {{
            currentTheme = themeName;
            localStorage.setItem('collection-theme', currentTheme);
            
            // Apply theme colors
            const theme = themes[themeName];
            if (theme) {{
                Object.entries(theme.colors).forEach(([property, value]) => {{
                    document.documentElement.style.setProperty(property, value);
                }});
            }}
            
            // Update active theme indicator
            document.querySelectorAll('.theme-option').forEach(option => {{
                option.classList.remove('active');
                if (option.dataset.theme === themeName) {{
                    option.classList.add('active');
                }}
            }});
            
            // Close theme selector
            if (themeSelectorOpen) {{
                toggleThemeSelector();
            }}
        }}

        function toggleTheme() {{
            // Legacy function for backwards compatibility
            const themeOrder = ['mocha', 'frappe', 'macchiato', 'latte'];
            const currentIndex = themeOrder.indexOf(currentTheme);
            const nextIndex = (currentIndex + 1) % themeOrder.length;
            setTheme(themeOrder[nextIndex]);
        }}

        function applyTheme() {{
            // Legacy function for backwards compatibility
            setTheme(currentTheme);
        }}
    </script>
</body>
</html>"""


def _generate_git_stats_html(git_stats: Dict) -> str:
    """Generate HTML for git-specific statistics."""
    return f"""
            <div class="stat-card">
                <span class="stat-value">{git_stats['git_repos']}</span>
                <span class="stat-label">Git Repos</span>
            </div>
            <div class="stat-card">
                <span class="stat-value">{git_stats['up_to_date']}</span>
                <span class="stat-label">Up to Date</span>
            </div>
            <div class="stat-card">
                <span class="stat-value">{git_stats['updates_available']}</span>
                <span class="stat-label">Updates Available</span>
            </div>
            <div class="stat-card">
                <span class="stat-value">{git_stats['errors']}</span>
                <span class="stat-label">Errors</span>
            </div>"""


def _generate_category_options(categories: List[str]) -> str:
    """Generate HTML options for category filter."""
    return '\n'.join(f'<option value="{cat}">{cat.replace("_", " ").title()}</option>' for cat in categories)


def _generate_status_filter_html(status_options: List[str]) -> str:
    """Generate HTML for status filter dropdown."""
    if not status_options:
        return ''
    
    options = '\n'.join(f'<option value="{status}">{status.replace("_", " ").title()}</option>' for status in status_options)
    
    return f"""
            <div class="control-group">
                <label for="status-filter">Status</label>
                <select id="status-filter" onchange="filterItems()">
                    <option value="">All Statuses</option>
                    {options}
                </select>
            </div>"""


def main():
    """CLI entry point for standalone Collection.md generation"""
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

    # Load index using the pipeline function to handle collection overview
    from pipeline import load_index
    items, collection_overview = load_index(index_path)

    # Generate Collection.md
    readme_path = collection_path / 'Collection.md'
    generate_collection(
        items=items,
        collection_name=config['name'],
        collection_type=config['collection_type'],
        output_path=readme_path,
        collection_overview=collection_overview
    )


if __name__ == '__main__':
    main()
