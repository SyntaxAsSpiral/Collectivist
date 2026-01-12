# Implementation Plan: Collectivist

## Overview

This implementation focuses on verifying and generalizing the existing repo indexer across distributed collection seeds, then creating collection-specific implementations.

## Tasks

### Foundation & Generalization

- [ ] 1. Verify Path Agnosticism of Existing Scripts
  - Test repo indexer scripts in all four collection seed locations
  - Ensure scripts work without hardcoded paths
  - _Requirements: 2.1, 2.5_

- [ ] 1.1 Test repo indexer in all collection seed locations
  - Test in `Z:\Documents\.collectivist`
  - Test in `C:\Users\synta.ZK-ZRRH\.dev\.drift\.collectivist`
  - Test in `Z:\Images\.collectivist`
  - Document any path-specific issues found
  - _Requirements: 2.1_

- [ ] 2. Extract Generalization Patterns from Repo Indexer
  - Analyze existing repo indexer architecture
  - Document the Analyzer → Scanner → Describer → Renderer flow
  - Extract scanner interface pattern for plugin architecture
  - Extract metadata schema patterns for extensibility
  - Extract AI description patterns for reuse
  - _Requirements: 3.1, 4.1, 4.2, 4.3, 4.4_

- [ ] 3. Design Collection Type Detection System
  - Define collection type detection rules for each type
  - Implement collection type detector script
  - _Requirements: 2.1, 2.2_

### Repository Collections (Already Implemented)

- [ ] 4. Verify Repository Collection Implementation
  - Confirm existing repo indexer covers all repository requirements
  - Test git metadata extraction, README parsing, AI descriptions
  - Ensure README generation works properly
  - _Requirements: 1.1, 2.2_

### Document Collections

- [ ] 5. Implement Document Collection Support
  - Design document collection index format (file types, word counts, modification dates)
  - Implement document scanner (metadata extraction, content summaries)
  - Create document collection README template (file statistics, recent changes)
  - _Requirements: 1.2, 2.2, 3.2, 6.1, 6.3_

### Media Collections

- [ ] 6. Implement Media Collection Support
  - Design media collection index format (dimensions, duration, EXIF data)
  - Implement media scanner (metadata extraction, preview generation)
  - Create media collection README template (galleries, timelines, metadata summaries)
  - _Requirements: 1.3, 2.2, 3.2, 6.1, 6.3_

### Research Collections

- [ ] 7. Implement Research Collection Support
  - Design research collection index format (citations, abstracts, publication data, DOIs)
  - Implement research scanner (PDF parsing, citation extraction, academic metadata)
  - Create research collection README template (citation lists, topic clustering, publication timelines)
  - _Requirements: 1.4, 2.2, 3.2, 6.1, 6.3_

### Integration & Testing

- [ ] 8. Checkpoint - Verify collection-specific implementations
  - Test each collection type in its respective seed location
  - Ensure all collection types generate appropriate indexes and READMEs
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 9. Final checkpoint - Complete system verification
  - Verify path agnosticism across all collection types
  - Test end-to-end functionality for each collection seed
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Repository collections already implemented via existing repo indexer
- Each collection type gets custom index format, scanner, and README template
- Path agnosticism is critical for distributed seed deployment
- Build incrementally: Foundation → Repos (verify) → Documents → Media → Research