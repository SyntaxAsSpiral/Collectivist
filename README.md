# The Collectivist

Universal collection indexing system with LLM-generated descriptions and category tagging.

## Overview

The Collectivist is a three-stage pipeline for cataloging and documenting collections of any type: repositories, media files, documents, music, datasets, and more. It uses AI to understand your collections and generate beautiful, searchable documentation.

**Three-Stage Pipeline:**
1. **Analyzer** - LLM inspects directory structure, determines collection type, generates config
2. **Scanner** - Domain-specific plugins discover items and extract metadata
3. **Describer** - LLM generates descriptions and assigns categories using concurrent workers

## Features

- **Plugin Architecture** - Extensible scanner system for different collection types
- **LLM Provider Abstraction** - Supports local (LMStudio, Ollama) and cloud (OpenRouter, Anthropic, OpenAI, Pollinations) providers
- **Concurrent Processing** - ThreadPoolExecutor with configurable workers for fast description generation
- **Incremental Saves** - Resumable operation with saves after each success
- **Category Taxonomy** - Domain-specific category assignment by LLM
- **Auto-generated README** - Beautiful markdown documentation with tables and categorized sections
- **Git Status Tracking** - Repository scanner tracks fetch status and supports auto-pull
- **Deterministic** - Same filesystem + config = same output

## Installation

```bash
cd C:\Users\synta.ZK-ZRRH\.dev\collectivist
pip install -r requirements.txt

# Configure LLM provider
cp .env.example .env
# Edit .env with your provider settings
```

## Quick Start

```bash
# Index a repository collection
python .index/pipeline.py C:\Users\synta\repos

# Force collection type (skip LLM detection)
python .index/pipeline.py C:\Users\synta\repos --force-type repositories

# Skip specific stages
python .index/pipeline.py C:\Users\synta\repos --skip-describe  # Skip LLM descriptions
python .index/pipeline.py C:\Users\synta\repos --skip-scan      # Regenerate README only
```

## Architecture

```
C:\Users\synta.ZK-ZRRH\.dev\collectivist\
├── .index\                          # Core pipeline machinery
│   ├── llm.py                       # LLM provider abstraction
│   ├── plugin_interface.py          # Scanner plugin interface
│   ├── analyzer.py                  # Stage 1: Collection type detection
│   ├── describer.py                 # Stage 3: LLM description generation
│   ├── readme_generator.py          # Stage 4: README generation
│   └── pipeline.py                  # Main orchestration
├── plugins\                         # Scanner plugins
│   └── repository_scanner.py        # Git repository scanner
├── web\                             # Web dashboard (future)
├── requirements.txt
├── .env.example
└── README.md

Your Collection\
├── .index\                          # Generated index data
│   └── collection-index.yaml        # Item metadata + descriptions
├── collection.yaml                  # Collection configuration
└── README.md                        # Auto-generated documentation
```

## Collection Configuration

The `collection.yaml` file defines your collection:

```yaml
collection_type: repositories
name: repos
path: C:\Users\synta\repos
categories:
  - phext_hyperdimensional
  - ai_llm_agents
  - terminal_ui
  - creative_aesthetic
  - dev_tools
  - esoteric_experimental
  - system_infrastructure
  - utilities_misc
exclude_hidden: true
scanner_config: {}
```

## Plugins

### Repository Scanner

Scans directories containing git repositories.

**Features:**
- Git status tracking (up_to_date, updates_available, error, no_remote, not_a_repo)
- Auto-pull support via `always_pull` flag
- README-based description generation
- Category taxonomy for software projects

**Categories:**
- `phext_hyperdimensional` - Phext, hyperdimensional text, multi-dimensional systems
- `ai_llm_agents` - AI agents, LLMs, machine learning infrastructure
- `terminal_ui` - Terminal UI frameworks, TUI components, CLI styling
- `creative_aesthetic` - Music, art, visualization, color schemes
- `dev_tools` - Development utilities, scaffolding, build tools
- `esoteric_experimental` - Esoteric programming, occult/mystical systems
- `system_infrastructure` - System-level tools, SSH, networking
- `utilities_misc` - General utilities, miscellaneous tools

### Creating Custom Plugins

Implement the `CollectionScanner` interface:

```python
from plugin_interface import CollectionScanner, CollectionItem, PluginRegistry

class MyScanner(CollectionScanner):
    def get_name(self) -> str:
        return "my_collection_type"

    def get_categories(self) -> List[str]:
        return ["category1", "category2"]

    def detect(self, path: Path) -> bool:
        # Return True if this scanner handles this path
        pass

    def scan(self, root_path: Path, config: Dict) -> List[CollectionItem]:
        # Discover items and extract metadata
        pass

    def get_description_prompt_template(self) -> str:
        # Return LLM prompt template for descriptions
        pass

    def get_content_for_description(self, item: CollectionItem) -> str:
        # Extract content for LLM analysis
        pass

# Register plugin
PluginRegistry.register("my_collection_type", MyScanner)
```

## LLM Configuration

### Local Providers

**LMStudio:**
```bash
LLM_PROVIDER=lmstudio
# No API key needed, uses localhost:1234
```

**Ollama:**
```bash
LLM_PROVIDER=ollama
# No API key needed, uses localhost:11434
```

### Cloud Providers

**OpenRouter:**
```bash
LLM_PROVIDER=openrouter
LLM_API_KEY=sk-or-v1-...
```

**Anthropic:**
```bash
LLM_PROVIDER=anthropic
LLM_API_KEY=sk-ant-...
```

**OpenAI:**
```bash
LLM_PROVIDER=openai
LLM_API_KEY=sk-...
```

## Pipeline Stages

### Stage 1: Analyzer

Inspects directory structure and determines collection type.

```bash
python .index/analyzer.py C:\Users\synta\repos
# Creates collection.yaml

# Force specific type
python .index/analyzer.py C:\Users\synta\repos repositories
```

### Stage 2: Scanner

Discovers items and extracts metadata using domain-specific plugin.

```bash
# Run via pipeline (recommended)
python .index/pipeline.py C:\Users\synta\repos --skip-describe --skip-readme
```

### Stage 3: Describer

Generates LLM descriptions with concurrent workers.

```bash
python .index/describer.py C:\Users\synta\repos\.index\collection-index.yaml

# Custom worker count
python .index/describer.py C:\Users\synta\repos\.index\collection-index.yaml 10
```

### Stage 4: README Generator

Transforms YAML index into formatted markdown.

```bash
python .index/readme_generator.py C:\Users\synta\repos
```

## Development

**Testing with existing .repos collection:**

```bash
# Test with force-type to skip LLM detection
python .index/pipeline.py C:\Users\synta.ZK-ZRRH\.dev\.repos --force-type repositories

# Validate output matches original system
diff C:\Users\synta.ZK-ZRRH\.dev\.repos\README.md <expected>
```

## Technical Doctrine

- **Fast-fail methodology**: LLM unreachable → exit immediately
- **No mock data**: Real metadata only, `null` for missing values
- **Deterministic**: Same filesystem + config = same output
- **Context compilation**: YAML → README transformation, not raw dumps
- **Anagoglyph recursion**: `.index\` hidden infrastructure layers
- **Leave no trace**: Clean final-state, no legacy artifacts
- **Incremental saves**: Resumable operation after each success

## Roadmap

### Phase 1: Core Pipeline (Complete)
- ✓ LLM provider abstraction
- ✓ Plugin architecture
- ✓ Repository scanner
- ✓ Three-stage pipeline
- ✓ README generation

### Phase 2: Additional Plugins
- Media scanner (video, audio, images)
- Document scanner (PDF, Word, Markdown)
- Music scanner (with metadata extraction)
- Dataset scanner (CSV, JSON, Parquet)

### Phase 3: Web Dashboard
- React frontend
- Live-updating README preview
- WebSocket updates during scanning
- Visual category browser

### Phase 4: Auto-scheduling
- Task Scheduler integration (Windows)
- Cron support (Linux/macOS)
- Configurable update intervals

## License

Private research tool - not for distribution.

---

**Last updated:** 2026-01-09

Infrastructure as palimpsest, data as compiled breath 🜍
