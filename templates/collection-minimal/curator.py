"""
Collection Curator - Schema Evolution Engine

The "Advanced Analyzer" that evolves collection schema over time.
Takes current schema + collection state → analyzes organization effectiveness → proposes schema improvements.

CORE QUESTIONS:
- Are files organized effectively under current schema?
- Are categories accurate, redundant, or optimally useful?
- Is folder structure conducive to semantic substrate?
- Should schema evolve for better efficacy while maintaining stability?

BALANCE: Keep schema stable as long as possible while ensuring maximum effectiveness.
Can't be afraid of mutation, can't be stagnant without efficacy.

GENERATES: Updated collection.yaml schema for next pipeline run.
Operator manual reorganization gets detected and incorporated.

HIERARCHICAL INTERVENTION (when evolution needed):
- Level 1: Metadata enrichment (safe, no structural changes)
- Level 2: Category refinement (moderate, when categories get crowded)
- Level 3: Structural reorganization (major, for fundamental domain shifts)
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
        """Run schema evolution analysis and update collection.yaml for next run"""
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

        # Analyze collection organization and effectiveness
        analysis = self._analyze_organization_effectiveness(index_data)

        # Determine if schema evolution is needed
        evolution_needed = self._should_evolve_schema(analysis)

        if not evolution_needed:
            print("✅ Schema is effective - maintaining stability")
            return

        # Generate evolved schema
        evolved_config = self._evolve_schema(analysis)

        # Generate proposals script for user review
        self._generate_proposals_script(analysis, evolved_config)

        print(f"🎯 Generated schema evolution proposals in {self.collection_path}/proposals.nu")
        print("   Review changes and run: nu proposals.nu"        print("   This will update collection.yaml for the next pipeline run")

    def _analyze_organization_effectiveness(self, index_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze how well the current schema organizes the collection."""
        items = index_data.get("items", [])
        current_categories = self.config.get("categories", [])

        # Core analysis questions
        analysis = {
            "total_items": len(items),
            "current_categories": current_categories,
            "effectiveness_metrics": {},
            "organizational_issues": [],
            "evolution_opportunities": []
        }

        # 1. Are files organized effectively under current schema?
        category_distribution = self._analyze_category_distribution(items)
        analysis["effectiveness_metrics"]["category_balance"] = category_distribution

        # 2. Are categories accurate, redundant, or optimally useful?
        category_effectiveness = self._analyze_category_effectiveness(items, current_categories)
        analysis["effectiveness_metrics"]["category_effectiveness"] = category_effectiveness

        # 3. Is folder structure conducive to semantic substrate?
        folder_structure = self._analyze_folder_structure(items)
        analysis["effectiveness_metrics"]["folder_structure"] = folder_structure

        # 4. Check for operator-induced changes (manual reorganization)
        operator_changes = self._detect_operator_changes(items)
        analysis["organizational_issues"].extend(operator_changes)

        # 5. Identify evolution opportunities
        evolution_opportunities = self._identify_evolution_opportunities(analysis)
        analysis["evolution_opportunities"] = evolution_opportunities

        return analysis

    def _should_evolve_schema(self, analysis: Dict[str, Any]) -> bool:
        """Determine if schema evolution is warranted."""
        # Evolution triggers:
        # - Significant organizational issues
        # - Very unbalanced categories (>3x difference)
        # - Categories with very low utility (<3 items each)
        # - Operator changes detected

        issues = len(analysis["organizational_issues"])
        opportunities = len(analysis["evolution_opportunities"])

        # Require multiple signals before evolving
        evolution_signals = issues + opportunities

        return evolution_signals >= 2  # Conservative threshold

    def _evolve_schema(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate evolved schema based on analysis."""
        evolved_config = self.config.copy()

        # Apply evolution opportunities
        for opportunity in analysis["evolution_opportunities"]:
            if opportunity["type"] == "category_consolidation":
                # Remove redundant categories
                evolved_config["categories"] = [
                    cat for cat in evolved_config["categories"]
                    if cat not in opportunity["redundant_categories"]
                ]
            elif opportunity["type"] == "category_split":
                # Add new subcategories
                evolved_config["categories"].extend(opportunity["new_categories"])

        # Update schema evolution timestamp
        evolved_config["schema_evolution"] = {
            "last_evolved": datetime.now().isoformat(),
            "rationale": "Automated schema evolution for better organization",
            "analysis_summary": f"{len(analysis['organizational_issues'])} issues, {len(analysis['evolution_opportunities'])} opportunities"
        }

        return evolved_config

    def _analyze_category_distribution(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze how well items are distributed across categories."""
        category_counts = {}
        uncategorized = 0

        for item in items:
            category = item.get("category")
            if category:
                category_counts[category] = category_counts.get(category, 0) + 1
            else:
                uncategorized += 1

        # Calculate balance metrics
        if category_counts:
            avg_per_category = sum(category_counts.values()) / len(category_counts)
            max_category = max(category_counts.values())
            min_category = min(category_counts.values())
            balance_ratio = max_category / max(1, min_category)
        else:
            avg_per_category = 0
            balance_ratio = 1

        return {
            "category_counts": category_counts,
            "uncategorized_count": uncategorized,
            "total_categories": len(category_counts),
            "avg_items_per_category": avg_per_category,
            "balance_ratio": balance_ratio,
            "is_balanced": balance_ratio <= 3.0  # 3x difference is acceptable
        }

    def _analyze_category_effectiveness(self, items: List[Dict[str, Any]], categories: List[str]) -> Dict[str, Any]:
        """Analyze if categories are accurate, redundant, or useful."""
        effectiveness = {
            "effective_categories": [],
            "underutilized_categories": [],  # < 3 items
            "potentially_redundant": [],
            "missing_categories_needed": []
        }

        category_usage = {}
        for item in items:
            category = item.get("category")
            if category:
                category_usage[category] = category_usage.get(category, 0) + 1

        # Check for underutilized categories
        for category in categories:
            count = category_usage.get(category, 0)
            if count < 3:
                effectiveness["underutilized_categories"].append({
                    "category": category,
                    "item_count": count
                })

        # Look for semantic redundancy (would need LLM analysis)
        # This is a placeholder for more sophisticated analysis

        return effectiveness

    def _analyze_folder_structure(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze if folder structure supports semantic organization."""
        # Analyze path patterns
        paths = [item.get("path", "") for item in items if item.get("path")]

        # Check for semantic folder naming
        semantic_folders = 0
        total_folders = set()

        for path in paths:
            parts = path.split("/")
            for part in parts:
                if part and not part.startswith("."):
                    total_folders.add(part)
                    # Simple heuristic: folders with multiple words or descriptive names
                    if len(part.split()) > 1 or len(part) > 15:
                        semantic_folders += 1

        return {
            "total_unique_folders": len(total_folders),
            "semantic_folders": semantic_folders,
            "semantic_ratio": semantic_folders / max(1, len(total_folders)),
            "supports_semantic_substrate": semantic_folders > len(total_folders) * 0.3
        }

    def _detect_operator_changes(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect manual reorganization by operator."""
        issues = []

        # Check for items that might have been moved
        # (This would need comparison with previous index to detect moves)

        # Check for folders that don't match category expectations
        category_folders = {}
        for item in items:
            path_parts = item.get("path", "").split("/")
            category = item.get("category")

            if len(path_parts) > 1 and category:
                folder = path_parts[0]
                if folder not in category_folders:
                    category_folders[folder] = set()
                category_folders[folder].add(category)

        # Flag folders with mixed categories (potential reorganization)
        for folder, categories in category_folders.items():
            if len(categories) > 1:
                issues.append({
                    "type": "mixed_categories_in_folder",
                    "folder": folder,
                    "categories": list(categories),
                    "description": f"Folder '{folder}' contains items from {len(categories)} different categories"
                })

        return issues

    def _identify_evolution_opportunities(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify concrete opportunities for schema evolution."""
        opportunities = []

        # Category consolidation opportunities
        underutilized = analysis["effectiveness_metrics"]["category_effectiveness"]["underutilized_categories"]
        if len(underutilized) > 1:
            opportunities.append({
                "type": "category_consolidation",
                "redundant_categories": [cat["category"] for cat in underutilized],
                "rationale": f"Consolidate {len(underutilized)} underutilized categories"
            })

        # Balance improvement opportunities
        balance = analysis["effectiveness_metrics"]["category_balance"]
        if not balance["is_balanced"]:
            opportunities.append({
                "type": "category_rebalancing",
                "imbalanced_categories": balance["category_counts"],
                "rationale": f"Balance categories (current ratio: {balance['balance_ratio']:.1f})"
            })

        return opportunities

    def _generate_proposals_script(self, analysis: Dict[str, Any], evolved_config: Dict[str, Any]) -> None:
        """Generate proposals.nu script for user review and schema application."""
        script_path = self.collection_path / "proposals.nu"

        script_lines = [
            "# Collectivist Schema Evolution Proposals",
            "# Review these suggestions and run to apply schema evolution",
            "# Generated on: " + datetime.now().isoformat(),
            "",
            "# Current Schema Analysis:",
            f"# - Total items: {analysis['total_items']}",
            f"# - Current categories: {len(analysis.get('current_categories', []))}",
            f"# - Organizational issues: {len(analysis.get('organizational_issues', []))}",
            f"# - Evolution opportunities: {len(analysis.get('evolution_opportunities', []))}",
            "",
            "# Proposed Schema Changes:",
        ]

        # Show what will change in the schema
        current_cats = set(analysis.get("current_categories", []))
        new_cats = set(evolved_config.get("categories", []))

        removed_cats = current_cats - new_cats
        added_cats = new_cats - current_cats

        if removed_cats:
            script_lines.append(f"# Categories to remove: {', '.join(removed_cats)}")
        if added_cats:
            script_lines.append(f"# Categories to add: {', '.join(added_cats)}")

        script_lines.extend([
            "",
            "# Apply schema evolution:",
            f"cp '{self.collection_dir}/collection.yaml' '{self.collection_dir}/collection.yaml.backup'",
            f"cat > '{self.collection_dir}/collection.yaml' << 'EOF'",
        ])

        # Include the evolved config in the script
        script_lines.append(yaml.dump(evolved_config, default_flow_style=False))

        script_lines.extend([
            "EOF",
            "",
            "# Verify the changes:",
            f"echo 'Schema updated. Run pipeline to see effects.'",
            "",
            "# To revert changes:",
            "# cp collection.yaml.backup collection.yaml",
            "",
            "# After applying, run the full pipeline:",
            "# collectivist update",
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