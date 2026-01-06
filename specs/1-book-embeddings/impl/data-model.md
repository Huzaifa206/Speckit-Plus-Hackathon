# Data Model: Book Content Embeddings

**Feature**: 1-book-embeddings
**Created**: 2026-01-07
**Status**: Complete

## Document Content Entity

Represents the original document extracted from a Docusaurus URL.

### Fields
- `id` (string): Unique identifier (UUID)
- `url` (string): Original source URL
- `title` (string): Document title extracted from HTML
- `content` (string): Clean text content
- `created_at` (datetime): Timestamp of ingestion
- `updated_at` (datetime): Timestamp of last update
- `word_count` (integer): Number of words in content
- `char_count` (integer): Number of characters in content

### Relationships
- Contains multiple Text Chunks (1 to many)

### Validation Rules
- URL must be a valid HTTP/HTTPS URL
- Content must not be empty
- Title must not exceed 500 characters

## Text Chunk Entity

Represents a segment of document content prepared for embedding generation.

### Fields
- `id` (string): Unique identifier (UUID)
- `document_id` (string): Reference to parent Document Content
- `content` (string): Text content of the chunk
- `chunk_index` (integer): Sequential position in document (0-based)
- `token_count` (integer): Number of tokens in chunk
- `start_pos` (integer): Starting character position in original document
- `end_pos` (integer): Ending character position in original document

### Relationships
- Belongs to one Document Content (many to 1)
- Associated with one Embedding Record (1 to 1)

### Validation Rules
- Content must not exceed maximum token limit for embedding model
- Chunk index must be sequential within document
- Content must not be empty

## Embedding Record Entity

Represents a vector embedding with associated metadata stored in Qdrant.

### Fields
- `id` (string): Unique identifier (UUID)
- `chunk_id` (string): Reference to source Text Chunk
- `vector` (array[float]): Embedding vector (dimension varies by model)
- `content` (string): Original chunk content (for retrieval)
- `document_url` (string): Source document URL
- `document_title` (string): Source document title
- `chunk_index` (integer): Position of chunk in document
- `created_at` (datetime): Timestamp of embedding generation
- `similarity_score` (float): Optional similarity score for retrieval

### Relationships
- Belongs to one Text Chunk (many to 1)

### Validation Rules
- Vector must match expected dimension for the embedding model
- Chunk_id must reference an existing Text Chunk
- Vector values must be finite numbers

## State Transitions

### Document Content Lifecycle
1. **Pending**: URL identified for crawling
2. **Processing**: Content being extracted and cleaned
3. **Completed**: Content successfully extracted
4. **Failed**: Error occurred during extraction

### Text Chunk Lifecycle
1. **Created**: Chunk generated from document content
2. **Ready**: Chunk validated and ready for embedding
3. **Embedded**: Embedding successfully generated
4. **Stored**: Embedding stored in vector database

### Embedding Record Lifecycle
1. **Generated**: Vector embedding created from text chunk
2. **Validated**: Embedding validated for storage
3. **Stored**: Successfully stored in Qdrant
4. **Indexed**: Available for retrieval queries