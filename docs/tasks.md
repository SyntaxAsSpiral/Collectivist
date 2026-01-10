# Implementation Plan: Collectivist

## Overview

Collectivist is an AI-powered collection curator that transforms intentional collections into living documentation substrates. The system analyzes, indexes, describes, and organizes collections with intelligent pattern learning.

**Current Status:** MVP pipeline complete with advanced three-phase LLM analysis, intelligent context management, and CLI interface.

**Architecture:** Minimal drop-in system with sophisticated internals - three-phase analysis (identification, schema generation, categorization) with intelligent context compilation avoiding LLM token waste.

## Current Status & Completed Tasks

### ✅ **MVP Pipeline Complete**
- [x] **Three-Phase LLM Analysis**: Identification → Schema Generation → Categorization
- [x] **Intelligent Context Management**: Progressive disclosure, concurrent processing, token optimization
- [x] **LLM Provider Support**: OpenAI, Anthropic, OpenRouter, Ollama, LMStudio with model selection
- [x] **CLI Interface**: `analyze`, `scan`, `describe`, `render`, `update` commands
- [x] **Collection Types**: Repositories, research papers, media, creative projects, datasets, custom schemas
- [x] **Smart Optimization**: Deterministic indexing refreshes metadata, LLM descriptions preserved for existing items

### ✅ **Advanced Features Complete**
- [x] **Custom Schema Generation**: LLM generates tailored categories and metadata fields per collection
- [x] **Context Fundamentals**: Progressive disclosure, attention budget management, finite resource treatment
- [x] **Context Optimization**: Concurrent phases, observation masking, KV-cache optimization patterns
- [x] **Context Compression**: Structured summaries with artifact trail integrity
- [x] **LLM Model Selection**: Choose specific models within providers
- [x] **Configuration Management**: Environment-based config with `.env.example` template

## Immediate Next Steps

### 🔬 **Test MVP Functionality**
- [ ] **Test minimal level with .dev/.repos collection**
  - Drop `.collection/` folder into test collection
  - Run full pipeline: `python -m .collection update`
  - Verify three-phase analysis works correctly
  - Test LLM-generated custom categories and metadata fields
  - Confirm optimization (existing descriptions preserved, only new items processed)
- [ ] **Validate context management**
  - Test intelligent context compilation (Phase 1 gets overview, Phase 2 gets schema focus, Phase 3 gets categorization hints)
  - Verify concurrent Phase 2+3 execution
  - Confirm token optimization (no stuffing, structured active state)

### 🎨 **Create Standard Installation (Interactive UI)**
- [ ] **Build Vite + Vue Frontend**
  - Modern web interface for collection management
  - Real-time pipeline progress visualization
  - Configuration management UI (LLM providers, models)
  - Collection browsing and item details
- [ ] **Implement FastAPI Backend**
  - REST API for collection operations
  - WebSocket support for real-time updates
  - Background task management
  - LLM provider configuration endpoints
- [ ] **Package as Standard Template**
  - Create `collection-standard.zip` with full UI stack
  - Include build scripts and deployment instructions
  - Ensure zero-install experience with local development server

### 📦 **Implement Package Manager**
- [ ] **Create `collectivist` CLI Package**
  - `pip install collectivist` for global installation
  - `collectivist init <path>` - generate collection template
  - `collectivist add <path>` - register existing collection
  - `collectivist list` - show all collections
  - `collectivist update <path>` - run pipeline on collection
- [ ] **Distribution Infrastructure**
  - Publish to PyPI
  - Include templates for both minimal and standard installations
  - Documentation for package manager usage
- [ ] **Upgrade System**
  - `collectivist upgrade` - update existing collections to new template versions
  - Backward compatibility for configuration files
  - Migration scripts for major version changes

## Future Enhancements (Post-Standard Release)

### 🔄 **Advanced Scheduling & Automation**
- Background scheduling system for automatic pipeline runs
- Filesystem change detection with inotify/fsevents
- Configurable intervals and triggers
- Email/Slack notifications for pipeline completion

### 🎯 **Enhanced Collection Types**
- Additional scanner plugins (music libraries, document archives, research databases)
- Specialized metadata extractors for domain-specific content
- Custom collection type registration system

### 🧠 **Intelligent Curation**
- Pattern learning from user organizational decisions
- Automated folder structure suggestions
- Content clustering and relationship detection
- Curation confidence scoring and user feedback integration

### 🌐 **Web Dashboard Features**
- Visual collection browser with search/filtering
- Pipeline history and analytics
- Bulk operations and batch processing
- Export capabilities (JSON, CSV, documentation)

### 🔧 **Enterprise Features**
- Multi-user support with permission systems
- Audit logging and compliance features
- Integration APIs for external systems
- High-availability deployment patterns

## Development Philosophy

**Current Approach:** Start minimal, build sophisticated internals, expand thoughtfully
**Quality Focus:** Every feature must demonstrate clear value and maintain the elegant, compilation-substrate aesthetic
**User-Centric:** Primary interface remains the filesystem + CLI, advanced features enhance without complicating

## Success Metrics

- ✅ **MVP Pipeline**: Intelligent three-phase analysis with context optimization
- 🔄 **Standard Release**: Full web UI with package manager distribution
- 🎯 **Adoption**: Users successfully curating intentional collections
- 🧠 **Intelligence**: System adapts to individual organizational patterns
- 📚 **Documentation**: Self-maintaining collection knowledge bases

---

- [x] 1. Add structured event emission to pipeline
  - [x] 1.1 Create EventEmitter abstraction for pipeline stages
    - Define event schema: stage, current_item, progress (i/n), percent, message, level, timestamp
    - Integrate EventEmitter into analyzer.py, describer.py, readme_generator.py
    - Emit structured events instead of print statements
    - _Requirements: Structured progress events for real-time updates_

  - [x] 1.2 Update pipeline.py to support event streaming
    - Accept event callback parameter in run_full_pipeline()
    - Route all stage events through callback system
    - Maintain backward compatibility with CLI usage
    - _Requirements: Pipeline event integration_

### Milestone 1: Complete Web Interface for Non-Terminal Users

- [x] 2. Create comprehensive FastAPI backend
  - [x] 2.1 Set up FastAPI application with full API
    - Created `web/backend/main.py` with complete REST API
    - Collection management endpoints (CRUD operations)
    - Pipeline execution endpoints (all stages + full pipeline)
    - Configuration management (LLM providers, scheduling)
    - Added CORS middleware and comprehensive error handling
    - _Requirements: Complete backend API for web UI_

  - [x] 2.2 Implement organic workflow API endpoints
    - New content detection and processing endpoints
    - Curation suggestion and application endpoints
    - Pattern learning insights API
    - Drag-and-drop content organization support
    - _Requirements: Web-based organic workflow management_

  - [x] 2.3 Add WebSocket endpoint for real-time events
    - `WS /ws` - WebSocket connection for live progress updates
    - Connection manager for multiple clients
    - Broadcast pipeline events to connected clients
    - Background task status updates
    - _Requirements: Real-time progress streaming_

- [x] 3. Implement background task execution and configuration management
  - [x] 3.1 Use FastAPI BackgroundTasks for pipeline execution
    - Wrapped all pipeline stages as background tasks
    - Generate unique run IDs and track status
    - Emit WebSocket events from background tasks
    - Support task cancellation and cleanup
    - _Requirements: Non-blocking pipeline execution_

  - [x] 3.2 Add comprehensive run management
    - Track run status: queued, running, completed, failed
    - Store run results, logs, and error messages
    - Run history and analytics
    - Concurrent run management and queuing
    - _Requirements: Complete run lifecycle management_

  - [x] 3.3 Implement LLM backend configuration management
    - LLM provider selection API (OpenAI, Anthropic, OpenRouter, Local, etc.)
    - API key and endpoint configuration through web UI
    - LLM connection testing and validation
    - Model selection and parameter configuration
    - Secure credential storage and management
    - _Requirements: Complete LLM backend configuration via web UI_

### Milestone 2: Organic Workflow Integration

- [x] 4. Enhance pipeline for organic filesystem interaction
  - [x] 4.1 Add "drop and process" workflow
    - Detect new items in collection root or staging areas
    - Automatically analyze, categorize, and suggest placement
    - Generate descriptions and file items into appropriate folders
    - **Optional feature** - can be disabled via CLI flags
    - _Requirements: Seamless new content integration_

  - [x] 4.2 Implement structure-based pattern learning
    - Learn organizational patterns from existing filesystem structure + index
    - Extract placement intelligence from structural reality (no separate storage)
    - Suggest new item placement based on existing category → folder mappings
    - **Structure IS the memory** - no external pattern files needed
    - _Requirements: Intelligence from structural reality_

  - [x] 4.3 Add flexible scheduling options
    - **Manual mode** (default): CLI-only, no automation
    - **Scheduled mode**: regular indexing without curation
    - **Organic mode**: full self-organizing workflow with curation
    - Configurable via collection.yaml schedule settings
    - **Primary interface**: Web UI for scheduling configuration
    - _Requirements: Flexible workflow optionality_

### Milestone 3: Complete React Frontend for Non-Terminal Users

- [x] 4. Create comprehensive React frontend
  - [x] 4.1 Set up React application with Vite
    - Created `web/frontend/` with Vite + React + TypeScript setup
    - Configured Vite for development and production builds with API proxy
    - Main dashboard layout with sidebar navigation
    - Collection management interface (add, configure, monitor)
    - Pipeline execution interface with real-time progress
    - _Requirements: Complete web UI for non-terminal users_

  - [x] 4.2 Implement LLM backend configuration UI
    - LLM provider selection dropdown (OpenAI, Anthropic, OpenRouter, Local)
    - API key input with secure handling and validation
    - Endpoint configuration for local providers (LMStudio, Ollama)
    - Model selection and parameter tuning interface
    - Connection testing with real-time feedback
    - _Requirements: User-friendly LLM backend configuration_

  - [x] 4.3 Add organic workflow and scheduling interfaces
    - Visual curation suggestions with approve/reject buttons
    - Scheduling configuration with mode selection (manual/scheduled/organic)
    - Auto-file settings and confidence threshold sliders
    - Pattern learning insights and organizational charts
    - _Requirements: Complete organic workflow management via web UI_

### Milestone 4: Self-Healing Scanner Integration

- [ ] 5. Enhance scanner with self-healing capabilities
  - [ ] 5.1 Implement filesystem change detection
    - Detect added, removed, and moved items between scans
    - Compare current filesystem state with previous index
    - Generate healing operations (add, remove, update paths)
    - _Requirements: Self-healing index adaptation_

  - [ ] 5.2 Add structural awareness to scanners
    - Enhance CollectionItem with structural metadata (folder context, depth, organizational intent)
    - Implement context inheritance for new items based on location
    - Add pattern learning for organizational preferences
    - _Requirements: Intelligent context inheritance_

  - [ ] 5.3 Implement graceful index healing
    - Heal missing references from deleted folders/items
    - Preserve metadata when items are moved or renamed
    - Update README to reflect structural changes automatically
    - _Requirements: Zero-friction filesystem interaction_

- [ ] 5. Create minimal React frontend
### Milestone 4: Minimal State Dashboard (Primary Scheduling Interface)

- [ ] 6. Create web interface for collection management and scheduling
  - [ ] 6.1 FastAPI backend for collection and schedule management
    - `GET /collections/{id}/status` - current collection state
    - `GET /collections/{id}/schedule` - current scheduling configuration
    - `PUT /collections/{id}/schedule` - update scheduling settings
    - `POST /collections/{id}/run` - trigger manual pipeline run
    - **Primary interface for scheduling configuration**
    - _Requirements: Web-based scheduling management_

  - [ ] 6.2 Web interface for scheduling and state monitoring
    - Collection scheduling configuration panel (manual/scheduled/organic modes)
    - Auto-file settings and confidence threshold controls
    - Recent activity log and pipeline run history
    - **Main interface for all scheduling operations**
    - _Requirements: User-friendly scheduling interface_

### Milestone 5: Intelligent Curation System

- [ ] 7. Implement organizational intelligence from structure
  - [ ] 7.1 Enhance structural pattern analysis
    - Analyze folder naming conventions and organizational depth preferences
    - Track category distribution and folder utilization patterns
    - Learn from manual organizational changes over time
    - _Requirements: Organizational memory from structural reality_

  - [ ] 7.2 Add curation intelligence to scanners
    - Analyze collection growth and category distribution
    - Detect organizational patterns and suggest improvements
    - Generate folder structure suggestions based on learned preferences
    - _Requirements: Intelligent organizational suggestions_

- [ ] 8. Create gentle curation interface
  - [ ] 8.1 Add CLI curation commands
    - `collectivist suggest <collection>` - show organizational suggestions
    - `collectivist curate <collection>` - apply approved curation changes
    - `collectivist patterns <collection>` - view learned organizational patterns
    - _Requirements: CLI-first curation management_

  - [ ] 8.2 Integrate curation with dashboard (optional)
    - Visual folder structure preview in web interface
    - Accept/reject suggestions when checking dashboard
    - Pattern learning display for organizational insights
    - _Requirements: Optional visual curation management_

### Milestone 6: Persistent Registry + Scheduling

- [ ] 9. Add collection registry and scheduling
  - [ ] 9.1 Implement registry.yaml read/write
    - Create `~/.collectivist/registry.yaml` on first run
    - Registry schema: collections with id, name, path, type, last_scan
    - Read registry on server startup
    - _Requirements: Persistent collection storage_

  - [ ] 9.2 Add autonomous scheduling system
    - Background process that monitors registered collections
    - Configurable intervals for automatic pipeline runs
    - Filesystem change detection triggers for immediate processing
    - _Requirements: Autonomous collection maintenance_

- [ ] 10. Add convenience CLI commands
  - [ ] 10.1 Create unified collectivist CLI
    - `collectivist add <path>` - register new collection
    - `collectivist drop <files>` - add files to collection and process
    - `collectivist status` - show all collections and recent activity
    - `collectivist dashboard` - launch optional web interface
    - _Requirements: Primary CLI workflow interface_

### Future Enhancements (Post-MVP)

- [ ] 11. Advanced features (implement as needed)
  - Add additional scanner plugins (media, documents, music)
  - Replace in-memory storage with SQLite for durability
  - Add Celery for distributed processing
  - Expand plugin ecosystem and template system
  - Add collection analytics and insights
  - Implement real-time filesystem watching

## Checkpoint Tasks

- [ ] Checkpoint 1: After Milestone 1 completion
  - Verify pipeline emits structured events correctly
  - Test FastAPI endpoints with curl or Postman
  - Confirm WebSocket events stream properly
  - Ask user if questions arise about event system

- [ ] Checkpoint 2: After Milestone 2 completion
  - Verify React frontend connects and displays events
  - Test README auto-refresh on pipeline completion
  - Ensure progress visualization works end-to-end
  - Ask user if questions arise about frontend integration

- [ ] Checkpoint 3: After Milestone 3 completion
  - Test registry persistence across server restarts
  - Verify run history tracking works correctly
  - Ensure collection selection workflow is smooth
  - Ask user if questions arise about persistence layer

## Notes

- **Organic Interaction First**: Primary interface is filesystem + CLI, dashboard is for scheduling and state monitoring
- **Web UI for Scheduling**: Main interface for configuring automatic pipeline runs and organic curation
- **Drop and Process**: Main workflow is adding content naturally and letting system organize it
- **Autonomous Operation**: Scheduling configured via web UI minimizes manual intervention
- **Bespoke Learning**: System adapts to your organizational patterns over time
- **CLI-Centric**: Most operations available via simple CLI commands, scheduling via web UI
- **Self-Healing**: System automatically adapts to filesystem changes without user intervention

This plan prioritizes shipping the essential live loop quickly while maintaining the elegant, compilation-substrate aesthetic of Collectivist.