# Collectivist

**AI-powered collection curator** for intentional collections. Transforms semantically coherent hoards (repositories, research papers, music libraries, photo archives, creative projects) into living documentation substrates with LLM-powered organization and curation.

**Not a general file organizer.** Collectivist shines on collections you care about enough to give them structure and meaning. For Downloads auto-sorting, check out llama-fs or Local-File-Organizer.

## Overview

Collectivist is a three-stage pipeline for **intentional collections** - semantically coherent hoards where each item matters. Whether it's your repository archive, research paper collection, music library, or creative project hoard, Collectivist uses AI to understand your collection's domain and generate beautiful, searchable documentation that evolves with your curation.

**Collection Types Supported:**
- **Repository Collections** - Git-aware metadata, commit summaries, category taxonomy
- **Research Paper Hoards** - Citation extraction, topic clustering, reading status
- **Media Libraries** - Timeline-aware organization, mood/genre inference
- **Creative Project Folders** - Version tracking, mood boards, linked assets
- **Dataset Collections** - Schema inference, sample previews, provenance notes

## What Makes Collectivist Different

**Collection-First Philosophy:** Unlike general file organizers that chase the dream of "never think about files again," Collectivist focuses on **intentional collections** - semantically coherent groups where each item carries meaning.

**Why This Matters:**
- **Depth over breadth** - Domain-specific intelligence (git metadata, ID3 tags, EXIF data) instead of generic rules
- **Pattern learning that works** - Structure carries strong semantic signal for meaningful suggestions
- **Documentation as artifact** - READMEs become real knowledge repositories, not directory listings
- **Curation feels magical** - Suggestions based on actual organizational intent

**Three-Stage Pipeline:**
1. **Analyzer** - LLM inspects directory structure, determines collection type, generates config
2. **Scanner** - Domain-specific plugins discover items and extract rich metadata
3. **Describer** - LLM generates descriptions and assigns categories using concurrent workers

## Features

- **Collection-First Design** - Optimized for intentional, semantically coherent collections
- **Domain-Specific Intelligence** - Rich metadata extraction (git status, ID3 tags, EXIF, citations, etc.)
- **LLM Provider Abstraction** - Supports local (LMStudio, Ollama) and cloud (OpenRouter, Anthropic, OpenAI, Pollinations) providers
- **Concurrent Processing** - ThreadPoolExecutor with configurable workers for fast description generation
- **Pattern Learning** - Learns your organizational preferences from structure and evolves suggestions
- **Living Documentation** - Auto-generated READMEs that become real knowledge artifacts
- **Self-Healing Curation** - Detects moves, additions, deletions and adapts gracefully
- **Plugin Architecture** - Extensible scanner system for new collection types
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

**First Question: What kind of collection is this?**
Collectivist asks this upfront to select the right domain-specific scanner and category taxonomy.

```bash
# Drop .collection/ folder into your collection directory
# For a repository collection:
cd ~/my-repos
python -m .collection analyze  # LLM detects "repositories" type
python -m .collection update   # Full pipeline with git-aware scanning

# For research papers:
cd ~/research-papers
python -m .collection analyze  # Detects document collection
python -m .collection update   # Citation extraction, topic clustering

# Force collection type if detection is off
python -m .collection update --force-type repositories

# View beautiful CLI dashboard
nu .collection/view.nu

# Open static HTML dashboard
open .collection/dashboard.html
```

## Architecture

```
C:\Users\synta.ZK-ZRRH\.dev\collectivist\
├── .collection\                     # Core pipeline machinery
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
├── .collection\                     # Generated index data
│   └── index.yaml                   # Item metadata + descriptions
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
python .collection/analyzer.py C:\Users\synta\repos
# Creates collection.yaml

# Force specific type
python .collection/analyzer.py C:\Users\synta\repos repositories
```

### Stage 2: Scanner

Discovers items and extracts metadata using domain-specific plugin.

```bash
# Run via pipeline (recommended)
python -m .collection update C:\Users\synta\repos --skip-describe --skip-readme
```

### Stage 3: Describer

Generates LLM descriptions with concurrent workers.

```bash
python -m .collection describe C:\Users\synta\repos

# Custom worker count
python -m .collection describe C:\Users\synta\repos 10
```

### Stage 4: README Generator

Transforms YAML index into formatted markdown.

```bash
python -m .collection render C:\Users\synta\repos
```

## Development

**Testing with existing .repos collection:**

```bash
# Test with force-type to skip LLM detection
python -m .collection update C:\Users\synta.ZK-ZRRH\.dev\.repos --force-type repositories

# Validate output matches original system
diff C:\Users\synta.ZK-ZRRH\.dev\.repos\README.md <expected>
```

## What Collectivist Is Not

**Not a general file organizer.** Collectivist is not designed for:
- Downloads folders with random files
- Desktop cleanup of miscellaneous documents
- Automatic organization of entire filesystems
- Handling infinite edge cases (temp files, caches, logs)

**For general file organization:** Check out llama-fs, Local-File-Organizer, or Sparkle.

**What Collectivist excels at:** Collections you care about enough to give them structure and meaning.

## Technical Doctrine

- **Collection-first constraint**: Focus enables depth over breadth
- **Fast-fail methodology**: LLM unreachable → exit immediately
- **No mock data**: Real metadata only, `null` for missing values
- **Deterministic**: Same filesystem + config = same output
- **Context compilation**: YAML → README transformation, not raw dumps
- **Anagoglyph recursion**: `.collection\` hidden infrastructure layers
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
