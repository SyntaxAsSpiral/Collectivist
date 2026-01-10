# Collectivist Plugin Template

This directory contains a template for creating new Collectivist plugins.

## Creating a New Plugin

1. **Copy the template:**
   ```bash
   cp plugin_template.py ../your_plugin_name.py
   ```

2. **Replace placeholders in the file:**
   - `PLUGIN_NAME` → your plugin name (e.g., `photos`, `videos`, `documents`)
   - `PLUGIN_DESCRIPTION` → description of what your plugin does
   - `PLUGIN_NAMEScanner` → your class name (e.g., `PhotosScanner`)

3. **Implement the required methods:**
   - `detect()` - detection logic for your collection type
   - `scan()` - scanning logic to find and extract items
   - `_extract_metadata()` - metadata extraction specific to your file types
   - `get_content_for_description()` - content extraction for LLM descriptions

4. **Customize categories and prompts:**
   - Update `get_categories()` with relevant categories
   - Modify `get_description_prompt_template()` for your content type
   - Add example descriptions in `get_example_descriptions()`

5. **Test your plugin:**
   ```bash
   # Copy to a test directory
   cp your_plugin_name.py /path/to/test/collection/.collection/plugins/

   # Test detection
   python -m .collection analyze

   # Test scanning
   python -m .collection scan
   ```

## Plugin Interface

All plugins must implement the `CollectionScanner` interface:

- `get_name()` - Plugin identifier
- `get_supported_types()` - Item types (`["file"]`, `["dir"]`, or both)
- `get_categories()` - Default categories for the collection
- `detect()` - Detect if path contains this collection type
- `scan()` - Scan and return `CollectionItem` objects
- `get_description_prompt_template()` - LLM prompt for descriptions
- `get_example_descriptions()` - Example descriptions for training
- `get_content_for_description()` - Extract content from items

## Examples

See the existing plugins for reference:
- `../repository_scanner.py` - Git repository collections
- `../obsidian.py` - Obsidian vault collections
- `../documents.py` - Document collections
- `../media.py` - Media file collections

## Registration

Plugins are automatically registered when imported. Make sure to update the `PluginRegistry.register()` call at the bottom with your plugin details.