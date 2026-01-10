"""
Collection Curator - Conservative Curation Engine

Implements the "architectural critic" approach with hierarchical intervention levels:
- Level 1: Metadata enrichment (safe, no structural changes)
- Level 2: Category refinement (moderate, when categories get crowded)
- Level 3: Structural reorganization (major, for fundamental domain shifts)

Generates proposals.nu script for user review before applying changes.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import yaml

from llm import LLMClient


class CollectionCurator:
    """Conservative curation engine that proposes improvements without breaking stability."""

    def __init__(self, collection_path: Path, collection_dir: Path, llm_client=None):
        """Initialize curator.

        Args:
            collection_path: Path to collection directory
            collection_dir: Path to .collection directory
            llm_client: Optional LLM client instance
        """
        self.collection_path = collection_path
        self.collection_dir = collection_dir
        self.llm_client = llm_client or LLMClient.from_config()

    def curate(self) -> None:
        """Run conservative curation analysis and generate proposals.nu"""
        # Load current index
        index_path = self.collection_dir / "index.yaml"
        if not index_path.exists():
            print("❌ No index found. Run indexer first.")
            return

        with open(index_path, 'r', encoding='utf-8') as f:
            index_data = yaml.safe_load(f)

        # Load collection config
        config_path = self.collection_dir / "collection.yaml"
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
        else:
            self.config = {}

        # Analyze collection for curation opportunities
        analysis = self._analyze_curation_opportunities(index_data)

        if not analysis["proposals"]:
            print("✅ Collection structure is optimal - no curation needed")
            return

        # Generate proposals script
        self._generate_proposals_script(analysis)

        print(f"🎯 Generated curation proposals in {self.collection_path}/proposals.nu")
        print("   Review and run: nu proposals.nu")

    def _analyze_curation_opportunities(self, index_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze collection for potential curation improvements."""
        items = index_data.get("items", [])
        categories = self.config.get("categories", [])

        # Level 1: Check for missing metadata
        missing_descriptions = sum(1 for item in items if not item.get("description"))
        missing_categories = sum(1 for item in items if not item.get("category"))

        # Level 2: Check for overcrowded categories
        category_sizes = {}
        for item in items:
            category = item.get("category", "uncategorized")
            category_sizes[category] = category_sizes.get(category, 0) + 1

        overcrowded_categories = []
        for category, size in category_sizes.items():
            if size > 20:  # Threshold for "crowded"
                overcrowded_categories.append({
                    "category": category,
                    "size": size,
                    "items": [item for item in items if item.get("category") == category][:5]  # Sample
                })

        # Level 3: Check for domain drift (would need historical analysis)

        analysis = {
            "total_items": len(items),
            "categories": categories,
            "category_sizes": category_sizes,
            "proposals": []
        }

        # Generate proposals based on findings
        if missing_descriptions > 0:
            analysis["proposals"].append({
                "level": 1,
                "type": "metadata_enrichment",
                "description": f"Fill in {missing_descriptions} missing descriptions",
                "action": "describe_missing_items"
            })

        for crowded in overcrowded_categories:
            analysis["proposals"].append({
                "level": 2,
                "type": "category_refinement",
                "description": f"Split overcrowded '{crowded['category']}' category ({crowded['size']} items)",
                "category": crowded["category"],
                "size": crowded["size"],
                "action": "propose_category_split"
            })

        return analysis

    def _generate_proposals_script(self, analysis: Dict[str, Any]) -> None:
        """Generate proposals.nu script for user review."""
        script_path = self.collection_path / "proposals.nu"

        script_lines = [
            "# Collectivist Curation Proposals",
            "# Review these suggestions and uncomment/run what you approve",
            "# Generated on: " + datetime.now().isoformat(),
            "",
            "# Collection Analysis:",
            f"# - Total items: {analysis['total_items']}",
            f"# - Categories: {', '.join(analysis['category_sizes'].keys())}",
            "",
        ]

        for i, proposal in enumerate(analysis["proposals"], 1):
            script_lines.extend([
                f"# Proposal {i}: {proposal['description']}",
                f"# Level: {proposal['level']} (conservative intervention)",
                "",
            ])

            if proposal["type"] == "metadata_enrichment":
                script_lines.extend([
                    "# This would run the describer on missing items only",
                    "# collectivist describe --only-missing",
                    "",
                ])
            elif proposal["type"] == "category_refinement":
                category = proposal["category"]
                script_lines.extend([
                    f"# Propose splitting '{category}' category",
                    f"# Would analyze items and suggest subcategories",
                    f"# collectivist curate --split-category '{category}'",
                    "",
                ])

        script_lines.extend([
            "# To apply all approved proposals:",
            "# nu proposals.nu",
            "",
            "# To reject all proposals:",
            "# rm proposals.nu",
        ])

        with open(script_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(script_lines))

    def propose_category_split(self, category: str, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate proposal for splitting an overcrowded category."""
        # Sample a few items for analysis
        sample_items = items[:10]

        prompt = f"""Analyze this overcrowded category and propose how to split it into logical subcategories.

CATEGORY: {category}
SAMPLE ITEMS:
{chr(10).join([f"- {item.get('name', 'Unknown')}: {item.get('description', 'No description')[:100]}" for item in sample_items])}

The category has {len(items)} total items. Propose 2-4 logical subcategories that would better organize this content.

Return JSON:
{{
  "subcategories": [
    {{
      "name": "subcategory_name",
      "description": "what this subcategory contains",
      "estimated_count": 15
    }}
  ],
  "rationale": "why this split makes sense"
}}
"""

        try:
            messages = [
                {"role": "system", "content": "You are a taxonomy expert. Suggest logical ways to split overcrowded categories while maintaining semantic coherence."},
                {"role": "user", "content": prompt}
            ]

            response = self.llm_client.chat(messages, temperature=0.3)

            import json
            result = json.loads(response)

            return {
                "category": category,
                "subcategories": result.get("subcategories", []),
                "rationale": result.get("rationale", "Category split proposal")
            }

        except Exception as e:
            return {
                "category": category,
                "error": str(e),
                "subcategories": []
            }