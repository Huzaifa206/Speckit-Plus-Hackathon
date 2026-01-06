"""
Custom exception classes for the Book Content Embeddings Backend.

Defines specific exception types for different error scenarios in the application.
"""

class BookEmbeddingsError(Exception):
    """Base exception class for the Book Content Embeddings application."""

    def __init__(self, message: str, error_code: str = None, details: dict = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "UNKNOWN_ERROR"
        self.details = details or {}

    def __str__(self):
        return f"[{self.error_code}] {self.message}"


class CrawlerError(BookEmbeddingsError):
    """Exception raised when there are issues with crawling or content extraction."""

    def __init__(self, message: str, url: str = None, status_code: int = None):
        super().__init__(
            message=message,
            error_code="CRAWLER_ERROR",
            details={
                "url": url,
                "status_code": status_code
            }
        )


class ContentExtractionError(CrawlerError):
    """Exception raised when content extraction fails."""

    def __init__(self, message: str, url: str = None, content_type: str = None):
        super().__init__(
            message=message,
            url=url,
            error_code="CONTENT_EXTRACTION_ERROR",
            details={
                "url": url,
                "content_type": content_type
            }
        )


class ChunkingError(BookEmbeddingsError):
    """Exception raised when text chunking fails."""

    def __init__(self, message: str, chunk_size: int = None, original_length: int = None):
        super().__init__(
            message=message,
            error_code="CHUNKING_ERROR",
            details={
                "chunk_size": chunk_size,
                "original_length": original_length
            }
        )


class EmbeddingError(BookEmbeddingsError):
    """Exception raised when embedding generation fails."""

    def __init__(self, message: str, model: str = None, text_length: int = None):
        super().__init__(
            message=message,
            error_code="EMBEDDING_ERROR",
            details={
                "model": model,
                "text_length": text_length
            }
        )


class CohereAPIError(EmbeddingError):
    """Exception raised when Cohere API calls fail."""

    def __init__(self, message: str, status_code: int = None, response_data: dict = None):
        super().__init__(
            message=message,
            error_code="COHERE_API_ERROR",
            details={
                "status_code": status_code,
                "response_data": response_data
            }
        )


class StorageError(BookEmbeddingsError):
    """Exception raised when storage operations fail."""

    def __init__(self, message: str, collection_name: str = None, operation: str = None):
        super().__init__(
            message=message,
            error_code="STORAGE_ERROR",
            details={
                "collection_name": collection_name,
                "operation": operation
            }
        )


class QdrantError(StorageError):
    """Exception raised when Qdrant operations fail."""

    def __init__(self, message: str, collection_name: str = None, operation: str = None, error_details: dict = None):
        super().__init__(
            message=message,
            collection_name=collection_name,
            operation=operation
        )
        self.details["error_details"] = error_details


class ConfigurationError(BookEmbeddingsError):
    """Exception raised when there are configuration issues."""

    def __init__(self, message: str, config_key: str = None):
        super().__init__(
            message=message,
            error_code="CONFIGURATION_ERROR",
            details={
                "config_key": config_key
            }
        )


class ValidationError(BookEmbeddingsError):
    """Exception raised when validation fails."""

    def __init__(self, message: str, field: str = None, value: str = None):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details={
                "field": field,
                "value": value
            }
        )