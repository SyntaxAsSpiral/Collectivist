"""
Collection Renderer - Multi-Format Output Generation

Generates beautiful outputs from collection index data:
- README.md (Markdown documentation)
- index.html (Web dashboard)
- index.json (API/programmatic access)
"""

from pathlib import Path
from typing import Dict, Any, List
import json
import yaml
from datetime import datetime


class CollectionRenderer:
    """Renders collection data into various output formats."""

    def __init__(self, collection_path: Path, collection_dir: Path):
        """Initialize renderer.

        Args:
            collection_path: Path to collection directory
            collection_dir: Path to .collection directory
        """
        self.collection_path = collection_path
        self.collection_dir = collection_dir

        # Load collection config and index
        self.config = self._load_config()
        self.index_data = self._load_index()

    def _load_config(self) -> Dict[str, Any]:
        """Load collection configuration."""
        config_path = self.collection_dir / "collection.yaml"
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return {}

    def _load_index(self) -> Dict[str, Any]:
        """Load collection index data."""
        index_path = self.collection_dir / "index.yaml"
        if index_path.exists():
            with open(index_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return {"items": []}

    def render(self) -> None:
        """Generate all configured output formats."""
        print("📝 Rendering collection outputs...")

        formats = self.config.get("output", {}).get("formats", ["markdown"])

        if "markdown" in formats:
            self._render_markdown()
        if "html" in formats:
            self._render_html()
        if "json" in formats:
            self._render_json()
        if "nushell" in formats:
            self._render_nushell()

        print("✅ Generated outputs:")
        for fmt in formats:
            if fmt == "markdown":
                print(f"  📄 {self.collection_path}/README.md")
            elif fmt == "html":
                print(f"  🌐 {self.collection_path}/index.html")
            elif fmt == "json":
                print(f"  📊 {self.collection_path}/index.json")
            elif fmt == "nushell":
                print(f"  🐚 {self.collection_path}/collection.nu")

    def _render_markdown(self) -> None:
        """Generate README.md with collection documentation."""
        title = self.config.get("title", "Collection")
        description = self.config.get("description", "")
        domain = self.config.get("domain", "unknown")

        items = self.index_data.get("items", [])
        total_items = len(items)

        # Group items by category
        categorized = {}
        uncategorized = []

        for item in items:
            category = item.get("category", "uncategorized")
            if category and category != "uncategorized":
                if category not in categorized:
                    categorized[category] = []
                categorized[category].append(item)
            else:
                uncategorized.append(item)

        # Generate markdown
        md = ["# " + title]
        md.append("")

        if description:
            md.append(description)
            md.append("")

        # Stats
        md.append(f"**Collection Stats:** {total_items} items")
        if categorized:
            md.append(f" • {len(categorized)} categories")
        md.append("")

        # Last updated
        last_scan = self.index_data.get("last_scan", "Unknown")
        if last_scan != "Unknown":
            try:
                dt = datetime.fromisoformat(last_scan.replace('Z', '+00:00'))
                md.append(f"**Last updated:** {dt.strftime('%Y-%m-%d %H:%M')}")
            except:
                md.append(f"**Last updated:** {last_scan}")
        md.append("")

        # Status overview
        if items:
            status_counts = {}
            for item in items:
                status = item.get("status", {}).get("git_status", "unknown")
                status_counts[status] = status_counts.get(status, 0) + 1

            md.append("## Status Overview")
            md.append("")
            for status, count in sorted(status_counts.items()):
                status_emoji = self._status_emoji(status)
                md.append(f"- {status_emoji} **{status.replace('_', ' ').title()}:** {count} items")
            md.append("")

        # Categorized sections
        for category, cat_items in sorted(categorized.items()):
            md.append(f"## {category.replace('_', ' ').title()}")
            md.append("")

            # Sort by name
            cat_items.sort(key=lambda x: x.get("name", "").lower())

            for item in cat_items:
                md.append(self._format_item_markdown(item))
                md.append("")

        # Uncategorized items
        if uncategorized:
            md.append("## Other Items")
            md.append("")

            for item in uncategorized:
                md.append(self._format_item_markdown(item))
                md.append("")

        # Footer
        md.append("---")
        md.append("")
        md.append("*Generated by Collectivist - AI-powered collection curator*")
        md.append(f"*Domain: {domain} • Items: {total_items}*")

        # Write file
        readme_path = self.collection_path / "README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(md))

    def _format_item_markdown(self, item: Dict[str, Any]) -> str:
        """Format a single item for markdown output."""
        name = item.get("name", "Unknown")
        description = item.get("description", "No description available")
        path = item.get("path", "")

        # Status indicator
        status = item.get("status", {}).get("git_status", "")
        status_emoji = self._status_emoji(status)

        # Format as markdown
        md = f"### {status_emoji} {name}"
        md += f"\n\n{description}"

        if path:
            md += f"\n\n*Path: `{path}`*"

        # Add metadata if interesting
        metadata = item.get("metadata", {})
        interesting_meta = []

        if "remote" in metadata and metadata["remote"]:
            interesting_meta.append(f"Remote: {metadata['remote']}")
        if "size" in metadata and metadata["size"] > 0:
            size_mb = metadata["size"] / (1024 * 1024)
            interesting_meta.append(f"Size: {size_mb:.1f} MB")

        if interesting_meta:
            md += "\n\n" + " • ".join(interesting_meta)

        return md

    def _render_html(self) -> None:
        """Generate index.html with interactive collection dashboard."""
        title = self.config.get("title", "Collection")
        items = self.index_data.get("items", [])

        # Create self-contained HTML with embedded data
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Collectivist</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f8f9fa;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }}
        .items {{
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .item {{
            padding: 15px;
            border-bottom: 1px solid #eee;
            transition: background 0.2s;
        }}
        .item:hover {{
            background: #f8f9fa;
        }}
        .item:last-child {{
            border-bottom: none;
        }}
        .item-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }}
        .item-name {{
            font-weight: bold;
            font-size: 1.1em;
        }}
        .item-status {{
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
        }}
        .status-up-to-date {{ background: #d4edda; color: #155724; }}
        .status-updates-available {{ background: #fff3cd; color: #856404; }}
        .status-modified {{ background: #f8d7da; color: #721c24; }}
        .status-unknown {{ background: #e2e3e5; color: #383d41; }}
        .item-description {{
            color: #666;
            margin-bottom: 8px;
        }}
        .item-meta {{
            font-size: 14px;
            color: #888;
        }}
        .footer {{
            text-align: center;
            margin-top: 30px;
            color: #666;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{title}</h1>
        <p>{self.config.get('description', 'AI-curated collection')}</p>
        <p><strong>{len(items)} items</strong> • Generated by Collectivist</p>
    </div>

    <div class="stats">
        <div class="stat-card">
            <div class="stat-number">{len(items)}</div>
            <div>Total Items</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{len(set(item.get('category') for item in items if item.get('category')))}</div>
            <div>Categories</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{sum(1 for item in items if item.get('status', {}).get('git_status') == 'up_to_date')}</div>
            <div>Up to Date</div>
        </div>
    </div>

    <div class="items">
"""

        # Sort items by category, then name
        sorted_items = sorted(items, key=lambda x: (x.get('category', 'zzz'), x.get('name', '').lower()))

        for item in sorted_items:
            status_class = self._status_class(item.get('status', {}).get('git_status', 'unknown'))
            status_text = item.get('status', {}).get('git_status', 'unknown').replace('_', ' ').title()

            html += f"""
        <div class="item">
            <div class="item-header">
                <div class="item-name">{item.get('name', 'Unknown')}</div>
                <div class="item-status {status_class}">{status_text}</div>
            </div>
            <div class="item-description">{item.get('description', 'No description available')}</div>
            <div class="item-meta">
                Category: {item.get('category', 'Uncategorized')} •
                Path: {item.get('path', 'Unknown')}
            </div>
        </div>"""

        html += """
    </div>

    <div class="footer">
        <p>Generated by <strong>Collectivist</strong> - AI-powered collection curator</p>
        <p>Domain: """ + str(self.config.get('domain', 'unknown')) + """ • Last updated: """ + str(self.index_data.get('last_scan', 'Unknown')) + """</p>
    </div>

    <script>
        // Simple interactivity
        document.querySelectorAll('.item').forEach(item => {
            item.addEventListener('click', () => {
                item.classList.toggle('expanded');
            });
        });
    </script>
</body>
</html>"""

        # Write HTML file
        html_path = self.collection_path / "index.html"
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html)

    def _render_json(self) -> None:
        """Generate index.json with complete collection data."""
        # Create clean JSON export
        export_data = {
            "collection": {
                "id": self.config.get("collection_id"),
                "title": self.config.get("title"),
                "domain": self.config.get("domain"),
                "description": self.config.get("description"),
                "created": self.config.get("created"),
                "last_scan": self.index_data.get("last_scan"),
                "total_items": self.index_data.get("total_items", 0)
            },
            "items": self.index_data.get("items", [])
        }

        # Write JSON file
        json_path = self.collection_path / "index.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

    def _render_nushell(self) -> None:
        """Generate collection.nu with Nushell interactive script."""
        nu_script = f'''# {self.config.get('title', 'Collection')} - Interactive Nushell Explorer
# Generated by Collectivist

# Load collection data
let data = (open index.yaml)

# Display collection overview
print $"Collection: {($data.collection_id)}"
print $"Domain: {($data.domain)}"
print $"Items: {($data.total_items)}"
print $"Last scan: {($data.last_scan)}"
print ""

# Show items table
print "📊 Collection Items:"
$data.items | table -e | sort-by category name

# Interactive functions
def show-by-category [category: string] {{
    print $"Items in category: ($category)"
    $data.items | where category == $category | table -e
}}

def search-items [query: string] {{
    print $"Searching for: ($query)"
    $data.items | where name =~ $query or description =~ $query | table -e
}}

def show-stats [] {{
    print "📈 Collection Statistics:"
    $data.items | group-by category | each {{|group|
        let cat = $group.group
        let count = ($group.items | length)
        print $"  ($cat): ($count) items"
    }}
}}

# Uncomment to explore interactively:
# show-stats
# show-by-category "ai_llm_agents"
# search-items "neural"
'''

        # Write Nushell script
        nu_path = self.collection_path / "collection.nu"
        with open(nu_path, 'w', encoding='utf-8') as f:
            f.write(nu_script)

    def _status_emoji(self, status: str) -> str:
        """Get emoji for status."""
        emojis = {
            "up_to_date": "✅",
            "updates_available": "🔄",
            "modified": "✏️",
            "ahead_of_remote": "⬆️",
            "no_remote": "🚫",
            "error": "❌",
            "unknown": "❓",
            "not_a_repo": "📁"
        }
        return emojis.get(status, "❓")

    def _status_class(self, status: str) -> str:
        """Get CSS class for status."""
        classes = {
            "up_to_date": "status-up-to-date",
            "updates_available": "status-updates-available",
            "modified": "status-modified",
            "unknown": "status-unknown"
        }
        return classes.get(status, "status-unknown")