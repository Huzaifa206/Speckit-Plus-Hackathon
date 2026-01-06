# Research Document: Book Content Embeddings

**Feature**: 1-book-embeddings
**Created**: 2026-01-07
**Status**: Complete

## R0.1: Python Project Structure with uv

**Decision**: Use flat project structure with pyproject.toml for dependency management
**Rationale**: uv is a fast Python package installer that works well with modern Python projects. A flat structure is simpler for a single-application backend.
**Alternatives considered**:
- src layout: More complex for this simple application
- Monorepo structure: Not needed for a single backend application

## R0.2: Docusaurus Content Extraction

**Decision**: Use requests + BeautifulSoup combination for static content extraction with optional Playwright for dynamic content
**Rationale**: Most Docusaurus sites serve static content that can be extracted with HTML parsing. Requests and BeautifulSoup are lightweight and efficient.
**Alternatives considered**:
- Selenium: Heavier than needed for most Docusaurus sites
- Playwright: Good for dynamic content but adds complexity
- Direct API access: Not available for most Docusaurus deployments

## R0.3: Text Chunking Strategies

**Decision**: Implement sentence-aware chunking with configurable size and overlap
**Rationale**: Sentence-aware chunking preserves semantic boundaries while allowing for configurable sizes that work well with embedding models.
**Alternatives considered**:
- Fixed token length: Harder to implement without tokenizer
- Paragraph-based: May result in chunks that are too large
- Character-based: Doesn't respect semantic boundaries

## R0.4: Qdrant Integration Patterns

**Decision**: Store embeddings with rich metadata including source URL, title, and chunk information
**Rationale**: Rich metadata enables better retrieval and debugging of the RAG system.
**Alternatives considered**:
- Minimal metadata: Reduces storage but makes retrieval harder to understand
- Separate metadata storage: Adds complexity without significant benefits