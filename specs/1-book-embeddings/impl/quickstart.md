# Quickstart Guide: Book Content Embeddings

**Feature**: 1-book-embeddings
**Created**: 2026-01-07
**Status**: Complete

## Overview

This guide provides instructions for setting up and running the book content embeddings backend. The system crawls Docusaurus documentation sites, processes the content, generates embeddings using Cohere models, and stores them in Qdrant for retrieval.

## Prerequisites

- Python 3.8 or higher
- uv package manager
- Cohere API key
- Qdrant Cloud account and API key

## Setup Instructions

### 1. Clone and Navigate to Project

```bash
# The backend will be created in the following directory:
mkdir -p backend
cd backend
```

### 2. Initialize Python Project with uv

```bash
# Create pyproject.toml with dependencies
uv init
```

### 3. Install Dependencies

Add the following dependencies to your pyproject.toml:

```toml
[project]
name = "book-embeddings"
version = "0.1.0"
dependencies = [
    "requests>=2.31.0",
    "beautifulsoup4>=4.12.0",
    "cohere>=4.0.0",
    "qdrant-client>=1.9.0",
    "python-dotenv>=1.0.0",
    "tqdm>=4.66.0"
]
```

Install dependencies:
```bash
uv pip install -e .
```

### 4. Environment Configuration

Create a `.env` file with your API keys:

```env
COHERE_API_KEY=your-cohere-api-key
QDRANT_URL=your-qdrant-instance-url
QDRANT_API_KEY=your-qdrant-api-key
DOCS_URL=https://your-docusaurus-site.com
```

### 5. Project Structure

Create the following directory structure:

```
backend/
├── main.py
├── .env
├── pyproject.toml
├── crawler/
│   ├── __init__.py
│   └── extractor.py
├── processor/
│   ├── __init__.py
│   └── chunker.py
├── embedder/
│   ├── __init__.py
│   └── generator.py
└── storage/
    ├── __init__.py
    └── qdrant_handler.py
```

## Running the Pipeline

### Execute Full Pipeline

```bash
python main.py
```

### Run Individual Components

```bash
# Just crawl and extract
python -m crawler.extractor --url https://example-docs.com

# Just process and chunk text
python -m processor.chunker --input-file content.txt

# Just generate embeddings
python -m embedder.generator --input-file chunks.json

# Just store embeddings
python -m storage.qdrant_handler --embeddings-file embeddings.json
```

## Configuration Options

The system accepts various configuration options:

- `CHUNK_SIZE`: Target size for text chunks (default: 300)
- `CHUNK_OVERLAP`: Overlap between chunks (default: 50)
- `EMBEDDING_MODEL`: Cohere model to use (default: 'multilingual-22-12')
- `VECTOR_DIMENSION`: Expected dimension of embeddings (default: 1024)

## Sample Usage

```python
from main import main

# Run the complete pipeline with default settings
result = main(
    source_url="https://example-docusaurus-site.com",
    collection_name="book_embeddings",
    chunk_size=300,
    chunk_overlap=50
)

print(f"Processed {result['documents']} documents")
print(f"Created {result['chunks']} chunks")
print(f"Stored {result['embeddings']} embeddings")
```

## Troubleshooting

### Common Issues

1. **API Rate Limits**: If encountering rate limits, reduce the concurrency or add delays between requests.

2. **Memory Issues**: For large documents, process content in batches or increase system memory.

3. **Connection Errors**: Verify API keys and network connectivity to external services.

### Logging

The system logs detailed information to help diagnose issues. Enable debug logging by setting the environment variable:

```bash
export LOG_LEVEL=DEBUG
```

## Next Steps

1. Customize the chunking algorithm for your specific content
2. Adjust embedding parameters for optimal retrieval performance
3. Set up monitoring for production deployments
4. Implement error recovery mechanisms for robust operation