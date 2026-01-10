"""
Collection Describer - LLM-Powered Description & Categorization

Generates descriptions and assigns categories for collection items using LLM.
"""

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, Any, List
import yaml

from llm import LLMClient


class CollectionDescriber:
    """Generates LLM-powered descriptions and categories."""

    def __init__(self, collection_path: Path, collection_dir: Path):
        """Initialize describer.

        Args:
            collection_path: Path to collection directory
            collection_dir: Path to .collection directory
        """
        self.collection_path = collection_path
        self.collection_dir = collection_dir

        # Load collection config
        config_path = collection_dir / "collection.yaml"
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
        else:
            self.config = {"domain": "repositories"}

        # Initialize LLM client
        self.llm_client = LLMClient.from_env()

        # Get categories for this domain
        self.categories = self.config.get("categories", [])

    def describe(self) -> None:
        """Generate descriptions and categories for items needing them."""
        # Load current index
        index_path = self.collection_dir / "index.yaml"
        if not index_path.exists():
            print("❌ No index found. Run scanner first.")
            return

        with open(index_path, 'r', encoding='utf-8') as f:
            index_data = yaml.safe_load(f)

        items = index_data.get("items", [])

        # Find items needing descriptions
        items_to_describe = []
        for item in items:
            if not item.get("description") or not item.get("category"):
                items_to_describe.append(item)

        if not items_to_describe:
            print("✅ All items already have descriptions and categories")
            return

        print(f"🧠 Describing {len(items_to_describe)} items...")

        # Process items with concurrent LLM calls
        updated_items = []
        successful_descriptions = 0

        with ThreadPoolExecutor(max_workers=3) as executor:
            # Submit all description tasks
            future_to_item = {}
            for item in items_to_describe:
                future = executor.submit(self._describe_item, item)
                future_to_item[future] = item

            # Process completed descriptions
            for future in as_completed(future_to_item):
                item = future_to_item[future]
                try:
                    updated_item = future.result()
                    updated_items.append(updated_item)
                    successful_descriptions += 1

                    # Progress indicator
                    print(f"  ✓ Described: {item['name']}")

                except Exception as e:
                    print(f"  ❌ Failed: {item['name']} - {e}")
                    # Keep original item if description fails
                    updated_items.append(item)

        # Update items in index data
        item_map = {item["id"]: item for item in updated_items}
        for i, item in enumerate(items):
            if item["id"] in item_map:
                items[i] = item_map[item["id"]]

        # Save updated index
        index_data["items"] = items
        index_data["last_description_run"] = "2026-01-09T15:30:00Z"  # Would use datetime.now()

        with open(index_path, 'w', encoding='utf-8') as f:
            yaml.dump(index_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

        print(f"📝 Generated {successful_descriptions}/{len(items_to_describe)} descriptions")
        print(f"   Updated: {index_path}")

    def _describe_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Generate description and category for a single item."""
        # Create LLM prompt
        prompt = self._create_description_prompt(item)

        try:
            # Query LLM
            messages = [
                {"role": "system", "content": "You analyze collection items and provide concise descriptions and category assignments. Be specific and helpful."},
                {"role": "user", "content": prompt}
            ]

            response = self.llm_client.chat("llama3.1-8b-instant", messages, temperature=0.2)
            result = self._parse_description_response(response)

            # Update item with results
            updated_item = item.copy()
            updated_item["description"] = result.get("description", item.get("description"))
            updated_item["category"] = result.get("category", item.get("category"))

            return updated_item

        except Exception as e:
            print(f"⚠️  LLM description failed for {item['name']}: {e}")
            # Return original item unchanged
            return item

    def _create_description_prompt(self, item: Dict[str, Any]) -> str:
        """Create LLM prompt for item description."""
        domain = self.config.get("domain", "repositories")

        # Domain-specific prompts
        domain_contexts = {
            "repositories": "This is a software repository/project. Focus on the technology stack, purpose, and functionality.",
            "research": "This is a research paper or academic work. Focus on the topic, methodology, and contributions.",
            "media": "This is a media file (photo/video/audio). Focus on content, context, and significance.",
            "creative": "This is a creative project or artwork. Focus on style, medium, and artistic intent.",
            "datasets": "This is a dataset. Focus on structure, domain, and potential use cases."
        }

        context = domain_contexts.get(domain, "This is a collection item.")

        prompt = f"""{context}

CATEGORY TAXONOMY (choose ONE):
{', '.join(self.categories)}

ITEM NAME: {item['name']}
ITEM TYPE: {item['type']}
ITEM PATH: {item['path']}

METADATA:
{yaml.dump(item.get('metadata', {}), default_flow_style=False)}

CONTENT SAMPLE:
{item.get('content_sample', 'No content sample available')}

Provide a concise description (max 150 characters) and assign the most appropriate category.

Return JSON:
{{
  "description": "Brief, specific description of this item",
  "category": "one_category_from_taxonomy_above"
}}
"""

        return prompt

    def _parse_description_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response into description and category."""
        try:
            import json
            import re

            # Look for JSON block
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                return result
            else:
                # Try parsing entire response
                return json.loads(response)

        except Exception as e:
            print(f"⚠️  Failed to parse LLM response: {e}")
            return {
                "description": "Description generation failed",
                "category": self.categories[0] if self.categories else "uncategorized"
            }