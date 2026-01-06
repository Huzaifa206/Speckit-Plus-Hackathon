"""
Data models for the Book Content Embeddings Backend.

Defines the core entities used throughout the application.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
from utils.helpers import generate_uuid, get_current_timestamp


@dataclass
class DocumentContent:
    """
    Represents the original document extracted from a Docusaurus URL.

    Attributes:
        id: Unique identifier (UUID)
        url: Original source URL
        title: Document title extracted from HTML
        content: Clean text content
        created_at: Timestamp of ingestion
        updated_at: Timestamp of last update
        word_count: Number of words in content
        char_count: Number of characters in content
    """

    id: str = field(default_factory=generate_uuid)
    url: str = ""
    title: str = ""
    content: str = ""
    created_at: datetime = field(default_factory=get_current_timestamp)
    updated_at: datetime = field(default_factory=get_current_timestamp)
    word_count: int = 0
    char_count: int = 0

    def __post_init__(self):
        """Calculate word and character counts after initialization."""
        if self.content:
            self.word_count = len(self.content.split())
            self.char_count = len(self.content)


@dataclass
class TextChunk:
    """
    Represents a segment of document content prepared for embedding generation.

    Attributes:
        id: Unique identifier (UUID)
        document_id: Reference to parent Document Content
        content: Text content of the chunk
        chunk_index: Sequential position in document (0-based)
        token_count: Number of tokens in chunk
        start_pos: Starting character position in original document
        end_pos: Ending character position in original document
        metadata: Additional metadata dictionary
    """

    id: str = field(default_factory=generate_uuid)
    document_id: str = ""
    content: str = ""
    chunk_index: int = 0
    token_count: int = 0
    start_pos: int = 0
    end_pos: int = 0
    metadata: Dict = field(default_factory=dict)

    def __post_init__(self):
        """Calculate token count after initialization."""
        if self.content:
            # Simple approximation: assume 1 token ≈ 4 characters
            self.token_count = len(self.content) // 4


@dataclass
class EmbeddingRecord:
    """
    Represents a vector embedding with associated metadata stored in Qdrant.

    Attributes:
        id: Unique identifier (UUID)
        chunk_id: Reference to source Text Chunk
        vector: Embedding vector (float array)
        content: Original chunk content (for retrieval)
        document_url: Source document URL
        document_title: Source document title
        chunk_index: Position of chunk in document
        created_at: Timestamp of embedding generation
        similarity_score: Optional similarity score for retrieval
        metadata: Additional metadata dictionary
    """

    id: str = field(default_factory=generate_uuid)
    chunk_id: str = ""
    vector: List[float] = field(default_factory=list)
    content: str = ""
    document_url: str = ""
    document_title: str = ""
    chunk_index: int = 0
    created_at: datetime = field(default_factory=get_current_timestamp)
    similarity_score: Optional[float] = None
    metadata: Dict = field(default_factory=dict)