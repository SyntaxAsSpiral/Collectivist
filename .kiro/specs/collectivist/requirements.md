# Requirements Document

## Introduction

Collectivist is an AI-powered collection curator that transforms semantically coherent collections into living documentation substrates. The system uses a distributed-to-centralized architecture where portable `.collectivist` seeds are deployed across different collection locations and automatically centralize to a coordination trunk for unified curation and documentation generation.

## Glossary

- **Collection**: A semantically coherent set of items (repositories, documents, media files, research papers, etc.)
- **Trunk**: Central coordination point that aggregates and processes data from distributed collection seeds
- **Seed**: A portable `.collectivist` folder deployed at a specific collection location
- **Scanner**: Domain-specific component that extracts metadata from collection items
- **Analyzer**: Component that processes raw collection data and determines structure
- **Describer**: AI-powered component that generates contextual summaries and categorizations
- **Renderer**: Component that transforms analyzed data into documentation using templates
- **Collection_Config**: Configuration file (`.collection/config.yaml`) that defines collection behavior
- **Centralization**: Process of aggregating data from distributed collection seeds to the trunk
- **Pipeline**: Multi-stage processing flow: Analyzer → Scanner → Describer → Renderer

## Requirements

### Requirement 1: Multi-Format Collection Support

**User Story:** As a curator, I want to organize different types of collections (repositories, documents, media, research papers), so that I can apply consistent curation across diverse content types.

#### Acceptance Criteria

1. WHEN a collection contains repositories, THE System SHALL extract git metadata, commit history, and README content
2. WHEN a collection contains documents, THE System SHALL extract file metadata, content summaries, and modification timestamps
3. WHEN a collection contains media files, THE System SHALL extract metadata, creation dates, and generate preview information
4. WHEN a collection contains research papers, THE System SHALL extract citations, abstracts, and publication metadata
5. WHERE multiple content types exist in one collection, THE System SHALL handle mixed-format scanning appropriately

### Requirement 2: Distributed Collection Architecture with Type Detection

**User Story:** As a curator, I want portable `.collectivist` seeds to automatically detect their collection type and produce custom indexes, so that each collection is processed with domain-appropriate logic.

#### Acceptance Criteria

1. WHEN a `.collectivist` folder is deployed, THE System SHALL automatically detect the collection type based on content analysis
2. WHEN collection type is detected, THE System SHALL produce a custom index format appropriate for that collection type
3. THE System SHALL support repository collections, document collections, media collections, and research paper collections
4. WHEN collection type cannot be determined, THE System SHALL default to generic file collection processing
5. THE System SHALL store collection type metadata for consistent processing across runs

### Requirement 3: Plugin Architecture for Domain-Specific Scanning

**User Story:** As a developer, I want to extend the system with domain-specific scanners, so that I can add support for new collection types without modifying core code.

#### Acceptance Criteria

1. THE System SHALL load scanner plugins from a defined plugin directory
2. WHEN a new file type is encountered, THE System SHALL route it to the appropriate scanner plugin
3. WHEN no specific scanner exists, THE System SHALL fall back to generic file metadata extraction
4. THE System SHALL allow scanner plugins to define their own metadata schemas
5. THE System SHALL provide a standard plugin interface for consistent integration

### Requirement 4: Multi-Stage Processing Pipeline

**User Story:** As a system architect, I want clear separation between analysis, scanning, description, and rendering stages, so that the system is maintainable and each stage can be optimized independently.

#### Acceptance Criteria

1. WHEN processing begins, THE Analyzer SHALL determine collection structure and item types
2. WHEN analysis is complete, THE Scanner SHALL extract metadata using appropriate domain-specific logic
3. WHEN scanning is complete, THE Describer SHALL generate AI-powered summaries and categorizations
4. WHEN description is complete, THE Renderer SHALL generate documentation using configured templates
5. THE System SHALL allow each stage to be run independently for debugging and incremental processing

### Requirement 5: AI-Powered Contextual Description

**User Story:** As a curator, I want AI-generated descriptions and categorizations for collection items, so that I can understand and organize large collections without manual review.

#### Acceptance Criteria

1. WHEN processing collection items, THE Describer SHALL generate one-sentence technical summaries
2. WHEN generating descriptions, THE Describer SHALL assign categories from a configurable taxonomy
3. WHEN multiple LLM providers are configured, THE System SHALL support fallback between providers
4. WHEN LLM services are unavailable, THE System SHALL continue processing with metadata-only descriptions
5. THE System SHALL preserve existing descriptions and only generate new ones for items with null descriptions

### Requirement 6: Template-Based Documentation Rendering with README Generation

**User Story:** As a documentation maintainer, I want each collection to generate its own README file with deterministic formatting, so that every collection has discoverable documentation at its root.

#### Acceptance Criteria

1. THE System SHALL generate a README.md file at the root of each collection directory
2. WHEN generating READMEs, THE System SHALL perform deeper content scanning to extract meaningful summaries
3. THE System SHALL use collection-type-specific README templates for appropriate formatting
4. WHEN README generation requires content analysis, THE System SHALL scan file contents beyond just metadata
5. THE System SHALL preserve manual edits in designated sections while regenerating automated content

### Requirement 7: Web Interface for Non-Terminal Users

**User Story:** As a non-technical user, I want a web interface to configure and monitor collection curation, so that I can use the system without command-line expertise.

#### Acceptance Criteria

1. THE Web_Interface SHALL provide collection discovery and status monitoring
2. WHEN collections are found, THE Web_Interface SHALL display processing status and generated summaries
3. THE Web_Interface SHALL allow configuration of LLM providers and processing options
4. WHEN processing is running, THE Web_Interface SHALL show real-time progress updates
5. THE Web_Interface SHALL provide manual trigger controls for re-processing collections

### Requirement 8: Configuration Management

**User Story:** As a system administrator, I want flexible configuration options at multiple levels, so that I can customize behavior for different collections and deployment scenarios.

#### Acceptance Criteria

1. THE System SHALL support global configuration for default behaviors and LLM settings
2. WHEN a `.collection/config.yaml` exists, THE System SHALL override global settings with collection-specific configuration
3. THE System SHALL validate configuration files and provide clear error messages for invalid settings
4. WHEN configuration changes, THE System SHALL apply new settings without requiring restart
5. THE System SHALL provide configuration templates and documentation for common use cases

### Requirement 9: Incremental Processing and Caching

**User Story:** As a performance-conscious user, I want the system to avoid re-processing unchanged items, so that large collections can be updated efficiently.

#### Acceptance Criteria

1. WHEN items haven't changed since last processing, THE System SHALL skip re-analysis and use cached results
2. WHEN new items are added, THE System SHALL process only the new items and merge with existing data
3. THE System SHALL detect file modifications using timestamps and checksums
4. WHEN forced refresh is requested, THE System SHALL re-process all items regardless of cache status
5. THE System SHALL store processing metadata to enable resumable operations after interruption

### Requirement 10: Error Handling and Resilience

**User Story:** As a system operator, I want robust error handling that doesn't stop processing when individual items fail, so that large collections can be processed reliably.

#### Acceptance Criteria

1. WHEN individual items fail processing, THE System SHALL log errors and continue with remaining items
2. WHEN LLM services are temporarily unavailable, THE System SHALL retry with exponential backoff
3. WHEN file access fails, THE System SHALL record the error and mark the item as inaccessible
4. THE System SHALL provide detailed error logs with context for debugging failed operations
5. WHEN critical errors occur, THE System SHALL save partial progress before terminating

### Requirement 11: Trunk Data Management and Web Interface

### Requirement 12: Collection Discovery and Registration

**User Story:** As a system administrator, I want the trunk to automatically discover and register distributed collection seeds, so that new collections are integrated without manual configuration.

#### Acceptance Criteria

1. THE Trunk SHALL scan configured paths for `.collectivist` folders and register them automatically
2. WHEN new collection seeds are found, THE Trunk SHALL add them to the SQLite registry with detected metadata
3. THE Trunk SHALL coordinate processing across multiple collection seeds in parallel
4. WHEN collection seeds are removed, THE Trunk SHALL mark them as inactive in the registry
5. THE System SHALL maintain collection seed identity and provenance in all aggregated data