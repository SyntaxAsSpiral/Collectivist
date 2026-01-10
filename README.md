# 💮 Collectivist

**AI-powered collection curator** for intentional collections. Transforms semantically coherent hoards into living documentation substrates with LLM-powered organization and curation.

**Not a general file organizer.** Collectivist shines on collections you care about enough to give them structure and meaning.

## 🌱 Features

- **Domain-specific intelligence**: Git metadata, ID3 tags, EXIF data, citations, and semantic understanding
- **Curation that feels magical**: Context-aware organization based on actual intent
- **LLM-powered analysis**: Automatic categorization and rich description generation. 
- **Living documentation**: Auto-generated READMEs that become real knowledge artifacts
- **Zero-install minimal mode**: Drop `.collection/` folder anywhere, works immediately.
- **Easy configuration**: Use any OpenAI compatible provider; local or cloud-hosted. Defaults to LM Studio
- **Multi-format outputs**: Markdown, HTML, JSON, interactive shell scripts
- **Collection types**: Repositories, Obsidian vaults, documents, media files, research papers, creative projects, datasets

## Installation

### 🧺 Minimal Zero-Install (Analyze + Index + Describe)
1) Clone repo
2) Copy .collection/ to your collection folder to be curated.<br>
**OR**:<br>
```bash
# Download .collection/ template from releases
# TODO: Update with actual release URL when first release is created
wget https://github.com/SyntaxAsSpiral/collectivist/releases/download/v0.1.0/collection-minimal.zip
unzip collection-minimal.zip
# Drop into any collection directory
cp -r .collection ~/my-repos/
cd ~/my-repos
```
3) Start using immediately
```bash
python -m .collection analyze
```

### 🎮 Standard Installation (Interactive UI + Curation Loop + Scheduling + Automation)
```bash
# Coming soon: pip install collectivist
# collectivist init ~/my-collection --standard
```
### 🤖 Configuration

See `config.example` (YAML) and `config.example.md` (Markdown-embedded) for examples.

Configure LLM providers by copying `config.example` to one of these locations and editing:

1. **`.collection/collectivist.yaml`** - Collection-specific configuration
2. **`.collection/collectivist.md`** - Collection config embedded in Markdown (Obsidian-friendly)
3. **`collectivist.md`** - Collection root config (Obsidian users - put in vault root)
4. **`~/.collectivist/config.yaml`** - Global user configuration

## Usage

### Full Drop-in Workflow

```bash
# 1. Get .collection/ template (download from GitHub)
# 2. Drop into any directory with content
cp -r .collection ~/my-collection/
cd ~/my-collection

# 3. Initialize and run curation loop
python -m .collection analyze   # ⚠️ Initialize collection (resets schema evolution)
python -m .collection update    # Full pipeline + curation loop

# 4. View results
nu .collection/view.nu          # Interactive CLI dashboard (shell)
bash .collection/view.sh        # Interactive CLI dashboard (POSIX shell)
open .collection/dashboard.html # Static HTML viewer
```

### ⚠️ Reinitialization Warning

Running `python -m .collection analyze` again will **reset your collection's schema evolution and curation history**. This action cannot be undone.

- **Use `analyze`** only for: First-time setup, major collection restructuring
- **Use `update`** for: Regular curation loop (preserves schema evolution)
- **Schema evolution** from the Curator is lost when re-analyzing

The curation loop is designed for continuous improvement - avoid reinitialization unless necessary!



## Collection Schema

#### Collection Types Auto-Detected
- **Repositories**: Git-aware scanning, commit summaries, category taxonomy
- **Research**: Citation extraction, topic clustering, reading status
- **Media**: Timeline organization, mood/genre inference, EXIF metadata
- **Creative**: Version tracking, asset linking, format intelligence
- **Datasets**: Schema inference, sample previews, data provenance
- **Obsidian**: Knowledge graph analysis, tag networks, link mapping, frontmatter extraction

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

## 🔌 Plugin Architecture

**Automatic Plugin Management:** Collectivist automatically downloads and installs plugins as needed during first-run analysis. No manual plugin installation required!

**Available Plugins:**
- **repositories** - Git repository collections with metadata extraction and status tracking
- **obsidian** - Obsidian vault collections with rich knowledge graph metadata
- **documents** - Document collections with metadata extraction from PDFs, Office docs, and text files
- **media** - Media collections with metadata extraction from images, audio, and video files

**Plugin Discovery:** When you run `analyze`, Collectivist detects your collection type and automatically downloads the appropriate plugin from the remote registry.

**Custom Plugins:** Implement the `CollectionScanner` interface. Copy the template from `plugins/template/plugin_template.py` and modify existing plugins as references.

## 🔗 Workflow Stages

### Stage 1: Analyzer

Inspects directory structure and determines collection type.

```bash
python -m .collection analyze ~/repos
# Creates collection.yaml

# Force specific type
python -m .collection analyze ~/repos repositories
```

### Stage 2: Indexer

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

Transforms YAML index into formatted output artifact (markdown, html, etc).

```bash
python -m .collection render ~/repos
```

## Why This Approach?

General file organizers chase "never think about files again" but usually end up with mediocre generic sorting. Collectivist focuses on **intentional collections** where each item matters, enabling:

- **Depth over breadth**: Domain-specific intelligence instead of one-size-fits-all rules
- **Curation system**: Ongoing pattern learning and intelligent reorganization (standard level)
- **Deterministic outputs**: Pattern learning is persisted explicitly in schema and index files, preserving deterministic outputs given the same learned state
- **Documentation as artifact**: READMEs become real knowledge repositories

## 📅 Roadmap

### Complete: Minimal Level MVP
- **Zero-install drop-in system** - `.collection/` folder works anywhere
- **LLM-powered collection analysis** - Auto-detects repository, research, media, creative, dataset types
- **Domain-specific intelligence** - Git metadata, EXIF, citations, schema inference
- **Hybrid Python/shell outputs** - Beautiful CLI + multiple formats (MD, HTML, JSON)
- **Self-contained architecture** - All code + deps in one folder

### Next: Standard Level (Schema Evolution)
- **Vite + Vue frontend** - Modern web interface for schema evolution
- **FastAPI backend** - REST API + WebSocket real-time updates
- **Conservative schema evolution** - Curator analyzes → evolves schema only when necessary
- **2-phase curation** - Phase 1 analyzes effectiveness, Phase 2 designs evolution (opt-in)
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
