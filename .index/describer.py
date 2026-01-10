#!/usr/bin/env python3
"""
Describer Stage - LLM Description Generation
Generates descriptions and assigns categories using ThreadPoolExecutor for concurrency
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import yaml

from llm import LLMClient, Message, test_llm_connection
from plugin_interface import CollectionScanner, CollectionItem, PluginRegistry


class CollectionDescriber:
    """Generates descriptions for collection items using LLM"""

    def __init__(
        self,
        llm_client: LLMClient,
        scanner: CollectionScanner,
        max_workers: int = 5
    ):
        self.llm = llm_client
        self.scanner = scanner
        self.max_workers = max_workers

    def generate_description(
        self,
        item: CollectionItem,
        examples: List[Dict[str, str]]
    ) -> Optional[Dict[str, str]]:
        """
        Generate description and category for a single item.

        Args:
            item: Collection item to describe
            examples: Example descriptions for few-shot learning

        Returns:
            Dict with 'description' and 'category' keys, or None if failed
        """
        # Get content for description
        content = self.scanner.get_content_for_description(item)

        if not content or len(content.strip()) == 0:
            return None

        # Build example text
        example_text = '\n'.join([
            f"- {ex['name']}: {ex['description']} [category: {ex.get('category', 'utilities_misc')}]"
            for ex in examples
        ])

        # Get prompt template and fill it
        prompt_template = self.scanner.get_description_prompt_template()
        prompt = prompt_template.format(content=content)

        # Add examples to context if available
        if example_text:
            prompt = f"Example descriptions from other items:\n{example_text}\n\n{prompt}"

        # Query LLM
        try:
            response = self.llm.chat(
                model="gpt-oss-20b",  # Use configured model
                messages=[Message(role="user", content=prompt)],
                temperature=0.1,
                max_tokens=500
            )

            # Parse JSON response
            try:
                result = json.loads(response.strip())
                description = result.get('description', '').strip()[:150]
                category = result.get('category', 'utilities_misc')

                # Validate category
                valid_categories = self.scanner.get_categories()
                if category not in valid_categories:
                    category = valid_categories[-1]  # Default to last category (usually misc)

                return {'description': description, 'category': category}

            except json.JSONDecodeError:
                # Fallback: treat as plain description
                return {
                    'description': response.strip()[:150],
                    'category': self.scanner.get_categories()[-1]
                }

        except Exception as e:
            print(f"  [X] LLM request failed: {e}")
            return None

    def process_item(
        self,
        item: CollectionItem,
        examples: List[Dict[str, str]],
        idx: int,
        total: int
    ) -> Dict[str, Any]:
        """
        Process a single item in worker thread.

        Returns dict with result status.
        """
        # Generate description
        result = self.generate_description(item, examples)

        if result is None:
            return {
                'item': item,
                'description': None,
                'category': None,
                'error': 'no_content_or_failed',
                'idx': idx,
                'total': total
            }

        return {
            'item': item,
            'description': result['description'],
            'category': result['category'],
            'error': None,
            'idx': idx,
            'total': total
        }

    def describe_collection(
        self,
        items: List[CollectionItem],
        save_callback: Optional[callable] = None
    ) -> List[CollectionItem]:
        """
        Generate descriptions for all items needing them.

        Args:
            items: List of collection items
            save_callback: Optional callback to save after each success (for incremental saves)

        Returns:
            Updated list of items with descriptions populated
        """
        # Filter items needing descriptions
        needs_description = [
            item for item in items
            if item.description is None or item.description == ''
        ]

        total = len(needs_description)

        if total == 0:
            print("[OK] All items already have descriptions")
            return items

        print(f"Found {total} items needing descriptions")
        print(f"Processing with {self.max_workers} concurrent workers...\n")

        # Build examples from items that already have descriptions
        examples = [
            {
                'name': item.short_name,
                'description': item.description,
                'category': item.category or 'utilities_misc'
            }
            for item in items
            if item.description is not None and item.description != ''
        ][:5]

        successful = 0
        failed = []

        # Process with ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            futures = {
                executor.submit(self.process_item, item, examples, idx, total): item
                for idx, item in enumerate(needs_description, 1)
            }

            # Process results as they complete
            for future in as_completed(futures):
                result = future.result()

                if result['error'] is not None:
                    print(f"  [{result['idx']}/{result['total']}] {result['item'].short_name}: [!] {result['error']}")
                    failed.append(result['item'])
                else:
                    print(f"  [{result['idx']}/{result['total']}] {result['item'].short_name}: [OK] {result['description']} [{result['category']}]")

                    # Update item in original list
                    for i, item in enumerate(items):
                        if item.path == result['item'].path:
                            items[i].description = result['description']
                            items[i].category = result['category']
                            break

                    # Call save callback if provided (incremental saves)
                    if save_callback:
                        save_callback(items)

                    successful += 1

        print(f"\n[OK] Completed: {successful}/{total} descriptions generated")
        if failed:
            print(f"[!] Failed: {len(failed)} items")

        return items


def describe_from_index(
    index_path: Path,
    llm_client: LLMClient,
    scanner: CollectionScanner,
    max_workers: int = 5
) -> List[CollectionItem]:
    """
    Load items from index YAML, generate descriptions, save back.

    Args:
        index_path: Path to collection-index.yaml
        llm_client: LLM client instance
        scanner: Scanner instance for this collection type
        max_workers: Number of concurrent workers

    Returns:
        Updated list of items
    """
    # Load index
    with open(index_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    # Convert to CollectionItem objects
    items = []
    for item_data in data:
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
            metadata=item_data.get('metadata', {})
        )
        items.append(item)

    # Create describer
    describer = CollectionDescriber(llm_client, scanner, max_workers)

    # Define save callback for incremental saves
    def save_items(updated_items: List[CollectionItem]):
        # Convert back to dicts
        data = []
        for item in updated_items:
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
                'metadata': item.metadata
            }
            data.append(item_dict)

        # Save
        with open(index_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    # Generate descriptions with incremental saves
    updated_items = describer.describe_collection(items, save_callback=save_items)

    return updated_items


def describe_collection_cli(index_path: str, max_workers: int = 5):
    """
    CLI helper: generate descriptions for items in index

    Args:
        index_path: Path to collection-index.yaml
        max_workers: Number of concurrent workers
    """
    from llm import create_client_from_config

    index_path = Path(index_path)

    # Load collection config to determine scanner type
    collection_dir = index_path.parent.parent
    config_path = collection_dir / 'collection.yaml'

    if not config_path.exists():
        raise FileNotFoundError(f"No collection.yaml found at {config_path}")

    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    collection_type = config['collection_type']

    # Get scanner
    scanner_class = PluginRegistry.get_plugin(collection_type)
    if not scanner_class:
        raise ValueError(f"No scanner found for type: {collection_type}")

    scanner = scanner_class()

    # Create LLM client
    llm_client = create_client_from_config()

    # Test LLM connection (fast-fail)
    print("Testing LLM connection...")
    if not test_llm_connection(llm_client):
        print("[X] FATAL: Cannot reach LLM endpoint")
        print("  Make sure LLM server is running and configured in .env")
        return False

    print("[OK] LLM connection OK\n")

    # Generate descriptions
    describe_from_index(index_path, llm_client, scanner, max_workers)

    return True


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: python describer.py <index_path> [max_workers]")
        print("\nExample: python describer.py C:\\Users\\synta\\repos\\.index\\collection-index.yaml")
        sys.exit(1)

    index_path = sys.argv[1]
    max_workers = int(sys.argv[2]) if len(sys.argv) > 2 else 5

    try:
        success = describe_collection_cli(index_path, max_workers)
        if success:
            print("\n[OK] Description generation complete")
            sys.exit(0)
        else:
            sys.exit(1)
    except Exception as e:
        print(f"\n[X] Description generation failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
