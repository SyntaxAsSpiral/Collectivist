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
from events import EventEmitter, EventStage


class CollectionDescriber:
    """Generates descriptions for collection items using LLM"""

    def __init__(
        self,
        llm_client: LLMClient,
        scanner: CollectionScanner,
        max_workers: int = 5,
        event_emitter: Optional[EventEmitter] = None
    ):
        self.llm = llm_client
        self.scanner = scanner
        self.max_workers = max_workers
        self.emitter = event_emitter

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

    def generate_collection_overview(
        self,
        items: List[CollectionItem],
        collection_type: str
    ) -> Optional[str]:
        """
        Generate a contextual overview of the entire collection.

        Args:
            items: List of all collection items with descriptions
            collection_type: Type of collection (repositories, media, etc.)

        Returns:
            Generated overview paragraph or None if failed
        """
        # Only generate overview if we have items with descriptions
        described_items = [item for item in items if item.description]
        if not described_items:
            return None

        # Gather collection statistics
        total_items = len(items)
        described_count = len(described_items)
        categories = {}
        
        for item in described_items:
            if item.category:
                categories[item.category] = categories.get(item.category, 0) + 1

        # Build context for LLM
        category_summary = ", ".join([f"{count} {cat}" for cat, count in categories.items()])
        
        # Sample descriptions for context (up to 10 items)
        sample_descriptions = []
        for item in described_items[:10]:
            sample_descriptions.append(f"- {item.short_name}: {item.description} [{item.category or 'uncategorized'}]")
        
        sample_text = "\n".join(sample_descriptions)

        # Create prompt for collection overview
        prompt = f"""Analyze this {collection_type} collection and generate a concise overview paragraph (2-3 sentences, max 200 words).

COLLECTION STATISTICS:
- Total items: {total_items}
- Items with descriptions: {described_count}
- Categories: {category_summary}

SAMPLE ITEMS:
{sample_text}

Generate a contextual overview that captures:
1. The main focus/theme of this collection
2. Key categories or types of content
3. Any notable patterns or characteristics

Return only the overview paragraph, no additional formatting or explanation."""

        try:
            response = self.llm.chat(
                messages=[Message(role="user", content=prompt)],
                temperature=0.3,
                max_tokens=300
            )
            
            # Clean and truncate the response
            overview = response.strip()
            if len(overview) > 500:  # Safety limit
                overview = overview[:497] + "..."
                
            return overview

        except Exception as e:
            if self.emitter:
                self.emitter.warn(f"Failed to generate collection overview: {e}")
            else:
                print(f"  [!] Failed to generate collection overview: {e}")
            return None

    def describe_collection(
        self,
        items: List[CollectionItem],
        save_callback: Optional[callable] = None
    ) -> tuple[List[CollectionItem], Optional[str]]:
        """
        Generate descriptions for all items needing them, then generate collection overview.

        Args:
            items: List of collection items
            save_callback: Optional callback to save after each success (for incremental saves)

        Returns:
            Tuple of (updated items list, collection overview string)
        """
        # Filter items needing descriptions
        needs_description = [
            item for item in items
            if item.description is None or item.description == ''
        ]

        total = len(needs_description)

        if total == 0:
            if self.emitter:
                self.emitter.info("All items already have descriptions")
            else:
                print("[OK] All items already have descriptions")
            return items

        if self.emitter:
            self.emitter.set_stage(EventStage.DESCRIBE, total_items=total)
            self.emitter.info(f"Found {total} items needing descriptions")
        else:
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
                    if self.emitter:
                        self.emitter.warn(f"{result['item'].short_name}: {result['error']}")
                    else:
                        print(f"  [{result['idx']}/{result['total']}] {result['item'].short_name}: [!] {result['error']}")
                    failed.append(result['item'])
                else:
                    if self.emitter:
                        self.emitter.set_progress(
                            result['idx'], 
                            result['item'].short_name
                        )
                        self.emitter.info(f"{result['item'].short_name}: {result['description']} [{result['category']}]")
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

        if self.emitter:
            self.emitter.complete_stage(f"Completed: {successful}/{total} descriptions generated")
            if failed:
                self.emitter.warn(f"Failed: {len(failed)} items")
        else:
            print(f"\n[OK] Completed: {successful}/{total} descriptions generated")
            if failed:
                print(f"[!] Failed: {len(failed)} items")

        # Generate collection overview after all descriptions are complete
        collection_overview = None
        if successful > 0:  # Only generate if we have some descriptions
            if self.emitter:
                self.emitter.info("Generating collection overview...")
            else:
                print("\nGenerating collection overview...")
            
            # We need collection_type - try to infer from scanner or use generic
            collection_type = getattr(self.scanner, 'collection_type', 'collection')
            if hasattr(self.scanner, 'get_name'):
                collection_type = self.scanner.get_name()
            
            collection_overview = self.generate_collection_overview(items, collection_type)
            
            if collection_overview:
                if self.emitter:
                    self.emitter.info(f"Collection overview: {collection_overview[:100]}...")
                else:
                    print(f"[OK] Collection overview generated: {collection_overview[:100]}...")

        return items, collection_overview


def describe_from_index(
    index_path: Path,
    llm_client: LLMClient,
    scanner: CollectionScanner,
    max_workers: int = 5
) -> tuple[List[CollectionItem], Optional[str]]:
    """
    Load items from index YAML, generate descriptions, save back with collection overview.

    Args:
        index_path: Path to collection-index.yaml
        llm_client: LLM client instance
        scanner: Scanner instance for this collection type
        max_workers: Number of concurrent workers

    Returns:
        Tuple of (updated items list, collection overview)
    """
    # Load index
    with open(index_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    # Handle both old format (list) and new format (dict with collection_overview)
    if isinstance(data, list):
        items_data = data
        existing_overview = None
    else:
        items_data = data.get('items', data)  # Support both 'items' key or direct list
        existing_overview = data.get('collection_overview')

    # Convert to CollectionItem objects
    items = []
    for item_data in items_data:
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

    # Define save callback for incremental saves with overview
    def save_items_with_overview(updated_items: List[CollectionItem], overview: Optional[str] = None):
        # Convert back to dicts
        items_data = []
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
            items_data.append(item_dict)

        # Create new format with collection_overview at top
        output_data = {}
        if overview or existing_overview:
            output_data['collection_overview'] = overview or existing_overview
        
        # Add items as a direct list (not under 'items' key to match expected format)
        # Based on requirements, the format should be:
        # collection_overview: "..."
        # - item1
        # - item2
        # So we need to save as a dict with collection_overview + direct list items
        
        # Actually, let's check the expected format again - it shows items as direct array
        # So we'll save in the expected format: overview field + direct item array
        with open(index_path, 'w', encoding='utf-8') as f:
            if overview or existing_overview:
                # Write overview first
                f.write(f"collection_overview: {yaml.dump(overview or existing_overview).strip()}\n\n")
            
            # Write items as direct array
            yaml.dump(items_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    # Generate descriptions with incremental saves (but don't save overview until the end)
    def incremental_save(updated_items: List[CollectionItem]):
        save_items_with_overview(updated_items, existing_overview)

    # Generate descriptions and overview
    updated_items, collection_overview = describer.describe_collection(items, save_callback=incremental_save)

    # Final save with the new overview
    save_items_with_overview(updated_items, collection_overview)

    return updated_items, collection_overview


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
    updated_items, collection_overview = describe_from_index(index_path, llm_client, scanner, max_workers)

    if collection_overview:
        print(f"\n[OK] Collection overview: {collection_overview}")

    return True


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: python describer.py <index_path> [max_workers]")
        print("\nExample: python describer.py C:\\Users\\synta\\repos\\.collection\\index.yaml")
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
