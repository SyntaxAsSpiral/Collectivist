# 💮 Collectivist

**AI-powered collection curator** for intentional collections. Transforms semantically coherent hoards into living documentation substrates with LLM-powered organization and curation.

**Not a general file organizer.** Collectivist shines on collections you care about enough to give them structure and meaning.

## 🌱 Features

- **Domain-specific intelligence**: Git metadata, ID3 tags, EXIF data, citations, and semantic understanding
- **LLM-powered analysis**: Automatic categorization and rich description generation
- **Living documentation**: Auto-generated READMEs that become real knowledge artifacts
- **Zero-install minimal mode**: Drop `.collection/` folder anywhere, works immediately
- **Multi-format outputs**: Markdown, HTML, JSON, interactive Nushell scripts
- **Collection types**: Repositories, research papers, media libraries, creative projects, datasets

## Why This Approach?

General file organizers chase "never think about files again" but usually end up with mediocre generic sorting. Collectivist focuses on **intentional collections** where each item matters, enabling:

- **Depth over breadth**: Domain-specific intelligence instead of one-size-fits-all rules
- **Curation system**: Ongoing pattern learning and intelligent reorganization (standard level)
- **Deterministic outputs**: Pattern learning is persisted explicitly in configuration and index files, preserving deterministic outputs given the same learned state
- **Documentation as artifact**: READMEs become real knowledge repositories
- **Curation that feels magical**: Context-aware organization based on actual intent

## 🧬 Pipeline

1. **Analyzer**: LLM inspects structure, determines collection type, generates config
2. **Indexer**: Domain plugins discover items with rich metadata extraction
3. **Describer**: LLM generates descriptions and assigns semantic categories
4. **Curator**: LLM organizes and reindexes collection on scheduled cadence 

## 🌐 Installation

### 🧺 Minimal Zero-Install (Analyze + Index + Describe)
```bash
# Download .collection/ template
wget https://github.com/SyntaxAsSpiral/collectivist/raw/main/templates/collection-minimal.zip
unzip collection-minimal.zip

# Drop into any collection directory
cp -r .collection ~/my-repos/
cd ~/my-repos

# Start using immediately
python -m .collection analyze
```

### 🎮 Standard Installation (Interactive UI + Curation + Scheduling + Automation)
```bash
# Coming soon: pip install collectivist
# collectivist init ~/my-collection --standard
```
## Usage

### Drop-in Workflow
```bash
# 1. Get .collection/ template (download from GitHub)
# 2. Drop into any directory with content
cp -r .collection ~/my-collection/
cd ~/my-collection

# 3. Analyze and organize
python -m .collection analyze   # LLM detects collection type
python -m .collection update    # Full pipeline: scan → describe → render

# 4. View results
nu .collection/view.nu          # Interactive CLI dashboard
open .collection/dashboard.html # Static HTML viewer
```

#### Collection Types Auto-Detected
- **Repositories**: Git-aware scanning, commit summaries, category taxonomy
- **Research**: Citation extraction, topic clustering, reading status
- **Media**: Timeline organization, mood/genre inference, EXIF metadata
- **Creative**: Version tracking, asset linking, format intelligence
- **Datasets**: Schema inference, sample previews, data provenance

### ⚙️ Configuration

Configure LLM providers via environment variables or copy `.env.example` to `.env` and edit. See `.env.example` for detailed examples.

## Architecture

```
collectivist-repo/
├── .collection/                     # Core pipeline machinery
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

The `collection.yaml` file defines your collection.

Example:
```yaml
collection_type: repositories
name: repos
path: ~/repos
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

## 🔌 Plugins

### Repository Scanner

Scans directories containing git repositories.

**Features:**
- Git status tracking (up_to_date, updates_available, error, no_remote, not_a_repo)
- Auto-pull support via `always_pull` flag
- README-based description generation

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
python -m .collection analyze ~/repos
# Creates collection.yaml

# Force specific type
python -m .collection analyze ~/repos repositories
```

### Stage 2: Scanner

Discovers items and extracts metadata using domain-specific plugin.

```bash
# Run via pipeline (recommended)
python -m .collection update ~/repos --skip-describe --skip-readme
```

### Stage 3: Describer

Generates LLM descriptions with concurrent workers.

```bash
python -m .collection describe ~/repos

# Custom worker count
python -m .collection describe ~/repos 10
```

### Stage 4: README Generator

Transforms YAML index into formatted markdown.

```bash
python -m .collection render ~/repos
```

## Development

**Testing with existing .repos collection:**

```bash
# Test with force-type to skip LLM detection
python -m .collection update ~/repos --force-type repositories

# Validate output matches original system
diff ~/repos/README.md <expected>
```

## 🚫 What Collectivist Is Not

**Not a general file organizer.** For Downloads auto-sorting, check out llama-fs or Local-File-Organizer.

Collectivist excels at **intentional collections** you care about enough to give structure and meaning.

## 🏛️ Architecture

- **Collection-first design**: Intentional collections enable domain depth
- **Two-tier system**: Minimal (indexing + descriptions) + Standard (ongoing curation)
- **Hybrid Python/Nushell**: Beautiful CLI experiences with data processing power
- **Zero-install minimal mode**: Drop folder, works immediately
- **LLM provider abstraction**: Local + cloud with unified interface
- **Plugin architecture**: Extensible scanners for new collection types
- **Deterministic outputs**: Same input → same beautiful results

## 📅 Roadmap

### Complete: Minimal Level MVP
- **Zero-install drop-in system** - `.collection/` folder works anywhere
- **LLM-powered collection analysis** - Auto-detects repository, research, media, creative, dataset types
- **Domain-specific intelligence** - Git metadata, EXIF, citations, schema inference
- **Hybrid Python/Nushell outputs** - Beautiful CLI + multiple formats (MD, HTML, JSON)
- **Self-contained architecture** - All code + deps in one folder

### Next: Standard Level (Interactive Curation)
- **Vite + Vue frontend** - Modern web interface for ongoing curation
- **FastAPI backend** - REST API + WebSocket real-time updates
- **Curation scheduler** - Ongoing pattern learning and reorganization
- **Intelligent suggestions** - Context-aware organization recommendations
- **LLM provider management** - Easy configuration of models/providers

### Future: Package Manager & Extensions
- **Central distribution** - `pip install collectivist` convenience
- **Additional scanners** - Media, documents, music, datasets
- **Auto-scheduling** - Background updates and maintenance

## Contributing

Issues and PRs welcome! This is an exploration of collection-first AI curation.

## License

Private research tool - not for distribution.

---

*Infrastructure as palimpsest, data as compiled breath 🜍*
