#!/usr/bin/env python3
"""
Collection Schema Definitions
Defines the schema structure for each collection type with proper status glyphs and categories
"""

from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class CollectionTypeSchema:
    """Schema definition for a collection type"""
    collection_type: str
    status_glyph: str
    default_categories: List[str]
    scanner_config_defaults: Dict[str, Any]
    description: str


# Collection Type Schema Definitions
COLLECTION_SCHEMAS = {
    "repositories": CollectionTypeSchema(
        collection_type="repositories",
        status_glyph="✓",
        default_categories=[
            "phext_hyperdimensional",     # Multi-dimensional text systems
            "ai_llm_agents",             # AI agents and LLM infrastructure
            "terminal_ui",               # Terminal UI frameworks and components
            "creative_aesthetic",        # Art, music, visualization tools
            "dev_tools",                 # Development utilities and build tools
            "esoteric_experimental",     # Experimental and occult systems
            "system_infrastructure",     # System-level networking tools
            "utilities_misc"             # General utilities and miscellaneous
        ],
        scanner_config_defaults={
            "always_pull": {},           # Repos to auto-pull: {repo_name: true}
            "fetch_timeout": 30          # Git fetch timeout in seconds
        },
        description="Git-aware metadata, commit summaries, category taxonomy"
    ),
    
    "media": CollectionTypeSchema(
        collection_type="media",
        status_glyph="🎵",
        default_categories=[
            "music_albums",              # Full album collections
            "music_singles",             # Individual tracks
            "video_movies",              # Movie files
            "video_series",              # TV series and episodes
            "images_photos",             # Photography collections
            "images_artwork",            # Digital art and graphics
            "audio_podcasts",            # Podcast episodes
            "video_tutorials"            # Educational video content
        ],
        scanner_config_defaults={
            "extract_metadata": True,    # Extract ID3, EXIF, etc.
            "generate_thumbnails": False, # Create preview thumbnails
            "supported_formats": {       # File extensions to scan
                "audio": [".mp3", ".flac", ".wav", ".m4a"],
                "video": [".mp4", ".mkv", ".avi", ".mov"],
                "image": [".jpg", ".png", ".gif", ".webp"]
            }
        },
        description="Timeline-aware organization, mood/genre inference"
    ),
    
    "documents": CollectionTypeSchema(
        collection_type="documents",
        status_glyph="📄",
        default_categories=[
            "research_papers",           # Academic and research documents
            "technical_docs",            # Technical documentation
            "reference_manuals",         # Reference and manual documents
            "creative_writing",          # Creative writing and literature
            "business_docs",             # Business and professional documents
            "personal_notes",            # Personal notes and journals
            "legal_documents",           # Legal and official documents
            "educational_materials"     # Educational and learning materials
        ],
        scanner_config_defaults={
            "extract_text": True,       # Extract text content for search
            "supported_formats": [      # Document types to scan
                ".pdf", ".docx", ".md", ".txt", ".rtf"
            ],
            "max_text_length": 5000     # Max chars to extract per document
        },
        description="Text content extraction, document metadata, reading status"
    ),
    
    "research": CollectionTypeSchema(
        collection_type="research",
        status_glyph="🔬",
        default_categories=[
            "primary_sources",           # Original research and data
            "literature_review",         # Academic literature and reviews
            "methodology_papers",        # Research methodology documents
            "data_analysis",             # Analysis and statistical documents
            "theoretical_frameworks",   # Theoretical and conceptual papers
            "case_studies",              # Case study documentation
            "experimental_results",     # Experimental data and results
            "meta_analysis"              # Meta-analysis and systematic reviews
        ],
        scanner_config_defaults={
            "extract_citations": True,  # Extract citation metadata
            "track_reading_status": True, # Track read/unread status
            "supported_formats": [
                ".pdf", ".bib", ".ris", ".md"
            ]
        },
        description="Citation extraction, topic clustering, reading status"
    ),
    
    "creative": CollectionTypeSchema(
        collection_type="creative",
        status_glyph="🎨",
        default_categories=[
            "digital_art",               # Digital artwork and graphics
            "music_production",          # Music creation and production
            "video_projects",            # Video creation and editing
            "writing_projects",          # Creative writing projects
            "design_assets",             # Design elements and assets
            "photography_shoots",        # Photography project collections
            "mixed_media",               # Multi-media creative projects
            "work_in_progress"           # Ongoing creative work
        ],
        scanner_config_defaults={
            "track_versions": True,      # Track project versions
            "link_assets": True,         # Link related project assets
            "supported_formats": {
                "projects": [".psd", ".ai", ".sketch", ".fig"],
                "assets": [".png", ".jpg", ".svg", ".mp3", ".mp4"]
            }
        },
        description="Version tracking, mood boards, linked assets"
    ),
    
    "datasets": CollectionTypeSchema(
        collection_type="datasets",
        status_glyph="📊",
        default_categories=[
            "structured_data",           # CSV, JSON, database exports
            "time_series",               # Time-based data collections
            "text_corpora",              # Text and language datasets
            "image_datasets",            # Image classification datasets
            "audio_datasets",            # Audio and speech datasets
            "scientific_data",           # Scientific measurement data
            "survey_data",               # Survey and questionnaire data
            "experimental_data"          # Experimental results and observations
        ],
        scanner_config_defaults={
            "infer_schema": True,        # Automatically infer data schema
            "sample_size": 100,          # Number of records to sample
            "supported_formats": [
                ".csv", ".json", ".parquet", ".xlsx", ".sqlite"
            ]
        },
        description="Schema inference, sample previews, provenance notes"
    ),
    
    "obsidian": CollectionTypeSchema(
        collection_type="obsidian",
        status_glyph="🧠",
        default_categories=[
            "knowledge_base",            # Core knowledge, concepts, and foundational information
            "personal_notes",            # Personal thoughts, reflections, and journaling
            "research_notes",            # Research findings, studies, and academic content
            "project_docs",              # Project documentation, plans, and specifications
            "creative_writing",          # Stories, poems, creative writing, and fiction
            "learning_notes",            # Study notes, tutorials, and learning materials
            "utilities_misc"             # Templates, utilities, and miscellaneous notes
        ],
        scanner_config_defaults={
            "extract_frontmatter": True, # Extract YAML frontmatter
            "extract_tags": True,        # Extract #tags from content
            "extract_links": True,       # Extract [[wiki links]]
            "supported_formats": [".md"] # Only markdown files
        },
        description="Knowledge management with frontmatter, tags, and wiki links"
    )
}


def get_collection_schema(collection_type: str) -> CollectionTypeSchema:
    """Get schema definition for a collection type"""
    if collection_type not in COLLECTION_SCHEMAS:
        raise ValueError(f"Unknown collection type: {collection_type}")
    return COLLECTION_SCHEMAS[collection_type]


def list_collection_types() -> List[str]:
    """List all available collection types"""
    return list(COLLECTION_SCHEMAS.keys())


def generate_collection_config(
    collection_type: str,
    name: str,
    path: str,
    custom_categories: List[str] = None,
    custom_scanner_config: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Generate collection.yaml configuration for a specific type.
    
    Args:
        collection_type: Type of collection (repositories, media, etc.)
        name: Collection name
        path: Collection path
        custom_categories: Override default categories
        custom_scanner_config: Override default scanner config
        
    Returns:
        Dict that can be saved as collection.yaml
    """
    schema = get_collection_schema(collection_type)
    
    # Build configuration
    config = {
        # REQUIRED FIELDS (in order per requirements)
        'collection_type': collection_type,
        'status': schema.status_glyph,
        'name': name,
        'path': path,
        'categories': custom_categories or schema.default_categories,
        
        # OPTIONAL FIELDS
        'exclude_hidden': True,
        'scanner_config': custom_scanner_config or schema.scanner_config_defaults.copy(),
        'schedule': {
            'enabled': False,
            'interval_days': 7,
            'operations': ['scan', 'describe', 'render'],
            'auto_file': False,
            'confidence_threshold': 0.8
        }
    }
    
    return config