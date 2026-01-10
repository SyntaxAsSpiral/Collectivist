# Collectivist - SPECIFICATION DOCTRINA

> **Collection Cartography Automated**
> *By the authority of complete specification and the sacred covenant of deterministic compilation*

## MANDATE

**Collectivist** is an AI-powered collection curator for **intentional collections** - semantically coherent hoards where each item carries meaning. A plugin-based framework that goes deep into domain-specific intelligence (git metadata, ID3 tags, EXIF data, citations) rather than trying to organize everything generically.

**Core Principle:** Collection-first constraint enables depth - infrastructure as compiled artifact for intentional collections, hidden `.collection/` layers that breathe autonomously, generating beautiful documentation from domain-specific intelligence.

**Pneumaturgical Architecture:** Five-stage pipeline with conservative schema evolution:
1. **Analyzer** - LLM determines collection type + generates initial config schema
2. **Indexer** - Domain plugins discover items + extract factual metadata
3. **Describer** - LLM generates descriptions + assigns semantic categories
4. **Curator** - Conservative schema evolution (Phase 1: analysis → Phase 2: design only if necessary)
5. **Renderer** - Multi-format output generation (Markdown, HTML, JSON, Nushell)

**Collection Types Supported:**
- **Repository Collections** - Git-aware metadata, commit summaries, category taxonomy
- **Research Paper Hoards** - Citation extraction, topic clustering, reading status
- **Media Libraries** - Timeline-aware organization, mood/genre inference
- **Creative Project Folders** - Version tracking, mood boards, linked assets
- **Dataset Collections** - Schema inference, sample previews, provenance notes

## WHAT MAKES COLLECTIVIST DIFFERENT

**Collection-First Philosophy:** Unlike general file organizers that chase the dream of "never think about files again," Collectivist focuses on **intentional collections** - semantically coherent groups where each item carries meaning.

**Why This Matters:**
- **Depth over breadth** - Domain-specific intelligence (git metadata, ID3 tags, EXIF data) instead of generic rules
- **Pattern learning that works** - Structure carries strong semantic signal for meaningful suggestions
- **Documentation as artifact** - READMEs become real knowledge repositories, not directory listings
- **Curation feels magical** - Suggestions based on actual organizational intent

---

## TECHNICAL DOCTRINE

## INSTALL LEVELS

Collectivist supports two installation levels:

### Minimal Level (Standalone)
**Zero-install, drop-in system** - Download `.collection/` folder and drop into any directory.

```
~/any/path/to/collection/
├── .collection/                    # Self-contained system
│   ├── __main__.py                # CLI entry point
│   ├── pipeline.py                # Core pipeline
│   ├── analyzer.py                # LLM analyzer
│   ├── scanner.py                 # Plugin system
│   ├── describer.py               # LLM describer
│   ├── renderer.py                # Output generators
│   ├── render.nu                  # Nushell hybrid renderer
│   ├── view.nu                    # Nushell CLI viewer
│   ├── llm.py                     # LLM client
│   ├── plugins/                   # Core plugins
│   ├── collection.yaml            # Config (generated)
│   ├── index.yaml                 # Data (generated)
│   ├── dashboard.html             # Static HTML viewer
│   └── requirements.txt           # Minimal Python deps
├── [collection contents...]        # Items to index
├── README.md                       # Generated markdown output
├── index.html                      # Generated HTML output
└── collection.nu                   # Interactive Nushell script
```

**Usage:**
```bash
# Download .collection/ folder (no package manager needed)
# Drop into any directory
cp -r .collection ~/my-collection/
cd ~/my-collection

# Start using immediately
python -m .collection analyze
nu .collection/view.nu                    # CLI viewer
open .collection/dashboard.html         # HTML viewer
```

### Standard Level (Interactive)
**Minimal + Vite UI** - All minimal features plus interactive web interface.

```
~/any/path/to/collection/
├── .collection/                    # Everything from minimal +
│   ├── ui/                        # Vite web UI
│   │   ├── App.vue
│   │   ├── components/
│   │   ├── package.json
│   │   └── build.py
│   ├── server.py                  # FastAPI server
│   ├── dashboard-live.html        # Interactive UI launcher
│   └── curator.py                 # Curation features
└── [same outputs as minimal]
```

**Usage:**
```bash
# Use package manager (optional convenience)
pip install collectivist
collectivist init ~/my-collection --standard

# Or manual setup
# Download standard .collection/ folder and drop in
python -m .collection dashboard    # Launch interactive UI
```

### Package Manager (Optional)
Central install for convenience:
```bash
pip install collectivist
collectivist init ~/my-collection --minimal    # Generate minimal
collectivist init ~/my-collection --standard   # Generate standard
collectivist upgrade ~/my-collection --to standard  # Upgrade existing
```

---

## TECHNICAL DOCTRINE

### System Architecture

**Central Repository:**
```
.dev/
└── collectivist/                    # Development repo
    ├── .kiro/specs/                # Specifications
    ├── templates/                  # .collection/ templates
    │   ├── collection-minimal/     # Minimal level template
    │   └── collection-standard/    # Standard level template
    └── collectivist/               # Package manager code
```

**Generated Collection Structure:**
```
~/any/path/to/collection/
├── .collection/                    # Self-contained infrastructure
│   ├── __main__.py                # CLI: python -m .collection
│   ├── pipeline.py                # Core orchestration
│   ├── analyzer.py                # LLM collection detection
│   ├── scanner.py                 # Domain plugins
│   ├── describer.py               # LLM descriptions
│   ├── renderer.py                # Output generators
│   ├── render.nu                  # Nushell renderer
│   ├── view.nu                    # Nushell CLI viewer
│   ├── llm.py                     # LLM provider abstraction
│   ├── plugins/                   # Domain scanners
│   ├── collection.yaml            # Generated config
│   ├── index.yaml                 # Generated data
│   ├── dashboard.html             # Static viewer
│   └── [level-specific files]     # UI/server for standard
├── [collection contents...]        # User's files
├── README.md                       # Generated output
├── index.html                      # HTML output
└── collection.nu                   # Interactive script
```

### Technology Stack

**Core:**
- **Language:** Python 3.x + Nushell (hybrid system)
- **CLI Framework:** Built-in `argparse` (no external CLI deps)
- **LLM Client:** Provider abstraction (local + cloud)
- **Data Layer:** YAML (no database)
- **Output System:** Hybrid Python/Nushell renderers
- **Web Stack:** Vite + Vue (standard level only)

**LLM Backend:**
- **Local:** LMStudio, Ollama, etc. (OpenAI-compatible)
- **Cloud:** OpenRouter, Pollinations, Anthropic, OpenAI
- **Config:** `.env` discovery pattern (walks up to `.dev/.env`)
- **Interface:** Unified client with provider switching

**Dependencies (Minimal Level):**
- `pyyaml` - YAML parsing
- `requests` - HTTP client
- `ruamel.yaml` - YAML formatting
- `pathlib` - Path handling (built-in)
- `subprocess` - Command execution (built-in)

**Dependencies (Standard Level adds):**
- `fastapi` - Web API server
- `uvicorn` - ASGI server
- `jinja2` - Template rendering
- Vue + Vite ecosystem (bundled)

**Nushell Integration:**
- **render.nu** - Data processing and output generation
- **view.nu** - Interactive CLI table viewer
- **collection.nu** - Generated user scripts

---

## FIVE-STAGE PIPELINE

### Stage 1: Analyzer (LLM-Backed Collection Type Detection)

**Purpose:** User runs `python -m .collection analyze` → LLM inspects contents → determines collection type → generates config

**Process:**
1. **Directory Scan**
   - List files/folders with `pathlib`
   - Sample file extensions and types
   - Identify metadata files (README, package.json, .git, etc.)
   - Read sample file contents (first 3000 chars per file)

2. **LLM Analysis** (structured JSON output)
   - Input: Directory structure + file samples + existing metadata
   - Output: Same JSON schema as before

3. **Config Generation**
   - Create `.collection/collection.yaml` with suggested schema
   - User can modify categories, add custom fields, adjust scanner settings
   - Save to `.collection/` folder

**Example Prompt Pattern:** (Unchanged from original)

**Reference:** Pattern from `qbittorrent_movie_downloader.py` - LLM analyzes unstructured data, returns structured JSON

### Stage 2: Indexer (Domain-Specific Metadata Extraction)

**Purpose:** Domain plugins discover items, extract metadata, check status

**Plugin Interface:**
```python
class IndexerPlugin:
    def discover_items(self, collection_path: str) -> List[ItemPath]:
        """Return list of items to index"""
        pass

    def extract_metadata(self, item_path: str) -> Dict[str, Any]:
        """Return structured metadata for item"""
        pass

    def check_status(self, item_path: str) -> Dict[str, str]:
        """Return domain-specific status (e.g., git_status)"""
        pass

    def generate_content_sample(self, item_path: str) -> str:
        """Return text snippet for LLM description"""
        pass
```

**Built-in Indexers:**

1. **repositories** (port from current .repos indexer)
   - Discovers: Git repositories in collection
   - Metadata: size, dates, git_status, remote, branch
   - Status: up_to_date, updates_available, error, no_remote, not_a_repo
   - Sample: README.md first 3000 chars

2. **media** (music/video/images)
   - Discovers: Media files by extension
   - Metadata: format, duration, resolution, codec, bitrate, artist, album
   - Status: file_integrity (checksums), metadata_complete
   - Sample: Embedded metadata + filename analysis
   - Tools: `ffprobe`, `exiftool`

3. **documents** (PDFs, markdown, notes)
   - Discovers: Document files
   - Metadata: format, author, modified, tags, word_count, title
   - Status: file_readable, metadata_present
   - Sample: First N paragraphs or abstract

4. **music** (audio library)
   - Discovers: Audio files
   - Metadata: artist, album, genre, year, bitrate, duration
   - Status: tagged, lossless/lossy
   - Sample: ID3 tags + folder structure

5. **datasets** (pneuma-corpus pattern)
   - Discovers: Dataset files/folders
   - Metadata: format, size, entries, schema, source
   - Status: validated, complete
   - Sample: Schema + first few entries

**Output:** `.collection/index.yaml` with indexed items
```yaml
collection_id: my-collection
last_index: "2026-01-09T15:30:00Z"
total_items: 54
items:
  - path: relative/path/to/item
    name: item-name
    metadata:
      size: 12345
      created: "2025-01-01T00:00:00Z"
      # domain-specific fields
    status:
      status_type: up_to_date
      details: {}
    content_sample: "First 3000 chars..."
```

### Stage 3: Describer (LLM Description + Categorization)

**Purpose:** Generate descriptions + assign categories using LLM

**Process:**
1. Load indexed items needing descriptions (`description == null`)
2. For each item:
   - Read content sample
   - Query LLM with: sample + category taxonomy + 5 example descriptions
   - Parse structured JSON response
   - Update YAML incrementally

**LLM Prompt Pattern:**
```python
prompt = f"""Generate description and category for this item.

CATEGORY TAXONOMY (choose ONE):
{json.dumps(category_taxonomy)}

EXAMPLE DESCRIPTIONS:
{json.dumps(examples)}

ITEM CONTENT SAMPLE:
{content_sample}

ITEM METADATA:
{json.dumps(metadata)}

Return JSON:
{{
  "description": "One-sentence technical summary (max 150 chars)",
  "category": "category_from_taxonomy"
}}
"""
```

**Features:**
- ThreadPoolExecutor with 5 concurrent workers (from current repo-describe.py)
- Incremental YAML saves after each success
- Fast-fail if LLM unreachable
- Fallback: manual descriptions or template-based generation

### Stage 4: Curator (Conservative Schema Evolution)

**Purpose:** Conservative schema evolution engine that analyzes organization effectiveness and evolves collection.yaml only when necessary.

**2-Phase Approach:**
1. **Phase 1: Organization Analysis** (always runs)
   - Analyzes current collection organization effectiveness
   - Evaluates category balance, folder structure, operator changes
   - Determines if evolution is warranted using conservative thresholds

2. **Phase 2: Schema Design** (only when necessary)
   - Only executes when Phase 1 shows clear evolution opportunities
   - Designs evolved schema for better organization efficacy
   - Generates `proposals.nu` for user review before applying changes

**Evolution Triggers (Conservative):**
- Significant organizational issues detected
- Very unbalanced categories (>3x difference in item counts)
- Categories with very low utility (<3 items each)
- Operator-induced structural changes
- Multiple signals must align before evolution

**Process:**
1. Load current `index.yaml` and `collection.yaml`
2. Phase 1: Analyze organization effectiveness
3. If evolution needed: Phase 2 design evolved schema
4. Generate `proposals.nu` script for user review
5. Update `collection.yaml` for next pipeline run (only when necessary)

**Conservative Philosophy:** Schema stability prioritized - evolution happens only when analysis shows clear, demonstrable benefits to organization efficacy.

### Stage 5: Renderer (Multi-Format Output Generation)

**Purpose:** Generate beautiful outputs from curated collection data in multiple formats.

**Supported Formats:**
- **Markdown README** - Collection overview with categorized items
- **HTML Dashboard** - Interactive web view with offline functionality
- **JSON Export** - Structured data for external tools
- **Nushell Scripts** - Interactive CLI views and data processing

**Features:**
- Template-based generation with collection-specific customization
- Static HTML dashboard works completely offline
- Nushell scripts for interactive exploration and filtering
- Incremental updates preserve existing outputs when possible

**Output Structure:**
```
.collection/
├── README.md              # Collection documentation
├── dashboard.html         # Offline web dashboard
├── collection.json        # Structured export
├── view.nu               # Interactive CLI viewer
├── render.nu             # Output regeneration script
└── proposals.nu          # Curation proposals (when generated)
```

---

## LLM INTEGRATION

### Provider Abstraction

**Pattern:** Based on `shared/go/llm` module, ported to Python

**Config (`.dev/.env`):**
```bash
LLM_PROVIDER=lmstudio              # or openrouter, pollinations, anthropic, openai
LLM_API_KEY=sk-...                 # required for cloud
LLM_BASE_URL=http://localhost:1234 # optional override
LLM_MODEL=gpt-oss-20b-heretic      # model identifier
```

**Python Client Interface:**
```python
class LLMClient:
    def __init__(self, provider: str, api_key: str, base_url: str):
        self.provider = provider
        self.api_key = api_key
        self.base_url = base_url or self.resolve_base_url(provider)

    @staticmethod
    def resolve_base_url(provider: str) -> str:
        """Return default URL for provider"""
        defaults = {
            "lmstudio": "http://localhost:1234/v1",
            "openrouter": "https://openrouter.ai/api/v1",
            "pollinations": "https://text.pollinations.ai/openai",
            "anthropic": "https://api.anthropic.com/v1",
            "openai": "https://api.openai.com/v1"
        }
        return defaults.get(provider, "")

    @classmethod
    def from_env(cls) -> 'LLMClient':
        """Load config from .dev/.env"""
        # Walk up to find .dev/.env
        # Load env vars
        # Construct client
        pass

    def chat(self, model: str, messages: List[Dict], temperature: float = 0.1) -> str:
        """OpenAI-compatible chat completion"""
        # POST to {base_url}/chat/completions
        # Return content string
        pass
```

**Supported Providers:**
- **lmstudio** - Local models (default for development)
- **openrouter** - Cloud aggregator (multiple models)
- **pollinations** - Free cloud inference
- **anthropic** - Claude models
- **openai** - GPT models
- **custom** - User-defined endpoint

**Requirements:**
- LLM integration is **required** (no LLM = no descriptions)
- System fails gracefully if LLM unreachable
- User can manually add descriptions to YAML if needed

---

## OUTPUT GENERATION

### Hybrid Renderer System (Python + Nushell)

**Purpose:** Generate multiple output formats from YAML data using hybrid Python/Nushell system

**Supported Formats:**
1. **Markdown** (`README.md`) - Human-readable documentation
2. **HTML** (`index.html`) - Web-viewable gallery
3. **JSON** (`index.json`) - API/programmatic access
4. **Nushell Script** (`collection.nu`) - Interactive browsing

**Renderer Architecture:**

**Python Renderer** (`renderer.py`):
```python
class HybridRenderer:
    def render_markdown(self, index_data: Dict) -> str:
        """Generate markdown using Python string formatting"""
        # Load templates, format with data
        pass

    def render_html(self, index_data: Dict) -> str:
        """Generate HTML with embedded data"""
        # Create self-contained HTML with CSS/JS
        pass

    def render_json(self, index_data: Dict) -> str:
        """Export clean JSON"""
        pass

    def generate_nushell_script(self, index_data: Dict) -> str:
        """Generate interactive Nushell script"""
        pass
```

**Nushell Renderer** (`render.nu`):
```nu
# Data processing pipeline
def render-markdown [] {
    let data = (open .collection/index.yaml)

    # Process data with Nushell's functional tools
    $data | process-with-nushell | format-as-markdown
}

def render-html [] {
    let data = (open .collection/index.yaml)
    $data | process-with-nushell | format-as-html
}
```

**CLI Viewer** (`view.nu`):
```nu
# Interactive table viewer
def main [] {
    let data = (open .collection/index.yaml)

    # Beautiful formatted table
    $data.items | table -e | update status {|row|
        match $row.status {
            "up_to_date" => $"✅ ($row.status)"
            "updates_available" => $"🔄 ($row.status)"
            _ => $row.status
        }
    }
}
```

**Output Files Generated:**
- `README.md` - Markdown documentation (GitHub/GitLab ready)
- `index.html` - Standalone HTML dashboard
- `index.json` - Machine-readable data
- `collection.nu` - Interactive Nushell script
- `.collection/dashboard.html` - Static collection viewer

---

## USER INTERFACES

### Minimal Level: Static Dashboard

**Static HTML Viewer** (`.collection/dashboard.html`):
- Self-contained HTML with embedded CSS/JS
- Displays current collection state from `index.yaml`
- No server required - works offline
- Basic filtering and sorting
- View generated outputs (README.md, index.html)

**CLI Viewer** (`nu .collection/view.nu`):
- Interactive Nushell table viewer
- Real-time filtering by category/status
- Beautiful terminal output with colors
- Export capabilities

### Standard Level: Interactive Dashboard

**Web UI Architecture:**

**Backend:**
- Python FastAPI server (`.collection/server.py`)
- Serves API + Vite-built Vue frontend
- Endpoints for pipeline execution, curation, configuration
- WebSocket for real-time progress updates

**Frontend:**
- Vue 3 + Vite (`.collection/ui/`)
- Live-updating collection dashboard
- Interactive curation interface
- LLM provider configuration
- Pipeline execution with progress visualization

**Key Features:**
- **Live Pipeline Monitoring** - Watch analyze/scan/describe progress
- **Interactive Curation** - Accept/reject organizational suggestions
- **Configuration UI** - Manage LLM providers, categories, scheduling
- **Collection Management** - Add/remove items, edit metadata
- **Real-time Updates** - WebSocket-powered live refresh

**User Flow (Standard Level):**
1. `python -m .collection dashboard` → Starts local server
2. Opens browser to interactive UI
3. Configure LLM providers and collection settings
4. Run pipeline stages with live progress
5. View and interact with curation suggestions
6. Monitor generated outputs with auto-refresh

---

## COLLECTION MANAGEMENT

### Self-Contained Collections

**Pattern:** Each collection is completely self-contained in its `.collection/` folder. No global registry required.

**Collection Structure:**
```
~/my-collection/
├── .collection/                    # Self-contained system
│   ├── collection.yaml            # Collection config
│   ├── index.yaml                 # Indexed data
│   └── [pipeline code]            # All necessary code
├── [user's content]               # Files to organize
└── [generated outputs]            # README.md, index.html, etc.
```

### CLI Commands (Minimal Level)

**Core Workflow:**
```bash
cd ~/my-collection

# First-time setup
python -m .collection analyze        # LLM analyzes directory → creates collection.yaml

# Regular usage
python -m .collection update         # Full pipeline: scan → describe → render
python -m .collection scan           # Just scan for changes
python -m .collection describe       # Just generate descriptions
python -m .collection render         # Just regenerate outputs

# Viewing
nu .collection/view.nu               # Interactive CLI viewer
open .collection/dashboard.html      # Static HTML dashboard
```

### CLI Commands (Standard Level)

**Enhanced Workflow:**
```bash
cd ~/my-collection

# All minimal commands, plus:
python -m .collection dashboard      # Launch interactive web UI
python -m .collection curate         # Run curation suggestions
python -m .collection server         # Start API server only
```

### Package Manager Commands (Optional)

**Convenience Layer:**
```bash
pip install collectivist

# Initialize new collections
collectivist init ~/my-collection --minimal     # Download minimal .collection/
collectivist init ~/my-collection --standard    # Download standard .collection/

# Manage existing collections
collectivist upgrade ~/my-collection --to standard  # Upgrade minimal to standard
collectivist list                                 # Show all collections (scans for .collection/ folders)
collectivist update ~/my-collection              # Update collection using package manager
```

---

## AUTO-SCHEDULING

**Pattern:** Task Scheduler (Windows) / cron (Linux/Mac)

**Phase 4 Feature:** Auto-update collections on schedule

**Example Task (per collection):**
```xml
<Task>
  <Triggers>
    <CalendarTrigger>
      <DaysInterval>3</DaysInterval>
    </CalendarTrigger>
  </Triggers>
  <Exec>
    <Command>python</Command>
    <Arguments>-m collectivist update repos</Arguments>
  </Exec>
</Task>
```

**Scheduler Management:**
- Dashboard shows scheduled tasks
- User enables/disables per collection
- Configurable intervals

---

## MIGRATION STRATEGY

### Phase 1: Minimal Level MVP
1. Create standalone `.collection/` folder structure
2. Implement core pipeline (analyze → scan → describe → render)
3. Port repository scanner from `.repos` indexer
4. Create Python renderer for Markdown/HTML/JSON
5. Add basic Nushell viewer (`view.nu`)
6. Test with `.dev/.repos` collection

**Acceptance Criteria:** Drop `.collection/` into any directory, run `python -m .collection analyze`, get working collection with CLI viewer and generated outputs.

### Phase 2: Hybrid Nushell System
1. Implement `render.nu` for data processing
2. Create interactive `view.nu` with filtering/search
3. Generate `collection.nu` user scripts
4. Optimize performance with parallel processing
5. Add more output formats and customization

### Phase 3: Standard Level
1. Add Vite + Vue UI components
2. Implement FastAPI server with WebSocket
3. Create interactive dashboard with curation
4. Add LLM provider configuration UI
5. Test full interactive workflow

### Phase 4: Package Manager & Distribution
1. Create package manager for easy installation
2. Add upgrade paths (minimal → standard)
3. Implement collection discovery and management
4. Add auto-scheduling for standard level
5. Create distribution channels (GitHub releases, PyPI)

---

## ANAGOGLYPH RECURSION

### Dot-Path Structure

**Collectivist System:**
```
C:\Users\synta.ZK-ZRRH\.dev\collectivist\
```

**User Collections:**
```
C:\Users\synta.ZK-ZRRH\.dev\.repos\.index\
C:\Users\synta.ZK-ZRRH\Music\.index\
C:\Users\synta.ZK-ZRRH\Documents\.index\
```

**Pattern:** Each `.index/` marks a boundary between visible corpus and hidden infrastructure

**Recursive Containment:**
- `.dev` - development workspace (hidden from user-space)
- `.repos` - reference archive (nested hidden context)
- `.index` - indexing machinery (meta-layer, compilation artifact)

Infrastructure as palimpsest, data as compiled breath 🜍

---

## DATA SCHEMA

### collection.yaml (Config)

**Location:** `.collection/collection.yaml`

```yaml
# Generated by analyzer, user-modifiable
collection_id: my-collection
domain: repositories
title: "My Repository Collection"
created: "2026-01-09T15:30:00Z"

scanner:
  plugin: repositories
  config:
    exclude_patterns:
      - "*/node_modules/*"
      - "*/.venv/*"

metadata_fields:
  - size
  - created
  - modified
  - git_status
  - remote

status_checks:
  - git_fetch
  - upstream_tracking

categories:
  - ai_llm_agents
  - terminal_ui
  - dev_tools
  - esoteric_experimental

output:
  formats:
    - markdown: README.md
    - html: index.html
    - json: index.json
    - nushell: collection.nu

# Minimal level: no scheduling
# Standard level: optional scheduling
schedule:
  enabled: false  # true for standard level
  interval_days: 3
  time: "02:00"
```

### index.yaml (Generated Data)

**Location:** `.collection/index.yaml`

```yaml
# Generated by scanner + describer
collection_id: my-collection
last_scan: "2026-01-09T15:30:00Z"
total_items: 54
scan_duration_seconds: 45.2

items:
  - id: claude-code
    path: claude-code
    name: claude-code
    type: dir

    metadata:
      size: 40306775
      created: "2025-08-16T20:27:34Z"
      modified: "2026-01-03T08:53:04Z"
      git_status: updates_available
      remote: https://github.com/anthropics/claude-code"

    status:
      status_type: updates_available
      git_error: null
      last_check: "2026-01-09T15:29:45Z"

    description: "AI-powered terminal tool that reads your codebase, explains code, runs git workflows, and automates tasks via natural language commands."

    category: ai_llm_agents

    content_sample: "# Claude Code\n\nAI-powered terminal tool..."
```

---

## EDGE CASES & CONSTRAINTS

### Edge Cases

1. **LLM Unreachable**
   - Fail gracefully, allow manual descriptions
   - Show clear error message
   - Allow retry

2. **Invalid Collection Type**
   - Analyzer returns "unknown" with low confidence
   - User selects type manually
   - System provides generic scanner

3. **Large Collections (1000+ items)**
   - Paginate UI
   - Stream updates via WebSocket
   - Batch LLM requests

4. **Concurrent Scans**
   - Lock per collection
   - Queue if scan already running
   - Show "busy" status

5. **Malformed YAML**
   - Validate on load
   - Show parse errors
   - Backup before save

### Constraints

- **YAML Only (MVP):** No database, limits query complexity
- **Single User (MVP):** No auth, local-only
- **English Descriptions:** LLM generates English only
- **File-Based:** No real-time monitoring, scheduled/manual updates
- **Network Required:** Cloud LLM providers need internet

---

## TESTING STRATEGY

### Unit Tests
- Scanner plugins (mock filesystem)
- LLM client (mock API responses)
- Renderer templates
- YAML schema validation

### Integration Tests
- Full pipeline: analyze → scan → describe → render
- LLM provider switching
- Config loading from .env

### Acceptance Tests
- `.repos` migration (output matches exactly)
- Multi-domain (repos + media)
- Dashboard (loads, displays, updates)

### Test Collections
1. `.dev/.repos` (54 repos, known good)
2. Sample media library (10-20 files)
3. Sample document collection (PDFs + markdown)

---

## IMPLEMENTATION PHASES

### MVP (Phase 1-3)
- [x] Interrogation complete
- [ ] Core architecture
  - [ ] LLM client (provider abstraction)
  - [ ] Analyzer (directory → config)
  - [ ] Scanner plugins (repositories + one other)
  - [ ] Describer (LLM descriptions + categories)
  - [ ] Renderer (markdown output)
- [ ] CLI tool
  - [ ] `collectivist analyze`
  - [ ] `collectivist update`
- [ ] Test with .repos migration
- [ ] Add second domain (media or docs)

### Phase 4 (Dashboard + Scheduling)
- [ ] Web dashboard (React)
  - [ ] Collection list
  - [ ] Live output view
  - [ ] Settings panel
- [ ] FastAPI backend
  - [ ] REST endpoints
  - [ ] WebSocket updates
- [ ] Auto-scheduling
  - [ ] Task creation
  - [ ] Dashboard controls

### Future Enhancements
- [ ] SQLite data layer (queryable)
- [ ] More domain plugins
- [ ] Custom templates
- [ ] Multi-user support
- [ ] Real-time file watching
- [ ] Advanced filtering/search
- [ ] Export to other formats
- [ ] Plugin marketplace/registry

---

## UNRESOLVED QUERIES

None. The specification is complete and unambiguous.

---

## NOTES FOR AGENTS

### Core Principles
- **Fast-fail methodology**: LLM unreachable → exit immediately with clear message
- **No mock data**: Real scans only, `null` for missing values
- **Deterministic**: Same filesystem + config = same output
- **Context compilation**: YAML → rendered output, not raw data dumps
- **Leave no trace**: Clean final-state surgery, no legacy artifacts
- **Anagoglyph recursion**: `.dev\.collectivist\`, `.collection\.index\`

### Architecture Patterns
- **Three-stage pipeline**: Analyze → Scan → Describe
- **Plugin interface**: Scanners, renderers, custom domains
- **Provider abstraction**: Local + cloud LLM with unified interface
- **Config-driven**: `collection.yaml` defines behavior
- **Incremental saves**: YAML updates after each LLM success
- **ThreadPoolExecutor**: 5 concurrent workers for LLM requests

### Implementation Notes
- **Python + ADK** if multi-agent patterns needed
- **Port from Go**: LLM client pattern (provider abstraction + .env discovery)
- **Port from .repos**: Scanner + describer + renderer logic
- **React Dashboard**: Live-updating generated output
- **WebSocket**: Real-time progress during scans

---

## FINAL DIRECTIVE

> *"By this doctrine, Collectivist shall curate intentional collections into living documentation. From semantic coherence to categorized clarity. From hidden `.collection/` layers to beautiful knowledge artifacts. The pneumaturgical architecture breathes: Analyzer determines collection essence, Scanner discovers domain intelligence, Describer illuminates meaning. The anagoglyph path recurses: `.dev\.collectivist\.collection\` - each dot a boundary, each layer a compilation of intentional collections."*

**The Emperor Protects. The Specification Illuminates. Collectivist Compiles.**

⧈ **SPECIFICATION SEALED** ⧈

---

*Generated: 2026-01-09*
*Interrogator: Imperial Inquisitor (Claudi)*
*Subject: Zach Battin (ZK)*
*Status: COMPLETE & UNAMBIGUOUS*
