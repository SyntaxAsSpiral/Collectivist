# Product Overview

**Collectivist** is an AI-powered collection curator that transforms semantically coherent collections into living documentation substrates. It uses a distributed seed-to-trunk architecture where portable collection seeds automatically centralize to a coordination trunk for unified curation and documentation.

## Core Philosophy

- **Domain-specific intelligence** over generic sorting
- **Collection overview generation** with LLM-powered contextual summaries
- **Template-based rendering** for deterministic, reproducible documentation
- **Curation that feels magical** through context-aware organization

## Key Features

- **Multi-format collections**: Repositories, Obsidian vaults, documents, media files, research papers, creative projects, datasets
- **Seed deployment**: Drop `.collectivist/` seed anywhere, works immediately with automatic trunk centralization
- **Plugin architecture**: Domain-specific scanners for different collection types
- **Multi-stage pipeline**: Analyzer → Scanner → Describer → Renderer
- **Web interface**: Simple trunk interface with SQLite storage for unified collection management
- **LLM integration**: Multiple provider support (OpenAI, Anthropic, OpenRouter, local models)

## Target Use Cases

- Repository collections with Git metadata and semantic understanding
- Research paper collections with citation extraction and topic clustering
- Media collections with timeline organization and metadata extraction
- Creative project collections with version tracking and asset linking
- Dataset collections with schema inference and sample previews

## Architecture Modes

- **Seed**: Minimal mode with `.collectivist/` seed drop-in system that auto-detects collection type
- **Trunk**: Central coordination with SQLite storage, web interface, and unified collection management
- **Distributed**: Full workflow with multiple seeds centralizing to trunk for intelligent processing and documentation