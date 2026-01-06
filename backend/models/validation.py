"""
Validation functions for the Book Content Embeddings Backend.

Validates data models and ensures they meet specified constraints.
"""

import re
from typing import Any, List
from urllib.parse import urlparse
from .entities import DocumentContent, TextChunk, EmbeddingRecord
from ..utils.exceptions import ValidationError


def is_valid_url(url: str) -> bool:
    """Check if a URL is valid."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def validate_document_content(doc: DocumentContent) -> List[str]:
    """Validate a DocumentContent entity and return a list of validation errors."""
    errors = []

    # Validate URL
    if not doc.url:
        errors.append("URL cannot be empty")
    elif not is_valid_url(doc.url):
        errors.append(f"Invalid URL format: {doc.url}")

    # Validate content
    if not doc.content.strip():
        errors.append("Content cannot be empty or whitespace only")

    # Validate title length
    if len(doc.title) > 500:
        errors.append(f"Title exceeds maximum length of 500 characters: {len(doc.title)}")

    return errors


def validate_text_chunk(chunk: TextChunk) -> List[str]:
    """Validate a TextChunk entity and return a list of validation errors."""
    errors = []

    # Validate document_id
    if not chunk.document_id:
        errors.append("Document ID cannot be empty")

    # Validate content
    if not chunk.content.strip():
        errors.append("Chunk content cannot be empty or whitespace only")

    # Validate chunk index
    if chunk.chunk_index < 0:
        errors.append(f"Chunk index must be non-negative: {chunk.chunk_index}")

    # Validate token count
    if chunk.token_count < 0:
        errors.append(f"Token count cannot be negative: {chunk.token_count}")

    # Validate positions
    if chunk.start_pos < 0 or chunk.end_pos < 0:
        errors.append(f"Start and end positions must be non-negative: {chunk.start_pos}, {chunk.end_pos}")
    if chunk.start_pos > chunk.end_pos:
        errors.append(f"Start position cannot be greater than end position: {chunk.start_pos} > {chunk.end_pos}")

    return errors


def validate_embedding_record(embedding: EmbeddingRecord) -> List[str]:
    """Validate an EmbeddingRecord entity and return a list of validation errors."""
    errors = []

    # Validate chunk_id
    if not embedding.chunk_id:
        errors.append("Chunk ID cannot be empty")

    # Validate vector
    if not embedding.vector:
        errors.append("Embedding vector cannot be empty")
    else:
        # Check that all values in vector are finite numbers
        for i, val in enumerate(embedding.vector):
            if not isinstance(val, (int, float)) or not (float('-inf') < val < float('inf')):
                errors.append(f"Vector value at index {i} is not a finite number: {val}")

    # Validate content
    if not embedding.content.strip():
        errors.append("Embedding content cannot be empty or whitespace only")

    # Validate similarity score if present
    if embedding.similarity_score is not None:
        if not isinstance(embedding.similarity_score, (int, float)):
            errors.append(f"Similarity score must be a number: {embedding.similarity_score}")
        elif not (0 <= embedding.similarity_score <= 1):
            errors.append(f"Similarity score must be between 0 and 1: {embedding.similarity_score}")

    return errors


def validate_entity(entity: Any) -> None:
    """
    Validate an entity and raise ValidationError if validation fails.

    Args:
        entity: The entity to validate (DocumentContent, TextChunk, or EmbeddingRecord)

    Raises:
        ValidationError: If validation fails
    """
    errors = []

    if isinstance(entity, DocumentContent):
        errors = validate_document_content(entity)
    elif isinstance(entity, TextChunk):
        errors = validate_text_chunk(entity)
    elif isinstance(entity, EmbeddingRecord):
        errors = validate_embedding_record(entity)
    else:
        raise ValidationError(
            f"Unknown entity type: {type(entity)}",
            field="type",
            value=type(entity).__name__
        )

    if errors:
        raise ValidationError(
            f"Validation failed for {type(entity).__name__}: {'; '.join(errors)}",
            field="validation",
            value=entity
        )


def validate_and_return_errors(entity: Any) -> List[str]:
    """
    Validate an entity and return a list of validation errors.

    Args:
        entity: The entity to validate (DocumentContent, TextChunk, or EmbeddingRecord)

    Returns:
        List of validation errors, empty if no errors
    """
    if isinstance(entity, DocumentContent):
        return validate_document_content(entity)
    elif isinstance(entity, TextChunk):
        return validate_text_chunk(entity)
    elif isinstance(entity, EmbeddingRecord):
        return validate_embedding_record(entity)
    else:
        return [f"Unknown entity type: {type(entity)}"]