# Collectivist - SPECIFICATION DOCTRINA

> **Collection Cartography Automated**
> *By the authority of complete specification and the sacred covenant of deterministic compilation*

## MANDATE

**Collectivist** is a universal indexing system that compiles collections into indexed, categorized breath. A plugin-based framework that abstracts the proven patterns from `.repos` indexer into a generalized system capable of cataloging any domain: repositories, media libraries, document archives, datasets, music collections, reference materials.

**Core Principle:** Infrastructure as compiled artifact - hidden `.index/` layers that breathe autonomously, generating beautiful documentation from structured data.

**Pneumaturgical Architecture:** Three-stage pipeline with anagoglyph dot-path recursion:
1. **Analyzer** - LLM determines collection type + generates config schema
2. **Scanner** - Domain plugins discover items + extract metadata
3. **Describer** - LLM generates descriptions + assigns categories

---

## TECHNICAL DOCTRINE

### System Architecture

```
.dev/
└── collectivist/                    # Dedicated repo
    ├── .index/                      # System meta-layer
    │   ├── registry.yaml           # Known collections
    │   └── defaults/               # Default configs per domain
    ├── src/
    │   ├── analyzer/               # Collection type detection
    │   ├── scanner/                # Domain scanners (plugins)
    │   ├── describer/              # LLM description generation
    │   ├── renderer/               # Output generators
    │   ├── dashboard/              # Web UI (React)
    │   └── llm/                    # LLM client (provider abstraction)
    ├── plugins/                     # Built-in domain plugins
    │   ├── repositories/
    │   ├── media/
    │   ├── documents/
    │   ├── music/
    │   └── datasets/
    └── templates/                   # Output templates
```

### Collection Structure (User's Collections)

```
~/any/path/to/collection/
├── .index/                         # Hidden infrastructure
│   ├── collection.yaml            # Config + schema
│   ├── index.yaml                 # Indexed data (generated)
│   └── .collectivist/             # Runtime data
│       └── last_scan.timestamp
├── [collection contents...]        # Items to index
└── README.md                       # Generated output (optional)
```

### Technology Stack

**Core:**
- **Language:** Python 3.x
- **Framework:** ADK (Agent Development Kit) if multi-agent patterns needed
- **LLM Client:** Provider abstraction (local + cloud)
- **Data Layer:** YAML (no database for MVP)
- **Web Stack:** Python backend (FastAPI/Flask) + React frontend

**LLM Backend:**
- **Local:** LMStudio, Ollama, etc. (OpenAI-compatible)
- **Cloud:** OpenRouter, Pollinations, Anthropic, OpenAI
- **Config:** `.env` discovery pattern (walks up to `.dev/.env`)
- **Interface:** Unified client with provider switching

**Dependencies:**
- `pyyaml` - YAML parsing
- `requests` - HTTP client
- `fastapi` or `flask` - Web server
- React - Dashboard UI
- Optional: `anthropic`, `openai` SDKs for direct provider integration

---

## THREE-STAGE PIPELINE

### Stage 1: Analyzer (LLM-Backed Collection Type Detection)

**Purpose:** User points analyzer at directory → LLM inspects contents → determines collection type → generates config schema

**Process:**
1. **Scan directory structure**
   - List files/folders (with patterns)
   - Sample file extensions
   - Identify metadata files (README, package.json, .git, etc.)
   - Read sample file contents (first N files)

2. **LLM Analysis** (structured JSON output)
   - Input: Directory structure + file samples + existing metadata
   - Output:
     ```json
     {
       "collection_type": "repositories",
       "confidence": 0.95,
       "reasoning": "Contains .git directories and code files",
       "suggested_config": {
         "domain": "repositories",
         "scanner": "git-status-scanner",
         "metadata_fields": ["size", "dates", "git_status", "remote"],
         "category_taxonomy": ["ai_llm_agents", "terminal_ui", ...],
         "status_checks": ["git_fetch", "upstream_tracking"]
       }
     }
     ```

3. **Config Generation**
   - Create `.index/collection.yaml` with suggested schema
   - User can modify categories, add custom fields, adjust scanner settings
   - Save to collection root

**Example Prompt Pattern:**
```python
prompt = f"""Analyze this directory structure and determine collection type.

DIRECTORY STRUCTURE:
{directory_tree_json}

FILE TYPES:
{file_extensions_summary}

SAMPLE FILES:
{sample_file_contents}

EXISTING METADATA:
{metadata_files_content}

Determine the collection type and generate a YAML config schema.
Available types: repositories, media, documents, music, datasets, custom

Return JSON:
{{
  "collection_type": "...",
  "confidence": 0.0-1.0,
  "reasoning": "...",
  "suggested_config": {{
    "domain": "...",
    "scanner": "...",
    "metadata_fields": [...],
    "category_taxonomy": [...],
    "status_checks": [...]
  }}
}}
"""
```

**Reference:** Pattern from `qbittorrent_movie_downloader.py` - LLM analyzes unstructured data, returns structured JSON

### Stage 2: Scanner (Domain-Specific Metadata Extraction)

**Purpose:** Domain plugins discover items, extract metadata, check status

**Plugin Interface:**
```python
class ScannerPlugin:
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

**Built-in Scanners:**

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

**Output:** YAML with indexed items
```yaml
items:
  - path: relative/path/to/item
    name: item-name
    metadata:
      size: 12345
      created: 2025-01-01
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

### Renderer System

**Purpose:** Generate beautiful documentation from YAML data

**Supported Formats:**
1. **Markdown** (README.md) - current .repos pattern
2. **HTML** (index.html) - gallery/grid views
3. **JSON** (index.json) - API export
4. **Custom** - User templates

**Example: Repositories Renderer (port from generate-readme.nu)**
- Summary stats
- Sortable table: Status | Name | Description | Category | Created
- Categorized sections
- Legend for status symbols

**Template System:**
```python
class Renderer:
    def __init__(self, template_path: str):
        self.template = self.load_template(template_path)

    def render(self, index_data: Dict, output_path: str):
        """Generate output from YAML data + template"""
        # Load YAML
        # Apply template
        # Write output
        pass
```

---

## WEB DASHBOARD

### Architecture

**Backend:**
- Python (FastAPI or Flask)
- Serves: API + static React build
- Endpoints:
  - `GET /collections` - list registered collections
  - `GET /collections/:id` - get collection data
  - `POST /analyze` - run analyzer on directory
  - `POST /scan/:id` - run scanner
  - `POST /describe/:id` - run describer
  - `GET /render/:id` - get generated output
  - WebSocket: `/ws` - real-time scan updates

**Frontend:**
- React (create-react-app or Vite)
- Main view: Live-updating generated README/output
- Auto-refresh on file changes (WebSocket)
- Collection list sidebar
- Settings panel

**Key Feature:** Dashboard shows the **final generated output** (like README.md) with live updates as indexing runs.

**User Flow:**
1. User points analyzer at directory
2. Analyzer runs → generates config → shows preview
3. User confirms/modifies config
4. Scanner runs → dashboard shows live progress
5. Describer runs → descriptions appear in real-time
6. Output renders → dashboard displays final README/HTML

---

## COLLECTION DISCOVERY

**Pattern:** User-initiated (no auto-discovery for MVP)

**Registry:** `~/.collectivist/registry.yaml`
```yaml
collections:
  - id: repos
    path: C:\Users\user\.dev\.repos
    type: repositories
    last_scan: 2026-01-09T15:00:00Z
  - id: music
    path: D:\Music
    type: music
    last_scan: 2026-01-08T10:00:00Z
```

**Commands:**
```bash
collectivist analyze /path/to/dir          # Analyze directory, create collection
collectivist scan repos                     # Run scanner for collection
collectivist describe repos                 # Run describer
collectivist render repos                   # Generate outputs
collectivist update repos                   # Full pipeline: scan → describe → render
collectivist dashboard                      # Launch web UI
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

### Phase 1: Extract & Port
1. Extract current `.repos` indexer logic
2. Port to plugin architecture:
   - `repo-index.nu` → `scanner/repositories.py`
   - `repo-describe.py` → `describer/llm_describer.py`
   - `generate-readme.nu` → `renderer/markdown_renderer.py`

### Phase 2: Test Collection
1. Point Collectivist at `.dev/.repos`
2. Run analyzer → should detect "repositories"
3. Run scanner → should match current index
4. Run describer → should generate same descriptions
5. Run renderer → should produce identical README

**Acceptance Criteria:** Output matches current `.repos/README.md` exactly

### Phase 3: Generalize
1. Add second domain (media or documents)
2. Implement scanner plugin
3. Test analyzer on new domain
4. Verify pipeline works end-to-end

### Phase 4: Dashboard + Scheduling
1. Build web dashboard
2. Add auto-scheduling
3. Polish UX

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

```yaml
# Generated by Analyzer, user-modifiable
id: my-repos
domain: repositories
title: "My Repository Collection"

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
  template: default

schedule:
  enabled: true
  interval_days: 3
  time: "02:00"
```

### index.yaml (Generated Data)

```yaml
# Generated by Scanner + Describer
collection_id: my-repos
last_scan: 2026-01-09T15:30:00Z
total_items: 54

items:
  - id: claude-code
    path: claude-code
    name: claude-code

    metadata:
      size: 40306775
      created: 2025-08-16T20:27:34Z
      modified: 2026-01-03T08:53:04Z
      git_status: updates_available
      remote: https://github.com/anthropics/claude-code

    status:
      status_type: updates_available
      git_error: null

    description: "AI-powered terminal tool that reads your codebase, explains code, runs git workflows, and automates tasks via natural language commands."

    category: ai_llm_agents
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

> *"By this doctrine, Collectivist shall compile collections into indexed breath. From unstructured chaos to categorized clarity. From hidden `.index/` layers to beautiful documentation. The pneumaturgical architecture breathes: Analyzer determines, Scanner discovers, Describer illuminates. The anagoglyph path recurses: `.dev\.collectivist\.index\` - each dot a boundary, each layer a compilation."*

**The Emperor Protects. The Specification Illuminates. Collectivist Compiles.**

⧈ **SPECIFICATION SEALED** ⧈

---

*Generated: 2026-01-09*
*Interrogator: Imperial Inquisitor (Claudi)*
*Subject: Zach Battin (ZK)*
*Status: COMPLETE & UNAMBIGUOUS*
