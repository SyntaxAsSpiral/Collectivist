# Collectivist - Design Document

## Overview

**Collectivist** is an AI-powered collection curator for **intentional collections** - semantically coherent hoards where each item carries meaning. A plugin-based framework that goes deep into domain-specific intelligence (git metadata, ID3 tags, EXIF data, citations) rather than trying to organize everything generically.

**Not a general file organizer.** Collectivist shines on collections you care about enough to give them structure and meaning. For Downloads auto-sorting, check out llama-fs or Local-File-Organizer.

**Collection Types Supported:**
- **Repository Collections** - Git-aware metadata, commit summaries, category taxonomy
- **Research Paper Hoards** - Citation extraction, topic clustering, reading status
- **Media Libraries** - Timeline-aware organization, mood/genre inference
- **Creative Project Folders** - Version tracking, mood boards, linked assets
- **Dataset Collections** - Schema inference, sample previews, provenance notes

**Core Architecture:** Collection-first constraint enables depth - infrastructure as compiled artifact for intentional collections, hidden `.collection/` layers that breathe autonomously, generating beautiful documentation from domain-specific intelligence.

## What Collectivist Is Not

**Not a general file organizer.** Collectivist is not designed for:
- Downloads folders with random files
- Desktop cleanup of miscellaneous documents
- Automatic organization of entire filesystems
- Handling infinite edge cases (temp files, caches, logs)

**For general file organization:** Check out llama-fs, Local-File-Organizer, or Sparkle.

**What Collectivist excels at:** Collections you care about enough to give them structure and meaning.

## What Makes Collectivist Different

**Collection-First Philosophy:** Unlike general file organizers that chase the dream of "never think about files again," Collectivist focuses on **intentional collections** - semantically coherent groups where each item carries meaning.

**Why This Matters:**
- **Depth over breadth** - Domain-specific intelligence (git metadata, ID3 tags, EXIF data) instead of generic rules
- **Pattern learning that works** - Structure carries strong semantic signal for meaningful suggestions
- **Documentation as artifact** - READMEs become real knowledge repositories, not directory listings
- **Curation feels magical** - Suggestions based on actual organizational intent

## Architecture

## INSTALL LEVELS ARCHITECTURE

### Two-Tier System

**Minimal Level** (Standalone, Zero-Install):
```
.collection/                         # Self-contained drop-in system
├── __main__.py                     # CLI entry point: python -m .collection
├── pipeline.py                     # Core orchestration
├── analyzer.py                     # LLM collection detection
├── scanner.py                      # Plugin system
├── describer.py                    # LLM descriptions
├── renderer.py                     # Output generators
├── render.nu                       # Nushell hybrid renderer
├── view.nu                         # CLI viewer
├── llm.py                          # LLM client abstraction
├── plugins/                        # Domain plugins
│   ├── repositories.py             # Git repo scanner
│   └── generic.py                  # Fallback scanner
├── collection.yaml                 # Generated config
├── index.yaml                      # Generated data
├── dashboard.html                  # Static HTML viewer
└── requirements.txt                # Minimal deps
```

**Standard Level** (Interactive):
```
.collection/                         # Everything above +
├── ui/                             # Vite + Vue frontend
│   ├── App.vue
│   ├── components/
│   ├── package.json
│   └── build.py                     # Generates dashboard-live.html
├── server.py                       # FastAPI backend
├── dashboard-live.html             # Interactive UI launcher
└── curator.py                      # Curation features
```

**Package Manager** (Optional Convenience):
```
collectivist/                       # Central install (pip install collectivist)
├── templates/                      # .collection/ folder templates
│   ├── collection-minimal/         # Minimal level template
│   └── collection-standard/        # Standard level template
├── collectivist/                   # Package manager code
│   ├── __main__.py
│   ├── init.py                     # Collection initialization
│   ├── upgrade.py                  # Level upgrades
│   └── discover.py                 # Collection discovery
└── pyproject.toml
```

### User Collection Structure

**Minimal Level:**
```
~/my-collection/
├── .collection/                    # Self-contained system
├── [user's content files]          # Files to organize
├── README.md                       # Generated markdown
├── index.html                      # Generated HTML
├── index.json                      # Generated JSON
└── collection.nu                   # Interactive script
```

**Standard Level:**
```
~/my-collection/
├── .collection/                    # Interactive system
├── [user's content files]          # Files to organize
└── [same generated outputs]
```

### Five-Stage Pipeline

#### Stage 1: Analyzer
- **Purpose:** LLM-backed collection type detection
- **Input:** Directory structure, file samples, metadata
- **Output:** `.collection/collection.yaml` configuration
- **Implementation:** `analyzer.py` - ✅ COMPLETE

**Process:**
1. Scan directory structure using `pathlib`
2. Sample files and extract metadata patterns
3. Query LLM with structured prompt for type detection
4. Generate configuration with categories and scanner settings
5. Save to `.collection/collection.yaml`

#### Stage 2: Indexer
- **Purpose:** Domain-specific metadata extraction
- **Input:** Collection path and configuration
- **Output:** `.collection/index.yaml` with item metadata
- **Implementation:** Plugin system - ✅ COMPLETE (repositories only)

**Process:**
1. Load indexer plugin based on collection type
2. Discover items using domain-specific logic
3. Extract metadata (size, dates, domain-specific fields)
4. Check status (git status, file integrity, etc.)
5. Save structured YAML to `.collection/index.yaml`

#### Stage 3: Describer
- **Purpose:** LLM description and categorization
- **Input:** Items needing descriptions from index
- **Output:** Updated index with descriptions and categories
- **Implementation:** `describer.py` - ✅ COMPLETE

**Process:**
1. Load items where `description` is missing/null
2. Use ThreadPoolExecutor for concurrent LLM requests (5 workers)
3. Generate descriptions using content samples and category taxonomy
4. Incremental YAML saves after each success
5. Fast-fail if LLM unreachable (graceful degradation)

#### Stage 4: Curator (Conservative Schema Evolution)
- **Purpose:** Analyze organization effectiveness and evolve schema only when necessary
- **Input:** Current index and collection configuration
- **Output:** Updated collection.yaml (only when evolution warranted)
- **Implementation:** `curator.py` - ✅ COMPLETE

**2-Phase Process:**
1. **Phase 1: Organization Analysis** - Always runs to evaluate current effectiveness
2. **Phase 2: Schema Design** - Only executes when evolution is clearly needed

#### Stage 5: Renderer (Multi-Format Output Generation)
- **Purpose:** Generate beautiful outputs in multiple formats from curated data
- **Input:** Complete index with descriptions and categories
- **Output:** README.md, dashboard.html, collection.json, view.nu scripts
- **Implementation:** `renderer.py` + Nushell scripts - ✅ COMPLETE

## Self-Healing Curation System

### Pneumaturgical Organizational Loop

Collectivist implements a **self-organizing compilation loop** where structure and index co-evolve in perfect harmony. The system becomes a living organizational substrate that breathes with your collection's growth.

**The Perfect Loop:**
```
Collection Growth → Curation → Structure Changes → Re-indexing → New Patterns → Curation...
```

### Zero-Friction Interaction

**Natural Filesystem Operations:**
- **Add Content:** Drop new files/folders → system automatically detects, describes, categorizes
- **Delete Folders:** Remove unwanted directories → index cleanly heals, removes references
- **Move Items:** Reorganize structure → system learns patterns, updates paths, preserves metadata
- **Rename Folders:** Change organization → system adapts terminology, maintains consistency

**Self-Healing Architecture:**
```python
class SelfHealingScanner:
    def heal_index(self, current_items: List[Item], filesystem_state: Dict):
        """Heal index to match current filesystem reality"""
        
        # Detect deletions - remove from index gracefully
        missing_items = self.find_missing_items(current_items)
        
        # Detect additions - add with inherited context
        new_items = self.discover_new_items(filesystem_state)
        
        # Detect moves - preserve metadata, update paths
        moved_items = self.detect_moves(current_items, filesystem_state)
        
        # Heal gracefully - no errors, just adaptation
        return self.merge_changes(current_items, missing_items, new_items, moved_items)
```

### Intelligent Context Inheritance

**Structural Awareness:**
- New items inherit organizational context from their location
- Folder hierarchy informs both content analysis and categorization
- System learns your organizational patterns and naming conventions

**Enhanced Item Metadata:**
```python
@dataclass
class CollectionItem:
    # ... existing fields ...
    structural_category: Optional[str]    # Inferred from folder location
    organizational_depth: int             # Depth in folder hierarchy
    folder_context: Dict[str, Any]        # Parent folder metadata
    organizational_intent: Optional[str]  # Learned from patterns
```

**Context-Aware Categorization:**
```yaml
# Items get both content-based AND location-based intelligence
- short_name: new-ai-tool
  path: ai-llm-agents/experimental/new-ai-tool
  category: ai_llm_agents              # From LLM content analysis
  structural_category: experimental    # From folder location
  organizational_intent: early_stage   # From learned patterns
  folder_context:
    depth: 2
    parent_folder: experimental
    graduation_pattern: "experimental → production after 3 months"
```

### Structure-Based Pattern Learning

**No External Memory Required:**
- **Filesystem structure** = organizational memory encoded in reality
- **Index metadata** = context about placement decisions that worked
- **Pattern analysis** = intelligence extracted from existing structure
- **Placement suggestions** = evolution based on structural reality

**Learning from Structure:**
```python
def _learn_from_structure(collection_root: Path, collection_config: Dict[str, Any]):
    """Extract organizational patterns from existing filesystem structure"""
    
    # Load existing index to understand current categorization
    index_data = load_collection_index(collection_root)
    
    # Extract category → folder mapping from filesystem reality
    category_folders = {}
    for item in index_data:
        if item.category and item.path:
            folder_name = Path(item.path).relative_to(collection_root).parts[0]
            category_folders.setdefault(item.category, {})[folder_name] = \
                category_folders[item.category].get(folder_name, 0) + 1
    
    # Analyze current folder hierarchy for organizational preferences
    folder_hierarchy = {}
    for folder in collection_root.iterdir():
        if folder.is_dir() and not folder.name.startswith('.'):
            folder_hierarchy[folder.name] = {
                'item_count': len(list(folder.rglob('*'))),
                'naming_style': detect_naming_convention(folder.name),
                'depth': calculate_folder_depth(folder)
            }
    
    # Structure IS the memory - return patterns extracted from reality
    return {
        'category_folders': category_folders,      # Where categories actually live
        'folder_hierarchy': folder_hierarchy,      # Current organizational structure
        'naming_conventions': extract_naming_patterns(folder_hierarchy),
        'depth_preferences': calculate_depth_preferences(folder_hierarchy)
    }
```

**Self-Reinforcing Intelligence:**
1. User organizes items naturally → structure reflects preferences
2. System analyzes structural reality → learns actual patterns from filesystem + index
3. New items suggested based on real patterns → structure evolves intelligently
4. Index mirrors evolved structure → memory encoded in filesystem reality

**No External Pattern Files:**
- No `.index/patterns.yaml` or separate pattern storage
- All organizational intelligence extracted from existing structure + index
- Placement suggestions based on "where do similar items actually live?"
- System learns by observing reality, not by maintaining separate memory

### Flexible Workflow Options

**Manual CLI Workflow (Default):**
- Pure manual control via CLI commands
- Run pipeline stages individually or together as needed
- No scheduling, no automatic operations
- Perfect for developers who want explicit control

**Scheduled Indexing (Optional):**
- Automatic pipeline runs on configurable intervals
- Standard indexing: scan → describe → render
- No organizational changes, just documentation updates
- Good for maintaining up-to-date documentation

**Organic Curation (Optional):**
- Includes new content processing and placement suggestions
- Structure-based pattern learning from filesystem reality
- Gentle organizational suggestions based on existing patterns
- Full pneumaturgical self-organizing workflow

### Configuration Levels

**collection.yaml scheduling options:**
```yaml
schedule:
  enabled: false                    # Default: manual only
  
  # Basic scheduling (when enabled: true)
  interval_days: 7
  operations: [scan, describe, render]
  
  # Organic curation (when enabled: "organic")
  operations: [process_new, scan, describe, render, suggest_curation]
  auto_file: false                  # Suggest only, never auto-move
  confidence_threshold: 0.8         # High threshold for any auto-operations
  
  # Advanced options
  detect_changes: true              # Monitor filesystem for changes
  change_threshold: 5               # Minimum changes to trigger run
```

**Three Workflow Modes:**
1. **Manual**: `schedule.enabled: false` - CLI only, no automation
2. **Scheduled**: `schedule.enabled: true` - regular indexing, no curation
3. **Organic**: `schedule.enabled: "organic"` - full self-organizing workflow

**Primary Scheduling Interface:**
- **Web UI**: Complete interface for non-terminal users (collection management, pipeline execution, scheduling, configuration)
- **CLI**: Power-user interface for terminal-inclined users and automation
- **Filesystem**: Natural content management (drop files, organize folders)

### Pure Pneumaturgical Flow

**Invisible Infrastructure:**
- Work with files naturally - add, delete, move, rename as needed
- Never think about "updating the index" or "maintaining the system"
- System continuously adapts to your changes and learns your patterns
- Beautiful documentation that reflects organizational reality

**Self-Healing Events:**
```python
# System emits gentle healing notifications
emitter.info("Detected 3 new items in ai-llm-agents/experimental/")
emitter.info("Healed 5 missing references from deleted folder")
emitter.info("Learned pattern: user prefers specific over generic categories")
emitter.success("Index healed - 47 items, 8 categories, all paths valid")
```

The collection becomes a **living organizational organism** that grows more intelligent and beautiful over time, with zero friction between human intent and system intelligence.

## Components and Interfaces

### LLM Provider Abstraction

**File:** `.index/llm.py`
**Status:** ✅ COMPLETE

```python
class LLMClient:
    def __init__(self, provider: ProviderType, api_key: str, base_url: str)
    def chat(self, model: str, messages: List[Message], **kwargs) -> str
    @classmethod
    def from_env(cls) -> 'LLMClient'
```

**Supported Providers:**
- Local: LMStudio, Ollama
- Cloud: OpenRouter, Pollinations, Anthropic, OpenAI
- Configuration via `.env` file with provider switching

### Plugin System

**File:** `.index/plugin_interface.py`
**Status:** ✅ COMPLETE

```python
class CollectionScanner(ABC):
    @abstractmethod
    def get_name(self) -> str
    @abstractmethod
    def detect(self, path: Path) -> bool
    @abstractmethod
    def scan(self, root_path: Path, config: Dict) -> List[CollectionItem]
    @abstractmethod
    def get_description_prompt_template(self) -> str
    @abstractmethod
    def get_content_for_description(self, item: CollectionItem) -> str
```

**Registry System:**
- `PluginRegistry` for plugin registration and discovery
- Auto-detection based on directory contents
- Extensible for new collection types

### Repository Scanner Plugin

**File:** `plugins/repository_scanner.py`
**Status:** ✅ COMPLETE

**Features:**
- Git status tracking (up_to_date, updates_available, error, no_remote, not_a_repo)
- README-based content sampling for LLM descriptions
- Category taxonomy for software projects
- Auto-pull support for repositories with updates

**Categories:**
- `phext_hyperdimensional` - Multi-dimensional text systems
- `ai_llm_agents` - AI agents and LLM infrastructure
- `terminal_ui` - Terminal UI frameworks and components
- `creative_aesthetic` - Art, music, visualization tools
- `dev_tools` - Development utilities and build tools
- `esoteric_experimental` - Experimental and occult systems
- `system_infrastructure` - System-level networking tools
- `utilities_misc` - General utilities and miscellaneous tools

## Data Models

### CollectionItem

```python
@dataclass
class CollectionItem:
    short_name: str              # Unique identifier
    type: str                    # Item type (dir, file, etc.)
    size: int                    # Size in bytes
    created: str                 # ISO timestamp
    modified: str                # ISO timestamp
    accessed: str                # ISO timestamp
    path: str                    # Full path
    description: Optional[str]   # LLM-generated description
    category: Optional[str]      # Assigned category
    metadata: Dict[str, Any]     # Domain-specific metadata
```

### Configuration Schema

**collection.yaml:**
```yaml
collection_type: repositories
name: my-repos
path: /path/to/collection
categories: [list of valid categories]
exclude_hidden: true
scanner_config: {}
```

**collection-index.yaml:**
```yaml
- short_name: item-name
  type: dir
  size: 12345
  created: "2026-01-09T15:30:00"
  modified: "2026-01-09T15:30:00"
  accessed: "2026-01-09T15:30:00"
  path: /full/path/to/item
  description: "LLM-generated description"
  category: "assigned_category"
  # Domain-specific metadata fields...
```

## User Interfaces

### Minimal Level: Static Dashboard

**Static HTML Viewer** (`.collection/dashboard.html`):
- Self-contained HTML with embedded CSS/JS
- Displays collection data from `index.yaml`
- No server required - works offline
- Basic filtering, sorting, and search
- Responsive design for different screen sizes

**CLI Viewer** (`view.nu`):
- Interactive Nushell table viewer
- Real-time filtering by category/status
- Beautiful terminal output with colors and icons
- Export capabilities to various formats

### Standard Level: Interactive Dashboard

### Backend Architecture (Standard Level)

**Technology:** FastAPI
**Status:** ❌ NOT IMPLEMENTED

**Required Endpoints:**
```python
# Collection Management
GET /api/collection                # Get current collection data
PUT /api/collection/config         # Update collection configuration

# Pipeline Operations
POST /api/analyze                  # Run analyzer
POST /api/scan                     # Run scanner
POST /api/describe                 # Run describer
POST /api/render                   # Generate outputs
POST /api/update                   # Full pipeline

# Curation (Standard Level)
GET /api/suggestions               # Get curation suggestions
POST /api/curate                   # Apply curation changes
GET /api/patterns                  # Get learned patterns

# Configuration
GET /api/config/llm                # Get LLM configuration
PUT /api/config/llm                # Update LLM settings
POST /api/config/llm/test          # Test LLM connection

# Real-time Updates
WebSocket /ws                      # Live progress and events
```

**Data Models:**
```python
class Collection(BaseModel):
    id: str
    name: str
    path: str
    type: str
    last_scan: Optional[datetime]
    status: str  # idle, scanning, describing, error

class ScanProgress(BaseModel):
    collection_id: str
    stage: str  # analyze, scan, describe, render
    progress: int  # 0-100
    current_item: Optional[str]
    message: str
```

### Frontend Architecture

**Technology:** Vite + React + TypeScript
**Status:** ❌ NOT IMPLEMENTED

**Required Components:**
```vue
<!-- Main Application -->
<App>
  <Sidebar>
    <CollectionStatus />
    <Navigation />
  </Sidebar>
  <MainContent>
    <DashboardView />
    <PipelineView />
    <ConfigView />
  </MainContent>
</App>

<!-- Dashboard View -->
<CollectionOverview />             <!-- Stats, recent activity -->
<ItemTable />                      <!-- Sortable, filterable table -->
<CategoryView />                   <!-- Grouped by categories -->
<StatusView />                     <!-- Grouped by status -->

<!-- Pipeline View -->
<PipelineRunner />                 <!-- Execute pipeline stages -->
<ProgressMonitor />                <!-- Real-time progress -->
<LogViewer />                      <!-- Execution logs -->

<!-- Configuration View -->
<LLMConfig />                      <!-- Provider selection, testing -->
<CategoryManager />                <!-- Edit categories -->
<SchedulingConfig />               <!-- Auto-update settings -->

<!-- Curation Features -->
<CurationSuggestions />            <!-- Accept/reject suggestions -->
<ManualOrganizer />                <!-- Drag-drop organization -->
<PatternInsights />                <!-- Learned organizational patterns -->
```

**Key Features:**
- **Self-Contained**: All UI code in `.collection/ui/`
- **Offline-Capable**: Basic viewing works without server
- **Progressive Enhancement**: Advanced features when server runs
- **Real-Time Updates**: WebSocket-powered live pipeline monitoring
- **Responsive Design**: Works on desktop, tablet, mobile
- **Curation Interface**: Visual organization and pattern learning

### User Experience Flows

#### Minimal Level User Flow

**Zero-Install CLI Workflow:**
1. **Drop-in Setup**
   - Download `.collection/` folder
   - Copy to any directory with content
   - Run `python -m .collection analyze`

2. **Basic Management**
   - `python -m .collection update` - Run full pipeline
   - `nu .collection/view.nu` - Interactive CLI browsing
   - `open .collection/dashboard.html` - Static HTML viewer
   - Generated `README.md`, `index.html` for documentation

**Philosophy:** Simple, portable, CLI-first. No servers, no complex setup.

#### Standard Level User Flow

**Interactive Web Experience:**
1. **Enhanced Setup**
   - Use package manager or download standard template
   - Drop `.collection/` into target directory
   - Run `python -m .collection dashboard`

2. **Full Interactive Management**
   - Visual dashboard with live pipeline monitoring
   - Interactive curation with suggestions
   - LLM provider configuration through UI
   - Scheduling and automation setup
   - Real-time progress and log viewing

**Dual-Level Philosophy:**
- **Minimal**: Portable, zero-setup CLI experience
- **Standard**: Full interactive experience for power users
- **Upgrade Path**: Start minimal, upgrade to standard when needed

## Error Handling

### LLM Connectivity
- Fast-fail methodology: test connection before processing
- Graceful degradation: allow manual descriptions if LLM unavailable
- Clear error messages with retry options

### Git Operations
- Timeout handling for fetch/pull operations
- Error categorization (network, auth, repository issues)
- Fallback to cached status if operations fail

### File System
- Permission error handling
- Large collection pagination (1000+ items)
- Concurrent scan prevention with collection locks

### YAML Processing
- Schema validation on load
- Parse error reporting with line numbers
- Automatic backup before saves

## Testing Strategy

### Unit Tests
- LLM client with mocked API responses
- Scanner plugins with mocked filesystem
- YAML schema validation
- README template rendering

### Integration Tests
- Full pipeline: analyze → scan → describe → render
- LLM provider switching
- Plugin registration and discovery
- Configuration loading from .env

### Property-Based Tests
- Collection scanning produces consistent results
- README generation is deterministic
- LLM descriptions maintain category constraints

### Acceptance Tests
- Repository migration (output matches existing .repos system)
- Multi-domain collections (repos + media)
- Web dashboard loads and displays correctly

## Implementation Status

### ✅ COMPLETE (Core Pipeline)
- Three-stage pipeline (analyze → scan → describe → render)
- LLM provider abstraction with multiple provider support
- Repository scanner plugin
- Concurrent description generation (ThreadPoolExecutor)
- YAML-based data storage
- Basic error handling and fast-fail methodology

### ❌ MISSING (Two-Tier System)

#### Minimal Level
- **Self-contained `.collection/` folder structure**
- **CLI entry point** (`python -m .collection`)
- **Static HTML dashboard** (`.collection/dashboard.html`)
- **Nushell CLI viewer** (`view.nu`)
- **Hybrid Python/Nushell renderers**
- **Standalone operation** (no package manager required)

#### Standard Level
- **Vite + Vue interactive UI** (`.collection/ui/`)
- **FastAPI backend** (`.collection/server.py`)
- **WebSocket real-time updates**
- **Curation interface** with suggestions
- **LLM provider configuration UI**
- **Scheduling and automation**

#### Package Manager (Optional)
- **Central install** (`pip install collectivist`)
- **Template generation** (`collectivist init --minimal/--standard`)
- **Upgrade utilities** (`collectivist upgrade`)
- **Collection discovery** (`collectivist list`)

### 🔄 PARTIAL
- **Configuration system** - Basic .env support, needs UI integration
- **Output generation** - Markdown/HTML working, needs Nushell integration
- **Plugin architecture** - Repository scanner complete, needs more domains

## Next Implementation Priorities

### Phase 1: Minimal Level MVP
1. **Create standalone `.collection/` template**
   - Self-contained folder with all Python scripts
   - CLI entry point and basic commands
   - Static HTML dashboard
   - Test with `.dev/.repos` collection

2. **Hybrid Nushell system**
   - `render.nu` for data processing
   - `view.nu` for interactive CLI browsing
   - Generated `collection.nu` scripts

3. **Distribution**
   - GitHub releases with `.collection/` downloads
   - Zero-install documentation

### Phase 2: Standard Level
1. **Interactive UI** (Vite + Vue)
   - Self-contained in `.collection/ui/`
   - Pipeline execution and monitoring
   - Basic configuration interface

2. **FastAPI backend**
   - REST API for collection management
   - WebSocket for real-time updates
   - Background task execution

### Phase 3: Package Manager
1. **Central distribution** (`pip install collectivist`)
2. **Template management** (init, upgrade, list commands)
3. **Convenience features** (auto-discovery, bulk operations)

The foundation is solid - we have a working pipeline. Now we need to package it into the collection-first two-tier system that transforms intentional collections into living documentation, making AI-powered curation accessible to everyone who cares about their digital hoards.