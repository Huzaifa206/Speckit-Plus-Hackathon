"""
Base service classes for the Book Content Embeddings Backend.

Defines common functionality and interfaces for all service classes.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from utils.logger import get_logger
from utils.exceptions import BookEmbeddingsError


class BaseService(ABC):
    """
    Base class for all services in the application.

    Provides common functionality like logging, error handling, and configuration access.
    """

    def __init__(self, name: str = None):
        """
        Initialize the base service.

        Args:
            name: Optional name for the service; defaults to class name if not provided
        """
        self.name = name or self.__class__.__name__
        self.logger = get_logger(self.name)

    def execute(self, *args, **kwargs) -> Any:
        """
        Execute the service operation with common error handling.

        Args:
            *args: Positional arguments for the operation
            **kwargs: Keyword arguments for the operation

        Returns:
            Result of the operation
        """
        try:
            self.logger.info(f"Starting execution of {self.name}")
            result = self._execute(*args, **kwargs)
            self.logger.info(f"Successfully completed execution of {self.name}")
            return result
        except BookEmbeddingsError:
            # Re-raise known application errors
            raise
        except Exception as e:
            # Wrap unexpected errors
            error_msg = f"Unexpected error in {self.name}: {str(e)}"
            self.logger.error(error_msg)
            raise BookEmbeddingsError(error_msg) from e

    @abstractmethod
    def _execute(self, *args, **kwargs) -> Any:
        """
        Abstract method that must be implemented by subclasses.

        Args:
            *args: Positional arguments for the operation
            **kwargs: Keyword arguments for the operation

        Returns:
            Result of the operation
        """
        pass


class CrawlerService(BaseService, ABC):
    """Base class for crawler services."""

    def __init__(self):
        super().__init__("CrawlerService")


class ProcessorService(BaseService, ABC):
    """Base class for processor services."""

    def __init__(self):
        super().__init__("ProcessorService")


class EmbedderService(BaseService, ABC):
    """Base class for embedder services."""

    def __init__(self):
        super().__init__("EmbedderService")


class StorageService(BaseService, ABC):
    """Base class for storage services."""

    def __init__(self):
        super().__init__("StorageService")