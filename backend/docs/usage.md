# Book Content Embeddings Backend - Usage Guide

## Overview

The Book Content Embeddings Backend is a system for crawling Docusaurus documentation sites, extracting clean content, chunking it, generating embeddings using Cohere models, and storing them in Qdrant for retrieval.

## Prerequisites

- Python 3.8 or higher
- A Cohere API key
- A Qdrant Cloud account and API key
- Internet access for crawling documentation sites

## Installation

1. Clone or download the repository
2. Navigate to the `backend` directory
3. Install dependencies using uv:

```bash
cd backend
uv pip install -e .
```

## Configuration

The system uses environment variables for configuration. Copy the `.env` file and update with your credentials:

```bash
cp .env .env.local
```

Then edit `.env.local` with your settings:

### Required Configuration

- `COHERE_API_KEY`: Your Cohere API key
- `QDRANT_URL`: Your Qdrant Cloud instance URL
- `QDRANT_API_KEY`: Your Qdrant API key

### Optional Configuration

- `DOCS_URL`: The Docusaurus documentation site URL to process (default: `https://example-docusaurus-site.com`)
- `CHUNK_SIZE`: Target size for text chunks (default: 300)
- `CHUNK_OVERLAP`: Overlap between chunks (default: 50)
- `VECTOR_DIMENSION`: Expected dimension of embeddings (default: 1024)
- `EMBEDDING_MODEL`: Cohere model to use (default: `multilingual-22-12`)
- `LOG_LEVEL`: Logging level (default: `INFO`)

## Usage

### Command Line Interface

Run the pipeline using the CLI:

```bash
# Basic usage with default settings
python -m cli --docs-url https://your-docusaurus-site.com

# With custom chunk size
python -m cli --docs-url https://your-site.com --chunk-size 400

# With verbose logging
python -m cli --docs-url https://your-site.com --verbose

# Dry run to see what would be done
python -m cli --docs-url https://your-site.com --dry-run
```

### Direct Python Usage

```python
from main import main

# Set environment variables or update config before running
main()
```

## Pipeline Stages

The system processes content through these stages:

1. **Crawling**: Extract clean content from Docusaurus URLs
2. **Chunking**: Break content into appropriately sized chunks
3. **Embedding**: Generate vector embeddings using Cohere
4. **Storage**: Store embeddings in Qdrant with metadata

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `COHERE_API_KEY` | Cohere API key (required) | - |
| `QDRANT_URL` | Qdrant instance URL (required) | - |
| `QDRANT_API_KEY` | Qdrant API key (required) | - |
| `DOCS_URL` | Documentation site to process | `https://example-docusaurus-site.com` |
| `CHUNK_SIZE` | Target size for text chunks | `300` |
| `CHUNK_OVERLAP` | Overlap between chunks | `50` |
| `VECTOR_DIMENSION` | Expected embedding dimension | `1024` |
| `EMBEDDING_MODEL` | Cohere model to use | `multilingual-22-12` |
| `LOG_LEVEL` | Logging level | `INFO` |

## CLI Options

```
--docs-url URL            URL of the Docusaurus documentation site
--chunk-size SIZE         Target size for text chunks
--chunk-overlap SIZE      Overlap between chunks
--collection-name NAME    Qdrant collection name
--model MODEL             Embedding model to use
--include-subpages        Include subpages when crawling
--dry-run                 Show what would be done without processing
--verbose, -v             Enable verbose logging
```

## Troubleshooting

### Common Issues

1. **API Rate Limits**: If you encounter rate limits from Cohere, consider adding delays between requests or upgrading your API plan.

2. **Memory Issues**: For very large documentation sites, the system processes content in batches to manage memory usage.

3. **Crawling Issues**: Some Docusaurus sites may have specific structures. The system attempts to extract content from common selectors.

### Logging

Enable verbose logging with the `--verbose` flag or by setting `LOG_LEVEL=DEBUG` to get more detailed information about the processing steps.

## Performance

The system includes performance monitoring that reports:
- Processing times for each stage
- Content extraction and chunking rates
- Embedding generation rates
- Storage rates

Success criteria include:
- Processing rate above 10 chunks per second
- Embedding success rate above 95%
- Storage reliability above 99%
- Total pipeline completion within 30 minutes for medium-sized sites